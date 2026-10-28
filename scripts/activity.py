#!/usr/bin/env python3
"""Write src/activity.json: per-day activity counts for the two grids on the home page.

  github  contributions per day, from the GitHub GraphQL API through the `gh` CLI
          (uses whatever account `gh` is logged in as; no token is stored here)
  claude  prompts typed per day in Claude Code, from ~/.claude/history.jsonl

Only a date and a count per day are written. No prompts, paths, or project names.
Run: python3 scripts/activity.py [other-history.jsonl ...]

Pass another machine's history.jsonl to save its per-day counts to OTHER_MACHINES
(replacing what was saved before). Later runs add those counts without the file.
"""
import collections
import datetime
import json
import pathlib
import subprocess
import sys

OUT = pathlib.Path(__file__).resolve().parent.parent / "src" / "activity.json"
HISTORY = pathlib.Path.home() / ".claude" / "history.jsonl"
OTHER_MACHINES = pathlib.Path(__file__).resolve().parent / "claude-other-machines.json"
# Both grids start here.
START = "2026-01-01"
QUERY = "{viewer{contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"


def with_levels(days):
    """Add a 0-4 level to each day, splitting the non-zero counts into quartiles."""
    counts = sorted(d["count"] for d in days if d["count"] > 0)
    cuts = [counts[len(counts) * q // 4] for q in (1, 2, 3)] if counts else []
    for d in days:
        d["level"] = 0 if d["count"] == 0 else 1 + sum(d["count"] >= c for c in cuts)
    return days


def github():
    raw = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"], capture_output=True, text=True, check=True)
    weeks = json.loads(raw.stdout)["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
    return with_levels([d for d in days if d["date"] >= START])


def prompts_per_day(path):
    # history.jsonl has one line per prompt typed. The stats cache is not used: it is
    # built from transcripts, which expire, so it has holes wherever it went unrefreshed.
    by_day = collections.Counter()
    for line in pathlib.Path(path).open(errors="ignore"):
        try:
            stamp = json.loads(line).get("timestamp")
        except json.JSONDecodeError:
            continue
        if isinstance(stamp, (int, float)):
            by_day[datetime.datetime.fromtimestamp(stamp / 1000).date().isoformat()] += 1
    return by_day


def claude(start, end):
    if sys.argv[1:]:
        other = sum((prompts_per_day(p) for p in sys.argv[1:]), collections.Counter())
        OTHER_MACHINES.write_text(json.dumps(dict(sorted(other.items())), indent=0) + "\n")
    by_day = prompts_per_day(HISTORY)
    if OTHER_MACHINES.exists():
        by_day.update(json.loads(OTHER_MACHINES.read_text()))
    first, last = min(by_day), max(by_day)
    # Pad both ends so this grid covers the same dates as the GitHub one.
    by_day.setdefault(start, 0)
    by_day.setdefault(end, 0)
    days = [{"date": k, "count": v} for k, v in sorted(by_day.items()) if start <= k <= end]
    return with_levels(days), max(first, start), last


gh_days = github()
claude_days, claude_since, claude_as_of = claude(gh_days[0]["date"], gh_days[-1]["date"])
OUT.write_text(
    json.dumps(
        {
            "since": START,
            "asOf": datetime.date.today().isoformat(),
            "claudeSince": claude_since,
            "claudeAsOf": claude_as_of,
            "github": gh_days,
            "claude": claude_days,
        }
    )
    + "\n"
)
print(f"wrote {OUT}: {len(gh_days)} GitHub days, {len(claude_days)} Claude Code days")
