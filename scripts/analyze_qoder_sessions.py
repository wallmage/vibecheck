#!/usr/bin/env python3
"""Analyze Qoder workspace SQLite data for session cost and waste patterns."""
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from analyze_sessions import MODEL_PATTERNS, PLATFORM_SIGNALS
from model_pricing import get_pricing


LIKELY_SESSION_KEY_TERMS = (
    'qoder',
    'chat',
    'conversation',
    'history',
    'session',
    'quest',
    'agent',
    'ai',
)


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
            raw /= 1000.0
        return datetime.fromtimestamp(raw, tz=timezone.utc).strftime('%Y-%m-%d')
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            raw = float(text)
            if raw > 1_000_000_000_000:
                raw /= 1000.0
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


def looks_like_message(item):
    if not isinstance(item, dict):
        return False
    keys = set(item.keys())
    if 'role' in keys and any(k in keys for k in ('content', 'text', 'parts', 'body', 'message')):
        return True
    if any(k in keys for k in ('sender', 'author', 'messageRole')) and any(k in keys for k in ('content', 'text', 'body')):
        return True
    return False


def looks_like_message_list(value):
    if not isinstance(value, list) or not value:
        return False
    return sum(1 for item in value if looks_like_message(item)) >= max(1, min(2, len(value)))


def extract_session_candidates(node, session_id=None, title=None, timestamp=None):
    candidates = []
    if isinstance(node, dict):
        messages = None
        for key in ('messages', 'messageList', 'chatMessages', 'conversation', 'items'):
            value = node.get(key)
            if looks_like_message_list(value):
                messages = value
                break
        if messages:
            candidates.append({
                'id': node.get('id') or node.get('sessionId') or node.get('conversationId') or session_id,
                'name': node.get('title') or node.get('name') or title or 'Untitled',
                'created_at': node.get('timestamp') or node.get('updatedAt') or node.get('createdAt') or timestamp,
                'messages': messages,
            })
        for key, value in node.items():
            next_id = session_id or node.get('id') or node.get('sessionId') or node.get('conversationId')
            next_title = title or node.get('title') or node.get('name')
            next_timestamp = timestamp or node.get('timestamp') or node.get('updatedAt') or node.get('createdAt')
            candidates.extend(extract_session_candidates(value, next_id, next_title, next_timestamp))
    elif isinstance(node, list):
        for item in node:
            candidates.extend(extract_session_candidates(item, session_id, title, timestamp))
    return candidates


def load_candidate_rows(workspace_db):
    conn = open_db(workspace_db)
    try:
        tables = list_tables(conn)
        if 'ItemTable' not in tables:
            return []

        rows = []
        row_key_expr = 'key'
        for candidate in ('key', '[key]'):
            try:
                conn.execute(f"SELECT {candidate} as row_key, value FROM ItemTable LIMIT 1").fetchone()
                row_key_expr = candidate
                break
            except sqlite3.DatabaseError:
                continue

        for term in LIKELY_SESSION_KEY_TERMS:
            try:
                found = conn.execute(
                    f"SELECT {row_key_expr} as row_key, value FROM ItemTable WHERE lower({row_key_expr}) LIKE ?",
                    (f'%{term}%',),
                ).fetchall()
                rows.extend(found)
            except sqlite3.DatabaseError:
                continue

        if not rows:
            try:
                rows = conn.execute(
                    f"SELECT {row_key_expr} as row_key, value FROM ItemTable LIMIT 500"
                ).fetchall()
            except sqlite3.DatabaseError:
                rows = []

        deduped = {}
        for row in rows:
            deduped[row['row_key']] = row
        return list(deduped.values())
    finally:
        conn.close()


def extract_message_text(message):
    for key in ('content', 'text', 'body', 'message'):
        value = message.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            texts = []
            for item in value:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict):
                    for nested_key in ('text', 'content', 'value', 'body'):
                        nested_value = item.get(nested_key)
                        if isinstance(nested_value, str):
                            texts.append(nested_value)
            if texts:
                return '\n'.join(texts)
    strings = collect_strings(message)
    return '\n'.join(strings)


def extract_session_model(session):
    for path, value in recursive_walk(session):
        key = path.rsplit('.', 1)[-1]
        if key in ('model', 'modelName', 'modelId') and isinstance(value, str):
            return value
    return None


def detect_role(message):
    for path, value in recursive_walk(message):
        key = path.rsplit('.', 1)[-1]
        if key in ('role', 'sender', 'author', 'messageRole') and isinstance(value, str):
            lower = value.lower()
            if 'assistant' in lower or lower == 'ai' or 'model' in lower:
                return 'assistant'
            if 'user' in lower or 'human' in lower:
                return 'user'
            if 'tool' in lower or 'system' in lower:
                return lower
    return 'assistant'


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
            code_block_chars += sum(len(json.dumps(item, ensure_ascii=False)) for item in value)

    return {
        'text': text,
        'commands': commands,
        'paths': paths,
        'token_count': token_count,
        'has_nonzero_token_count': had_nonzero_token_count,
        'exit_codes': exit_codes,
        'code_block_chars': code_block_chars,
        'role': detect_role(message),
        'timestamp': message.get('timestamp') or message.get('updatedAt') or message.get('createdAt'),
    }


def load_conversations(workspace_entry):
    rows = load_candidate_rows(workspace_entry['path'])
    conversations = []
    seen = set()

    for row in rows:
        data = parse_json_maybe(row['value'])
        if data is None:
            continue
        for session in extract_session_candidates(data):
            if not session.get('messages'):
                continue
            session_id = session.get('id') or row['row_key']
            session_key = (session_id, len(session['messages']))
            if session_key in seen:
                continue
            seen.add(session_key)
            conversations.append({
                'id': session_id,
                'name': session.get('name') or 'Untitled',
                'created_at': session.get('created_at') or workspace_entry['timestamp'],
                'messages': session['messages'],
                'workspace_entry': workspace_entry,
                'session': session,
            })

    return conversations


def detect_platform(message_metrics):
    scores = defaultdict(int)
    for metric in message_metrics:
        for cmd in metric['commands']:
            for platform_name, signals in PLATFORM_SIGNALS.items():
                for pattern in signals['bash_patterns']:
                    if pattern in cmd:
                        scores[platform_name] += 3
        for path in metric['paths']:
            for platform_name, signals in PLATFORM_SIGNALS.items():
                for extension in signals['file_exts']:
                    if path.endswith(extension) or extension in path:
                        scores[platform_name] += 2
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
            estimated_context = min(200000, sum(estimate_tokens(other['text']) for other in metrics if other is not metric))
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
    total_cost = sum(result['total_cost'] for result in results)
    total_turns = sum(result['total_turns'] for result in results)

    waste_totals = defaultdict(lambda: {'turns': 0, 'count': 0, 'cost': 0})
    for result in results:
        for key, waste in result['waste'].items():
            waste_totals[key]['cost'] += waste['cost']
            waste_totals[key]['turns'] += waste.get('turns', 0)
            waste_totals[key]['count'] += waste.get('count', 0)
            waste_totals[key]['description'] = waste['description']

    total_waste_raw = sum(waste['cost'] for waste in waste_totals.values())
    total_waste = min(total_waste_raw, total_cost * 0.85)

    total_output_tokens = sum(result['total_output_tokens'] for result in results)
    total_cache_read = sum(result['total_cache_read'] for result in results)
    total_cache_create = sum(result['total_cache_create'] for result in results)
    total_input_tokens = total_cache_read + total_cache_create

    output = {
        'summary': {
            'sessions': n,
            'total_sessions': n,
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
                result['waste']['idle_narration']['turns']
                + result['waste']['chainable_bash']['turns']
                + result['waste']['unbatched_edits']['turns']
                + result['waste']['sleep_poll_loops'].get('count', 0)
                + result['waste']['git_ceremony']['turns']
                + result['waste']['codebase_wandering']['turns']
                for result in results
            ),
            'wasteful_turns_pct': 0,
            'context_rot_sessions': sum(1 for result in results if result['waste']['context_rot']['detected']),
            'context_rot_pct': round(sum(1 for result in results if result['waste']['context_rot']['detected']) / n * 100, 1),
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

    for key in sorted(waste_totals, key=lambda item: -waste_totals[item]['cost']):
        waste = waste_totals[key]
        output['waste_breakdown'][key] = {
            'total_cost': round(waste['cost'], 2),
            'per_session': round(waste['cost'] / n, 3),
            'percentage_of_waste': round(waste['cost'] / total_waste_raw * 100, 1) if total_waste_raw > 0 else 0,
            'description': waste['description'],
        }

    projects = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0, 'waste': 0})
    for result in results:
        project = projects[result['project']]
        project['sessions'] += 1
        project['cost'] += result['total_cost']
        project['turns'] += result['total_turns']
        project['waste'] += sum(waste['cost'] for waste in result['waste'].values())
    output['per_project'] = {}
    for project_name in sorted(projects, key=lambda item: -projects[item]['cost']):
        project = projects[project_name]
        output['per_project'][project_name] = {
            'sessions': project['sessions'],
            'total_cost': round(project['cost'], 2),
            'avg_cost': round(project['cost'] / project['sessions'], 2),
            'avg_turns': round(project['turns'] / project['sessions'], 1),
            'waste': round(project['waste'], 2),
            'waste_pct': round(min(project['waste'], project['cost'] * 0.85) / project['cost'] * 100, 1) if project['cost'] > 0 else 0,
        }

    models = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0})
    for result in results:
        model = models[result['model']]
        model['sessions'] += 1
        model['cost'] += result['total_cost']
        model['turns'] += result['total_turns']
    output['model_mix'] = {}
    for model_name in sorted(models, key=lambda item: -models[item]['cost']):
        model = models[model_name]
        output['model_mix'][model_name] = {
            'sessions': model['sessions'],
            'pct_sessions': round(model['sessions'] / n * 100, 1),
            'total_cost': round(model['cost'], 2),
            'pct_cost': round(model['cost'] / total_cost * 100, 1) if total_cost > 0 else 0,
            'avg_cost': round(model['cost'] / model['sessions'], 2),
            'avg_turns': round(model['turns'] / model['sessions'], 1),
        }

    platforms = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0, 'waste': 0})
    for result in results:
        platform_name = platforms[result['platform']]
        platform_name['sessions'] += 1
        platform_name['cost'] += result['total_cost']
        platform_name['turns'] += result['total_turns']
        platform_name['waste'] += sum(waste['cost'] for waste in result['waste'].values())
    output['platform_mix'] = {}
    for platform_name in sorted(platforms, key=lambda item: -platforms[item]['cost']):
        platform_info = platforms[platform_name]
        output['platform_mix'][platform_name] = {
            'sessions': platform_info['sessions'],
            'total_cost': round(platform_info['cost'], 2),
            'avg_cost': round(platform_info['cost'] / platform_info['sessions'], 2),
            'waste_pct': round(min(platform_info['waste'], platform_info['cost'] * 0.85) / platform_info['cost'] * 100, 1) if platform_info['cost'] > 0 else 0,
        }

    output['reviewer_roi'] = {}
    total_sleep_polls = sum(result['waste'].get('sleep_poll_loops', {}).get('count', 0) for result in results)
    output['polling_summary'] = {
        'total_sleep_poll_turns': total_sleep_polls,
        'avg_per_session': round(total_sleep_polls / n, 1),
        'estimated_cost': round(total_sleep_polls * 0.03, 2),
    }
    return output


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_qoder_sessions.py <sessions.json>")
        sys.exit(1)

    with open(sys.argv[1]) as handle:
        data = json.load(handle)

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

    results.sort(key=lambda result: result['timestamp'])
    if not results:
        print(json.dumps({'error': 'No valid Qoder conversations parsed'}))
        sys.exit(1)

    print(json.dumps(aggregate_results(results), indent=2))


if __name__ == '__main__':
    main()
