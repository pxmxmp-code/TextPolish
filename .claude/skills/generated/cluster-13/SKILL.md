---
name: cluster-13
description: "Skill for the Cluster_13 area of TextPolish. 6 symbols across 1 files."
---

# Cluster_13

6 symbols | 1 files | Cohesion: 100%

## When to Use

- Working with code in `src/`
- Understanding how clean_text work
- Modifying cluster_13-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/textpolish/core/text_processor.py` | clean_text, _remove_special_symbols, _replace_punctuation, _process_quotes, _clean_whitespace (+1) |

## Entry Points

Start here when exploring this area:

- **`clean_text`** (Method) — `src/textpolish/core/text_processor.py:18`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `clean_text` | Method | `src/textpolish/core/text_processor.py` | 18 |
| `_remove_special_symbols` | Method | `src/textpolish/core/text_processor.py` | 48 |
| `_replace_punctuation` | Method | `src/textpolish/core/text_processor.py` | 59 |
| `_process_quotes` | Method | `src/textpolish/core/text_processor.py` | 75 |
| `_clean_whitespace` | Method | `src/textpolish/core/text_processor.py` | 83 |
| `_clean_paragraphs` | Method | `src/textpolish/core/text_processor.py` | 95 |

## How to Explore

1. `gitnexus_context({name: "clean_text"})` — see callers and callees
2. `gitnexus_query({query: "cluster_13"})` — find related execution flows
3. Read key files listed above for implementation details
