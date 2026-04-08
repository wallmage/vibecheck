#!/usr/bin/env python3
"""Generate a human-readable cost optimization report from analysis JSON."""
import json, sys, os, subprocess
from pathlib import Path

def fmt(amount):
    return f"${amount:.2f}" if amount >= 1 else f"${amount:.3f}"

def main():
    if len(sys.argv) < 2:
        print("Usage: report.py <analysis.json> [instruction_file_path]")
        sys.exit(1)

    analysis_path = sys.argv[1]
    if not os.path.exists(analysis_path):
        print(f"Error: analysis file not found: {analysis_path}", file=sys.stderr)
        sys.exit(1)

    with open(analysis_path) as f:
        content = f.read().strip()
    if not content:
        print(f"Error: analysis file is empty: {analysis_path}", file=sys.stderr)
        print("This usually means the previous script (analyze_*_sessions.py) failed or produced no output.", file=sys.stderr)
        print("Re-run the scan from the beginning.", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {analysis_path}: {e}", file=sys.stderr)
        sys.exit(1)

    instruction_file_path = sys.argv[2] if len(sys.argv) > 2 else None
    instruction_file_name = Path(instruction_file_path).name if instruction_file_path else "instruction file"

    s = data['summary']
    w = data['waste_breakdown']
    analysis_confidence = data.get('analysis_confidence', {
        'label': 'estimated',
        'score': 0.5,
        'reason': 'Confidence metadata was not included in this analysis.',
    })
    pricing_metadata = data.get('pricing_metadata', {})

    print("=" * 70)
    print("VIBECHECK COST OPTIMIZATION REPORT")
    print("=" * 70)
    print()
    print(f"  Period:              {s['date_range']}")
    print(f"  Sessions analyzed:   {s['sessions']}")
    print(f"  Total spend:         ${s['total_cost']:.2f}")
    print(f"  Avg cost/session:    ${s['avg_cost_per_session']:.2f}")
    print(f"  Avg turns/session:   {s['avg_turns_per_session']:.1f}")
    print(f"  Avg cost/turn:       ${s['avg_cost_per_turn']:.4f}")
    print(f"  Confidence:          {analysis_confidence['label']} ({analysis_confidence.get('score', 0):.2f})")
    if pricing_metadata:
        print(f"  Pricing registry:    {pricing_metadata.get('registry_label', 'unknown')}")
        print(f"  Billing mode:        {pricing_metadata.get('billing_mode', 'token_only_estimate')}")
    print()
    print(f"  Confidence note:     {analysis_confidence['reason']}")
    print()

    header_statistics = data.get('header_statistics', {})
    duration_notes = data.get('duration_notes', {})
    if header_statistics:
        print("-" * 70)
        print("HEADER STATISTICS")
        print("-" * 70)
        print()
        overall = header_statistics.get('overall', {})
        overall_health = overall.get('health', {})
        if overall_health:
            print(f"  Overall:             {overall_health.get('emoji', '')} {overall_health.get('label', '')} ({overall.get('avg_waste_ratio_pct', 0):.1f}% waste)")
            print(f"  Log session duration:{'':<2} {overall.get('avg_session_duration_minutes', '—')} min")
            print(f"  Active session duration: {overall.get('avg_active_session_duration_minutes', '—')} min")
            print()

        if duration_notes:
            print("  Duration notes:")
            print(f"    - {duration_notes.get('log_session_duration', {}).get('label', 'Log session duration')}: {duration_notes.get('log_session_duration', {}).get('description', '')}")
            print(f"    - {duration_notes.get('active_session_duration', {}).get('label', 'Active session duration')}: {duration_notes.get('active_session_duration', {}).get('description', '')}")
            print()

        tools = header_statistics.get('tools', [])
        if tools:
            print("  Tools ranked by usage:")
            print(f"  {'#':>2} {'Health':<8} {'Tool':<24} {'Sess':>5} {'Avg$':>7} {'Turns':>7} {'LogMin':>7} {'ActMin':>7} {'Waste%':>7}")
            print(f"  {'-'*2:>2} {'-'*8} {'-'*24} {'-'*5} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
            for item in tools:
                print(
                    f"  {item.get('rank', 0):>2} "
                    f"{item.get('health', {}).get('emoji', '➖'):<8} "
                    f"{item.get('label', item.get('id')):<24} "
                    f"{item.get('sessions', 0):>5} "
                    f"${item.get('avg_cost_per_session', 0):>6.2f} "
                    f"{item.get('avg_turns_per_session', 0):>6.1f} "
                    f"{item.get('avg_session_duration_minutes', '—'):>6} "
                    f"{item.get('avg_active_session_duration_minutes', '—'):>6} "
                    f"{item.get('avg_waste_ratio_pct', 0):>6.1f}%"
                )
            print()

        models = header_statistics.get('models', [])
        if models:
            print("  Models:")
            print(f"  {'Health':<8} {'Model':<22} {'Sess':>5} {'Avg$':>7} {'Turns':>7} {'LogMin':>7} {'ActMin':>7} {'Waste%':>7}")
            print(f"  {'-'*8} {'-'*22} {'-'*5} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
            for item in models:
                print(
                    f"  {item.get('health', {}).get('emoji', '➖'):<8} "
                    f"{item.get('label', item.get('id')):<22} "
                    f"{item.get('sessions', 0):>5} "
                    f"${item.get('avg_cost_per_session', 0):>6.2f} "
                    f"{item.get('avg_turns_per_session', 0):>6.1f} "
                    f"{item.get('avg_session_duration_minutes', '—'):>6} "
                    f"{item.get('avg_active_session_duration_minutes', '—'):>6} "
                    f"{item.get('avg_waste_ratio_pct', 0):>6.1f}%"
                )
            print()

    # Model mix
    tool_inventory = data.get('tool_inventory', [])
    tool_mix = data.get('tool_mix', {})
    if tool_inventory:
        print("-" * 70)
        print("ALL DETECTED TOOLS")
        print("-" * 70)
        print()
        print(f"  {'Tool':<24} {'Status':<12} {'Sessions':>8} {'Total$':>9} {'Waste%':>8} {'Mode':>18}")
        print(f"  {'-'*24} {'-'*12} {'-'*8} {'-'*9} {'-'*8} {'-'*18}")
        for item in tool_inventory:
            print(
                f"  {item.get('name', item.get('id')):<24} "
                f"{item.get('status', 'detected'):<12} "
                f"{item.get('sessions', 0):>8} "
                f"${item.get('total_cost', 0):>8.2f} "
                f"{item.get('waste_pct', 0):>7.1f}% "
                f"{item.get('analysis_mode', 'unknown'):>18}"
            )
        print()

    if tool_mix:
        print("-" * 70)
        print("TOOL BREAKDOWN")
        print("-" * 70)
        print()
        print(f"  {'Tool':<24} {'Sessions':>8} {'Total$':>9} {'Waste%':>8} {'Mode':>18}")
        print(f"  {'-'*24} {'-'*8} {'-'*9} {'-'*8} {'-'*18}")
        for tool_id, info in tool_mix.items():
            print(f"  {info['name']:<24} {info['sessions']:>8} ${info['total_cost']:>8.2f} {info['waste_pct']:>7.1f}% {info.get('analysis_mode', 'unknown'):>18}")
        print()

    skipped_tools = data.get('skipped_tools', [])
    unsupported_tools = data.get('unsupported_tools', [])
    failed_tools = data.get('failed_tools', [])
    if unsupported_tools or skipped_tools or failed_tools:
        print("-" * 70)
        print("SCAN COVERAGE")
        print("-" * 70)
        print()
        if unsupported_tools:
            print("  Unsupported detected tools:")
            for item in unsupported_tools:
                print(f"    - {item.get('name', item.get('id'))}: {item.get('support_level', 'limited')}")
            print()
        if skipped_tools:
            print("  Skipped tools:")
            for item in skipped_tools:
                print(f"    - {item.get('tool_name', item.get('tool_id'))}: {item.get('reason', 'skipped')}")
            print()
        if failed_tools:
            print("  Failed tools:")
            for item in failed_tools:
                print(f"    - {item.get('tool_name', item.get('tool_id'))} during {item.get('stage', 'unknown')}")
            print()

    optimization_targets = data.get('optimization_targets', [])
    if optimization_targets:
        print("-" * 70)
        print("OPTIMIZATION TARGETS")
        print("-" * 70)
        print()
        for target in optimization_targets:
            kind = target.get('kind', 'instruction_file')
            scope = target.get('scope', 'project')
            priority = target.get('priority_band', 'primary')
            action = target.get('action', 'update')
            filename = target.get('filename') or Path(target.get('file', '')).name
            tool_name = target.get('tool_name', target.get('tool'))
            print(f"  - {tool_name}: {filename} [{kind}, {scope}, {priority}, {action}]")
            print(f"    {target.get('file')}")
        print()

    optimization_plan = data.get('optimization_plan', {})
    if optimization_plan.get('tools'):
        print("-" * 70)
        print("OPTIMIZATION ROADMAP")
        print("-" * 70)
        print()
        for tool in optimization_plan.get('tools', []):
            before_after = tool.get('before_after', {})
            strategy = tool.get('optimization_strategy', {})
            print(
                f"  {tool.get('priority_rank', 0)}. "
                f"{tool.get('health', {}).get('emoji', '➖')} "
                f"{tool.get('tool_label', tool.get('tool_id'))}"
            )
            print(
                f"     Avg$/session: {fmt(before_after.get('current_avg_cost_per_session', 0))} "
                f"-> {fmt(before_after.get('projected_avg_cost_per_session', 0))} | "
                f"Monthly savings: {fmt(before_after.get('projected_monthly_savings', 0))}"
            )
            if strategy:
                print(
                    f"     Strategy: {strategy.get('mode', 'no_targets')} | "
                    f"Primary targets: {strategy.get('counts', {}).get('primary', 0)} | "
                    f"Fallback targets: {strategy.get('counts', {}).get('fallback', 0)}"
                )
            for step in tool.get('steps', []):
                print(
                    f"     {step.get('rank', 0)}. "
                    f"{step.get('health', {}).get('emoji', '➖')} "
                    f"{step.get('title', 'Untitled step')} "
                    f"({step.get('waste_ratio_pct', 0):.1f}% waste)"
                )
            print()

    # Model mix
    model_mix = data.get('model_mix', {})
    if model_mix:
        print("-" * 70)
        print("MODEL MIX")
        print("-" * 70)
        print()

    provider_mix = data.get('provider_mix', {})
    if provider_mix and len(provider_mix) > 1:
        print("-" * 70)
        print("PROVIDER MIX")
        print("-" * 70)
        print()
        print(f"  {'Provider':<16} {'Sessions':>8} {'%Sess':>7} {'Total$':>9} {'%Cost':>7}")
        print(f"  {'-'*16} {'-'*8} {'-'*7} {'-'*9} {'-'*7}")
        for provider, info in provider_mix.items():
            print(f"  {provider:<16} {info['sessions']:>8} {info['pct_sessions']:>6.1f}% ${info['total_cost']:>8.2f} {info['pct_cost']:>6.1f}%")
        print()
        print(f"  {'Model':<20} {'Sessions':>8} {'%Sess':>7} {'Total$':>9} {'%Cost':>7} {'Avg$/sess':>10}")
        print(f"  {'-'*20} {'-'*8} {'-'*7} {'-'*9} {'-'*7} {'-'*10}")
        for model, info in model_mix.items():
            print(f"  {model:<20} {info['sessions']:>8} {info['pct_sessions']:>6.1f}% ${info['total_cost']:>8.2f} {info['pct_cost']:>6.1f}% ${info['avg_cost']:>9.2f}")
        print()

    if pricing_metadata:
        print("-" * 70)
        print("PRICING BASIS")
        print("-" * 70)
        print()
        print(f"  Canonical model:     {pricing_metadata.get('canonical_model', 'unknown')}")
        print(f"  Provider:            {pricing_metadata.get('provider', 'unknown')}")
        print(f"  Registry version:    {pricing_metadata.get('registry_version', 'unknown')}")
        print(f"  Billing mode:        {pricing_metadata.get('billing_mode', 'token_only_estimate')}")
        if pricing_metadata.get('provider') == 'multi':
            print("  Interpretation:      Multiple providers were merged into one machine-wide scan.")
        elif pricing_metadata.get('billing_mode') == 'full_billing':
            print("  Interpretation:      Frontier model with provider-specific billing rules enabled.")
        else:
            print("  Interpretation:      Token/cache pricing is modeled, but tool surcharges remain estimate-only.")
        print()

    # Per-project breakdown
    per_project = data.get('per_project', {})
    if per_project and len(per_project) > 1:
        print("-" * 70)
        print("PER-PROJECT BREAKDOWN")
        print("-" * 70)
        print()
        print(f"  {'Project':<40} {'Sess':>5} {'Avg$':>7} {'Waste%':>7}")
        print(f"  {'-'*40} {'-'*5} {'-'*7} {'-'*7}")
        for proj, info in per_project.items():
            short = proj[:40]
            print(f"  {short:<40} {info['sessions']:>5} ${info['avg_cost']:>6.2f} {info['waste_pct']:>6.1f}%")
        print()

    # Waste breakdown
    print("-" * 70)
    print("WASTE IDENTIFIED")
    print("-" * 70)
    print()

    fixes = []
    for key, info in w.items():
        if info['total_cost'] < 0.01:
            continue
        risk = "SAFE" if key in ('idle_narration', 'chainable_bash', 'toolsearch', 'git_ceremony',
                                    'sleep_poll_loops', 'verbose_output', 'context_rot') else "REVIEW"
        fixes.append((key, info, risk))
        print(f"  {key}:")
        print(f"    {info['description']}")
        print(f"    Cost: {fmt(info['per_session'])}/session ({info['percentage_of_waste']:.0f}% of waste)")
        print(f"    Risk: {risk}")
        print()

    # Savings projection
    print("-" * 70)
    print("SAVINGS PROJECTION")
    print("-" * 70)
    print()
    print(f"  Current avg:         ${s['avg_cost_per_session']:.2f}/session")
    print(f"  Total waste:         {fmt(s['waste_per_session'])}/session ({s['waste_percentage']:.0f}% of spend)")
    print(f"  After optimization:  ${s['projected_cost_after_fix']:.2f}/session")
    print(f"  Savings:             {s['waste_percentage']:.0f}%")
    print()

    if s['sessions'] > 0:
        days_in_range = 14
        daily = s['sessions'] / days_in_range
        monthly_current = s['avg_cost_per_session'] * daily * 30
        monthly_after = s['projected_cost_after_fix'] * daily * 30
        print(f"  At your pace ({daily:.1f} sessions/day):")
        print(f"    Current monthly:   ${monthly_current:.0f}")
        print(f"    After fix:         ${monthly_after:.0f}")
        print(f"    Monthly savings:   ${monthly_current - monthly_after:.0f}")
    print()

    # Recommended fixes
    print("-" * 70)
    print("RECOMMENDED FIXES (in order of impact)")
    print("-" * 70)
    print()

    safe_fixes = [f for f in fixes if f[2] == "SAFE"]
    review_fixes = [f for f in fixes if f[2] == "REVIEW"]

    fix_labels = {
        'idle_narration': 'Add guidance to avoid status-only replies when the next action can happen immediately.',
        'chainable_bash': 'Add: "Chain Bash with && instead of separate turns."',
        'toolsearch': 'Add: "Call MCP tools directly, skip ToolSearch."',
        'duplicate_reads': 'Add guidance to avoid re-reading files unless they changed or accuracy depends on it.',
        'failed_tools': 'Review common failures and add guardrails.',
        'unbatched_edits': 'Add: "Batch multiple Edits into one turn."',
        'sleep_poll_loops': 'Add: "Use --wait flags or run_in_background, never sleep+poll."',
        'git_ceremony': 'Add: "Chain git commands with &&."',
        'context_rot': 'Add guidance to start a fresh thread between unrelated tasks or after long debugging loops.',
        'verbose_output': 'Add: "Pipe verbose commands to /tmp/. Use --quiet flags. Tail last 50 lines."',
        'codebase_wandering': 'Add guidance to prefer focused exploration and use the project instruction file map before broad searching.',
        'pingpong_debugging': 'Add: "After 2 failed fixes, stop → read error → think → single fix."',
        'heartbeat_idle': 'Reduce heartbeat frequency. Check every 30min, not every 5min.',
        'workspace_bloat': 'Compress SOUL.md/AGENTS.md. Remove verbose personality text AI doesn\'t need.',
        'memory_accumulation': 'Add session pruning. Archive sessions >50 turns. Use /compact or equivalent.',
    }

    if safe_fixes:
        print("  AUTO-APPLY (100% safe, no behavior change):")
        for i, (key, info, _) in enumerate(safe_fixes, 1):
            print(f"    {i}. {fix_labels.get(key, key)} (saves {fmt(info['per_session'])}/session)")
        print()

    if review_fixes:
        print("  NEEDS REVIEW (may change behavior):")
        for i, (key, info, _) in enumerate(review_fixes, 1):
            print(f"    {i}. {fix_labels.get(key, key)} (saves {fmt(info['per_session'])}/session)")
        print()

    # Platform-specific recommendations
    platform_mix = data.get('platform_mix', {})
    if platform_mix:
        print("-" * 70)
        print("PLATFORM DETECTION")
        print("-" * 70)
        print()
        primary = list(platform_mix.keys())[0] if platform_mix else 'general'
        print(f"  Primary stack: {primary}")
        if len(platform_mix) > 1:
            others = ', '.join(list(platform_mix.keys())[1:])
            print(f"  Also detected: {others}")
        print()

        PLATFORM_TIPS = {
            'ios': [
                'XcodeBuildMCP: call directly, skip ToolSearch for build/test',
                'Simulator boot: reuse running sim, never boot fresh per session',
                'Swift build + test: chain with &&, never run in parallel (lockfile deadlock)',
                '.pbxproj edits: build immediately after, revert if broken',
                'SourceKit false positives: ignore "No such module" silently',
            ],
            'android': [
                'Gradle: chain assembleDebug + test in one && command',
                'Emulator: reuse running instance, skip boot commands',
                'ADB: batch install + logcat in one turn',
            ],
            'web_frontend': [
                'npm/yarn: chain install + build + test with &&',
                'Dev server: start once, don\'t restart per change (HMR handles it)',
                'node_modules: never explore — use package.json for deps',
                'ESLint/Prettier: run once at end, not per file',
                'Bundle size: check once, not after every edit',
            ],
            'backend': [
                'Docker: rebuild only when Dockerfile changes, not every test',
                'API testing: batch curl/httpie calls, don\'t test endpoint-by-endpoint',
                'go/cargo test: run full suite once, not individual tests sequentially',
                'kubectl: batch get/describe commands with &&',
                'Terraform: plan once, don\'t re-plan after each file edit',
            ],
            'python': [
                'pytest: run once at end with -x (fail-fast), not per-file',
                'pip install: gather all deps, one install command',
                'Type checking: mypy once at end, not incremental',
                'Virtual env: activate once at session start, not per command',
            ],
            'devops': [
                'Terraform output: suppress verbose plan, use -compact-warnings',
                'kubectl: batch commands, pipe long output to /tmp/ instead of reading inline',
                'Docker build: use --quiet to suppress layer output',
                'AWS CLI: batch describe calls, use --query to filter output',
            ],
            'general': [
                'No platform-specific optimizations detected',
                'Universal rules (narration, batching, chaining) apply',
            ],
        }

        tips = PLATFORM_TIPS.get(primary, PLATFORM_TIPS['general'])
        print(f"  Recommendations for {primary} development:")
        for i, tip in enumerate(tips, 1):
            print(f"    {i}. {tip}")
        print()

    # Reviewer fleet ROI
    reviewer_roi = data.get('reviewer_roi', {})
    if reviewer_roi and reviewer_roi.get('sessions_with', 0) > 0:
        print("-" * 70)
        print("REVIEWER FLEET ROI")
        print("-" * 70)
        print()
        print(f"  Sessions with reviewers:    {reviewer_roi['sessions_with']} (avg ${reviewer_roi['avg_cost_with']:.2f})")
        print(f"  Sessions without:           {reviewer_roi['sessions_without']} (avg ${reviewer_roi['avg_cost_without']:.2f})")
        print(f"  Marginal cost of reviews:   ${reviewer_roi['marginal_cost']:.2f}/session")
        print(f"  Extra turns per session:    {reviewer_roi['avg_turns_with'] - reviewer_roi['avg_turns_without']:.0f}")
        print()
        types = reviewer_roi.get('reviewer_types_seen', {})
        if types:
            print(f"  Reviewer types used: {', '.join(f'{k}({v}x)' for k,v in types.items())}")
            print()
        print("  Optimization tips:")
        print("    - Launch all reviewers in parallel (one message, multiple Agent calls)")
        print("    - Use --wait flag for codex instead of sleep/poll loops")
        print("    - Triage rule: fix if user-visible, skip code-internal hygiene")
        print("    - Batch all review fixes into one turn (multiple Edits)")
        print()

    # Polling/wait analysis
    polling = data.get('polling_summary', {})
    if polling.get('total_sleep_poll_turns', 0) > 0:
        print("-" * 70)
        print("POLLING / WAIT OVERHEAD")
        print("-" * 70)
        print()
        print(f"  Sleep/poll turns detected:  {polling['total_sleep_poll_turns']} ({polling['avg_per_session']:.1f}/session)")
        print(f"  Estimated cost:             ${polling['estimated_cost']:.2f}")
        print()
        print("  Each poll turn re-reads the full context ($0.01-0.05).")
        print("  Fix: Use --wait flags where available, or run background tasks")
        print("  with run_in_background:true and let the system notify on completion.")
        print()

    # Instruction file scan
    print("-" * 70)
    print("INSTRUCTION FILE ANALYSIS")
    print("-" * 70)
    print()

    instruction_targets = data.get('instruction_targets', [])
    if instruction_targets:
        print(f"  Detected instruction targets across tools:")
        for target in instruction_targets:
            print(f"    - {target.get('tool_name', target.get('tool'))}: {target.get('file')}")
        print()

    if instruction_file_path and os.path.exists(instruction_file_path):
        with open(instruction_file_path) as f:
            content = f.read()
        chars = len(content)
        words = len(content.split())
        tokens_est = chars // 4
        avg_turns = s['avg_turns_per_session']
        # Context tax: tokens * turns * cache_read_price
        tax_per_session = tokens_est * avg_turns * 0.3 / 1_000_000

        # Estimate compression potential (empirical: 25-40% typical)
        # Heuristic: count markdown overhead, verbose phrases, duplicate content
        markdown_overhead = content.count('**') + content.count('##') + content.count('```') * 3
        verbose_phrases = sum(1 for phrase in ['in order to', 'it is important', 'make sure to', 'this means that',
                                                'which allows', 'note that', 'keep in mind', 'please ensure']
                            if phrase in content.lower())
        blank_line_pairs = content.count('\n\n\n')
        compression_est = min(50, max(15, 20 + verbose_phrases * 3 + blank_line_pairs * 2 + (markdown_overhead // 10)))

        projected_tokens = int(tokens_est * (1 - compression_est / 100))
        projected_tax = projected_tokens * avg_turns * 0.3 / 1_000_000
        tax_savings = tax_per_session - projected_tax

        print(f"  File: {instruction_file_path}")
        print(f"  Size: {words:,} words, ~{tokens_est:,} tokens")
        print(f"  Context tax: ${tax_per_session:.3f}/session (re-read on every turn)")
        print(f"  Estimated compression: ~{compression_est}%")
        print(f"  Projected: ~{projected_tokens:,} tokens → ${projected_tax:.3f}/session")
        print(f"  Savings: ${tax_savings:.3f}/session")
        print()
        print(f"  Your {instruction_file_name} can likely be trimmed by ~{compression_est}%, which translates")
        print(f"  to ${tax_savings:.3f} per session cost reduction.")
        print(f"  Run /vibecheck compress to proceed (approval required for each change).")
    else:
        print("  No instruction file path provided or file not found.")
        if optimization_targets:
            print("  Use the optimization targets above to choose the next file/settings pass.")
        else:
            print("  Pass the instruction file path as the second argument for compression analysis.")
    print()

if __name__ == "__main__":
    main()
