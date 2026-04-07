#!/usr/bin/env python3
"""Parse and analyze Claude Code session logs for cost and waste patterns."""
import json, sys, os
from collections import defaultdict
from pathlib import Path

# Pricing per MTok: {input, output, cache_read_mult, cache_create_mult}
# cache_read = input * cache_read_mult, cache_create = input * cache_create_mult
PRICING = {
    # Claude models
    'sonnet': {'input': 3, 'output': 15, 'cache_read_mult': 0.1, 'cache_create_mult': 1.25},
    'opus': {'input': 5, 'output': 25, 'cache_read_mult': 0.1, 'cache_create_mult': 1.25},
    'haiku': {'input': 0.80, 'output': 4, 'cache_read_mult': 0.1, 'cache_create_mult': 1.25},
    # OpenAI models (no prompt caching in same sense — treat cache_read as input)
    'gpt-4o': {'input': 2.50, 'output': 10, 'cache_read_mult': 0.5, 'cache_create_mult': 1.0},
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60, 'cache_read_mult': 0.5, 'cache_create_mult': 1.0},
    'gpt-4.1': {'input': 2.00, 'output': 8, 'cache_read_mult': 0.5, 'cache_create_mult': 1.0},
    'gpt-4.1-mini': {'input': 0.40, 'output': 1.60, 'cache_read_mult': 0.5, 'cache_create_mult': 1.0},
    'o1': {'input': 15, 'output': 60, 'cache_read_mult': 0.5, 'cache_create_mult': 1.0},
    'o3': {'input': 10, 'output': 40, 'cache_read_mult': 0.5, 'cache_create_mult': 1.0},
    'o3-mini': {'input': 1.10, 'output': 4.40, 'cache_read_mult': 0.5, 'cache_create_mult': 1.0},
    'o4-mini': {'input': 1.10, 'output': 4.40, 'cache_read_mult': 0.5, 'cache_create_mult': 1.0},
    # Google models
    'gemini-2.5-pro': {'input': 1.25, 'output': 10, 'cache_read_mult': 0.25, 'cache_create_mult': 1.0},
    'gemini-2.5-flash': {'input': 0.15, 'output': 0.60, 'cache_read_mult': 0.25, 'cache_create_mult': 1.0},
    'gemini-2.0-flash': {'input': 0.10, 'output': 0.40, 'cache_read_mult': 0.25, 'cache_create_mult': 1.0},
    # DeepSeek
    'deepseek-v3': {'input': 0.27, 'output': 1.10, 'cache_read_mult': 0.1, 'cache_create_mult': 1.0},
    'deepseek-r1': {'input': 0.55, 'output': 2.19, 'cache_read_mult': 0.14, 'cache_create_mult': 1.0},
}

def calc_cost(usage, model='sonnet'):
    p = PRICING.get(model, PRICING['sonnet'])
    inp = usage.get('input_tokens', 0)
    out = usage.get('output_tokens', 0)
    cr = usage.get('cache_read_input_tokens', 0)
    cc = usage.get('cache_creation_input_tokens', 0)
    return (inp * p['input'] + cr * p['input'] * p['cache_read_mult'] +
            cc * p['input'] * p['cache_create_mult'] + out * p['output']) / 1_000_000

MODEL_PATTERNS = [
    ('opus', 'opus'), ('sonnet', 'sonnet'), ('haiku', 'haiku'),
    ('gpt-4o-mini', 'gpt-4o-mini'), ('gpt-4o', 'gpt-4o'),
    ('gpt-4.1-mini', 'gpt-4.1-mini'), ('gpt-4.1', 'gpt-4.1'),
    ('o4-mini', 'o4-mini'), ('o3-mini', 'o3-mini'), ('o3', 'o3'), ('o1', 'o1'),
    ('gemini-2.5-pro', 'gemini-2.5-pro'), ('gemini-2.5-flash', 'gemini-2.5-flash'),
    ('gemini-2.0-flash', 'gemini-2.0-flash'),
    ('deepseek-v3', 'deepseek-v3'), ('deepseek-r1', 'deepseek-r1'),
]

def detect_model(records):
    for r in records:
        model_str = r.get('message', {}).get('model', '').lower()
        if not model_str:
            continue
        for pattern, key in MODEL_PATTERNS:
            if pattern in model_str:
                return key
    return 'sonnet'  # default fallback

def analyze_session(filepath):
    records = []
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except (IOError, PermissionError):
        return None

    if not records:
        return None

    # Get timestamp
    first_ts = None
    for r in records:
        if 'timestamp' in r:
            first_ts = r['timestamp']
            break
    if not first_ts:
        return None

    model = detect_model(records)

    # Analyze assistant turns
    assistant_turns = []
    for r in records:
        if r.get('type') != 'assistant':
            continue
        msg = r.get('message', {})
        usage = msg.get('usage', {})
        content = msg.get('content', '')

        tools = []
        text_output = 0
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    if block.get('type') == 'tool_use':
                        tools.append(block.get('name', ''))
                    elif block.get('type') == 'text':
                        text_output += len(block.get('text', ''))
        else:
            text_output = len(str(content))

        out = usage.get('output_tokens', 0)
        cost = calc_cost(usage, model)

        assistant_turns.append({
            'tools': tools,
            'has_tool': len(tools) > 0,
            'output_tokens': out,
            'text_chars': text_output,
            'cost': cost,
            'cache_read': usage.get('cache_read_input_tokens', 0),
            'cache_create': usage.get('cache_creation_input_tokens', 0),
        })

    if len(assistant_turns) < 3:
        return None

    # === WASTE DETECTION ===

    # 1. Idle narration turns (no tool, <150 output tokens)
    idle_turns = [t for t in assistant_turns if not t['has_tool'] and t['output_tokens'] < 150]
    idle_cost = sum(t['cost'] for t in idle_turns)

    # 2. Consecutive solo Bash (chainable with &&)
    chainable = 0
    prev_bash = False
    for t in assistant_turns:
        is_solo_bash = t['tools'] == ['Bash']
        if is_solo_bash and prev_bash:
            chainable += 1
        prev_bash = is_solo_bash

    # 3. File re-reads
    files_read = defaultdict(int)
    for r in records:
        if r.get('type') != 'assistant':
            continue
        content = r.get('message', {}).get('content', '')
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'tool_use' and block.get('name') == 'Read':
                    fpath = block.get('input', {}).get('file_path', '')
                    if fpath:
                        files_read[fpath] += 1
    duplicate_reads = sum(count - 1 for count in files_read.values() if count > 1)

    # 4. ToolSearch calls (often avoidable)
    toolsearch_count = sum(1 for t in assistant_turns if 'ToolSearch' in t['tools'])

    # 5. Failed tool calls
    failed_tools = 0
    for r in records:
        if r.get('type') != 'user':
            continue
        content = r.get('message', {}).get('content', '')
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'tool_result' and block.get('is_error'):
                    failed_tools += 1

    # 6. Edit batching missed (consecutive single-Edit turns)
    edit_runs = []
    run = 0
    for t in assistant_turns:
        if 'Edit' in t['tools']:
            run += 1
        else:
            if run > 0:
                edit_runs.append(run)
            run = 0
    if run > 0:
        edit_runs.append(run)
    batchable_edits = sum(r - 1 for r in edit_runs if r > 1)

    # 7. Multi-edit turns (already batching?)
    multi_edit_turns = 0
    for t in assistant_turns:
        if t['tools'].count('Edit') > 1:
            multi_edit_turns += 1

    # Totals
    total_cost = sum(t['cost'] for t in assistant_turns)
    total_turns = len(assistant_turns)
    total_cache_read = sum(t['cache_read'] for t in assistant_turns)
    total_cache_create = sum(t['cache_create'] for t in assistant_turns)
    total_output = sum(t['output_tokens'] for t in assistant_turns)

    return {
        'file': os.path.basename(filepath),
        'timestamp': first_ts,
        'model': model,
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
                'description': 'Turns with no tool call and <150 output tokens (pure narration)',
            },
            'chainable_bash': {
                'turns': chainable,
                'cost': round(chainable * 0.02, 4),
                'description': 'Consecutive solo Bash turns that could use &&',
            },
            'duplicate_reads': {
                'count': duplicate_reads,
                'cost': round(duplicate_reads * 0.02, 4),
                'description': 'Same file Read multiple times in one session',
            },
            'toolsearch': {
                'count': toolsearch_count,
                'cost': round(toolsearch_count * 0.025, 4),
                'description': 'ToolSearch calls (often avoidable with direct tool names)',
            },
            'failed_tools': {
                'count': failed_tools,
                'cost': round(failed_tools * 0.04, 4),
                'description': 'Failed tool calls (wasted turn + retry)',
            },
            'unbatched_edits': {
                'turns': batchable_edits,
                'cost': round(batchable_edits * 0.02, 4),
                'description': 'Consecutive Edit turns that could be batched into one',
            },
        },
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_sessions.py <sessions.json>")
        print("  Input: JSON from find_logs.py (reads 'sessions' array)")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    sessions_meta = data.get('sessions', [])
    if not sessions_meta:
        print(json.dumps({"error": "No sessions found"}))
        sys.exit(1)

    results = []
    for meta in sessions_meta:
        result = analyze_session(meta['path'])
        if result:
            result['project'] = meta.get('project', 'unknown')
            result['date'] = meta.get('date', 'unknown')
            results.append(result)

    # Aggregate stats
    n = len(results)
    if n == 0:
        print(json.dumps({"error": "No valid sessions parsed"}))
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

    total_waste = sum(w['cost'] for w in waste_totals.values())

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
            'projected_cost_after_fix': round((total_cost - total_waste) / n, 2),
        },
        'waste_breakdown': {},
        'sessions': results,
    }

    for key in sorted(waste_totals, key=lambda k: -waste_totals[k]['cost']):
        w = waste_totals[key]
        output['waste_breakdown'][key] = {
            'total_cost': round(w['cost'], 2),
            'per_session': round(w['cost'] / n, 3),
            'percentage_of_waste': round(w['cost'] / total_waste * 100, 1) if total_waste > 0 else 0,
            'description': w['description'],
        }

    # Per-project breakdown
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

    # Model mix analysis
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

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
