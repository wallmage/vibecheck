#!/usr/bin/env python3
"""Analyze Antigravity brain artifacts for cost and waste patterns."""
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from analyze_sessions import PLATFORM_SIGNALS
from model_pricing import get_pricing


def estimate_tokens(text):
    return len(text) // 4


def calc_cost(input_tokens, cached_input_tokens, output_tokens):
    pricing = get_pricing('gemini-2.5-pro', total_input_tokens=input_tokens)
    cached_input_tokens = min(cached_input_tokens, input_tokens)
    fresh_input = max(0, input_tokens - cached_input_tokens)
    return (
        fresh_input * pricing['input']
        + cached_input_tokens * pricing.get('cache_read_price', pricing['input'] * pricing['cache_read_mult'])
        + output_tokens * pricing['output']
    ) / 1_000_000


def detect_platform(text):
    scores = defaultdict(int)
    for platform_name, signals in PLATFORM_SIGNALS.items():
        for ext in signals['file_exts']:
            if ext in text:
                scores[platform_name] += 2
        for pattern in signals['bash_patterns']:
            if pattern in text:
                scores[platform_name] += 3
    return max(scores, key=scores.get) if scores else 'general'


def parse_ts(value, fallback):
    if not value:
        return fallback
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return fallback


def analyze_session(session):
    convo_dir = Path(session['path'])
    metadata_files = sorted(convo_dir.glob('*.metadata.json'))
    markdown_files = sorted(convo_dir.glob('*.md'))
    resolved_files = sorted(convo_dir.glob('*.resolved*'))
    artifact_text = []
    latest = parse_ts(session['timestamp'], datetime.now().astimezone())
    summaries = []

    for meta in metadata_files:
        try:
            data = json.loads(meta.read_text())
        except Exception:
            continue
        latest = max(latest, parse_ts(data.get('updatedAt'), latest))
        summary = data.get('summary')
        if isinstance(summary, str):
            summaries.append(summary)

    for md in markdown_files + resolved_files:
        try:
            artifact_text.append(md.read_text(errors='ignore'))
        except OSError:
            continue

    combined = '\n'.join(artifact_text + summaries)
    output_tokens = max(32, estimate_tokens(combined))
    input_tokens = max(output_tokens * 2, output_tokens + len(markdown_files) * 600)
    cache_read = int(input_tokens * 0.5)
    total_cost = calc_cost(input_tokens, cache_read, output_tokens)
    verbose = 1 if len(combined) > 6000 else 0
    artifact_churn = max(0, len(resolved_files))
    planning_overhead = 1 if len(markdown_files) >= 3 else 0
    context_rot = 1 if len(resolved_files) >= 2 or output_tokens > 1500 else 0
    wandering = 1 if len(markdown_files) >= 4 else 0

    return {
        'file': convo_dir.name,
        'timestamp': latest.isoformat(),
        'model': 'gemini-2.5-pro',
        'platform': detect_platform(combined),
        'total_turns': max(2, len(markdown_files) + len(resolved_files)),
        'total_cost': round(total_cost, 4),
        'total_output_tokens': output_tokens,
        'total_cache_read': cache_read,
        'total_cache_create': 0,
        'cost_per_turn': round(total_cost / max(2, len(markdown_files) + len(resolved_files)), 4),
        'waste': {
            'idle_narration': {'turns': 0, 'cost': 0, 'description': 'Short assistant messages that narrate the next action instead of doing it'},
            'chainable_bash': {'turns': 0, 'cost': 0, 'description': 'Consecutive command-heavy assistant steps that could likely be grouped'},
            'duplicate_reads': {'count': artifact_churn, 'cost': round(artifact_churn * 0.02, 4), 'description': 'Repeated resolved artifact versions that indicate redundant rereads or rewrites'},
            'toolsearch': {'count': planning_overhead, 'cost': round(planning_overhead * 0.015, 4), 'description': 'Repeated planning or exploration artifacts before converging'},
            'failed_tools': {'count': 0, 'cost': 0, 'description': 'Failed actions or visible error loops that force retries'},
            'unbatched_edits': {'turns': artifact_churn, 'cost': round(artifact_churn * 0.02, 4), 'description': 'Multiple artifact revisions that could likely be batched more tightly'},
            'sleep_poll_loops': {'count': 0, 'cost': 0, 'description': 'Polling or sleep loops that add waiting turns'},
            'git_ceremony': {'turns': 0, 'cost': 0, 'description': 'Consecutive git-only command steps that could be grouped'},
            'context_rot': {'detected': context_rot, 'total_turns': max(2, len(markdown_files) + len(resolved_files)), 'cost': round(total_cost * 0.2 if context_rot else 0, 4), 'description': 'Conversation grew large enough that reread context likely dominated later turns'},
            'verbose_output': {'count': verbose, 'chars': len(combined), 'cost': round(total_cost * 0.1 if verbose else 0, 4), 'description': 'Large artifact payloads that add significant reread cost'},
            'codebase_wandering': {'turns': wandering, 'cost': round(wandering * 0.03, 4), 'description': 'Extended exploration before acting'},
            'pingpong_debugging': {'cycles': 0, 'cost': 0, 'description': 'Repeated failure cycles across adjacent assistant steps'},
            'heartbeat_idle': {'turns': 0, 'cost': 0, 'description': 'Always-on heartbeat idle cost'},
            'workspace_bloat': {'tokens': 0, 'cost': 0, 'description': 'Large always-on system files reread every wake-up'},
            'memory_accumulation': {'detected': 1 if len(resolved_files) >= 3 else 0, 'cost': round(0.03 if len(resolved_files) >= 3 else 0, 4), 'description': 'Always-on session history growth without pruning'},
        },
        'review_fleet': {'reviewer_agents': 0, 'reviewer_types': [], 'agent_spawns': 0, 'skill_calls': 0},
        'project': session['project'],
        'date': latest.strftime('%Y-%m-%d'),
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
            'wasteful_turns_total': sum(result['waste']['unbatched_edits']['turns'] + result['waste']['codebase_wandering']['turns'] for result in results),
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

    out['per_project'] = {}
    out['model_mix'] = {'gemini-2.5-pro': {'sessions': n, 'pct_sessions': 100.0, 'total_cost': round(total_cost, 2), 'pct_cost': 100.0 if total_cost > 0 else 0, 'avg_cost': round(total_cost / n, 2), 'avg_turns': round(total_turns / n, 1)}}
    platform_totals = defaultdict(lambda: {'sessions': 0, 'cost': 0, 'waste': 0})
    for result in results:
        info = platform_totals[result['platform']]
        info['sessions'] += 1
        info['cost'] += result['total_cost']
        info['waste'] += sum(waste['cost'] for waste in result['waste'].values())
    out['platform_mix'] = {
        platform_name: {
            'sessions': info['sessions'],
            'total_cost': round(info['cost'], 2),
            'avg_cost': round(info['cost'] / info['sessions'], 2),
            'waste_pct': round(min(info['waste'], info['cost'] * 0.85) / info['cost'] * 100, 1) if info['cost'] > 0 else 0,
        }
        for platform_name, info in sorted(platform_totals.items(), key=lambda item: -item[1]['cost'])
    }
    out['reviewer_roi'] = {}
    out['polling_summary'] = {'total_sleep_poll_turns': 0, 'avg_per_session': 0, 'estimated_cost': 0}
    return out


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_antigravity_sessions.py <sessions.json>")
        sys.exit(1)
    with open(sys.argv[1]) as handle:
        data = json.load(handle)
    sessions = data.get('sessions', [])
    if not sessions:
        print(json.dumps({'error': 'No sessions found'}))
        sys.exit(1)
    results = [analyze_session(session) for session in sessions]
    results.sort(key=lambda result: result['timestamp'])
    print(json.dumps(aggregate(results), indent=2))


if __name__ == '__main__':
    main()
