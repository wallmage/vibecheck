#!/usr/bin/env python3
"""Analyze Codex session JSONL logs for cost and waste patterns."""
import json
import os
import re
import shlex
import sys
from collections import defaultdict
from pathlib import Path

from analyze_sessions import MODEL_PATTERNS, PLATFORM_SIGNALS
from model_pricing import get_billing_mode, get_pricing, get_pricing_metadata

READ_PREFIXES = ('cat ', 'sed ', 'nl ', 'head ', 'tail ', 'rg ', 'find ', 'ls ', 'tree ', 'wc ', 'stat ')
SEARCH_PREFIXES = ('rg ', 'grep ', 'find ', 'fd ', 'ls ', 'tree ')
WRITE_TOOL_NAMES = {'apply_patch'}
AGENT_TOOL_NAMES = {'spawn_agent', 'send_input', 'wait_agent', 'resume_agent', 'close_agent'}
DISCOVERY_TOOL_NAMES = {'list_mcp_resources', 'list_mcp_resource_templates'}


def normalize_model(model):
    model = (model or '').lower()
    for pattern, key in MODEL_PATTERNS:
        if pattern in model:
            return key
    return 'gpt-5.4'


def calc_cost(usage, model):
    input_tokens = usage.get('input_tokens', 0)
    cached_input = usage.get('cached_input_tokens', 0)
    fresh_input = max(0, input_tokens - cached_input)
    output_tokens = usage.get('output_tokens', 0) + usage.get('reasoning_output_tokens', 0)
    p = get_pricing(model, total_input_tokens=input_tokens)
    return (
        fresh_input * p['input']
        + cached_input * p.get('cache_read_price', p['input'] * p['cache_read_mult'])
        + output_tokens * p['output']
    ) / 1_000_000


def build_analysis_confidence(results):
    if not results:
        return {
            'label': 'estimated',
            'score': 0.4,
            'reason': 'No parsed Codex sessions.',
        }
    models = {r.get('model', 'gpt-5.4') for r in results}
    if all(get_billing_mode(model) == 'full_billing' for model in models):
        return {
            'label': 'measured',
            'score': 0.97,
            'reason': 'Codex logs expose per-step token telemetry, and the detected models are in the full-billing frontier set.',
        }
    return {
        'label': 'partial',
        'score': 0.84,
        'reason': 'Codex logs expose per-step token telemetry, but some detected models are outside the full-billing frontier set so tool surcharges stay estimate-only.',
    }


def empty_turn():
    return {
        'turn_id': None,
        'model': 'gpt-5.4',
        'assistant_messages': [],
        'tool_calls': [],
        'tool_outputs': [],
        'token_usages': [],
        'commands': [],
        'user_text': '',
    }


def extract_text_blocks(content):
    texts = []
    if not isinstance(content, list):
        return texts
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get('type') in ('output_text', 'input_text'):
            texts.append(block.get('text', ''))
    return texts


def parse_arguments(payload):
    args = payload.get('arguments')
    if isinstance(args, str):
        try:
            return json.loads(args)
        except json.JSONDecodeError:
            return {}
    if isinstance(payload.get('input'), dict):
        return payload['input']
    return {}


def extract_exit_code(output):
    m = re.search(r'Process exited with code (\d+)', output)
    return int(m.group(1)) if m else 0


def split_turns(records):
    turns = []
    current = None
    session_model = 'gpt-5.4'

    for obj in records:
        otype = obj.get('type')
        payload = obj.get('payload', {})

        if otype == 'session_meta':
            base_model = payload.get('model') or payload.get('model_slug')
            if base_model:
                session_model = normalize_model(base_model)
            continue

        if otype == 'turn_context':
            if current is not None:
                turns.append(current)
            current = empty_turn()
            current['turn_id'] = payload.get('turn_id')
            current['model'] = normalize_model(payload.get('model') or session_model)
            continue

        if current is None:
            continue

        if otype == 'response_item':
            ptype = payload.get('type')
            if ptype == 'message':
                role = payload.get('role')
                text = '\n'.join(extract_text_blocks(payload.get('content')))
                if role == 'assistant':
                    current['assistant_messages'].append({
                        'phase': payload.get('phase'),
                        'text': text,
                    })
                elif role == 'user':
                    current['user_text'] += text
            elif ptype in ('function_call', 'custom_tool_call'):
                name = payload.get('name', '')
                args = parse_arguments(payload)
                current['tool_calls'].append({'name': name, 'args': args})
                if name == 'exec_command':
                    cmd = args.get('cmd', '')
                    if cmd:
                        current['commands'].append(cmd)
                elif name == 'write_stdin':
                    chars = args.get('chars', '')
                    if chars == '':
                        current['commands'].append('poll')
            elif ptype in ('function_call_output', 'custom_tool_call_output'):
                output = payload.get('output', '')
                current['tool_outputs'].append(str(output))

        elif otype == 'event_msg':
            etype = payload.get('type')
            if etype == 'token_count':
                info = payload.get('info') or {}
                last_usage = info.get('last_token_usage')
                if last_usage:
                    current['token_usages'].append(last_usage)
            elif etype == 'user_message':
                current['user_text'] += payload.get('message', '')

    if current is not None:
        turns.append(current)
    return turns


def summarize_usage(token_usages):
    total = defaultdict(int)
    for usage in token_usages:
        for key in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'total_tokens'):
            total[key] += usage.get(key, 0)
    return dict(total)


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
    if not scores:
        return 'general'
    return max(scores, key=scores.get)


def analyze_session(filepath):
    try:
        with open(filepath) as f:
            records = [json.loads(line) for line in f if line.strip()]
    except (OSError, json.JSONDecodeError):
        return None

    if not records:
        return None

    session_meta = next((r.get('payload', {}) for r in records if r.get('type') == 'session_meta'), {})
    first_ts = session_meta.get('timestamp') or records[0].get('timestamp')
    if not first_ts:
        return None

    turns = split_turns(records)
    turns = [t for t in turns if t['assistant_messages'] or t['tool_calls'] or t['token_usages']]
    if len(turns) < 2:
        return None

    summarized = []
    for turn in turns:
        usage = summarize_usage(turn['token_usages'])
        assistant_text = '\n'.join(m['text'] for m in turn['assistant_messages'])
        output_tokens = usage.get('output_tokens', 0) + usage.get('reasoning_output_tokens', 0)
        cost = calc_cost(usage, turn['model'])
        tool_names = [call['name'] for call in turn['tool_calls']]
        exit_codes = [extract_exit_code(output) for output in turn['tool_outputs']]
        summarized.append({
            'model': turn['model'],
            'assistant_text': assistant_text,
            'assistant_messages': turn['assistant_messages'],
            'commands': turn['commands'],
            'tool_names': tool_names,
            'has_meaningful_tool': any(name not in ('update_plan',) for name in tool_names),
            'output_tokens': output_tokens,
            'cost': cost,
            'cache_read': usage.get('cached_input_tokens', 0),
            'cache_create': 0,
            'input_tokens': usage.get('input_tokens', 0),
            'exit_codes': exit_codes,
            'tool_outputs': turn['tool_outputs'],
        })

    model = summarized[0]['model']
    total_turns = len(summarized)
    total_cost = sum(t['cost'] for t in summarized)

    idle_turns = [
        t for t in summarized
        if not t['has_meaningful_tool']
        and t['output_tokens'] < 150
        and not any(m.get('phase') == 'final_answer' for m in t['assistant_messages'])
    ]
    idle_cost = sum(t['cost'] for t in idle_turns)

    chainable = 0
    prev_solo_exec = False
    for turn in summarized:
        exec_only = len(turn['commands']) == 1 and all(name in ('exec_command', 'write_stdin') for name in turn['tool_names'])
        if exec_only and prev_solo_exec:
            chainable += 1
        prev_solo_exec = exec_only

    files_read = defaultdict(int)
    for turn in summarized:
        for cmd in turn['commands']:
            if is_read_command(cmd):
                for path in extract_paths_from_command(cmd):
                    files_read[path] += 1
    duplicate_reads = sum(count - 1 for count in files_read.values() if count > 1)

    toolsearch_count = sum(
        1 for turn in summarized for name in turn['tool_names']
        if name in DISCOVERY_TOOL_NAMES
    )

    failed_tools = sum(
        1 for turn in summarized for code in turn['exit_codes']
        if code not in (0, None)
    )

    edit_runs = []
    run = 0
    for turn in summarized:
        has_edit = any(name in WRITE_TOOL_NAMES for name in turn['tool_names'])
        if has_edit:
            run += 1
        else:
            if run > 0:
                edit_runs.append(run)
            run = 0
    if run > 0:
        edit_runs.append(run)
    batchable_edits = sum(r - 1 for r in edit_runs if r > 1)

    sleep_poll_turns = sum(
        1 for turn in summarized for cmd in turn['commands']
        if cmd == 'poll' or (cmd != 'poll' and 'sleep ' in cmd and 'grep' not in cmd and 'rg ' not in cmd)
    )

    git_ceremony = 0
    prev_git = False
    for turn in summarized:
        git_only = bool(turn['commands']) and all(is_git_only_command(cmd) for cmd in turn['commands'])
        if git_only and prev_git:
            git_ceremony += 1
        prev_git = git_only

    reviewer_agents = 0
    reviewer_types = set()
    agent_spawns = 0
    for turn in summarized:
        for name in turn['tool_names']:
            if name in AGENT_TOOL_NAMES:
                agent_spawns += 1

    session_context_rot = 0
    if total_turns > 20:
        quarter = max(1, total_turns // 4)
        early = sum(t['cache_read'] for t in summarized[:quarter]) / quarter
        late = sum(t['cache_read'] for t in summarized[-quarter:]) / quarter
        if early > 0 and late / early > 3:
            session_context_rot = 1
    context_rot_cost = 0
    if session_context_rot and total_turns > 20:
        excess_turns = total_turns - 20
        avg_turn_cost = total_cost / total_turns if total_turns > 0 else 0
        context_rot_cost = round(excess_turns * avg_turn_cost * 0.5, 4)

    verbose_output_chars = sum(
        len(output) for turn in summarized for output in turn['tool_outputs']
        if len(output) > 5000
    )
    verbose_output_count = sum(
        1 for turn in summarized for output in turn['tool_outputs']
        if len(output) > 5000
    )
    verbose_output_tokens = verbose_output_chars // 4
    p = get_pricing(model, total_input_tokens=verbose_output_tokens)
    verbose_cost = round(
        verbose_output_tokens * p['input'] / 1_000_000
        + verbose_output_tokens * total_turns * p.get('cache_read_price', p['input'] * p['cache_read_mult']) / 1_000_000,
        4,
    )

    explore_streak = 0
    total_explore_waste = 0
    for turn in summarized:
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
    for idx in range(1, len(summarized)):
        prev_failed = any(code not in (0, None) for code in summarized[idx - 1]['exit_codes'])
        curr_failed = any(code not in (0, None) for code in summarized[idx]['exit_codes'])
        if prev_failed and curr_failed:
            pingpong_cycles += 1

    total_output = sum(t['output_tokens'] for t in summarized)
    total_cache_read = sum(t['cache_read'] for t in summarized)
    total_cache_create = sum(t['cache_create'] for t in summarized)
    detected_platform = detect_platform_from_turns(turns)

    return {
        'file': os.path.basename(filepath),
        'timestamp': first_ts,
        'model': model,
        'platform': detected_platform,
        'total_turns': total_turns,
        'total_cost': round(total_cost, 4),
        'total_output_tokens': total_output,
        'total_cache_read': total_cache_read,
        'total_cache_create': total_cache_create,
        'cost_per_turn': round(total_cost / total_turns, 4) if total_turns > 0 else 0,
        'waste': {
            'idle_narration': {
                'turns': len(idle_turns),
                'cost': round(idle_cost, 4),
                'description': 'Turns with commentary but no meaningful tool action before the next user turn',
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
                'count': toolsearch_count,
                'cost': round(toolsearch_count * 0.02, 4),
                'description': 'Tool discovery calls that may be avoidable once the tool is known',
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
                'description': 'Session too long without a fresh start — cached context dominates later turns',
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
            'reviewer_agents': reviewer_agents,
            'reviewer_types': list(reviewer_types),
            'agent_spawns': agent_spawns,
            'skill_calls': 0,
        },
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_codex_sessions.py <sessions.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    sessions_meta = data.get('sessions', [])
    if not sessions_meta:
        print(json.dumps({'error': 'No sessions found'}))
        sys.exit(1)

    results = []
    for meta in sessions_meta:
        result = analyze_session(meta['path'])
        if result:
            result['project'] = meta.get('project', 'unknown')
            result['date'] = meta.get('date', 'unknown')
            results.append(result)

    n = len(results)
    if n == 0:
        print(json.dumps({'error': 'No valid sessions parsed'}))
        sys.exit(1)

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
    total_agent_spawns = sum(r['review_fleet']['agent_spawns'] for r in results)

    wasteful_turns_total = 0
    for r in results:
        w = r['waste']
        wasteful_turns_total += (
            w['idle_narration']['turns']
            + w['chainable_bash']['turns']
            + w['unbatched_edits']['turns']
            + w['sleep_poll_loops'].get('count', 0)
            + w['git_ceremony']['turns']
            + w['codebase_wandering']['turns']
        )

    context_rot_sessions = sum(1 for r in results if r['waste']['context_rot']['detected'])

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
            'projected_cost_after_fix': round(max(0, (total_cost - total_waste)) / n, 2),
            'avg_context_window_tokens': round(total_input_tokens / total_turns) if total_turns > 0 else 0,
            'avg_output_tokens_per_turn': round(total_output_tokens / total_turns) if total_turns > 0 else 0,
            'avg_agent_spawns_per_session': round(total_agent_spawns / n, 1),
            'total_agent_spawns': total_agent_spawns,
            'wasteful_turns_total': wasteful_turns_total,
            'wasteful_turns_pct': round(wasteful_turns_total / total_turns * 100, 1) if total_turns > 0 else 0,
            'context_rot_sessions': context_rot_sessions,
            'context_rot_pct': round(context_rot_sessions / n * 100, 1) if n > 0 else 0,
            'total_turns': total_turns,
            'total_output_tokens': total_output_tokens,
            'total_cache_read': total_cache_read,
            'total_cache_create': total_cache_create,
        },
        'waste_breakdown': {},
        'sessions': results,
        'analysis_confidence': build_analysis_confidence(results),
    }

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
            'waste_pct': round(p['waste'] / p['cost'] * 100, 1) if p['cost'] > 0 else 0,
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
        plat = platforms[r.get('platform', 'general')]
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
            'waste_pct': round(p['waste'] / p['cost'] * 100, 1) if p['cost'] > 0 else 0,
        }

    output['reviewer_roi'] = {}
    total_sleep_polls = sum(r['waste'].get('sleep_poll_loops', {}).get('count', 0) for r in results)
    output['polling_summary'] = {
        'total_sleep_poll_turns': total_sleep_polls,
        'avg_per_session': round(total_sleep_polls / n, 1),
        'estimated_cost': round(total_sleep_polls * 0.03, 2),
    }
    output['pricing_metadata'] = get_pricing_metadata(next(iter(output['model_mix']), results[0]['model']))

    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
