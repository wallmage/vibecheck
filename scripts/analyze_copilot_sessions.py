#!/usr/bin/env python3
"""Analyze GitHub Copilot / VS Code chat sessions for cost and waste patterns."""
import json
import os
import re
import shlex
import sys
from collections import defaultdict

from analyze_sessions import MODEL_PATTERNS, PLATFORM_SIGNALS
from find_copilot_logs import reconstruct_jsonl
from model_pricing import get_billing_mode, get_pricing, get_pricing_metadata

READ_PREFIXES = ('cat ', 'sed ', 'nl ', 'head ', 'tail ', 'rg ', 'find ', 'ls ', 'tree ', 'wc ', 'stat ')
SEARCH_PREFIXES = ('rg ', 'grep ', 'find ', 'fd ', 'ls ', 'tree ')
WRITE_TOOL_NAMES = {'copilot_replacestring', 'copilot_createfile', 'copilot_insertedit', 'copilot_applyworkspaceedit'}
DISCOVERY_TOOL_NAMES = {'copilot_findtextinfiles', 'copilot_searchworkspace'}
AGENT_TOOL_NAMES = {'runsubagent'}


def normalize_model(model):
    text = (model or '').lower()
    if text.startswith('copilot/'):
        text = text[len('copilot/'):]
    if 'claude-sonnet-4' in text:
        return 'sonnet'
    for pattern, replacement in MODEL_PATTERNS:
        if pattern in text:
            return replacement
    return text or 'gpt-4.1'


def calc_cost(input_tokens, output_tokens, model):
    pricing = get_pricing(model, total_input_tokens=input_tokens)
    return (
        input_tokens * pricing['input']
        + output_tokens * pricing['output']
    ) / 1_000_000


def build_analysis_confidence(results):
    if not results:
        return {
            'label': 'estimated',
            'score': 0.4,
            'reason': 'No parsed Copilot sessions.',
        }
    models = {r.get('model', 'gpt-4.1') for r in results}
    if all(get_billing_mode(model) == 'full_billing' for model in models):
        return {
            'label': 'partial',
            'score': 0.82,
            'reason': 'Copilot analysis mixes stored token usage with reconstructed turn sizes, and the detected models are in the full-billing frontier set.',
        }
    return {
        'label': 'estimated',
        'score': 0.68,
        'reason': 'Copilot analysis relies partly on reconstructed chat/session payloads, and some detected models are outside the full-billing frontier set.',
    }


def walk_json(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_json(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_json(value)


def text_from_parts(parts):
    texts = []
    if not isinstance(parts, list):
        return texts
    for part in parts:
        if not isinstance(part, dict):
            continue
        kind = str(part.get('kind', '')).lower()
        if kind in ('text', 'markdowncontent', 'markdown', '1', 'textpart'):
            text = part.get('text') or part.get('value') or part.get('markdown') or ''
            if isinstance(text, str):
                texts.append(text)
    return texts


def coerce_text(value):
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        if 'parts' in value:
            return '\n'.join(text_from_parts(value.get('parts')))
        chunks = []
        for key in ('text', 'value', 'markdown', 'content', 'body', 'message'):
            if key in value:
                chunks.append(coerce_text(value[key]))
        return '\n'.join(chunk for chunk in chunks if chunk)
    if isinstance(value, list):
        return '\n'.join(chunk for chunk in (coerce_text(item) for item in value) if chunk)
    return ''


def extract_usage(obj):
    usage = {
        'input_tokens': 0,
        'output_tokens': 0,
    }
    aliases = {
        'input_tokens': ('inputTokens', 'promptTokens', 'contextTokens', 'input_tokens', 'prompt_tokens'),
        'output_tokens': ('outputTokens', 'completionTokens', 'output_tokens', 'completion_tokens'),
    }
    for node in walk_json(obj):
        if not isinstance(node, dict):
            continue
        for dest, keys in aliases.items():
            if usage[dest]:
                continue
            for key in keys:
                value = node.get(key)
                if isinstance(value, (int, float)):
                    usage[dest] = int(value)
                    break
    return usage


def extract_model_from_request(request):
    for node in walk_json(request):
        if not isinstance(node, dict):
            continue
        for key in ('modelId', 'model', 'modelName'):
            value = node.get(key)
            if isinstance(value, str) and value:
                return normalize_model(value)
    return 'gpt-4.1'


def parse_tool_invocation(item):
    serialized = item.get('toolInvocationSerialized') or item.get('toolInvocation')
    payload = None
    if isinstance(serialized, str):
        try:
            payload = json.loads(serialized)
        except json.JSONDecodeError:
            payload = {'toolId': serialized}
    elif isinstance(serialized, dict):
        payload = serialized

    if not payload:
        return None

    tool_id = (payload.get('toolId') or payload.get('toolName') or payload.get('name') or '').lower()
    args = payload.get('toolSpecificData') or payload.get('args') or {}
    if not isinstance(args, dict):
        args = {'value': args}
    return {
        'name': tool_id,
        'args': args,
    }


def extract_response_items(response):
    items = []
    if isinstance(response, list):
        items.extend(response)
    elif isinstance(response, dict):
        if isinstance(response.get('value'), list):
            items.extend(response['value'])
        else:
            items.append(response)
    return [item for item in items if isinstance(item, dict)]


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
    return any(stripped.startswith(prefix) for prefix in READ_PREFIXES)


def is_search_command(cmd):
    stripped = cmd.strip()
    return any(stripped.startswith(prefix) for prefix in SEARCH_PREFIXES)


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
    if not scores:
        return 'general'
    return max(scores, key=scores.get)


def parse_session(path):
    try:
        if path.endswith('.json'):
            with open(path) as f:
                session = json.load(f)
        else:
            session = reconstruct_jsonl(path)
    except (OSError, json.JSONDecodeError):
        return None
    return session if isinstance(session, dict) else None


def estimate_input_tokens(turns, current_user_text, explicit_input):
    if explicit_input:
        return explicit_input
    prior_chars = sum(len(turn['user_text']) + len(turn['assistant_text']) for turn in turns)
    current_chars = len(current_user_text)
    return max(1, (prior_chars + current_chars) // 4)


def analyze_session(meta):
    session = parse_session(meta['path'])
    if not session:
        return None

    requests = session.get('requests', [])
    if not isinstance(requests, list) or not requests:
        return None

    turns = []
    for req in requests:
        if not isinstance(req, dict):
            continue
        user_text = coerce_text(req.get('message'))
        response_items = extract_response_items(req.get('response'))
        assistant_text_parts = []
        tool_calls = []
        tool_outputs = []
        exit_codes = []

        for item in response_items:
            invocation = parse_tool_invocation(item)
            if invocation:
                tool_calls.append(invocation)
                continue

            tool_result = item.get('toolResult') or item.get('toolInvocationResult')
            if tool_result:
                text = coerce_text(tool_result)
                if text:
                    tool_outputs.append(text)
                for node in walk_json(tool_result):
                    if not isinstance(node, dict):
                        continue
                    for key in ('exitCode', 'exit_code', 'returncode'):
                        value = node.get(key)
                        if isinstance(value, int):
                            exit_codes.append(value)
                continue

            text = coerce_text(item)
            if text:
                assistant_text_parts.append(text)

        assistant_text = '\n'.join(part for part in assistant_text_parts if part).strip()
        usage = extract_usage(req)
        model = extract_model_from_request(req)
        input_tokens = estimate_input_tokens(turns, user_text, usage['input_tokens'])
        output_tokens = usage['output_tokens'] or max(1, len(assistant_text) // 4)
        commands = []
        for call in tool_calls:
            args = call.get('args') or {}
            for key in ('command', 'cmd'):
                value = args.get(key)
                if isinstance(value, str) and value.strip():
                    commands.append(value.strip())
                    break
        turns.append({
            'user_text': user_text,
            'assistant_text': assistant_text,
            'tool_calls': tool_calls,
            'tool_names': [call['name'] for call in tool_calls],
            'commands': commands,
            'tool_outputs': tool_outputs,
            'exit_codes': exit_codes,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': calc_cost(input_tokens, output_tokens, model),
            'model': model,
            'has_meaningful_tool': any(name and name not in DISCOVERY_TOOL_NAMES for name in [call['name'] for call in tool_calls]),
        })

    turns = [turn for turn in turns if turn['user_text'] or turn['assistant_text'] or turn['tool_calls']]
    if len(turns) < 2:
        return None

    total_turns = len(turns)
    total_cost = sum(t['cost'] for t in turns)
    total_output = sum(t['output_tokens'] for t in turns)
    total_input = sum(t['input_tokens'] for t in turns)
    model = turns[0]['model']
    avg_turn_cost = total_cost / total_turns if total_turns > 0 else 0

    idle_turns = [t for t in turns if not t['has_meaningful_tool'] and t['output_tokens'] < 150]
    idle_cost = sum(t['cost'] for t in idle_turns)

    chainable = 0
    prev_exec_only = False
    for turn in turns:
        exec_only = len(turn['commands']) == 1 and len(turn['tool_names']) <= 1
        if exec_only and prev_exec_only:
            chainable += 1
        prev_exec_only = exec_only

    files_read = defaultdict(int)
    for turn in turns:
        for cmd in turn['commands']:
            if is_read_command(cmd):
                for path in extract_paths_from_command(cmd):
                    files_read[path] += 1
        for call in turn['tool_calls']:
            name = call['name']
            args = call.get('args') or {}
            if 'read' in name:
                for key in ('uri', 'resource', 'filePath', 'path'):
                    value = args.get(key)
                    if isinstance(value, str) and value:
                        files_read[value] += 1
    duplicate_reads = sum(count - 1 for count in files_read.values() if count > 1)

    toolsearch_count = sum(
        1 for turn in turns for name in turn['tool_names']
        if name in DISCOVERY_TOOL_NAMES or 'findtext' in name or 'search' in name
    )

    failed_tools = sum(
        1 for turn in turns for code in turn['exit_codes']
        if code not in (0, None)
    )

    edit_runs = []
    run = 0
    for turn in turns:
        has_edit = any(name in WRITE_TOOL_NAMES or 'edit' in name or 'replace' in name or 'createfile' in name for name in turn['tool_names'])
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
        avg_turn_cost = total_cost / total_turns if total_turns else 0
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
    for idx in range(1, len(turns)):
        prev_failed = any(code not in (0, None) for code in turns[idx - 1]['exit_codes'])
        curr_failed = any(code not in (0, None) for code in turns[idx]['exit_codes'])
        if prev_failed and curr_failed:
            pingpong_cycles += 1

    agent_spawns = sum(
        1 for turn in turns for name in turn['tool_names']
        if name in AGENT_TOOL_NAMES or 'subagent' in name
    )

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
                'description': 'Search and discovery calls that may be avoidable once the tool or path is known',
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
            'agent_spawns': agent_spawns,
            'skill_calls': 0,
        },
    }


def aggregate_results(results):
    n = len(results)
    total_cost = sum(r['total_cost'] for r in results)
    total_turns = sum(r['total_turns'] for r in results)
    total_output_tokens = sum(r['total_output_tokens'] for r in results)
    total_input_tokens = sum(r['total_input_tokens'] for r in results)
    total_agent_spawns = sum(r['review_fleet']['agent_spawns'] for r in results)

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
            'avg_agent_spawns_per_session': round(total_agent_spawns / n, 1),
            'total_agent_spawns': total_agent_spawns,
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
        'analysis_confidence': build_analysis_confidence(results),
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

    output['reviewer_roi'] = {}
    total_sleep_polls = sum(result['waste'].get('sleep_poll_loops', {}).get('count', 0) for result in results)
    output['polling_summary'] = {
        'total_sleep_poll_turns': total_sleep_polls,
        'avg_per_session': round(total_sleep_polls / n, 1),
        'estimated_cost': round(total_sleep_polls * 0.03, 2),
    }
    output['pricing_metadata'] = get_pricing_metadata(next(iter(output['model_mix']), results[0]['model']))
    return output


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_copilot_sessions.py <sessions.json>")
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
        print(json.dumps({'error': 'No valid Copilot sessions parsed'}))
        sys.exit(1)

    print(json.dumps(aggregate_results(results), indent=2))


if __name__ == '__main__':
    main()
