---
name: cluster-10
description: "Skill for the Cluster_10 area of TextPolish. 6 symbols across 1 files."
---

# Cluster_10

6 symbols | 1 files | Cohesion: 100%

## When to Use

- Working with code in `src/`
- Understanding how repl, generate_wps_html work
- Modifying cluster_10-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/textpolish/core/html_generator.py` | _western_font_declaration, _western_font_declarations, _western_span_style, repl, _normalize_wps_western_font (+1) |

## Entry Points

Start here when exploring this area:

- **`repl`** (Function) — `src/textpolish/core/html_generator.py:75`
- **`generate_wps_html`** (Method) — `src/textpolish/core/html_generator.py:420`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `repl` | Function | `src/textpolish/core/html_generator.py` | 75 |
| `generate_wps_html` | Method | `src/textpolish/core/html_generator.py` | 420 |
| `_western_font_declaration` | Method | `src/textpolish/core/html_generator.py` | 54 |
| `_western_font_declarations` | Method | `src/textpolish/core/html_generator.py` | 58 |
| `_western_span_style` | Method | `src/textpolish/core/html_generator.py` | 65 |
| `_normalize_wps_western_font` | Method | `src/textpolish/core/html_generator.py` | 412 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Repl → _western_font_declaration` | intra_community | 4 |
| `Generate_wps_html → _western_font_declaration` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "repl"})` — see callers and callees
2. `gitnexus_query({query: "cluster_10"})` — find related execution flows
3. Read key files listed above for implementation details
