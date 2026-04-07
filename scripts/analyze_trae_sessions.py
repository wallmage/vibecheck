#!/usr/bin/env python3
"""Analyze TRAE chat SQLite data."""
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone

from analyze_sessions import PLATFORM_SIGNALS, MODEL_PATTERNS
from model_pricing import get_pricing


CHAT_KEY_PREFIX = 'memento/icube-ai-ng-chat-storage'


def normalize_model(model):
    model = (model or '').lower()
    for pattern, key in MODEL_PATTERNS:
        if pattern in model:
            return key
    return 'sonnet'


def estimate_tokens(text):
    return len(text) // 4


def calc_cost(model, input_tokens, cached_input_tokens, output_tokens):
    pricing = get_pricing(model, total_input_tokens=input_tokens)
    cached_input_tokens = min(cached_input_tokens, input_tokens)
    fresh_input = max(0, input_tokens - cached_input_tokens)
    return (
        fresh_input * pricing['input']
        + cached_input_tokens * pricing.get('cache_read_price', pricing['input'] * pricing['cache_read_mult'])
        + output_tokens * pricing['output']
    ) / 1_000_000


def normalize_date(value, fallback):
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw > 1_000_000_000_000:
            raw = raw / 1000.0
        return datetime.fromtimestamp(raw, tz=timezone.utc).strftime('%Y-%m-%d')
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            raw = float(text)
            if raw > 1_000_000_000_000:
                raw = raw / 1000.0
            return datetime.fromtimestamp(raw, tz=timezone.utc).strftime('%Y-%m-%d')
        return text[:10]
    return fallback


def open_db(path):
    conn = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def list_tables(conn):
    return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def parse_json_maybe(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return None


def load_chat_rows(workspace_db):
    conn = open_db(workspace_db)
    try:
        tables = list_tables(conn)
        if 'ItemTable' not in tables:
            return []
        rows = []
        for column in ('key', '[key]'):
            try:
                found = conn.execute(
                    f"SELECT {column} as row_key, value FROM ItemTable WHERE {column} LIKE ?",
                    (f'{CHAT_KEY_PREFIX}%',),
                ).fetchall()
                if found:
                    rows = found
                    break
            except sqlite3.DatabaseError:
                continue
        return rows
    finally:
        conn.close()


def recursive_walk(node, path=''):
    if isinstance(node, dict):
        for key, value in node.items():
            next_path = f'{path}.{key}' if path else key
            yield next_path, value
            yield from recursive_walk(value, next_path)
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            next_path = f'{path}[{idx}]'
            yield next_path, value
            yield from recursive_walk(value, next_path)


def collect_strings(node):
    out = []
    for _, value in recursive_walk(node):
        if isinstance(value, str) and value.strip():
            out.append(value)
    return out


def extract_message_text(message):
    content = message.get('content')
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                for key in ('text', 'content', 'value'):
                    value = item.get(key)
                    if isinstance(value, str):
                        texts.append(value)
        if texts:
            return '\n'.join(texts)
    parsed_query = message.get('parsedQuery')
    if isinstance(parsed_query, list) and parsed_query:
        return '\n'.join(str(x) for x in parsed_query if x)
    if isinstance(parsed_query, str):
        return parsed_query
    strings = collect_strings(message)
    return '\n'.join(strings)


def extract_session_model(session):
    for path, value in recursive_walk(session):
        key = path.rsplit('.', 1)[-1]
        if key in ('model', 'modelName', 'modelId') and isinstance(value, str):
            return value
    return None


def extract_message_metrics(message):
    text = extract_message_text(message)
    commands = []
    paths = []
    token_count = {'input_tokens': 0, 'output_tokens': 0}
    had_nonzero_token_count = False
    exit_codes = []
    code_block_chars = 0

    for path, value in recursive_walk(message):
        key = path.rsplit('.', 1)[-1]
        if key in ('command', 'cmd', 'terminalCommand') and isinstance(value, str):
            commands.append(value)
        elif key in ('filePath', 'path', 'relativePath') and isinstance(value, str):
            if '/' in value or '.' in Path(value).name:
                paths.append(value)
        elif key in ('exitCode', 'code') and isinstance(value, int):
            exit_codes.append(value)
        elif key in ('inputTokens', 'input_tokens') and isinstance(value, (int, float)):
            token_count['input_tokens'] += int(value)
            had_nonzero_token_count = had_nonzero_token_count or value > 0
        elif key in ('outputTokens', 'output_tokens') and isinstance(value, (int, float)):
            token_count['output_tokens'] += int(value)
            had_nonzero_token_count = had_nonzero_token_count or value > 0
        elif key in ('codeBlocks', 'codeBlockDiff') and isinstance(value, list):
            code_block_chars += sum(len(json.dumps(v, ensure_ascii=False)) for v in value)

    return {
        'text': text,
        'commands': commands,
        'paths': paths,
        'token_count': token_count,
        'has_nonzero_token_count': had_nonzero_token_count,
        'exit_codes': exit_codes,
        'code_block_chars': code_block_chars,
        'role': str(message.get('role', 'assistant')).lower(),
        'timestamp': message.get('timestamp'),
        'status': message.get('status'),
    }


def load_conversations(workspace_entry):
    rows = load_chat_rows(workspace_entry['path'])
    conversations = []

    for row in rows:
        data = parse_json_maybe(row['value'])
        if not isinstance(data, dict):
            continue
        sessions = data.get('list') if isinstance(data.get('list'), list) else []
        for session in sessions:
            if not isinstance(session, dict):
                continue
            messages = session.get('messages')
            if not isinstance(messages, list) or not messages:
                continue
            conversations.append({
                'id': session.get('id') or session.get('sessionId') or row['row_key'],
                'name': session.get('name') or session.get('title') or 'Untitled',
                'created_at': session.get('timestamp') or session.get('updatedAt') or workspace_entry['timestamp'],
                'messages': messages,
                'workspace_entry': workspace_entry,
                'session': session,
            })
    return conversations


def detect_platform(message_metrics):
    scores = defaultdict(int)
    for metric in message_metrics:
        for cmd in metric['commands']:
            for platform, signals in PLATFORM_SIGNALS.items():
                for pat in signals['bash_patterns']:
                    if pat in cmd:
                        scores[platform] += 3
        for path in metric['paths']:
            for platform, signals in PLATFORM_SIGNALS.items():
                for ext in signals['file_exts']:
                    if path.endswith(ext) or ext in path:
                        scores[platform] += 2
    return max(scores, key=scores.get) if scores else 'general'


def analyze_conversation(conversation):
    metrics = [extract_message_metrics(message) for message in conversation['messages']]
    role_counts = Counter(metric['role'] for metric in metrics)
    if role_counts['assistant'] == 0:
        return None

    model = normalize_model(extract_session_model(conversation['session']))
    assistant_messages = [metric for metric in metrics if metric['role'] == 'assistant']
    total_turns = max(1, len(assistant_messages))

    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_read = 0
    file_reads = Counter()
    all_commands = []
    failed_tools = 0
    verbose_output_chars = 0
    verbose_output_count = 0
    idle_turns = 0
    edit_like_messages = 0
    batchable_edits = 0
    chainable = 0
    git_ceremony = 0
    sleep_poll_turns = 0
    toolsearch_count = 0
    codebase_wandering = 0
    pingpong_cycles = 0

    prev_cmd_turn = False
    prev_git_turn = False
    prev_failed = False

    for metric in assistant_messages:
        text = metric['text']
        text_tokens = estimate_tokens(text)
        nonzero = metric['has_nonzero_token_count']
        input_tokens = metric['token_count']['input_tokens']
        output_tokens = metric['token_count']['output_tokens']
        if not nonzero:
            output_tokens = max(output_tokens, text_tokens)
            estimated_context = min(200000, sum(estimate_tokens(m['text']) for m in metrics if m is not metric))
            input_tokens = max(input_tokens, estimated_context + sum(estimate_tokens(cmd) for cmd in metric['commands']))
        cached_input = int(input_tokens * 0.6) if input_tokens else 0

        total_input_tokens += input_tokens
        total_output_tokens += output_tokens
        total_cache_read += cached_input

        commands = metric['commands']
        all_commands.extend(commands)
        cmd_turn = bool(commands)
        if cmd_turn and prev_cmd_turn:
            chainable += 1
        prev_cmd_turn = cmd_turn

        git_turn = bool(commands) and all(cmd.strip().startswith('git ') for cmd in commands)
        if git_turn and prev_git_turn:
            git_ceremony += 1
        prev_git_turn = git_turn

        if any('sleep ' in cmd for cmd in commands):
            sleep_poll_turns += 1

        if any(cmd.strip().startswith(('rg ', 'grep ', 'find ', 'ls ', 'tree ', 'fd ')) for cmd in commands):
            toolsearch_count += 1

        if any(cmd.strip().startswith(('cat ', 'sed ', 'head ', 'tail ', 'nl ', 'rg ', 'find ')) for cmd in commands):
            for path in metric['paths']:
                file_reads[path] += 1

        lower_text = text.lower()
        is_idle = (
            len(text.strip()) > 0
            and len(text) < 280
            and any(phrase in lower_text for phrase in ("i'll", "i will", "going to", "next i'll", "让我", "我将"))
            and not commands
            and metric['code_block_chars'] == 0
        )
        if is_idle:
            idle_turns += 1

        if len(text) > 5000 or metric['code_block_chars'] > 5000:
            verbose_output_count += 1
            verbose_output_chars += max(len(text), metric['code_block_chars'])

        if metric['code_block_chars'] > 0 or any('diff' in cmd.lower() for cmd in commands):
            edit_like_messages += 1

        failed_now = any(code not in (0, None) for code in metric['exit_codes']) or 'error' in lower_text
        if failed_now:
            failed_tools += 1
        if prev_failed and failed_now:
            pingpong_cycles += 1
        prev_failed = failed_now

    if edit_like_messages > 1:
        batchable_edits = edit_like_messages - 1

    duplicate_reads = sum(count - 1 for count in file_reads.values() if count > 1)
    read_like_count = sum(1 for cmd in all_commands if cmd.strip().startswith(('cat ', 'sed ', 'head ', 'tail ', 'rg ', 'find ', 'ls ')))
    if read_like_count >= 5:
        codebase_wandering = max(0, read_like_count - 3)

    avg_input_per_assistant = total_input_tokens / max(1, len(assistant_messages))
    avg_output_per_assistant = total_output_tokens / max(1, len(assistant_messages))
    session_context_rot = 1 if len(assistant_messages) > 12 and avg_input_per_assistant > avg_output_per_assistant * 2 else 0

    total_cost = calc_cost(model, total_input_tokens, total_cache_read, total_output_tokens)
    verbose_cost = calc_cost(model, verbose_output_chars // 4, int((verbose_output_chars // 4) * 0.6), 0)
    idle_cost = total_cost * (idle_turns / max(1, len(assistant_messages))) * 0.35
    context_rot_cost = total_cost * 0.25 if session_context_rot else 0

    return {
        'file': os.path.basename(conversation['workspace_entry']['path']),
        'timestamp': conversation['created_at'],
        'model': model,
        'platform': detect_platform(metrics),
        'total_turns': total_turns,
        'total_cost': round(total_cost, 4),
        'total_output_tokens': total_output_tokens,
        'total_cache_read': total_cache_read,
        'total_cache_create': 0,
        'cost_per_turn': round(total_cost / total_turns, 4) if total_turns > 0 else 0,
        'waste': {
            'idle_narration': {
                'turns': idle_turns,
                'cost': round(idle_cost, 4),
                'description': 'Short assistant messages that narrate the next action instead of doing it',
            },
            'chainable_bash': {
                'turns': chainable,
                'cost': round(chainable * 0.02, 4),
                'description': 'Consecutive command-heavy assistant steps that could likely be grouped',
            },
            'duplicate_reads': {
                'count': duplicate_reads,
                'cost': round(duplicate_reads * 0.02, 4),
                'description': 'Same file or path referenced multiple times in one conversation',
            },
            'toolsearch': {
                'count': toolsearch_count,
                'cost': round(toolsearch_count * 0.015, 4),
                'description': 'Repeated search/exploration actions before narrowing to a concrete change',
            },
            'failed_tools': {
                'count': failed_tools,
                'cost': round(failed_tools * 0.04, 4),
                'description': 'Failed actions or visible error loops that force retries',
            },
            'unbatched_edits': {
                'turns': batchable_edits,
                'cost': round(batchable_edits * 0.02, 4),
                'description': 'Multiple edit-like responses that could be grouped more tightly',
            },
            'sleep_poll_loops': {
                'count': sleep_poll_turns,
                'cost': round(sleep_poll_turns * 0.03, 4),
                'description': 'Polling or sleep loops that add waiting turns',
            },
            'git_ceremony': {
                'turns': git_ceremony,
                'cost': round(git_ceremony * 0.02, 4),
                'description': 'Consecutive git-only command steps that could be grouped',
            },
            'context_rot': {
                'detected': session_context_rot,
                'total_turns': total_turns,
                'cost': round(context_rot_cost, 4),
                'description': 'Conversation grew large enough that reread context likely dominated later turns',
            },
            'verbose_output': {
                'count': verbose_output_count,
                'chars': verbose_output_chars,
                'cost': round(verbose_cost, 4),
                'description': 'Large output or diff payloads that add significant reread cost',
            },
            'codebase_wandering': {
                'turns': codebase_wandering,
                'cost': round(codebase_wandering * 0.03, 4),
                'description': 'Extended exploration before acting',
            },
            'pingpong_debugging': {
                'cycles': pingpong_cycles,
                'cost': round(pingpong_cycles * 0.05, 4),
                'description': 'Repeated failure cycles across adjacent assistant steps',
            },
            'heartbeat_idle': {
                'turns': 0,
                'cost': 0,
                'description': 'Always-on heartbeat idle cost',
            },
            'workspace_bloat': {
                'tokens': 0,
                'cost': 0,
                'description': 'Large always-on system files reread every wake-up',
            },
            'memory_accumulation': {
                'detected': 0,
                'cost': 0,
                'description': 'Always-on session history growth without pruning',
            },
        },
        'review_fleet': {
            'reviewer_agents': 0,
            'reviewer_types': [],
            'agent_spawns': 0,
            'skill_calls': 0,
        },
        'project': conversation['workspace_entry']['project'],
        'date': normalize_date(conversation['created_at'], conversation['workspace_entry']['date']),
    }


def aggregate_results(results):
    n = len(results)
    total_cost = sum(r['total_cost'] for r in results)
    total_turns = sum(r['total_turns'] for r in results)

    waste_totals = defaultdict(lambda: {'turns': 0, 'count': 0, 'cost': 0})
    for r in results:
        for key, w in r['waste'].items():
            waste_totals[key]['cost'] += w['cost']
            waste_totals[key]['turns'] += w.get('turns', 0)
            waste_totals[key]['count'] += w.get('count', 0)
            waste_totals[key]['description'] = w['description']

    total_waste_raw = sum(w['cost'] for w in waste_totals.values())
    total_waste = min(total_waste_raw, total_cost * 0.85)

    total_output_tokens = sum(r['total_output_tokens'] for r in results)
    total_cache_read = sum(r['total_cache_read'] for r in results)
    total_cache_create = sum(r['total_cache_create'] for r in results)
    total_input_tokens = total_cache_read + total_cache_create

    output = {
        'summary': {
            'sessions': n,
            'date_range': f"{results[0]['date']} to {results[-1]['date']}",
            'total_cost': round(total_cost, 2),
            'avg_cost_per_session': round(total_cost / n, 2),
            'avg_turns_per_session': round(total_turns / n, 1),
            'avg_cost_per_turn': round(total_cost / total_turns, 4) if total_turns > 0 else 0,
            'total_waste': round(total_waste, 2),
            'waste_per_session': round(total_waste / n, 3),
            'waste_percentage': round(total_waste / total_cost * 100, 1) if total_cost > 0 else 0,
            'projected_cost_after_fix': round(max(0, total_cost - total_waste) / n, 2),
            'avg_context_window_tokens': round(total_input_tokens / total_turns) if total_turns > 0 else 0,
            'avg_output_tokens_per_turn': round(total_output_tokens / total_turns) if total_turns > 0 else 0,
            'avg_agent_spawns_per_session': 0.0,
            'total_agent_spawns': 0,
            'wasteful_turns_total': sum(
                r['waste']['idle_narration']['turns']
                + r['waste']['chainable_bash']['turns']
                + r['waste']['unbatched_edits']['turns']
                + r['waste']['sleep_poll_loops'].get('count', 0)
                + r['waste']['git_ceremony']['turns']
                + r['waste']['codebase_wandering']['turns']
                for r in results
            ),
            'wasteful_turns_pct': 0,
            'context_rot_sessions': sum(1 for r in results if r['waste']['context_rot']['detected']),
            'context_rot_pct': round(sum(1 for r in results if r['waste']['context_rot']['detected']) / n * 100, 1),
            'total_turns': total_turns,
            'total_output_tokens': total_output_tokens,
            'total_cache_read': total_cache_read,
            'total_cache_create': total_cache_create,
        },
        'waste_breakdown': {},
        'sessions': results,
    }
    output['summary']['wasteful_turns_pct'] = round(
        output['summary']['wasteful_turns_total'] / total_turns * 100, 1
    ) if total_turns > 0 else 0

    for key in sorted(waste_totals, key=lambda k: -waste_totals[k]['cost']):
        w = waste_totals[key]
        output['waste_breakdown'][key] = {
            'total_cost': round(w['cost'], 2),
            'per_session': round(w['cost'] / n, 3),
            'percentage_of_waste': round(w['cost'] / total_waste_raw * 100, 1) if total_waste_raw > 0 else 0,
            'description': w['description'],
        }

    projects = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0, 'waste': 0})
    for r in results:
        p = projects[r['project']]
        p['sessions'] += 1
        p['cost'] += r['total_cost']
        p['turns'] += r['total_turns']
        p['waste'] += sum(w['cost'] for w in r['waste'].values())
    output['per_project'] = {}
    for proj in sorted(projects, key=lambda p: -projects[p]['cost']):
        p = projects[proj]
        output['per_project'][proj] = {
            'sessions': p['sessions'],
            'total_cost': round(p['cost'], 2),
            'avg_cost': round(p['cost'] / p['sessions'], 2),
            'avg_turns': round(p['turns'] / p['sessions'], 1),
            'waste': round(p['waste'], 2),
            'waste_pct': round(min(p['waste'], p['cost'] * 0.85) / p['cost'] * 100, 1) if p['cost'] > 0 else 0,
        }

    models = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0})
    for r in results:
        m = models[r['model']]
        m['sessions'] += 1
        m['cost'] += r['total_cost']
        m['turns'] += r['total_turns']
    output['model_mix'] = {}
    for model in sorted(models, key=lambda m: -models[m]['cost']):
        m = models[model]
        output['model_mix'][model] = {
            'sessions': m['sessions'],
            'pct_sessions': round(m['sessions'] / n * 100, 1),
            'total_cost': round(m['cost'], 2),
            'pct_cost': round(m['cost'] / total_cost * 100, 1) if total_cost > 0 else 0,
            'avg_cost': round(m['cost'] / m['sessions'], 2),
            'avg_turns': round(m['turns'] / m['sessions'], 1),
        }

    platforms = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0, 'waste': 0})
    for r in results:
        plat = platforms[r['platform']]
        plat['sessions'] += 1
        plat['cost'] += r['total_cost']
        plat['turns'] += r['total_turns']
        plat['waste'] += sum(w['cost'] for w in r['waste'].values())
    output['platform_mix'] = {}
    for plat in sorted(platforms, key=lambda p: -platforms[p]['cost']):
        p = platforms[plat]
        output['platform_mix'][plat] = {
            'sessions': p['sessions'],
            'total_cost': round(p['cost'], 2),
            'avg_cost': round(p['cost'] / p['sessions'], 2),
            'waste_pct': round(min(p['waste'], p['cost'] * 0.85) / p['cost'] * 100, 1) if p['cost'] > 0 else 0,
        }

    output['reviewer_roi'] = {}
    total_sleep_polls = sum(r['waste'].get('sleep_poll_loops', {}).get('count', 0) for r in results)
    output['polling_summary'] = {
        'total_sleep_poll_turns': total_sleep_polls,
        'avg_per_session': round(total_sleep_polls / n, 1),
        'estimated_cost': round(total_sleep_polls * 0.03, 2),
    }
    return output


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_trae_sessions.py <sessions.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    workspace_entries = data.get('sessions', [])
    if not workspace_entries:
        print(json.dumps({'error': 'No sessions found'}))
        sys.exit(1)

    results = []
    for entry in workspace_entries:
        conversations = load_conversations(entry)
        for conversation in conversations:
            analyzed = analyze_conversation(conversation)
            if analyzed:
                results.append(analyzed)

    results.sort(key=lambda r: r['timestamp'])
    if not results:
        print(json.dumps({'error': 'No valid TRAE conversations parsed'}))
        sys.exit(1)

    print(json.dumps(aggregate_results(results), indent=2))


if __name__ == '__main__':
    main()
