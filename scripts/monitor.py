#!/usr/bin/env python3
"""Weekly cost monitor — compares current week vs previous week, flags regression."""
import json, sys, os
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from pathlib import Path

def load_sessions(analysis_path):
    with open(analysis_path) as f:
        return json.load(f)

def split_by_week(sessions):
    """Split sessions into current week (last 7 days) and previous week (7-14 days ago)."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    current = []
    previous = []
    for s in sessions:
        try:
            dt = datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00'))
        except (ValueError, KeyError):
            continue
        if dt >= week_ago:
            current.append(s)
        else:
            previous.append(s)
    return current, previous

def week_stats(sessions):
    if not sessions:
        return None
    n = len(sessions)
    total_cost = sum(s['total_cost'] for s in sessions)
    total_turns = sum(s['total_turns'] for s in sessions)
    total_waste = sum(sum(w['cost'] for w in s['waste'].values()) for s in sessions)
    return {
        'sessions': n,
        'total_cost': round(total_cost, 2),
        'avg_cost': round(total_cost / n, 2),
        'avg_turns': round(total_turns / n, 1),
        'total_waste': round(total_waste, 2),
        'waste_pct': round(total_waste / total_cost * 100, 1) if total_cost > 0 else 0,
        'idle_per_session': round(sum(s['waste']['idle_narration']['turns'] for s in sessions) / n, 1),
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: monitor.py <analysis.json>")
        sys.exit(1)

    data = load_sessions(sys.argv[1])
    sessions = data.get('sessions', [])

    current, previous = split_by_week(sessions)
    cs = week_stats(current)
    ps = week_stats(previous)

    print("=" * 60)
    print("WEEKLY COST MONITOR")
    print("=" * 60)
    print()

    if not cs:
        print("  No sessions in the current week.")
        sys.exit(0)

    fmt = "{:<25} {:>12} {:>12} {:>10}"
    print(fmt.format('', 'This week', 'Last week', 'Delta'))
    print("-" * 60)

    if ps:
        def row(label, cv, pv, unit='$', lower_better=True):
            if unit == '$':
                cs_str = f"${cv:.2f}"
                ps_str = f"${pv:.2f}"
            elif unit == '%':
                cs_str = f"{cv:.1f}%"
                ps_str = f"{pv:.1f}%"
            else:
                cs_str = f"{cv:.1f}"
                ps_str = f"{pv:.1f}"
            delta = cv - pv
            if unit == '$':
                d_str = f"${delta:+.2f}"
            elif unit == '%':
                d_str = f"{delta:+.1f}%"
            else:
                d_str = f"{delta:+.1f}"

            good = (delta < 0) if lower_better else (delta > 0)
            flag = "" if abs(delta) < 0.01 else (" \u2705" if good else " \u26a0\ufe0f")
            print(fmt.format(label, cs_str, ps_str, d_str + flag))

        row('Sessions', cs['sessions'], ps['sessions'], '#', False)
        row('Avg cost/session', cs['avg_cost'], ps['avg_cost'])
        row('Avg turns/session', cs['avg_turns'], ps['avg_turns'], '#')
        row('Waste %', cs['waste_pct'], ps['waste_pct'], '%')
        row('Idle turns/session', cs['idle_per_session'], ps['idle_per_session'], '#')
        row('Total spend', cs['total_cost'], ps['total_cost'])
    else:
        print(f"  Sessions:        {cs['sessions']}")
        print(f"  Avg cost:        ${cs['avg_cost']:.2f}")
        print(f"  Waste:           {cs['waste_pct']:.1f}%")
        print(f"  (No previous week data for comparison)")

    print()

    # Alerts
    alerts = []
    if ps:
        if cs['waste_pct'] > ps['waste_pct'] + 5:
            alerts.append(f"Waste increased from {ps['waste_pct']:.0f}% to {cs['waste_pct']:.0f}% — review your instruction-file rules")
        if cs['avg_cost'] > ps['avg_cost'] * 1.3:
            alerts.append(f"Avg session cost up {((cs['avg_cost']/ps['avg_cost'])-1)*100:.0f}% — check for scope creep")
        if cs['idle_per_session'] > ps['idle_per_session'] + 3:
            alerts.append(f"Idle turns up from {ps['idle_per_session']:.0f} to {cs['idle_per_session']:.0f} — narration rules may not be sticking")

    if alerts:
        print("ALERTS:")
        for a in alerts:
            print(f"  \u26a0\ufe0f  {a}")
    else:
        print("No regression detected. Costs are stable or improving.")
    print()

    # Output JSON for programmatic use
    result = {
        'current_week': cs,
        'previous_week': ps,
        'alerts': alerts,
        'regression': len(alerts) > 0,
    }
    # Write to file for scheduled task consumption
    out_path = '/tmp/vibecheck_monitor_result.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
