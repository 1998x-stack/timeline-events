#!/usr/bin/env python3
"""Compatibility adapter. Source of truth: skills/timeline-events/scripts/render_html.py."""
from pathlib import Path
import importlib.util
import sys

TARGET = Path(__file__).resolve().parents[1] / 'skills' / 'timeline-events' / 'scripts' / 'render_html.py'
SPEC = importlib.util.spec_from_file_location('timeline_skill_render_html', TARGET)
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)
for key in dir(engine):
    if not key.startswith('__'):
        globals()[key] = getattr(engine, key)

if __name__ == '__main__':
    raise SystemExit(engine.main())
