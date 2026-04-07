#!/usr/bin/env python3
"""Analyze Windsurf transcript sessions for cost and waste patterns."""
import json
import os
import re
import shlex
import sys
from collections import defaultdict

from analyze_sessions import MODEL_PATTERNS, PLATFORM_SIGNALS
from model_pricing import get_pricing

READ_STEP_TYPES = {'view_file', 'read_file', 'list_directory', 'grep_search', 'find', 'search_codebase'}
SEARCH_STEP_TYPES = {'find', 'grep_search', 'search_web', 'web_search', 'search_docs'}
EDIT_STEP_TYPES = {'code_action', 'edit_code', 'propose_code', 'write_file'}
COMMAND_STEP_TYPES = {'run_command', 'command_action'}
MCP_STEP_TYPES = {'mcp_tool_use', 'mcp_action'}


def normalize_model(model):
    text = (model or '').lower()
    if 'swe-1.5' in text:
        return 'gpt-4.1'
    if 'swe-1' in text:
        return 'gpt-4.1-mini'
    for pattern, key in MODEL_PATTERNS:
        if pattern in text:
            return key
    return 'sonnet'


def calc_cost(input_tokens, output_tokens, model):
    pricing = get_pricing(model, total_input_tokens=input_tokens)
    return (
        input_tokens * pricing['input']
        + output_tokens * pricing['output']
    ) / 1_000_000


def walk_json(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_json(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_json(value)


def coerce_text(value):
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        chunks = []
        for key in ('response', 'text', 'user_response', 'output', 'message', 'summary'):
            if key in value:
                chunks.append(coerce_text(value[key]))
        return '\n'.join(chunk for chunk in chunks if chunk)
    if isinstance(value, list):
        return '\n'.join(chunk for chunk in (coerce_text(item) for item in value) if chunk)
    return ''


def extract_payload(record):
    step_type = record.get('type')
    if isinstance(step_type, str) and isinstance(record.get(step_type), dict):
        return step_type, record.get(step_type)
    for key, value in record.items():
        if key in ('type', 'status', 'timestamp'):
            continue
        if isinstance(value, dict):
            return key, value
    return str(step_type or ''), {}


def extract_model(payload):
    for node in walk_json(payload):
        if not isinstance(node, dict):
            continue
        for key in ('model', 'model_name', 'selected_model', 'modelId'):
            value = node.get(key)
            if isinstance(value, str) and value:
                return normalize_model(value)
    return None


def extract_command(payload):
    for key in ('command_line', 'command', 'cmd'):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def extract_path(payload):
    for key in ('path', 'file_path', 'directory_path'):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def extract_output(payload):
    for key in ('output', 'response', 'mcp_result', 'search_results', 'results'):
        value = payload.get(key)
        text = coerce_text(value)
        if text:
            return text
    return ''


def extract_exit_code(payload, status):
    for key in ('exit_code', 'exitCode', 'returncode'):
        value = payload.get(key)
        if isinstance(value, int):
            return value
    if status == 'failed':
        return 1
    return 0


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


def is_read_command(cmd):
    stripped = cmd.strip()
    return stripped.startswith(('cat ', 'sed ', 'head ', 'tail ', 'rg ', 'find ', 'ls ', 'tree '))


def is_search_command(cmd):
    stripped = cmd.strip()
    return stripped.startswith(('rg ', 'grep ', 'find ', 'fd ', 'ls ', 'tree '))


def is_git_only_command(cmd):
    return cmd.strip().startswith('git ')


def detect_platform_from_turns(turns):
    scores = defaultdict(int)
    for turn in turns:
        for cmd in turn['commands']:
            for platform, signals in PLATFORM_SIGNALS.items():
                for pat in signals['bash_patterns']:
                    if pat in cmd:
                        scores[platform] += 3
                for path in extract_paths_from_command(cmd):
                    for ext in signals['file_exts']:
                        if path.endswith(ext) or ext in path:
                            scores[platform] += 2
        for path in turn['paths']:
            for platform, signals in PLATFORM_SIGNALS.items():
                for ext in signals['file_exts']:
                    if path.endswith(ext) or ext in path:
                        scores[platform] += 2
    if not scores:
        return 'general'
    return max(scores, key=scores.get)


def analyze_session(meta):
    try:
        with open(meta['path']) as f:
            records = [json.loads(line) for line in f if line.strip()]
    except (OSError, json.JSONDecodeError):
        return None
    if not records:
        return None

    turns = []
    current = None
    current_model = normalize_model(meta.get('model'))

    def ensure_turn():
        nonlocal current
        if current is None:
            current = {
                'user_text': '',
                'assistant_text_parts': [],
                'commands': [],
                'tool_names': [],
                'tool_outputs': [],
                'exit_codes': [],
                'paths': [],
                'model': current_model or 'sonnet',
            }

    def flush_turn():
        nonlocal current
        if current is None:
            return
        assistant_text = '\n'.join(part for part in current['assistant_text_parts'] if part).strip()
        input_tokens = max(1, (len(current['user_text']) + len(assistant_text) + sum(len(out) for out in current['tool_outputs'])) // 4)
        output_tokens = max(1, (len(assistant_text) + sum(len(out) for out in current['tool_outputs']) // 2) // 4)
        model = current.get('model') or 'sonnet'
        turns.append({
            'user_text': current['user_text'],
            'assistant_text': assistant_text,
            'commands': current['commands'],
            'tool_names': current['tool_names'],
            'tool_outputs': current['tool_outputs'],
            'exit_codes': current['exit_codes'],
            'paths': current['paths'],
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': calc_cost(input_tokens, output_tokens, model),
            'model': model,
            'has_meaningful_tool': any(name not in ('planner_response',) for name in current['tool_names']),
        })
        current = None

    for record in records:
        step_type, payload = extract_payload(record)
        step_type = (step_type or '').lower()
        status = str(record.get('status', 'done')).lower()
        payload_model = extract_model(payload)
        if payload_model:
            current_model = payload_model

        if step_type == 'user_input':
            flush_turn()
            ensure_turn()
            current['model'] = current_model or 'sonnet'
            current['user_text'] = coerce_text(payload.get('user_response') or payload.get('prompt'))
            continue

        ensure_turn()
        current['model'] = current_model or current['model']

        if step_type == 'planner_response':
            text = coerce_text(payload.get('response') or payload)
            if text:
                current['assistant_text_parts'].append(text)
            current['tool_names'].append('planner_response')
        elif step_type in EDIT_STEP_TYPES:
            path = extract_path(payload)
            if path:
                current['paths'].append(path)
            summary = f"Edited {path}" if path else 'Edited code'
            current['assistant_text_parts'].append(summary)
            current['tool_names'].append(step_type)
        elif step_type in READ_STEP_TYPES:
            path = extract_path(payload)
            if path:
                current['paths'].append(path)
            current['tool_names'].append(step_type)
            output = extract_output(payload)
            if output:
                current['tool_outputs'].append(output)
        elif step_type in SEARCH_STEP_TYPES:
            current['tool_names'].append(step_type)
            output = extract_output(payload)
            if output:
                current['tool_outputs'].append(output)
        elif step_type in COMMAND_STEP_TYPES:
            command = extract_command(payload)
            if command:
                current['commands'].append(command)
            current['tool_names'].append(step_type)
            output = extract_output(payload)
            if output:
                current['tool_outputs'].append(output)
            current['exit_codes'].append(extract_exit_code(payload, status))
        elif step_type in MCP_STEP_TYPES:
            current['tool_names'].append(step_type)
            output = extract_output(payload)
            if output:
                current['tool_outputs'].append(output)
        else:
            text = coerce_text(payload)
            if text:
                current['assistant_text_parts'].append(text)
            if step_type:
                current['tool_names'].append(step_type)

    flush_turn()
    turns = [turn for turn in turns if turn['user_text'] or turn['assistant_text'] or turn['tool_names']]
    if len(turns) < 1:
        return None

    total_turns = len(turns)
    total_cost = sum(t['cost'] for t in turns)
    total_output = sum(t['output_tokens'] for t in turns)
    total_input = sum(t['input_tokens'] for t in turns)
    model = turns[0]['model']
    avg_turn_cost = total_cost / total_turns if total_turns else 0

    idle_turns = [t for t in turns if not t['has_meaningful_tool'] and t['output_tokens'] < 150]
    idle_cost = sum(t['cost'] for t in idle_turns)

    chainable = 0
    prev_exec_only = False
    for turn in turns:
        exec_only = len(turn['commands']) == 1 and len(turn['tool_names']) <= 2
        if exec_only and prev_exec_only:
            chainable += 1
        prev_exec_only = exec_only

    files_read = defaultdict(int)
    for turn in turns:
        for path in turn['paths']:
            files_read[path] += 1
        for cmd in turn['commands']:
            if is_read_command(cmd):
                for path in extract_paths_from_command(cmd):
                    files_read[path] += 1
    duplicate_reads = sum(count - 1 for count in files_read.values() if count > 1)

    toolsearch_count = sum(
        1 for turn in turns for name in turn['tool_names']
        if name in SEARCH_STEP_TYPES
    )

    failed_tools = sum(
        1 for turn in turns for code in turn['exit_codes']
        if code not in (0, None)
    )

    edit_runs = []
    run = 0
    for turn in turns:
        has_edit = any(name in EDIT_STEP_TYPES for name in turn['tool_names'])
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
        1 for turn in turns for cmd in turn['commands']
        if 'sleep ' in cmd or 'poll' in cmd.lower()
    )

    git_ceremony = 0
    prev_git = False
    for turn in turns:
        git_only = bool(turn['commands']) and all(is_git_only_command(cmd) for cmd in turn['commands'])
        if git_only and prev_git:
            git_ceremony += 1
        prev_git = git_only

    session_context_rot = 0
    if total_turns > 20:
        quarter = max(1, total_turns // 4)
        early = sum(t['input_tokens'] for t in turns[:quarter]) / quarter
        late = sum(t['input_tokens'] for t in turns[-quarter:]) / quarter
        if early > 0 and late / early > 2.5:
            session_context_rot = 1
    context_rot_cost = 0
    if session_context_rot:
        context_rot_cost = round(avg_turn_cost * max(0, total_turns - 20) * 0.4, 4)

    verbose_output_chars = sum(len(output) for turn in turns for output in turn['tool_outputs'] if len(output) > 5000)
    verbose_output_count = sum(1 for turn in turns for output in turn['tool_outputs'] if len(output) > 5000)
    verbose_output_tokens = verbose_output_chars // 4
    price = get_pricing(model, total_input_tokens=verbose_output_tokens)
    verbose_cost = round(
        verbose_output_tokens * price['input'] / 1_000_000
        + verbose_output_tokens * total_turns * price.get('cache_read_price', price['input'] * price['cache_read_mult']) / 1_000_000,
        4,
    )

    explore_streak = 0
    total_explore_waste = 0
    for turn in turns:
        is_explore_turn = bool(turn['tool_names']) and all(name in READ_STEP_TYPES or name in SEARCH_STEP_TYPES or name == 'planner_response' for name in turn['tool_names'])
        has_edit = any(name in EDIT_STEP_TYPES for name in turn['tool_names'])
        has_command = bool(turn['commands'])
        if is_explore_turn and not has_edit and not has_command:
            explore_streak += 1
        else:
            if explore_streak >= 5:
                total_explore_waste += explore_streak - 3
            explore_streak = 0
    if explore_streak >= 5:
        total_explore_waste += explore_streak - 3

    pingpong_cycles = 0
    for idx in range(1, len(turns)):
        prev_failed = any(code not in (0, None) for code in turns[idx - 1]['exit_codes'])
        curr_failed = any(code not in (0, None) for code in turns[idx]['exit_codes'])
        if prev_failed and curr_failed:
            pingpong_cycles += 1

    return {
        'file': os.path.basename(meta['path']),
        'timestamp': meta['timestamp'],
        'model': model,
        'platform': detect_platform_from_turns(turns),
        'total_turns': total_turns,
        'total_cost': round(total_cost, 4),
        'total_output_tokens': total_output,
        'total_input_tokens': total_input,
        'total_cache_read': 0,
        'total_cache_create': 0,
        'cost_per_turn': round(total_cost / total_turns, 4) if total_turns > 0 else 0,
        'waste': {
            'idle_narration': {
                'turns': len(idle_turns),
                'cost': round(idle_cost, 4),
                'description': 'Turns with commentary but no meaningful tool action before the next user turn',
            },
            'chainable_bash': {
                'turns': chainable,
                'cost': round(chainable * avg_turn_cost * 0.5, 4),
                'description': 'Consecutive single-command turns that could often be grouped',
            },
            'duplicate_reads': {
                'count': duplicate_reads,
                'cost': round(duplicate_reads * avg_turn_cost * 0.6, 4),
                'description': 'Same file or path inspected multiple times in one session',
            },
            'toolsearch': {
                'count': toolsearch_count,
                'cost': round(toolsearch_count * avg_turn_cost * 0.5, 4),
                'description': 'Search and discovery steps that may be avoidable once the tool or path is known',
            },
            'failed_tools': {
                'count': failed_tools,
                'cost': round(failed_tools * avg_turn_cost * 1.5, 4),
                'description': 'Command or tool failures that force extra retries',
            },
            'unbatched_edits': {
                'turns': batchable_edits,
                'cost': round(batchable_edits * avg_turn_cost * 0.5, 4),
                'description': 'Consecutive edit turns that could be batched',
            },
            'sleep_poll_loops': {
                'count': sleep_poll_turns,
                'cost': round(sleep_poll_turns * avg_turn_cost * 0.75, 4),
                'description': 'Polling turns waiting for a result instead of using a wait signal',
            },
            'git_ceremony': {
                'turns': git_ceremony,
                'cost': round(git_ceremony * avg_turn_cost * 0.5, 4),
                'description': 'Consecutive git-only turns that could be grouped',
            },
            'context_rot': {
                'detected': session_context_rot,
                'total_turns': total_turns,
                'cost': context_rot_cost,
                'description': 'Session too long without compaction or a fresh start — later turns drag larger context',
            },
            'verbose_output': {
                'count': verbose_output_count,
                'chars': verbose_output_chars,
                'cost': verbose_cost,
                'description': 'Large command outputs injected into context and reread later',
            },
            'codebase_wandering': {
                'turns': total_explore_waste,
                'cost': round(total_explore_waste * avg_turn_cost * 0.75, 4),
                'description': 'Long explore-only streaks before acting',
            },
            'pingpong_debugging': {
                'cycles': pingpong_cycles,
                'cost': round(pingpong_cycles * avg_turn_cost * 1.5, 4),
                'description': 'Back-to-back failure cycles across turns',
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
    }


def aggregate_results(results):
    n = len(results)
    total_cost = sum(r['total_cost'] for r in results)
    total_turns = sum(r['total_turns'] for r in results)
    total_output_tokens = sum(r['total_output_tokens'] for r in results)
    total_input_tokens = sum(r['total_input_tokens'] for r in results)

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
        )

    context_rot_sessions = sum(1 for result in results if result['waste']['context_rot']['detected'])

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
            'total_turns': total_turns,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_cache_read': 0,
            'total_cache_create': 0,
        },
        'waste_breakdown': {},
        'sessions': results,
        'reviewer_roi': {},
        'polling_summary': {
            'total_sleep_poll_turns': sum(result['waste'].get('sleep_poll_loops', {}).get('count', 0) for result in results),
            'avg_per_session': round(sum(result['waste'].get('sleep_poll_loops', {}).get('count', 0) for result in results) / n, 1),
            'estimated_cost': round(sum(result['waste'].get('sleep_poll_loops', {}).get('count', 0) for result in results) * 0.03, 2),
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
        data = models[model]
        output['model_mix'][model] = {
            'sessions': data['sessions'],
            'pct_sessions': round(data['sessions'] / n * 100, 1),
            'total_cost': round(data['cost'], 2),
            'pct_cost': round(data['cost'] / total_cost * 100, 1) if total_cost > 0 else 0,
            'avg_cost': round(data['cost'] / data['sessions'], 2),
            'avg_turns': round(data['turns'] / data['sessions'], 1),
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
        data = platforms[plat]
        output['platform_mix'][plat] = {
            'sessions': data['sessions'],
            'total_cost': round(data['cost'], 2),
            'avg_cost': round(data['cost'] / data['sessions'], 2),
            'waste_pct': round(min(data['waste'], data['cost'] * 0.85) / data['cost'] * 100, 1) if data['cost'] > 0 else 0,
        }

    return output


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_windsurf_sessions.py <sessions.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    sessions_meta = data.get('sessions', [])
    if not sessions_meta:
        print(json.dumps({'error': 'No sessions found'}))
        sys.exit(1)

    results = []
    for meta in sessions_meta:
        result = analyze_session(meta)
        if result:
            result['project'] = meta.get('project', 'unknown')
            result['date'] = meta.get('date', 'unknown')
            results.append(result)

    results.sort(key=lambda r: r['timestamp'])
    if not results:
        print(json.dumps({'error': 'No valid Windsurf sessions parsed'}))
        sys.exit(1)

    print(json.dumps(aggregate_results(results), indent=2))


if __name__ == '__main__':
    main()
