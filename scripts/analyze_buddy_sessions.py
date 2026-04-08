#!/usr/bin/env python3
"""Analyze CodeBuddy / WorkBuddy sessions from session index DB plus runtime logs."""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from analyze_sessions import MODEL_PATTERNS, PLATFORM_SIGNALS
from model_pricing import get_pricing, get_pricing_metadata


RUN_MAP_RE = re.compile(r"Reporting session created for (?P<run>run-[^:]+(?::\d+)?): conversationId=(?P<session>[a-f0-9]+)")
MODEL_SET_RE = re.compile(r"Setting session model for (?P<session>[a-f0-9]+): (?P<model>.+)")
PROMPT_RE = re.compile(r"Prompting session (?P<session>[a-f0-9]+)")
SUCCESS_RE = re.compile(r"Sub-run (?P<run>run-[^:]+(?::\d+)?) completed successfully, output length: (?P<output>\d+), .* messageCount: (?P<count>\d+)")
FAIL_RE = re.compile(r"Sub-run (?P<run>run-[^:]+(?::\d+)?) failed: (?P<error>.+)")
CLAW_RE = re.compile(r"claw session upsert: (?P<session>[a-f0-9]+)")
TS_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}\.\d+)")
BUDDY_LOG_NAMES = {"codebuddy.log", "workbuddy.log"}


def normalize_model(model):
    model = (model or '').lower()
    for pattern, key in MODEL_PATTERNS:
        if pattern in model:
            return key
    if 'glm' in model:
        return 'gpt-4o-mini'
    if 'gemini' in model:
        return 'gemini-2.5-pro'
    return 'sonnet'


def calc_cost(model, input_tokens, cached_input_tokens, output_tokens):
    pricing = get_pricing(model, total_input_tokens=input_tokens)
    cached_input_tokens = min(cached_input_tokens, input_tokens)
    fresh_input = max(0, input_tokens - cached_input_tokens)
    return (
        fresh_input * pricing['input']
        + cached_input_tokens * pricing.get('cache_read_price', pricing['input'] * pricing['cache_read_mult'])
        + output_tokens * pricing['output']
    ) / 1_000_000


def parse_log_ts(line):
    match = TS_RE.match(line)
    if not match:
        return None
    return datetime.fromisoformat(f"{match.group('date')}T{match.group('time')}+00:00")


def parse_logs(logs_dir):
    per_session = defaultdict(lambda: {
        'models': set(),
        'runs': 0,
        'message_count': 0,
        'output_chars': 0,
        'failures': 0,
        'prompt_events': 0,
        'claw_upserts': 0,
    })
    run_to_session = {}

    if not logs_dir or not Path(logs_dir).exists():
        return per_session

    log_paths = sorted(
        path
        for path in Path(logs_dir).rglob("*")
        if path.is_file() and path.name in BUDDY_LOG_NAMES
    )

    for log_path in log_paths:
        try:
            with open(log_path) as handle:
                for line in handle:
                    if RUN_MAP_RE.search(line):
                        match = RUN_MAP_RE.search(line)
                        run_to_session[match.group('run')] = match.group('session')
                    elif MODEL_SET_RE.search(line):
                        match = MODEL_SET_RE.search(line)
                        per_session[match.group('session')]['models'].add(match.group('model').strip())
                    elif PROMPT_RE.search(line):
                        match = PROMPT_RE.search(line)
                        per_session[match.group('session')]['prompt_events'] += 1
                    elif SUCCESS_RE.search(line):
                        match = SUCCESS_RE.search(line)
                        sid = run_to_session.get(match.group('run'))
                        if sid:
                            per_session[sid]['runs'] += 1
                            per_session[sid]['message_count'] = max(per_session[sid]['message_count'], int(match.group('count')))
                            per_session[sid]['output_chars'] += int(match.group('output'))
                    elif FAIL_RE.search(line):
                        match = FAIL_RE.search(line)
                        sid = run_to_session.get(match.group('run'))
                        if sid:
                            per_session[sid]['failures'] += 1
                    elif CLAW_RE.search(line):
                        match = CLAW_RE.search(line)
                        per_session[match.group('session')]['claw_upserts'] += 1
        except OSError:
            continue

    return per_session


def detect_platform(cwd, title):
    scores = defaultdict(int)
    for text in (cwd or '', title or ''):
        for platform_name, signals in PLATFORM_SIGNALS.items():
            for ext in signals['file_exts']:
                if ext in text:
                    scores[platform_name] += 2
            for pattern in signals['bash_patterns']:
                if pattern in text:
                    scores[platform_name] += 3
    return max(scores, key=scores.get) if scores else 'general'


def analyze_session(session, stats):
    model = normalize_model(next(iter(stats['models']), ''))
    total_turns = max(2, stats['message_count'] or stats['runs'] * 4 or 2)
    output_tokens = max(8, stats['output_chars'] // 4)
    input_tokens = max(output_tokens * 3, len(session.get('title', '')) * 6 + total_turns * 120)
    cache_read = int(input_tokens * 0.45)
    total_cost = calc_cost(model, input_tokens, cache_read, output_tokens)

    failed_tools = stats['failures']
    chainable = max(0, stats['prompt_events'] - stats['runs'])
    toolsearch = 1 if stats['prompt_events'] and total_turns > 6 else 0
    heartbeat_idle = stats['claw_upserts']
    memory_accumulation = 1 if heartbeat_idle >= 3 else 0
    context_rot = 1 if total_turns >= 12 or stats['output_chars'] >= 4000 else 0
    verbose_count = 1 if stats['output_chars'] >= 4000 else 0
    codebase_wandering = 1 if total_turns >= 10 else 0

    return {
        'file': Path(session['path']).name,
        'timestamp': session['timestamp'],
        'model': model,
        'platform': detect_platform(session.get('cwd'), session.get('title')),
        'total_turns': total_turns,
        'total_cost': round(total_cost, 4),
        'total_output_tokens': output_tokens,
        'total_cache_read': cache_read,
        'total_cache_create': 0,
        'cost_per_turn': round(total_cost / total_turns, 4),
        'waste': {
            'idle_narration': {'turns': 0, 'cost': 0, 'description': 'Short assistant messages that narrate the next action instead of doing it'},
            'chainable_bash': {'turns': chainable, 'cost': round(chainable * 0.02, 4), 'description': 'Consecutive command-heavy assistant steps that could likely be grouped'},
            'duplicate_reads': {'count': 0, 'cost': 0, 'description': 'Same file or path referenced multiple times in one conversation'},
            'toolsearch': {'count': toolsearch, 'cost': round(toolsearch * 0.015, 4), 'description': 'Repeated search/exploration actions before narrowing to a concrete change'},
            'failed_tools': {'count': failed_tools, 'cost': round(failed_tools * 0.04, 4), 'description': 'Failed actions or visible error loops that force retries'},
            'unbatched_edits': {'turns': 0, 'cost': 0, 'description': 'Multiple edit-like responses that could be grouped more tightly'},
            'sleep_poll_loops': {'count': 0, 'cost': 0, 'description': 'Polling or sleep loops that add waiting turns'},
            'git_ceremony': {'turns': 0, 'cost': 0, 'description': 'Consecutive git-only command steps that could be grouped'},
            'context_rot': {'detected': context_rot, 'total_turns': total_turns, 'cost': round(total_cost * 0.2 if context_rot else 0, 4), 'description': 'Conversation grew large enough that reread context likely dominated later turns'},
            'verbose_output': {'count': verbose_count, 'chars': stats['output_chars'], 'cost': round(total_cost * 0.1 if verbose_count else 0, 4), 'description': 'Large output or diff payloads that add significant reread cost'},
            'codebase_wandering': {'turns': codebase_wandering, 'cost': round(codebase_wandering * 0.03, 4), 'description': 'Extended exploration before acting'},
            'pingpong_debugging': {'cycles': max(0, failed_tools - 1), 'cost': round(max(0, failed_tools - 1) * 0.05, 4), 'description': 'Repeated failure cycles across adjacent assistant steps'},
            'heartbeat_idle': {'turns': heartbeat_idle, 'cost': round(heartbeat_idle * 0.01, 4), 'description': 'Always-on heartbeat idle cost'},
            'workspace_bloat': {'tokens': heartbeat_idle * 600, 'cost': round(heartbeat_idle * 0.01, 4), 'description': 'Large always-on system files reread every wake-up'},
            'memory_accumulation': {'detected': memory_accumulation, 'cost': round(0.03 if memory_accumulation else 0, 4), 'description': 'Always-on session history growth without pruning'},
        },
        'review_fleet': {'reviewer_agents': 0, 'reviewer_types': [], 'agent_spawns': 0, 'skill_calls': 0},
        'project': session['project'],
        'date': session['date'],
    }


def aggregate(results):
    n = len(results)
    total_cost = sum(result['total_cost'] for result in results)
    total_turns = sum(result['total_turns'] for result in results)
    waste_totals = defaultdict(lambda: {'cost': 0, 'description': ''})

    for result in results:
        for key, waste in result['waste'].items():
            waste_totals[key]['cost'] += waste['cost']
            waste_totals[key]['description'] = waste['description']

    total_waste_raw = sum(item['cost'] for item in waste_totals.values())
    total_waste = min(total_waste_raw, total_cost * 0.85)
    total_output_tokens = sum(result['total_output_tokens'] for result in results)
    total_cache_read = sum(result['total_cache_read'] for result in results)

    out = {
        'summary': {
            'sessions': n,
            'total_sessions': n,
            'date_range': f"{results[0]['date']} to {results[-1]['date']}",
            'total_cost': round(total_cost, 2),
            'avg_cost_per_session': round(total_cost / n, 2),
            'avg_turns_per_session': round(total_turns / n, 1),
            'avg_cost_per_turn': round(total_cost / total_turns, 4) if total_turns else 0,
            'total_waste': round(total_waste, 2),
            'waste_per_session': round(total_waste / n, 3),
            'waste_percentage': round(total_waste / total_cost * 100, 1) if total_cost > 0 else 0,
            'projected_cost_after_fix': round(max(0, total_cost - total_waste) / n, 2),
            'avg_context_window_tokens': round(total_cache_read / total_turns) if total_turns else 0,
            'avg_output_tokens_per_turn': round(total_output_tokens / total_turns) if total_turns else 0,
            'avg_agent_spawns_per_session': 0.0,
            'total_agent_spawns': 0,
            'wasteful_turns_total': sum(result['waste']['chainable_bash']['turns'] + result['waste']['codebase_wandering']['turns'] + result['waste']['heartbeat_idle']['turns'] for result in results),
            'wasteful_turns_pct': 0,
            'context_rot_sessions': sum(1 for result in results if result['waste']['context_rot']['detected']),
            'context_rot_pct': round(sum(1 for result in results if result['waste']['context_rot']['detected']) / n * 100, 1),
            'total_turns': total_turns,
            'total_output_tokens': total_output_tokens,
            'total_cache_read': total_cache_read,
            'total_cache_create': 0,
        },
        'waste_breakdown': {},
        'sessions': results,
    }
    out['summary']['wasteful_turns_pct'] = round(out['summary']['wasteful_turns_total'] / total_turns * 100, 1) if total_turns else 0

    for key in sorted(waste_totals, key=lambda item: -waste_totals[item]['cost']):
        waste = waste_totals[key]
        out['waste_breakdown'][key] = {
            'total_cost': round(waste['cost'], 2),
            'per_session': round(waste['cost'] / n, 3),
            'percentage_of_waste': round(waste['cost'] / total_waste_raw * 100, 1) if total_waste_raw > 0 else 0,
            'description': waste['description'],
        }

    projects = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0, 'waste': 0})
    models = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0})
    platforms = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'turns': 0, 'waste': 0})
    for result in results:
        projects[result['project']]['sessions'] += 1
        projects[result['project']]['cost'] += result['total_cost']
        projects[result['project']]['turns'] += result['total_turns']
        projects[result['project']]['waste'] += sum(waste['cost'] for waste in result['waste'].values())
        models[result['model']]['sessions'] += 1
        models[result['model']]['cost'] += result['total_cost']
        models[result['model']]['turns'] += result['total_turns']
        platforms[result['platform']]['sessions'] += 1
        platforms[result['platform']]['cost'] += result['total_cost']
        platforms[result['platform']]['turns'] += result['total_turns']
        platforms[result['platform']]['waste'] += sum(waste['cost'] for waste in result['waste'].values())

    out['per_project'] = {
        project: {
            'sessions': info['sessions'],
            'total_cost': round(info['cost'], 2),
            'avg_cost': round(info['cost'] / info['sessions'], 2),
            'avg_turns': round(info['turns'] / info['sessions'], 1),
            'waste': round(info['waste'], 2),
            'waste_pct': round(min(info['waste'], info['cost'] * 0.85) / info['cost'] * 100, 1) if info['cost'] > 0 else 0,
        }
        for project, info in sorted(projects.items(), key=lambda item: -item[1]['cost'])
    }
    out['model_mix'] = {
        model: {
            'sessions': info['sessions'],
            'pct_sessions': round(info['sessions'] / n * 100, 1),
            'total_cost': round(info['cost'], 2),
            'pct_cost': round(info['cost'] / total_cost * 100, 1) if total_cost > 0 else 0,
            'avg_cost': round(info['cost'] / info['sessions'], 2),
            'avg_turns': round(info['turns'] / info['sessions'], 1),
        }
        for model, info in sorted(models.items(), key=lambda item: -item[1]['cost'])
    }
    out['platform_mix'] = {
        platform_name: {
            'sessions': info['sessions'],
            'total_cost': round(info['cost'], 2),
            'avg_cost': round(info['cost'] / info['sessions'], 2),
            'waste_pct': round(min(info['waste'], info['cost'] * 0.85) / info['cost'] * 100, 1) if info['cost'] > 0 else 0,
        }
        for platform_name, info in sorted(platforms.items(), key=lambda item: -item[1]['cost'])
    }
    out['reviewer_roi'] = {}
    out['polling_summary'] = {'total_sleep_poll_turns': 0, 'avg_per_session': 0, 'estimated_cost': 0}
    primary_model = next(iter(out['model_mix']), results[0]['model'])
    out['analysis_confidence'] = {
        'score': 0.45,
        'label': 'estimated',
        'reason': 'CodeBuddy analysis reconstructs token counts from runtime logs; no billing-grade usage data is available.',
    }
    out['pricing_metadata'] = get_pricing_metadata(primary_model)
    return out


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_buddy_sessions.py <sessions.json>")
        sys.exit(1)

    with open(sys.argv[1]) as handle:
        data = json.load(handle)

    sessions = data.get('sessions', [])
    if not sessions:
        print(json.dumps({'error': 'No sessions found'}))
        sys.exit(1)

    log_stats = parse_logs(sessions[0].get('logs_dir'))
    results = [analyze_session(session, log_stats.get(session.get('conversation_id'), {'models': set(), 'runs': 0, 'message_count': 0, 'output_chars': 0, 'failures': 0, 'prompt_events': 0, 'claw_upserts': 0})) for session in sessions]
    results.sort(key=lambda result: result['timestamp'])
    print(json.dumps(aggregate(results), indent=2))


if __name__ == '__main__':
    main()
