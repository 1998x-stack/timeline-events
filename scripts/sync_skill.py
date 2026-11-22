#!/usr/bin/env python3
"""Build/check portable, complete skill mirrors for Pi and Agent clients."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / 'skills' / 'timeline-events'
TARGETS = [ROOT / '.pi/skills/timeline-events', ROOT / '.agent/skills/timeline-events']
EXCLUDES = {'__pycache__', '.DS_Store', '.pytest_cache'}

def inventory(directory: Path) -> dict[str, bytes]:
    result = {}
    for file in sorted(directory.rglob('*')):
        if not file.is_file() or any(x in EXCLUDES for x in file.relative_to(directory).parts):
            continue
        result[file.relative_to(directory).as_posix()] = file.read_bytes()
    return result

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Sync canonical skill to Pi/Agent installable mirrors')
    parser.add_argument('--check', action='store_true', help='Fail if any mirror differs, without changing files')
    args = parser.parse_args(argv)
    if not (CANONICAL / 'SKILL.md').is_file():
        print('Missing canonical SKILL.md', file=sys.stderr)
        return 2
    expected = inventory(CANONICAL)
    for target in TARGETS:
        if args.check:
            current = inventory(target) if target.exists() else {}
            if current != expected:
                missing = sorted(set(expected) - set(current))
                extra = sorted(set(current) - set(expected))
                modified = sorted(p for p in set(expected) & set(current) if expected[p] != current[p])
                print(f'DRIFT {target}: missing={missing}, extra={extra}, modified={modified}', file=sys.stderr)
                return 2
        else:
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(CANONICAL, target, ignore=shutil.ignore_patterns(*EXCLUDES))
    print(f'OK: {len(expected)} files, mirrors: {len(TARGETS)}; mode: {"check" if args.check else "sync"}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
