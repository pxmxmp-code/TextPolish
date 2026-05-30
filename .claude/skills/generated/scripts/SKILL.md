---
name: scripts
description: "Skill for the Scripts area of TextPolish. 8 symbols across 2 files."
---

# Scripts

8 symbols | 2 files | Cohesion: 100%

## When to Use

- Working with code in `scripts/`
- Understanding how get_current_version, update_version, run_command work
- Modifying scripts-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/release.py` | get_current_version, update_version, run_command, check_git_status, get_latest_tag (+1) |
| `scripts/test-build.py` | run_command, main |

## Entry Points

Start here when exploring this area:

- **`get_current_version`** (Function) — `scripts/release.py:12`
- **`update_version`** (Function) — `scripts/release.py:31`
- **`run_command`** (Function) — `scripts/release.py:51`
- **`check_git_status`** (Function) — `scripts/release.py:74`
- **`get_latest_tag`** (Function) — `scripts/release.py:97`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `get_current_version` | Function | `scripts/release.py` | 12 |
| `update_version` | Function | `scripts/release.py` | 31 |
| `run_command` | Function | `scripts/release.py` | 51 |
| `check_git_status` | Function | `scripts/release.py` | 74 |
| `get_latest_tag` | Function | `scripts/release.py` | 97 |
| `main` | Function | `scripts/release.py` | 112 |
| `run_command` | Function | `scripts/test-build.py` | 13 |
| `main` | Function | `scripts/test-build.py` | 33 |

## How to Explore

1. `gitnexus_context({name: "get_current_version"})` — see callers and callees
2. `gitnexus_query({query: "scripts"})` — find related execution flows
3. Read key files listed above for implementation details
