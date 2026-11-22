#!/usr/bin/env python3
"""Legacy CI entrypoint for full Skill package verification."""
from sync_skill import main
if __name__ == '__main__':
    raise SystemExit(main(['--check']))
