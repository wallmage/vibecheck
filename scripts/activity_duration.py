#!/usr/bin/env python3
"""Helpers for estimating active session duration from event timestamps."""

from datetime import datetime


ACTIVE_GAP_CAP_MINUTES = 5.0


def parse_iso_timestamp(value):
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def estimate_active_duration_minutes(timestamps, gap_cap_minutes=ACTIVE_GAP_CAP_MINUTES):
    points = [point for point in timestamps if point is not None]
    if len(points) < 2:
        return None

    points = sorted(points)
    total_minutes = 0.0
    for left, right in zip(points, points[1:]):
        gap_minutes = (right - left).total_seconds() / 60.0
        if gap_minutes <= 0:
            continue
        total_minutes += min(gap_minutes, gap_cap_minutes)

    return round(total_minutes, 1) if total_minutes > 0 else None
