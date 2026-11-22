#!/usr/bin/env python3
"""Prevent drift between the Pi and Agent Skill entrypoints."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
pi = root / ".pi/skills/timeline-events/SKILL.md"
agent = root / ".agent/skills/timeline-events/SKILL.md"
missing = [str(p) for p in (pi, agent, root / "scripts/timeline_events.py", root / "README.md") if not p.is_file()]
if missing:
    sys.exit("Missing files: " + ", ".join(missing))
a, b = pi.read_bytes(), agent.read_bytes()
if a != b:
    sys.exit("Skill copies differ: update both .pi and .agent versions")
if not a.startswith(b"---\n"):
    sys.exit("SKILL.md frontmatter is missing")
print("OK: Pi and Agent skills match byte-for-byte")
