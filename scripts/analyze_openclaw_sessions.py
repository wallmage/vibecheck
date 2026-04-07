#!/usr/bin/env python3
"""Analyze OpenClaw session JSONL logs for cost and waste patterns."""
import json
import os
import re
import shlex
import sys
from collections import defaultdict

from analyze_sessions import MODEL_PATTERNS, PLATFORM_SIGNALS
from model_pricing import get_pricing

READ_PREFIXES = ('cat ', 'sed ', 'nl ', 'head ', 'tail ', 'rg ', 'find ', 'ls ', 'tree ', 'wc ', 'stat ')
SEARCH_PREFIXES = ('rg ', 'grep ', 'find ', 'fd ', 'ls ', 'tree ')
WRITE_TOOL_NAMES = {'write', 'write_file', 'edit', 'apply_patch', 'patch', 'replace'}
MEANINGFUL_TOOL_NAMES = {'exec', 'bash', 'browser', 'web', 'read', 'write', 'edit', 'patch', 'mcp', 'search'}
WORKSPACE_FILES = ('SOUL.md', 'AGENTS.md', 'HEARTBEAT.md', 'IDENTITY.md', 'TOOLS.md', 'SOUVENIR.md', 'GOALS.md', 'BOOT.md')


def normalize_model(model):
    model = (model or '').lower()
    for pattern, key in MODEL_PATTERNS:
        if pattern in model:
            return key
    return 'sonnet'


def calc_cost(usage, model):
    if usage.get('cost_usd'):
        return usage['cost_usd']
    input_tokens = usage.get('input_tokens', 0)
    cached_input = usage.get('cache_read_input_tokens', 0)
    cache_create = usage.get('cache_creation_input_tokens', 0)
    fresh_input = max(0, input_tokens - cached_input - cache_create)
    output_tokens = usage.get('output_tokens', 0)
    p = get_pricing(model, total_input_tokens=input_tokens)
    return (
        fresh_input * p['input']
        + cached_input * p.get('cache_read_price', p['input'] * p['cache_read_mult'])
        + cache_create * p.get('cache_write_price', p['input'] * p['cache_create_mult'])
        + output_tokens * p['output']
    ) / 1_000_000


def walk_json(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_json(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_json(value)


def parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value > 1_000_000_000_000:
            value = value / 1000.0
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.isdigit():
            raw = int(text)
            if raw > 1_000_000_000_000:
                raw = raw / 1000.0
            return raw
    return None


def coerce_text(value):
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        chunks = []
        for key in ('text', 'content', 'body', 'message', 'output', 'result'):
            if key in value:
                chunks.append(coerce_text(value[key]))
        return '\n'.join(chunk for chunk in chunks if chunk)
    if isinstance(value, list):
        return '\n'.join(chunk for chunk in (coerce_text(item) for item in value) if chunk)
    return ''


def extract_role(record):
    for candidate in (
        record.get('role'),
        record.get('message', {}).get('role'),
        record.get('event', {}).get('role'),
    ):
        if isinstance(candidate, str) and candidate:
            return candidate.lower()

    rtype = (record.get('type') or record.get('message', {}).get('type') or '').lower()
    if rtype in ('tool', 'tool_result', 'toolresult'):
        return 'tool'
    if rtype in ('assistant', 'agent'):
        return 'assistant'
    if rtype == 'user':
        return 'user'
    return None


def extract_model(record):
    candidates = []
    for obj in walk_json(record):
        for key in ('model', 'modelName', 'modelId'):
            value = obj.get(key)
            if isinstance(value, str) and value:
                candidates.append(value)
    return normalize_model(candidates[0]) if candidates else 'sonnet'


def extract_usage(record):
    usage = {
        'input_tokens': 0,
        'output_tokens': 0,
        'cache_read_input_tokens': 0,
        'cache_creation_input_tokens': 0,
        'total_tokens': 0,
        'cost_usd': 0.0,
    }

    aliases = {
        'input_tokens': ('input_tokens', 'inputTokens', 'prompt_tokens', 'promptTokens', 'contextTokens', 'context_tokens'),
        'output_tokens': ('output_tokens', 'outputTokens', 'completion_tokens', 'completionTokens'),
        'cache_read_input_tokens': ('cache_read_input_tokens', 'cacheReadInputTokens', 'cachedInputTokens', 'cached_input_tokens'),
        'cache_creation_input_tokens': ('cache_creation_input_tokens', 'cacheCreationInputTokens', 'cache_creation_tokens'),
        'total_tokens': ('total_tokens', 'totalTokens'),
        'cost_usd': ('costUsd', 'cost_usd'),
    }

    for obj in walk_json(record):
        if not isinstance(obj, dict):
            continue
        for dest, keys in aliases.items():
            if usage[dest]:
                continue
            for key in keys:
                value = obj.get(key)
                if isinstance(value, (int, float)):
                    usage[dest] = float(value) if dest == 'cost_usd' else int(value)
                    break
        if usage['cost_usd']:
            continue
        cost = obj.get('cost')
        if isinstance(cost, dict):
            for key in ('total', 'usd', 'value'):
                value = cost.get(key)
                if isinstance(value, (int, float)):
                    usage['cost_usd'] = float(value)
                    break

    if not usage['total_tokens']:
        usage['total_tokens'] = usage['input_tokens'] + usage['output_tokens']
    return usage


def collect_tool_calls(record):
    calls = []
    seen = set()

    def add(name, args):
        normalized = (name or '').strip().lower()
        if not normalized:
            return
        key = (normalized, json.dumps(args or {}, sort_keys=True, default=str))
        if key in seen:
            return
        seen.add(key)
        calls.append({'name': normalized, 'args': args or {}})

    metadata_tools = record.get('metadata', {}).get('toolsUsed')
    if isinstance(metadata_tools, list):
        for name in metadata_tools:
            if isinstance(name, str):
                add(name, {})

    for obj in walk_json(record):
        if not isinstance(obj, dict):
            continue
        otype = (obj.get('type') or '').lower()
        if otype in ('tool_use', 'tooluse', 'toolcall', 'function_call'):
            name = obj.get('name') or obj.get('toolName') or obj.get('tool') or obj.get('function')
            args = obj.get('input') or obj.get('args') or obj.get('arguments') or obj.get('parameters') or {}
            add(name, args if isinstance(args, dict) else {'value': args})
            continue
        if 'toolName' in obj and ('args' in obj or 'input' in obj):
            name = obj.get('toolName')
            args = obj.get('input') or obj.get('args') or {}
            add(name, args if isinstance(args, dict) else {'value': args})

    return calls


def extract_tool_outputs(record):
    outputs = []
    role = extract_role(record)
    if role == 'tool':
        text = coerce_text(record.get('content') or record.get('message') or record.get('output') or record.get('result'))
        if text:
            outputs.append(text)
    for obj in walk_json(record):
        if not isinstance(obj, dict):
            continue
        otype = (obj.get('type') or '').lower()
        if otype in ('tool_result', 'toolresult', 'function_call_output'):
            text = coerce_text(obj.get('content') or obj.get('output') or obj.get('result'))
            if text:
                outputs.append(text)
    return outputs


def extract_commands(tool_calls):
    commands = []
    for call in tool_calls:
        args = call.get('args') or {}
        for key in ('cmd', 'command', 'shellCommand', 'bash'):
            value = args.get(key)
            if isinstance(value, str) and value.strip():
                commands.append(value.strip())
                break
    return commands


def extract_exit_codes(record):
    codes = []
    for obj in walk_json(record):
        if not isinstance(obj, dict):
            continue
        for key in ('exitCode', 'exit_code', 'returncode'):
            value = obj.get(key)
            if isinstance(value, int):
                codes.append(value)
    return codes


def extract_text(record):
    content = record.get('content')
    if content is None and 'message' in record and isinstance(record['message'], dict):
        content = record['message'].get('content')
    if content is None:
        content = record.get('text') or record.get('body') or record.get('output') or record.get('result')
    return coerce_text(content).strip()


def is_read_command(cmd):
    stripped = cmd.strip()
    return any(stripped.startswith(prefix) for prefix in READ_PREFIXES)


def is_search_command(cmd):
    stripped = cmd.strip()
    return any(stripped.startswith(prefix) for prefix in SEARCH_PREFIXES)


def is_git_only_command(cmd):
    return cmd.strip().startswith('git ')


def extract_paths_from_command(cmd):
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        tokens = cmd.split()
    paths = []
    for token in tokens[1:]:
        token = token.strip("'\"")
        if not token or token.startswith('-') or token in ('&&', '||', ';', '|'):
            continue
        if '/' in token or token.startswith('.') or re.search(r'\.[A-Za-z0-9]{1,10}$', token):
            paths.append(token)
    return paths


def detect_platform_from_commands(commands):
    scores = defaultdict(int)
    for cmd in commands:
        for platform, signals in PLATFORM_SIGNALS.items():
            for pat in signals['bash_patterns']:
                if pat in cmd:
                    scores[platform] += 3
            for path in extract_paths_from_command(cmd):
                for ext in signals['file_exts']:
                    if path.endswith(ext) or ext in path:
                        scores[platform] += 2
    if not scores:
        return 'general'
    return max(scores, key=scores.get)


def workspace_context_tokens(agent_dir, workspace_dir):
    total_chars = 0
    checked = set()
    for base in (workspace_dir, agent_dir):
        if not base:
            continue
        if base in checked:
            continue
        checked.add(base)
        for name in WORKSPACE_FILES:
            path = os.path.join(base, name)
            if not os.path.exists(path):
                continue
            try:
                total_chars += os.path.getsize(path)
            except OSError:
                continue
    return total_chars // 4


def heartbeat_session_key(session_key):
    key = (session_key or '').lower()
    return any(token in key for token in ('cron', 'schedule', 'timer', 'heartbeat', 'daemon', 'watch'))


def analyze_session(meta):
    filepath = meta['path']
    try:
        with open(filepath) as f:
            records = [json.loads(line) for line in f if line.strip()]
    except (OSError, json.JSONDecodeError):
        return None
    if not records:
        return None

    assistant_turns = []
    pending_user_text = ''
    all_commands = []
    model = normalize_model(meta.get('model'))
    first_ts = meta.get('timestamp')

    for record in records:
        role = extract_role(record)
        text = extract_text(record)
        usage = extract_usage(record)
        tool_calls = collect_tool_calls(record)
        tool_outputs = extract_tool_outputs(record)
        exit_codes = extract_exit_codes(record)
        commands = extract_commands(tool_calls)
        if commands:
            all_commands.extend(commands)
        if role == 'user':
            if text:
                pending_user_text = f'{pending_user_text}\n{text}'.strip()
            continue
        if role == 'tool':
            if assistant_turns:
                assistant_turns[-1]['tool_outputs'].extend(tool_outputs or ([text] if text else []))
                assistant_turns[-1]['exit_codes'].extend(exit_codes)
            continue
        if role != 'assistant':
            continue

        if model == 'sonnet':
            model = extract_model(record)
        cost = calc_cost(usage, model)
        output_tokens = usage.get('output_tokens', 0) or max(0, len(text) // 4)
        assistant_turns.append({
            'assistant_text': text,
            'user_text': pending_user_text,
            'tool_calls': tool_calls,
            'tool_names': [call['name'] for call in tool_calls],
            'commands': commands,
            'tool_outputs': tool_outputs,
            'exit_codes': exit_codes,
            'input_tokens': usage.get('input_tokens', 0),
            'cache_read': usage.get('cache_read_input_tokens', 0),
            'cache_create': usage.get('cache_creation_input_tokens', 0),
            'output_tokens': output_tokens,
            'cost': cost,
            'has_meaningful_tool': any(
                any(signal in name for signal in MEANINGFUL_TOOL_NAMES)
                for name in [call['name'] for call in tool_calls]
            ),
        })
        pending_user_text = ''

    assistant_turns = [turn for turn in assistant_turns if turn['assistant_text'] or turn['tool_calls'] or turn['input_tokens'] or turn['output_tokens']]
    if len(assistant_turns) < 1:
        return None

    total_turns = len(assistant_turns)
    total_cost = sum(t['cost'] for t in assistant_turns)
    total_output = sum(t['output_tokens'] for t in assistant_turns)
    total_input_tokens = sum(t['input_tokens'] for t in assistant_turns)
    total_cache_read = sum(t['cache_read'] for t in assistant_turns)
    total_cache_create = sum(t['cache_create'] for t in assistant_turns)

    idle_turns = [t for t in assistant_turns if not t['has_meaningful_tool'] and t['output_tokens'] < 150]
    idle_cost = sum(t['cost'] for t in idle_turns)

    heartbeat_turns = [
        t for t in assistant_turns
        if not t['user_text']
        and not t['has_meaningful_tool']
        and t['output_tokens'] < 120
    ]
    heartbeat_turns_count = len(heartbeat_turns)
    heartbeat_cost = sum(t['cost'] for t in heartbeat_turns)
    if heartbeat_session_key(meta.get('session_key')):
        heartbeat_turns_count = max(heartbeat_turns_count, 1)
        heartbeat_cost = max(heartbeat_cost, total_cost * 0.5)

    chainable = 0
    prev_exec_only = False
    for turn in assistant_turns:
        exec_only = len(turn['commands']) == 1 and len(turn['tool_names']) <= 1
        if exec_only and prev_exec_only:
            chainable += 1
        prev_exec_only = exec_only

    files_read = defaultdict(int)
    for turn in assistant_turns:
        for cmd in turn['commands']:
            if is_read_command(cmd):
                for path in extract_paths_from_command(cmd):
                    files_read[path] += 1
    duplicate_reads = sum(count - 1 for count in files_read.values() if count > 1)

    failed_tools = sum(1 for turn in assistant_turns for code in turn['exit_codes'] if code not in (0, None))

    edit_runs = []
    run = 0
    for turn in assistant_turns:
        has_edit = any(
            name in WRITE_TOOL_NAMES or 'patch' in name or 'write' in name or 'edit' in name
            for name in turn['tool_names']
        ) or any('apply_patch' in cmd for cmd in turn['commands'])
        if has_edit:
            run += 1
        else:
            if run > 0:
                edit_runs.append(run)
            run = 0
    if run > 0:
        edit_runs.append(run)
    batchable_edits = sum(length - 1 for length in edit_runs if length > 1)

    sleep_poll_turns = sum(
        1 for turn in assistant_turns for cmd in turn['commands']
        if 'sleep ' in cmd or 'poll' in cmd.lower()
    )

    git_ceremony = 0
    prev_git = False
    for turn in assistant_turns:
        git_only = bool(turn['commands']) and all(is_git_only_command(cmd) for cmd in turn['commands'])
        if git_only and prev_git:
            git_ceremony += 1
        prev_git = git_only

    quarter = max(1, total_turns // 4)
    session_context_rot = 0
    if total_turns > 12:
        early = sum(t['input_tokens'] or t['cache_read'] for t in assistant_turns[:quarter]) / quarter
        late = sum(t['input_tokens'] or t['cache_read'] for t in assistant_turns[-quarter:]) / quarter
        if early > 0 and late / early > 2.5:
            session_context_rot = 1

    context_rot_cost = 0
    if session_context_rot:
        avg_turn_cost = total_cost / total_turns if total_turns else 0
        context_rot_cost = round(avg_turn_cost * max(0, total_turns - 12) * 0.4, 4)

    verbose_output_chars = sum(len(output) for turn in assistant_turns for output in turn['tool_outputs'] if len(output) > 5000)
    verbose_output_count = sum(1 for turn in assistant_turns for output in turn['tool_outputs'] if len(output) > 5000)
    verbose_output_tokens = verbose_output_chars // 4
    price = get_pricing(model, total_input_tokens=verbose_output_tokens)
    verbose_cost = round(
        verbose_output_tokens * price['input'] / 1_000_000
        + verbose_output_tokens * total_turns * price.get('cache_read_price', price['input'] * price['cache_read_mult']) / 1_000_000,
        4,
    )

    explore_streak = 0
    total_explore_waste = 0
    for turn in assistant_turns:
        is_explore_turn = bool(turn['commands']) and all(is_search_command(cmd) or is_read_command(cmd) for cmd in turn['commands'])
        has_edit = any(name in WRITE_TOOL_NAMES for name in turn['tool_names'])
        if is_explore_turn and not has_edit:
            explore_streak += 1
        else:
            if explore_streak >= 5:
                total_explore_waste += explore_streak - 3
            explore_streak = 0
    if explore_streak >= 5:
        total_explore_waste += explore_streak - 3

    pingpong_cycles = 0
    for idx in range(1, len(assistant_turns)):
        prev_failed = any(code not in (0, None) for code in assistant_turns[idx - 1]['exit_codes'])
        curr_failed = any(code not in (0, None) for code in assistant_turns[idx]['exit_codes'])
        if prev_failed and curr_failed:
            pingpong_cycles += 1

    workspace_tokens = workspace_context_tokens(meta.get('agent_dir'), meta.get('cwd'))
    workspace_bloat_cost = round(
        workspace_tokens * max(1, heartbeat_turns_count) * price['input'] / 1_000_000,
        4,
    ) if workspace_tokens else 0

    memory_accumulation_detected = 1 if total_turns > 20 or session_context_rot else 0
    memory_accumulation_cost = round(context_rot_cost * 0.6 + max(0, total_turns - 20) * 0.01, 4) if memory_accumulation_detected else 0

    return {
        'file': os.path.basename(filepath),
        'timestamp': first_ts,
        'model': model,
        'platform': detect_platform_from_commands(all_commands),
        'total_turns': total_turns,
        'total_cost': round(total_cost, 4),
        'total_output_tokens': total_output,
        'total_input_tokens': total_input_tokens,
        'total_cache_read': total_cache_read,
        'total_cache_create': total_cache_create,
        'cost_per_turn': round(total_cost / total_turns, 4) if total_turns > 0 else 0,
        'waste': {
            'idle_narration': {
                'turns': len(idle_turns),
                'cost': round(idle_cost, 4),
                'description': 'Turns with commentary but no meaningful action before the next message',
            },
            'chainable_bash': {
                'turns': chainable,
                'cost': round(chainable * 0.02, 4),
                'description': 'Consecutive single-command turns that could often be grouped',
            },
            'duplicate_reads': {
                'count': duplicate_reads,
                'cost': round(duplicate_reads * 0.02, 4),
                'description': 'Same file or path inspected multiple times in one session',
            },
            'toolsearch': {
                'count': 0,
                'cost': 0,
                'description': 'Tool discovery overhead inside the agent runtime',
            },
            'failed_tools': {
                'count': failed_tools,
                'cost': round(failed_tools * 0.04, 4),
                'description': 'Command or tool failures that force extra retries',
            },
            'unbatched_edits': {
                'turns': batchable_edits,
                'cost': round(batchable_edits * 0.02, 4),
                'description': 'Consecutive edit turns that could be batched',
            },
            'sleep_poll_loops': {
                'count': sleep_poll_turns,
                'cost': round(sleep_poll_turns * 0.03, 4),
                'description': 'Polling turns waiting for a result instead of using a wait signal',
            },
            'git_ceremony': {
                'turns': git_ceremony,
                'cost': round(git_ceremony * 0.02, 4),
                'description': 'Consecutive git-only turns that could be grouped',
            },
            'context_rot': {
                'detected': session_context_rot,
                'total_turns': total_turns,
                'cost': context_rot_cost,
                'description': 'Session too long without compaction or reset — later turns drag large history',
            },
            'verbose_output': {
                'count': verbose_output_count,
                'chars': verbose_output_chars,
                'cost': verbose_cost,
                'description': 'Large command outputs injected into context and reread later',
            },
            'codebase_wandering': {
                'turns': total_explore_waste,
                'cost': round(total_explore_waste * 0.03, 4),
                'description': 'Long explore-only streaks before acting',
            },
            'pingpong_debugging': {
                'cycles': pingpong_cycles,
                'cost': round(pingpong_cycles * 0.05, 4),
                'description': 'Back-to-back failure cycles across turns',
            },
            'heartbeat_idle': {
                'turns': heartbeat_turns_count,
                'cost': round(heartbeat_cost, 4),
                'description': 'Always-on wakeups that consume context even when there is little or no real work',
            },
            'workspace_bloat': {
                'tokens': workspace_tokens,
                'cost': workspace_bloat_cost,
                'description': 'Large OpenClaw workspace files reread across always-on wakeups',
            },
            'memory_accumulation': {
                'detected': memory_accumulation_detected,
                'cost': memory_accumulation_cost,
                'description': 'Long-lived always-on session history without enough reset or compaction',
            },
        },
        'review_fleet': {
            'reviewer_agents': 0,
            'reviewer_types': [],
            'agent_spawns': 0,
            'skill_calls': 0,
        },
    }


def aggregate_results(results):
    n = len(results)
    total_cost = sum(r['total_cost'] for r in results)
    total_turns = sum(r['total_turns'] for r in results)
    total_output_tokens = sum(r['total_output_tokens'] for r in results)
    total_input_tokens = sum(r.get('total_input_tokens', 0) for r in results)
    total_cache_read = sum(r['total_cache_read'] for r in results)
    total_cache_create = sum(r['total_cache_create'] for r in results)

    waste_totals = defaultdict(lambda: {'turns': 0, 'count': 0, 'cost': 0})
    for result in results:
        for key, waste in result['waste'].items():
            waste_totals[key]['cost'] += waste['cost']
            waste_totals[key]['turns'] += waste.get('turns', 0)
            waste_totals[key]['count'] += waste.get('count', 0)
            waste_totals[key]['description'] = waste['description']

    total_waste_raw = sum(w['cost'] for w in waste_totals.values())
    total_waste = min(total_waste_raw, total_cost * 0.85)

    wasteful_turns_total = 0
    for result in results:
        waste = result['waste']
        wasteful_turns_total += (
            waste['idle_narration']['turns']
            + waste['chainable_bash']['turns']
            + waste['unbatched_edits']['turns']
            + waste['sleep_poll_loops'].get('count', 0)
            + waste['git_ceremony']['turns']
            + waste['codebase_wandering']['turns']
            + waste['heartbeat_idle']['turns']
        )

    context_rot_sessions = sum(1 for result in results if result['waste']['context_rot']['detected'])
    heartbeat_sessions = sum(1 for result in results if result['waste']['heartbeat_idle']['turns'] > 0)

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
            'avg_agent_spawns_per_session': 0,
            'total_agent_spawns': 0,
            'wasteful_turns_total': wasteful_turns_total,
            'wasteful_turns_pct': round(wasteful_turns_total / total_turns * 100, 1) if total_turns > 0 else 0,
            'context_rot_sessions': context_rot_sessions,
            'context_rot_pct': round(context_rot_sessions / n * 100, 1) if n > 0 else 0,
            'heartbeat_sessions': heartbeat_sessions,
            'heartbeat_sessions_pct': round(heartbeat_sessions / n * 100, 1) if n > 0 else 0,
            'total_turns': total_turns,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_cache_read': total_cache_read,
            'total_cache_create': total_cache_create,
        },
        'waste_breakdown': {},
        'sessions': results,
        'reviewer_roi': {},
        'polling_summary': {
            'total_sleep_poll_turns': sum(result['waste']['sleep_poll_loops'].get('count', 0) for result in results),
            'avg_per_session': round(sum(result['waste']['sleep_poll_loops'].get('count', 0) for result in results) / n, 1),
            'estimated_cost': round(sum(result['waste']['sleep_poll_loops'].get('count', 0) for result in results) * 0.03, 2),
        },
    }

    for key in sorted(waste_totals, key=lambda k: -waste_totals[k]['cost']):
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
        project['waste'] += sum(w['cost'] for w in result['waste'].values())
    output['per_project'] = {}
    for proj in sorted(projects, key=lambda p: -projects[p]['cost']):
        project = projects[proj]
        output['per_project'][proj] = {
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
    for model in sorted(models, key=lambda m: -models[m]['cost']):
        model_info = models[model]
        output['model_mix'][model] = {
            'sessions': model_info['sessions'],
            'pct_sessions': round(model_info['sessions'] / n * 100, 1),
            'total_cost': round(model_info['cost'], 2),
            'pct_cost': round(model_info['cost'] / total_cost * 100, 1) if total_cost > 0 else 0,
            'avg_cost': round(model_info['cost'] / model_info['sessions'], 2),
            'avg_turns': round(model_info['turns'] / model_info['sessions'], 1),
        }

    platforms = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0, 'waste': 0})
    for result in results:
        plat = platforms[result['platform']]
        plat['sessions'] += 1
        plat['cost'] += result['total_cost']
        plat['turns'] += result['total_turns']
        plat['waste'] += sum(w['cost'] for w in result['waste'].values())
    output['platform_mix'] = {}
    for plat in sorted(platforms, key=lambda p: -platforms[p]['cost']):
        plat_info = platforms[plat]
        output['platform_mix'][plat] = {
            'sessions': plat_info['sessions'],
            'total_cost': round(plat_info['cost'], 2),
            'avg_cost': round(plat_info['cost'] / plat_info['sessions'], 2),
            'waste_pct': round(min(plat_info['waste'], plat_info['cost'] * 0.85) / plat_info['cost'] * 100, 1) if plat_info['cost'] > 0 else 0,
        }

    return output


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_openclaw_sessions.py <sessions.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    sessions_meta = data.get('sessions', [])
    if not sessions_meta:
        print(json.dumps({'error': 'No sessions found'}))
        sys.exit(1)

    results = []
    for meta in sessions_meta:
        analyzed = analyze_session(meta)
        if not analyzed:
            continue
        analyzed['project'] = meta.get('project', 'unknown')
        analyzed['date'] = meta.get('date', 'unknown')
        analyzed['session_key'] = meta.get('session_key')
        results.append(analyzed)

    results.sort(key=lambda result: result['timestamp'])
    if not results:
        print(json.dumps({'error': 'No valid OpenClaw sessions parsed'}))
        sys.exit(1)

    print(json.dumps(aggregate_results(results), indent=2))


if __name__ == '__main__':
    main()
