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
        data = json.load(f)

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

    # Model mix
    model_mix = data.get('model_mix', {})
    if model_mix:
        print("-" * 70)
        print("MODEL MIX")
        print("-" * 70)
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
        if pricing_metadata.get('billing_mode') == 'full_billing':
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
        print("  Pass the instruction file path as the second argument for compression analysis.")
    print()

if __name__ == "__main__":
    main()
