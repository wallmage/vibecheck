#!/usr/bin/env python3
"""Before/after comparison with operational metrics and persistent snapshots.

Stores snapshots locally so each scan auto-compares against baseline.
Shows: turns, sub-agents, context window, wasteful %, cost — before vs after."""
import json, sys, os
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_DIR = Path.home() / '.vibecheck' / 'snapshots'

def load_json(path):
    if not os.path.exists(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        content = f.read().strip()
    if not content:
        print(f"Error: file is empty: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

def find_latest_snapshot():
    """Find the most recent saved snapshot for auto-comparison."""
    if not SNAPSHOT_DIR.exists():
        return None
    snapshots = sorted(SNAPSHOT_DIR.glob('snapshot_*.json'), reverse=True)
    return snapshots[0] if snapshots else None

def save_snapshot(analysis):
    """Save current analysis as a persistent snapshot."""
    try:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = SNAPSHOT_DIR / f'snapshot_{ts}.json'
        snapshot = {
            'schema_version': 1,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': analysis.get('summary', {}),
            'waste_breakdown': analysis.get('waste_breakdown', {}),
            'model_mix': analysis.get('model_mix', {}),
            'per_project': analysis.get('per_project', {}),
            'platform_mix': analysis.get('platform_mix', {}),
        }
        with open(path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        return path
    except OSError:
        return None

def fmt_tokens(n):
    """Format token count as human-readable."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def infer_period_days(summary):
    summary = summary or {}

    raw_period_days = summary.get('period_days')
    if isinstance(raw_period_days, (int, float)) and raw_period_days > 0:
        return max(1, int(raw_period_days))

    date_range = summary.get('date_range')
    if isinstance(date_range, str) and ' to ' in date_range:
        left, right = date_range.split(' to ', 1)
        try:
            start = datetime.strptime(left, '%Y-%m-%d').date()
            end = datetime.strptime(right, '%Y-%m-%d').date()
            return max(1, (end - start).days + 1)
        except ValueError:
            pass

    return 14


def summary_defaults(summary):
    summary = summary or {}
    sessions = summary.get('sessions', summary.get('total_sessions', 0))
    return {
        'date_range': summary.get('date_range') or 'unavailable',
        'period_days': infer_period_days(summary),
        'sessions': sessions,
        'avg_turns_per_session': summary.get('avg_turns_per_session', 0),
        'avg_agent_spawns_per_session': summary.get('avg_agent_spawns_per_session', 0),
        'avg_context_window_tokens': summary.get('avg_context_window_tokens', 0),
        'avg_output_tokens_per_turn': summary.get('avg_output_tokens_per_turn', 0),
        'wasteful_turns_pct': summary.get('wasteful_turns_pct', 0),
        'wasteful_turns_total': summary.get('wasteful_turns_total', 0),
        'total_turns': summary.get('total_turns', 0),
        'context_rot_sessions': summary.get('context_rot_sessions', 0),
        'context_rot_pct': summary.get('context_rot_pct', 0),
        'total_cost': summary.get('total_cost', 0),
        'avg_cost_per_session': summary.get('avg_cost_per_session', 0),
        'avg_cost_per_turn': summary.get('avg_cost_per_turn', 0),
        'total_waste': summary.get('total_waste', 0),
        'waste_percentage': summary.get('waste_percentage', 0),
        'waste_per_session': summary.get(
            'waste_per_session',
            (summary.get('total_waste', 0) / sessions) if sessions else 0,
        ),
        'projected_cost_after_fix': summary.get('projected_cost_after_fix', summary.get('avg_cost_per_session', 0)),
    }


def has_meaningful_baseline(summary):
    summary = summary or {}
    sessions = summary.get('sessions', summary.get('total_sessions', 0))
    numeric_signals = (
        summary.get('total_cost', 0),
        summary.get('avg_cost_per_session', 0),
        summary.get('avg_turns_per_session', 0),
        summary.get('total_turns', 0),
        summary.get('total_waste', 0),
    )
    return sessions > 0 or any(value > 0 for value in numeric_signals)


def normalize_waste_item(info, sessions, total_waste):
    info = info or {}
    per_session = info.get('per_session')
    total_cost = info.get('total_cost')

    if per_session is None and total_cost is not None and sessions > 0:
        per_session = total_cost / sessions
    if total_cost is None and per_session is not None:
        total_cost = per_session * sessions

    total_cost = total_cost or 0
    if per_session is None:
        per_session = (total_cost / sessions) if sessions > 0 else 0

    percentage = info.get('percentage_of_waste')
    if percentage is None:
        percentage = (total_cost / total_waste * 100) if total_waste > 0 else 0

    return {
        'total_cost': total_cost,
        'per_session': per_session,
        'percentage_of_waste': percentage,
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: compare.py <analysis.json> [previous_snapshot.json]")
        print("  Single arg: show current metrics + projected savings")
        print("  Two args: actual before/after comparison")
        print("  Auto-detects previous snapshot from ~/.vibecheck/snapshots/")
        sys.exit(1)

    current = load_json(sys.argv[1])

    # Find previous: explicit arg > auto-detect
    previous = None
    if len(sys.argv) > 2:
        previous = load_json(sys.argv[2])
    else:
        prev_path = find_latest_snapshot()
        if prev_path:
            previous = load_json(prev_path)

    if previous and not has_meaningful_baseline(previous.get('summary')):
        previous = None

    cs = summary_defaults(current.get('summary'))
    wb = current.get('waste_breakdown', {})

    # ========================================
    # CURRENT OPERATIONAL METRICS
    # ========================================
    print("=" * 70)
    print("YOUR CODING SESSIONS — FULL PICTURE")
    print("=" * 70)
    print()
    print(f"  Period:              {cs['date_range']}")
    print(f"  Sessions:            {cs['sessions']}")
    print()

    print("  OPERATIONAL METRICS")
    print("  " + "-" * 50)
    print(f"  Avg turns/session:   {cs['avg_turns_per_session']:.1f}")
    print(f"  Avg sub-agents:      {cs.get('avg_agent_spawns_per_session', 0):.1f} per session")
    print(f"  Avg context window:  {fmt_tokens(cs.get('avg_context_window_tokens', 0))} tokens/turn")
    print(f"  Avg AI output:       {fmt_tokens(cs.get('avg_output_tokens_per_turn', 0))} tokens/turn")
    print(f"  Wasteful turns:      {cs.get('wasteful_turns_pct', 0):.1f}%  ({cs.get('wasteful_turns_total', 0)} of {cs.get('total_turns', 0)})")
    print(f"  Context rot:         {cs.get('context_rot_sessions', 0)} sessions ({cs.get('context_rot_pct', 0):.0f}%)")
    print()

    print("  COST")
    print("  " + "-" * 50)
    print(f"  Total spend:         ${cs['total_cost']:.2f}")
    print(f"  Avg cost/session:    ${cs['avg_cost_per_session']:.2f}")
    print(f"  Avg cost/turn:       ${cs.get('avg_cost_per_turn', 0):.4f}")
    print(f"  Total waste:         ${cs['total_waste']:.2f}  ({cs['waste_percentage']:.0f}% of spend)")
    print()

    # Top waste patterns
    top5 = list(wb.items())[:5]
    if top5:
        print("  TOP WASTE PATTERNS")
        print("  " + "-" * 50)
        for k, v in top5:
            item = normalize_waste_item(v, cs['sessions'], cs['total_waste'])
            print(f"  {k:25s}  ${item['total_cost']:>7.2f}  ({item['percentage_of_waste']:.0f}%)")
        print()

    # Per-model breakdown
    model_mix = current.get('model_mix', {})
    if model_mix and len(model_mix) > 1:
        print("  MODELS USED")
        print("  " + "-" * 50)
        fmt = "  {:<18} {:>6} {:>9} {:>9}"
        print(fmt.format('Model', 'Sess', 'Total$', 'Avg$'))
        for model, info in model_mix.items():
            print(fmt.format(model, info['sessions'], f"${info['total_cost']:.2f}", f"${info['avg_cost']:.2f}"))
        print()

    # Per-project breakdown
    per_project = current.get('per_project', {})
    if per_project and len(per_project) > 1:
        print("  PROJECTS")
        print("  " + "-" * 50)
        fmt = "  {:<35} {:>4} {:>8} {:>6}"
        print(fmt.format('Project', 'Sess', 'Avg$', 'Waste'))
        for proj, info in per_project.items():
            print(fmt.format(proj[:35], info['sessions'], f"${info['avg_cost']:.2f}", f"{info['waste_pct']:.0f}%"))
        print()

    # ========================================
    # BEFORE / AFTER
    # ========================================
    if previous:
        ps = summary_defaults(previous.get('summary'))

        print("=" * 70)
        print("BEFORE / AFTER COMPARISON")
        print("=" * 70)
        print()

        # Header
        fmt_row = "  {:<28} {:>14} {:>14} {:>14}"
        print(fmt_row.format('', 'BEFORE', 'NOW', 'CHANGE'))
        print("  " + "-" * 66)

        def row(label, before, after, unit='$', lower_better=True):
            if unit == '$':
                b_str, a_str = f"${before:.2f}", f"${after:.2f}"
                d = after - before
                d_str = f"${d:+.2f}"
            elif unit == '%':
                b_str, a_str = f"{before:.1f}%", f"{after:.1f}%"
                d = after - before
                d_str = f"{d:+.1f}%"
            elif unit == 'K':
                b_str = fmt_tokens(int(before))
                a_str = fmt_tokens(int(after))
                d = after - before
                d_pct = (d / before * 100) if before > 0 else 0
                d_str = f"{d_pct:+.0f}%"
            elif unit == '#':
                b_str, a_str = f"{before:.1f}", f"{after:.1f}"
                d = after - before
                d_str = f"{d:+.1f}"
            else:
                b_str, a_str = str(before), str(after)
                d = after - before
                d_str = f"{d:+.1f}"

            good = (d < 0) if lower_better else (d > 0)
            flag = "" if abs(d) < 0.01 else (" ✅" if good else " ⚠️")
            print(fmt_row.format(label, b_str, a_str, d_str + flag))

        # Operational metrics
        print()
        print("  Operational:")
        row('Avg turns/session',
            ps.get('avg_turns_per_session', 0),
            cs.get('avg_turns_per_session', 0), '#')
        row('Avg sub-agents/session',
            ps.get('avg_agent_spawns_per_session', 0),
            cs.get('avg_agent_spawns_per_session', 0), '#')
        row('Avg context window',
            ps.get('avg_context_window_tokens', 0),
            cs.get('avg_context_window_tokens', 0), 'K')
        row('Avg output/turn',
            ps.get('avg_output_tokens_per_turn', 0),
            cs.get('avg_output_tokens_per_turn', 0), 'K', lower_better=False)
        row('Wasteful turns',
            ps.get('wasteful_turns_pct', 0),
            cs.get('wasteful_turns_pct', 0), '%')
        row('Context rot sessions',
            ps.get('context_rot_pct', 0),
            cs.get('context_rot_pct', 0), '%')

        # Cost metrics
        print()
        print("  Cost:")
        row('Avg cost/session',
            ps.get('avg_cost_per_session', 0),
            cs.get('avg_cost_per_session', 0))
        row('Avg cost/turn',
            ps.get('avg_cost_per_turn', 0),
            cs.get('avg_cost_per_turn', 0))
        row('Waste %',
            ps.get('waste_percentage', 0),
            cs.get('waste_percentage', 0), '%')
        row('Waste/session',
            ps.get('waste_per_session', 0),
            cs.get('waste_per_session', 0))

        # Per-pattern comparison
        print()
        print("  Per-pattern:")
        pwb = previous.get('waste_breakdown', {})
        cwb = current.get('waste_breakdown', {})
        all_patterns = sorted(
            set(list(pwb.keys()) + list(cwb.keys())),
            key=lambda p: -(pwb.get(p, {}).get('per_session', 0))
        )
        for pattern in all_patterns:
            b_cost = pwb.get(pattern, {}).get('per_session', 0)
            a_cost = cwb.get(pattern, {}).get('per_session', 0)
            if b_cost > 0.001 or a_cost > 0.001:
                d = a_cost - b_cost
                flag = "✅" if d < -0.001 else ("⚠️" if d > 0.001 else "—")
                print(f"    {pattern:25s}  ${b_cost:.3f} → ${a_cost:.3f}  ({flag})")
        print()

        # Bottom line
        actual_savings = ps['avg_cost_per_session'] - cs['avg_cost_per_session']
        daily_sessions = cs['sessions'] / cs['period_days'] if cs['period_days'] > 0 else 0
        print("=" * 70)
        if actual_savings > 0.01:
            pct = actual_savings / ps['avg_cost_per_session'] * 100
            monthly = actual_savings * daily_sessions * 30
            print(f"  You're saving ${actual_savings:.2f}/session ({pct:.0f}%) vs before!")
            print(f"  At {daily_sessions:.1f} sessions/day, that's ~${monthly:.0f}/month in real savings.")
            print()
            # Show efficiency gains
            turns_before = ps['avg_turns_per_session']
            turns_now = cs['avg_turns_per_session']
            if turns_now < turns_before:
                print(f"  Efficiency: same work in {turns_now:.0f} turns (was {turns_before:.0f})")
            waste_before = ps.get('wasteful_turns_pct', 0)
            waste_now = cs.get('wasteful_turns_pct', 0)
            if waste_now < waste_before:
                print(f"  Clean turns: {100 - waste_now:.0f}% productive (was {100 - waste_before:.0f}%)")
        elif actual_savings < -0.01:
            print(f"  Costs increased by ${-actual_savings:.2f}/session. Check patterns above for ⚠️.")
        else:
            print(f"  No significant change yet. Run again in 1-2 weeks after the fixes take effect.")
        print("=" * 70)

    else:
        # ========================================
        # PROJECTIONS (no previous baseline)
        # ========================================
        print("=" * 70)
        print("PROJECTED — AFTER APPLYING FIXES")
        print("=" * 70)
        print()

        projected_cost = cs['projected_cost_after_fix']
        savings_per_session = cs['avg_cost_per_session'] - projected_cost
        daily_sessions = cs['sessions'] / cs['period_days'] if cs['period_days'] > 0 else 0
        monthly_current = cs['avg_cost_per_session'] * daily_sessions * 30
        monthly_after = projected_cost * daily_sessions * 30
        monthly_savings = monthly_current - monthly_after

        # Projected operational metrics
        waste_pct = cs['waste_percentage'] / 100
        projected_turns = cs['avg_turns_per_session'] * (1 - waste_pct * 0.6)  # ~60% of waste turns eliminated
        projected_wasteful = cs.get('wasteful_turns_pct', 0) * 0.2  # target: 80% reduction
        projected_context = cs.get('avg_context_window_tokens', 0) * (1 - waste_pct * 0.4)  # fewer turns = smaller window
        context_base = cs.get('avg_context_window_tokens', 0)
        if context_base > 0:
            context_change = f"{-(1 - projected_context / context_base) * 100:.0f}%"
        else:
            context_change = "0%"

        fmt_row = "  {:<28} {:>14} {:>14} {:>14}"
        print(fmt_row.format('', 'NOW', 'PROJECTED', 'SAVINGS'))
        print("  " + "-" * 66)

        print()
        print("  Operational:")
        print(fmt_row.format('Avg turns/session',
              f"{cs['avg_turns_per_session']:.1f}",
              f"{projected_turns:.1f}",
              f"{cs['avg_turns_per_session'] - projected_turns:+.1f}"))
        print(fmt_row.format('Avg context window',
              fmt_tokens(cs.get('avg_context_window_tokens', 0)),
              fmt_tokens(int(projected_context)),
              context_change))
        print(fmt_row.format('Wasteful turns',
              f"{cs.get('wasteful_turns_pct', 0):.1f}%",
              f"{projected_wasteful:.1f}%",
              f"{projected_wasteful - cs.get('wasteful_turns_pct', 0):+.1f}%"))

        print()
        print("  Cost:")
        print(fmt_row.format('Avg cost/session',
              f"${cs['avg_cost_per_session']:.2f}",
              f"${projected_cost:.2f}",
              f"${savings_per_session:.2f} ({cs['waste_percentage']:.0f}%)"))
        print(fmt_row.format('Monthly spend',
              f"${monthly_current:.0f}",
              f"${monthly_after:.0f}",
              f"${monthly_savings:.0f}"))
        print()

        print(f"  Your pace: {daily_sessions:.1f} sessions/day")
        print()
        print("=" * 70)
        print(f"  Potential: ${savings_per_session:.2f}/session → ~${monthly_savings:.0f}/month")
        print()
        print(f"  Run again in 1-2 weeks to see ACTUAL results.")
        print(f"  The optimizer auto-compares against today's baseline.")
        print("=" * 70)

    print()

    # Save persistent snapshot
    snapshot_path = save_snapshot(current)
    if snapshot_path:
        print(f"  Snapshot saved: {snapshot_path}")
    else:
        print("  Snapshot saved: unavailable in this environment")

    # Also list history
    if snapshot_path and SNAPSHOT_DIR.exists():
        all_snaps = sorted(SNAPSHOT_DIR.glob('snapshot_*.json'))
        if len(all_snaps) > 1:
            print(f"  History: {len(all_snaps)} snapshots in {SNAPSHOT_DIR}")

if __name__ == "__main__":
    main()
