#!/usr/bin/env python3
"""GDPR breach clock: the Art. 33 72-hour deadline and the POL-05 milestones.

Live use, from the moment of awareness:
    py tools\\breach_clock.py --aware 2026-11-17T18:40:00Z
Check a documented incident (event times in TIMELINES below):
    py tools\\breach_clock.py --inc INC-01

Milestones (POL-05):
    awareness + 1 h   Managing Director informed (SEV-1)
    awareness + 24 h  breach risk assessment done (statement 5)
    awareness + 72 h  notification to the BlnBDI (Art. 33(1) GDPR)
Exit code 1 if a documented milestone was missed or the 72 h deadline has passed
without a notification. Standard library only.
"""
import argparse
import sys
from datetime import datetime, timedelta, timezone

# Event times (UTC) of documented incidents, taken from the evidence:
#   attack-start  evidence/phase4/attack/attack-log.json (first request)
#   detection     evidence/phase4/detection/alerts.json (detection_run_utc)
#   all others    evidence/phase4/response/exercise-log.txt
TIMELINES = {
    "INC-01": [
        ("attack-start", "2026-11-17T17:37:37Z"),
        ("detection", "2026-11-17T17:37:55Z"),
        ("awareness", "2026-11-17T17:39:18Z"),
        ("md-informed", "2026-11-17T17:39:19Z"),
        ("risk-assessed", "2026-11-17T17:40:13Z"),
        ("notification-decision", "2026-11-17T17:40:13Z"),
        ("authority-notified", "2026-11-17T17:40:13Z"),
    ],
}
MILESTONES = [
    ("md-informed", timedelta(hours=1), "Managing Director informed (POL-05, SEV-1)"),
    ("risk-assessed", timedelta(hours=24), "Breach risk assessment done (POL-05 statement 5)"),
    ("authority-notified", timedelta(hours=72), "BlnBDI notified (Art. 33(1) GDPR)"),
]


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


def fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def hours(td):
    return f"{td.total_seconds() / 3600:+.1f} h"


def load_timeline(inc):
    if inc not in TIMELINES:
        raise SystemExit(f"No timeline for {inc}; known incidents: {', '.join(TIMELINES)}")
    return [{"event_type": kind, "time_utc": ts} for kind, ts in TIMELINES[inc]]


def first(events, kind):
    times = [parse(e["time_utc"]) for e in events if e["event_type"] == kind]
    return min(times) if times else None


def report(aware, events=None, now=None):
    now = now or datetime.now(timezone.utc)
    deadline = aware + timedelta(hours=72)
    print(f"Awareness:          {fmt(aware)}")
    print(f"Art. 33 deadline:   {fmt(deadline)}")
    late = False
    print("\n| Milestone | Due | Done | Margin | Status |")
    print("|---|---|---|---|---|")
    for kind, offset, label in MILESTONES:
        due = aware + offset
        done = first(events, kind) if events is not None else None
        if done:
            status = "met" if done <= due else "MISSED"
            late |= done > due
            print(f"| {label} | {fmt(due)} | {fmt(done)} | {hours(due - done)} | {status} |")
        else:
            status = "open" if now <= due else "OVERDUE"
            late |= now > due and kind == "authority-notified"
            print(f"| {label} | {fmt(due)} | - | {hours(due - now)} left | {status} |")
    if events is not None:
        start, detect = first(events, "attack-start"), first(events, "detection")
        decision = first(events, "notification-decision")
        print()
        if start and detect:
            print(f"KPI-06 time to detect:          {(detect - start).total_seconds() / 3600:.2f} h")
        if decision:
            print(f"KPI-05 awareness to decision:   {(decision - aware).total_seconds() / 3600:.2f} h "
                  f"(target <= 72 h: {'met' if decision - aware <= timedelta(hours=72) else 'MISSED'})")
        if detect and detect > aware:
            print("WARNING: awareness is recorded before detection; check the timeline")
    return 1 if late else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--aware", help="awareness time, ISO 8601 (for example 2026-11-17T18:40:00Z)")
    g.add_argument("--inc", help="incident ID with a timeline in TIMELINES, for example INC-01")
    ap.add_argument("--now", help="evaluate at this time instead of the current time (ISO 8601)")
    args = ap.parse_args()
    now = parse(args.now) if args.now else None
    if args.aware:
        return report(parse(args.aware), None, now)
    events = load_timeline(args.inc)
    aware = first(events, "awareness")
    if not aware:
        raise SystemExit(f"{args.inc}: the timeline has no 'awareness' event")
    print(f"Incident {args.inc}")
    return report(aware, events, now)


if __name__ == "__main__":
    sys.exit(main())
