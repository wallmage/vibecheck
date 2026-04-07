#!/usr/bin/env python3
"""Generate human-readable cost optimization report from analysis JSON."""
import json, sys, os, subprocess
from pathlib import Path

def fmt(amount):
    return f"${amount:.2f}" if amount >= 1 else f"${amount:.3f}"

def main():
    if len(sys.argv) < 2:
        print("Usage: report.py <analysis.json> [claude_md_path]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    claude_md_path = sys.argv[2] if len(sys.argv) > 2 else None

    s = data['summary']
    w = data['waste_breakdown']

    print("=" * 70)
    print("CLAUDE CODE COST OPTIMIZATION REPORT")
    print("=" * 70)
    print()
    print(f"  Period:              {s['date_range']}")
    print(f"  Sessions analyzed:   {s['sessions']}")
    print(f"  Total spend:         ${s['total_cost']:.2f}")
    print(f"  Avg cost/session:    ${s['avg_cost_per_session']:.2f}")
    print(f"  Avg turns/session:   {s['avg_turns_per_session']:.1f}")
    print(f"  Avg cost/turn:       ${s['avg_cost_per_turn']:.4f}")
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
        risk = "SAFE" if key in ('idle_narration', 'chainable_bash', 'toolsearch') else "REVIEW"
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
        'idle_narration': 'Add: "No turn without tool call. No narration."',
        'chainable_bash': 'Add: "Chain Bash with && instead of separate turns."',
        'toolsearch': 'Add: "Call MCP tools directly, skip ToolSearch."',
        'duplicate_reads': 'Add: "File re-reads banned."',
        'failed_tools': 'Review common failures and add guardrails.',
        'unbatched_edits': 'Add: "Batch multiple Edits into one turn."',
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

    # CLAUDE.md scan
    print("-" * 70)
    print("CLAUDE.MD ANALYSIS")
    print("-" * 70)
    print()

    if claude_md_path and os.path.exists(claude_md_path):
        with open(claude_md_path) as f:
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

        print(f"  File: {claude_md_path}")
        print(f"  Size: {words:,} words, ~{tokens_est:,} tokens")
        print(f"  Context tax: ${tax_per_session:.3f}/session (re-read on every turn)")
        print(f"  Estimated compression: ~{compression_est}%")
        print(f"  Projected: ~{projected_tokens:,} tokens → ${projected_tax:.3f}/session")
        print(f"  Savings: ${tax_savings:.3f}/session")
        print()
        print(f"  Your CLAUDE.md can be trimmed by ~{compression_est}%, which translates")
        print(f"  to ${tax_savings:.3f} per session cost reduction.")
        print(f"  Run /cost-optimizer compress to proceed (approval required for each change).")
    else:
        print("  No CLAUDE.md path provided or file not found.")
        print("  Pass CLAUDE.md path as second argument for compression analysis.")
    print()

if __name__ == "__main__":
    main()
