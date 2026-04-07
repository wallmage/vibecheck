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

# === PLATFORM / STACK DETECTION ===
# Detect dev type from tool calls, file paths, bash commands

PLATFORM_SIGNALS = {
    'ios': {
        'file_exts': {'.swift', '.xcodeproj', '.xcworkspace', '.pbxproj', '.storyboard', '.xib', '.xcstrings', '.plist'},
        'bash_patterns': ['xcodebuild', 'xcrun', 'simctl', 'swift build', 'swift test', 'swift package',
                          'pod install', 'carthage', 'xcpretty', 'instruments', 'altool', 'notarytool'],
        'tool_patterns': ['XcodeBuildMCP', 'preview_start'],
    },
    'android': {
        'file_exts': {'.kt', '.java', '.gradle', '.kts'},
        'bash_patterns': ['gradle', 'gradlew', 'adb', 'emulator', 'sdkmanager', 'aapt', 'apktool'],
        'tool_patterns': [],
    },
    'web_frontend': {
        'file_exts': {'.tsx', '.jsx', '.vue', '.svelte', '.css', '.scss', '.less', '.html'},
        'bash_patterns': ['npm ', 'npx ', 'yarn ', 'pnpm ', 'vite', 'webpack', 'next ', 'nuxt',
                          'eslint', 'prettier', 'tsc ', 'playwright', 'cypress'],
        'tool_patterns': [],
    },
    'backend': {
        'file_exts': {'.go', '.rs', '.rb', '.php', '.ex', '.exs'},
        'bash_patterns': ['go build', 'go test', 'cargo build', 'cargo test', 'rails', 'bundle',
                          'composer', 'mix ', 'docker build', 'docker-compose', 'docker compose',
                          'kubectl', 'terraform', 'ansible'],
        'tool_patterns': [],
    },
    'python': {
        'file_exts': {'.py', '.pyi', '.ipynb'},
        'bash_patterns': ['pip install', 'pip3 install', 'poetry ', 'uv ', 'pytest', 'mypy',
                          'ruff ', 'black ', 'flask', 'django', 'fastapi', 'uvicorn'],
        'tool_patterns': [],
    },
    'devops': {
        'file_exts': {'.tf', '.yml', '.yaml', '.Dockerfile'},
        'bash_patterns': ['terraform', 'kubectl', 'helm', 'docker', 'ansible', 'pulumi',
                          'aws ', 'gcloud', 'az ', 'k9s'],
        'tool_patterns': [],
    },
}

def detect_platform(records):
    """Detect development platform/stack from session content."""
    scores = defaultdict(int)

    for r in records:
        if r.get('type') != 'assistant':
            continue
        content = r.get('message', {}).get('content', '')
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue

            # Check tool names
            tool_name = block.get('name', '')
            for platform, signals in PLATFORM_SIGNALS.items():
                if tool_name in signals['tool_patterns']:
                    scores[platform] += 5

            # Check file paths in tool inputs
            tool_input = block.get('input', {})
            if isinstance(tool_input, dict):
                for val in tool_input.values():
                    if isinstance(val, str):
                        for platform, signals in PLATFORM_SIGNALS.items():
                            for ext in signals['file_exts']:
                                if val.endswith(ext) or ext in val:
                                    scores[platform] += 2

            # Check bash commands
            if block.get('type') == 'tool_use' and block.get('name') == 'Bash':
                cmd = tool_input.get('command', '') if isinstance(tool_input, dict) else ''
                for platform, signals in PLATFORM_SIGNALS.items():
                    for pat in signals['bash_patterns']:
                        if pat in cmd:
                            scores[platform] += 3

    if not scores:
        return 'general'
    return max(scores, key=scores.get)

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

    # 8. Sleep/poll loops (generic — not just codex)
    sleep_poll_turns = 0
    for r in records:
        if r.get('type') != 'assistant':
            continue
        content = r.get('message', {}).get('content', '')
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'tool_use' and block.get('name') == 'Bash':
                    cmd = block.get('input', {}).get('command', '') if isinstance(block.get('input'), dict) else ''
                    # Detect sleep commands (not grep for sleep)
                    if ('sleep ' in cmd or 'sleep(' in cmd) and 'grep' not in cmd and 'rg ' not in cmd:
                        sleep_poll_turns += 1

    # 9. Agent spawn overhead
    agent_spawns = sum(1 for t in assistant_turns if 'Agent' in t['tools'])

    # 10. Git ceremony (consecutive git-only turns)
    git_ceremony = 0
    prev_git = False
    for r in records:
        if r.get('type') != 'assistant':
            continue
        content = r.get('message', {}).get('content', '')
        if isinstance(content, list):
            is_git_only = False
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'tool_use' and block.get('name') == 'Bash':
                    cmd = block.get('input', {}).get('command', '') if isinstance(block.get('input'), dict) else ''
                    if cmd.strip().startswith('git '):
                        is_git_only = True
            if is_git_only and prev_git:
                git_ceremony += 1
            prev_git = is_git_only

    # 11. Reviewer fleet detection
    reviewer_agents = 0
    reviewer_types = set()
    for t in assistant_turns:
        if 'Agent' in t['tools']:
            # Check if agent description contains reviewer keywords
            pass  # Detected from agent spawn descriptions below

    for r in records:
        if r.get('type') != 'assistant':
            continue
        content = r.get('message', {}).get('content', '')
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'tool_use' and block.get('name') == 'Agent':
                    inp = block.get('input', {})
                    desc = inp.get('description', '').lower() if isinstance(inp, dict) else ''
                    agent_type = inp.get('subagent_type', '').lower() if isinstance(inp, dict) else ''
                    for rtype in ['qa', 'design', 'judgment', 'ux', 'codex']:
                        if rtype in desc or rtype in agent_type:
                            reviewer_agents += 1
                            reviewer_types.add(rtype)

    # 12. Skill calls
    skill_calls = sum(1 for t in assistant_turns if 'Skill' in t['tools'])

    # === NEW UNIVERSAL WASTE DETECTORS ===

    # Pre-compute totals for detectors below
    total_turns = len(assistant_turns)
    total_cost = sum(t['cost'] for t in assistant_turns)

    # 13. Context rot (conversation too long — cost per turn grows linearly)
    # Break-even is ~12 turns; after that, /clear + fresh start is cheaper.
    # We flag sessions where context tax dominates: high cache_read relative to output.
    session_context_rot = 0
    if total_turns > 20:
        # Late turns cost much more than early turns due to accumulated context
        # Measure: avg cache_read in last 25% of turns vs first 25%
        quarter = max(1, total_turns // 4)
        early_cr = sum(t['cache_read'] for t in assistant_turns[:quarter]) / quarter
        late_cr = sum(t['cache_read'] for t in assistant_turns[-quarter:]) / quarter
        if early_cr > 0 and late_cr / early_cr > 3:
            session_context_rot = 1
    context_rot_cost = 0
    if session_context_rot and total_turns > 20:
        # Estimate: turns beyond 20 that could have been a fresh session
        excess_turns = total_turns - 20
        avg_turn_cost = total_cost / total_turns if total_turns > 0 else 0
        # Late turns cost ~2x average, so excess cost ≈ excess_turns * avg_turn_cost
        context_rot_cost = round(excess_turns * avg_turn_cost * 0.5, 4)

    # 14. Verbose tool output flooding (bash outputs that inject huge context)
    # Detect: tool_result blocks with >5000 chars (build logs, npm output, etc.)
    verbose_output_count = 0
    verbose_output_chars = 0
    for r in records:
        if r.get('type') != 'user':
            continue
        content = r.get('message', {}).get('content', '')
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'tool_result':
                    result_content = block.get('content', '')
                    if isinstance(result_content, list):
                        for sub in result_content:
                            if isinstance(sub, dict) and sub.get('type') == 'text':
                                chars = len(sub.get('text', ''))
                                if chars > 5000:
                                    verbose_output_count += 1
                                    verbose_output_chars += chars
                    elif isinstance(result_content, str) and len(result_content) > 5000:
                        verbose_output_count += 1
                        verbose_output_chars += len(result_content)
    # Each verbose output adds to cache_create AND every future cache_read
    verbose_output_tokens = verbose_output_chars // 4
    p = PRICING.get(model, PRICING['sonnet'])
    verbose_cost = round(verbose_output_tokens * p['input'] * p['cache_create_mult'] / 1_000_000
                         + verbose_output_tokens * total_turns * p['input'] * p['cache_read_mult'] / 1_000_000, 4)

    # 15. Codebase wandering (excessive Read/Grep/Glob exploration without Edits)
    # Detect: sequences of 5+ consecutive read/search turns with no Edit/Write
    explore_streak = 0
    max_explore_streak = 0
    total_explore_waste = 0
    for t in assistant_turns:
        explore_tools = {'Read', 'Grep', 'Glob', 'Agent'}
        action_tools = {'Edit', 'Write', 'Bash', 'NotebookEdit'}
        if any(tool in explore_tools for tool in t['tools']) and not any(tool in action_tools for tool in t['tools']):
            explore_streak += 1
        else:
            if explore_streak >= 5:
                total_explore_waste += explore_streak - 3  # 3 reads is reasonable, rest is waste
            explore_streak = 0
    if explore_streak >= 5:
        total_explore_waste += explore_streak - 3

    # 16. Ping-pong debugging (Edit → error → Edit → error cycles)
    # Detect: alternating Edit turns and failed tool results on same file
    pingpong_cycles = 0
    recent_edit_file = None
    recent_error = False
    for r in records:
        if r.get('type') == 'assistant':
            content = r.get('message', {}).get('content', '')
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'tool_use':
                        if block.get('name') in ('Edit', 'Write'):
                            fpath = block.get('input', {}).get('file_path', '') if isinstance(block.get('input'), dict) else ''
                            if recent_error and fpath == recent_edit_file:
                                pingpong_cycles += 1
                            recent_edit_file = fpath
                            recent_error = False
        elif r.get('type') == 'user':
            content = r.get('message', {}).get('content', '')
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'tool_result' and block.get('is_error'):
                        recent_error = True

    # Totals
    total_cost = sum(t['cost'] for t in assistant_turns)
    # total_turns already computed above for waste detectors
    total_cache_read = sum(t['cache_read'] for t in assistant_turns)
    total_cache_create = sum(t['cache_create'] for t in assistant_turns)
    total_output = sum(t['output_tokens'] for t in assistant_turns)

    # Detect platform
    detected_platform = detect_platform(records)

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
            'sleep_poll_loops': {
                'count': sleep_poll_turns,
                'cost': round(sleep_poll_turns * 0.03, 4),
                'description': 'Sleep/poll turns waiting for background processes',
            },
            'git_ceremony': {
                'turns': git_ceremony,
                'cost': round(git_ceremony * 0.02, 4),
                'description': 'Consecutive git-only turns that could be &&-chained',
            },
            'context_rot': {
                'detected': session_context_rot,
                'total_turns': total_turns,
                'cost': context_rot_cost,
                'description': 'Session too long without /clear — late turns cost 3x+ early turns',
            },
            'verbose_output': {
                'count': verbose_output_count,
                'chars': verbose_output_chars,
                'cost': verbose_cost,
                'description': 'Bash/tool outputs >5K chars flooding context (build logs, npm, etc.)',
            },
            'codebase_wandering': {
                'turns': total_explore_waste,
                'cost': round(total_explore_waste * 0.03, 4),
                'description': '5+ consecutive read/search turns with no action — exploring instead of doing',
            },
            'pingpong_debugging': {
                'cycles': pingpong_cycles,
                'cost': round(pingpong_cycles * 0.05, 4),
                'description': 'Edit→error→re-edit cycles on same file — fix/break/fix loops',
            },
            # Always-on agent patterns — only scored for sessions with 100+ turns
            # AND high idle ratio (indicating heartbeat/cron behavior)
            'heartbeat_idle': {
                'turns': len([t for t in assistant_turns if not t['has_tool'] and t['output_tokens'] < 50]) if total_turns > 100 else 0,
                'cost': round(len([t for t in assistant_turns if not t['has_tool'] and t['output_tokens'] < 50]) * 0.015, 4) if total_turns > 100 else 0,
                'description': 'Heartbeat/wake turns with <50 output tokens and no action (always-on agent idle cost)',
            },
            'workspace_bloat': {
                'tokens': total_cache_create if total_turns > 100 else 0,
                'cost': round(total_cache_create * p['input'] * p['cache_create_mult'] / 1_000_000 * 0.15, 4) if total_turns > 100 else 0,
                'description': 'System prompt files (SOUL.md/AGENTS.md) re-injected every message',
            },
            'memory_accumulation': {
                'detected': 1 if total_turns > 100 else 0,
                'cost': round(max(0, (total_turns - 100) * 0.005), 4) if total_turns > 100 else 0,
                'description': 'Session grew beyond 100+ turns without pruning — context expands indefinitely',
            },
        },
        'review_fleet': {
            'reviewer_agents': reviewer_agents,
            'reviewer_types': list(reviewer_types),
            'agent_spawns': agent_spawns,
            'skill_calls': skill_calls,
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

    total_waste_raw = sum(w['cost'] for w in waste_totals.values())
    # Cap waste at 85% of total cost — patterns overlap, can't eliminate 100%
    total_waste = min(total_waste_raw, total_cost * 0.85)

    # === OPERATIONAL METRICS ===
    total_output_tokens = sum(r['total_output_tokens'] for r in results)
    total_cache_read = sum(r['total_cache_read'] for r in results)
    total_cache_create = sum(r['total_cache_create'] for r in results)
    total_input_tokens = total_cache_read + total_cache_create  # approximate context window
    total_agent_spawns = sum(r['review_fleet']['agent_spawns'] for r in results)

    # Wasteful turns: idle narration + chainable bash + batchable edits + sleep polls + git ceremony
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
            + w.get('heartbeat_idle', {}).get('turns', 0)
        )

    # Context rot sessions
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
            # Operational metrics for before/after comparison
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

    # Platform/stack detection (aggregate)
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

    # Reviewer fleet ROI analysis
    sessions_with_reviewers = [r for r in results if r['review_fleet']['reviewer_agents'] > 0]
    sessions_without_reviewers = [r for r in results if r['review_fleet']['reviewer_agents'] == 0]

    reviewer_roi = {}
    if sessions_with_reviewers and sessions_without_reviewers:
        avg_with = sum(r['total_cost'] for r in sessions_with_reviewers) / len(sessions_with_reviewers)
        avg_without = sum(r['total_cost'] for r in sessions_without_reviewers) / len(sessions_without_reviewers)
        avg_turns_with = sum(r['total_turns'] for r in sessions_with_reviewers) / len(sessions_with_reviewers)
        avg_turns_without = sum(r['total_turns'] for r in sessions_without_reviewers) / len(sessions_without_reviewers)

        # Collect reviewer type frequency
        type_counts = defaultdict(int)
        for r in sessions_with_reviewers:
            for rt in r['review_fleet']['reviewer_types']:
                type_counts[rt] += 1

        reviewer_roi = {
            'sessions_with': len(sessions_with_reviewers),
            'sessions_without': len(sessions_without_reviewers),
            'avg_cost_with': round(avg_with, 2),
            'avg_cost_without': round(avg_without, 2),
            'marginal_cost': round(avg_with - avg_without, 2),
            'avg_turns_with': round(avg_turns_with, 1),
            'avg_turns_without': round(avg_turns_without, 1),
            'reviewer_types_seen': dict(type_counts),
            'total_reviewer_spawns': sum(r['review_fleet']['reviewer_agents'] for r in results),
        }

    output['reviewer_roi'] = reviewer_roi

    # Sleep/poll aggregate
    total_sleep_polls = sum(r['waste'].get('sleep_poll_loops', {}).get('count', 0) for r in results)
    output['polling_summary'] = {
        'total_sleep_poll_turns': total_sleep_polls,
        'avg_per_session': round(total_sleep_polls / n, 1),
        'estimated_cost': round(total_sleep_polls * 0.03, 2),
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
