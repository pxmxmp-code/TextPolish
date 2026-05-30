---
name: textpolish
description: "Skill for the Textpolish area of TextPolish. 33 symbols across 5 files."
---

# Textpolish

33 symbols | 5 files | Cohesion: 80%

## When to Use

- Working with code in `src/`
- Understanding how main, update_style, update_patterns work
- Modifying textpolish-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/textpolish/config.py` | update_style, update_patterns, add_pattern, remove_pattern, toggle_pattern (+11) |
| `src/textpolish/core/html_generator.py` | convert_to_html, _process_line, _is_title_level, _process_special_format, _generate_special_format_html (+4) |
| `src/textpolish/app.py` | create_application, create_main_window, run, main |
| `src/textpolish/ui/config_interface.py` | import_config, refresh_all_configs, export_config |
| `src/textpolish/utils/icon.py` | set_app_icon |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `src/textpolish/app.py:76`
- **`update_style`** (Method) — `src/textpolish/config.py:288`
- **`update_patterns`** (Method) — `src/textpolish/config.py:294`
- **`add_pattern`** (Method) — `src/textpolish/config.py:309`
- **`remove_pattern`** (Method) — `src/textpolish/config.py:315`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `main` | Function | `src/textpolish/app.py` | 76 |
| `update_style` | Method | `src/textpolish/config.py` | 288 |
| `update_patterns` | Method | `src/textpolish/config.py` | 294 |
| `add_pattern` | Method | `src/textpolish/config.py` | 309 |
| `remove_pattern` | Method | `src/textpolish/config.py` | 315 |
| `toggle_pattern` | Method | `src/textpolish/config.py` | 321 |
| `save_config` | Method | `src/textpolish/config.py` | 328 |
| `get_enabled_patterns` | Method | `src/textpolish/config.py` | 390 |
| `convert_to_html` | Method | `src/textpolish/core/html_generator.py` | 18 |
| `create_application` | Method | `src/textpolish/app.py` | 16 |
| `create_main_window` | Method | `src/textpolish/app.py` | 43 |
| `run` | Method | `src/textpolish/app.py` | 53 |
| `set_app_icon` | Method | `src/textpolish/utils/icon.py` | 55 |
| `load_config` | Method | `src/textpolish/config.py` | 354 |
| `reset_to_default` | Method | `src/textpolish/config.py` | 385 |
| `load_from_app_config` | Method | `src/textpolish/config.py` | 504 |
| `get_style_dict` | Method | `src/textpolish/config.py` | 397 |
| `import_config_from_file` | Method | `src/textpolish/config.py` | 460 |
| `initialize_from_project_config` | Method | `src/textpolish/config.py` | 486 |
| `import_config` | Method | `src/textpolish/ui/config_interface.py` | 1109 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `__init__ → Save_config` | cross_community | 8 |
| `Add_rule → Save_config` | cross_community | 6 |
| `Main → Get_icon_path` | cross_community | 6 |
| `On_rule_changed → Save_config` | cross_community | 4 |
| `__init__ → Load_from_app_config` | intra_community | 4 |
| `Convert_to_html → Get_enabled_patterns` | intra_community | 4 |
| `Convert_to_html → Get_style_dict` | cross_community | 4 |
| `Convert_to_html → _wrap_numbers_with_western_font` | cross_community | 4 |
| `Reset_to_default → Load_from_app_config` | intra_community | 3 |
| `Import_config → Save_config` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Ui | 1 calls |

## How to Explore

1. `gitnexus_context({name: "main"})` — see callers and callees
2. `gitnexus_query({query: "textpolish"})` — find related execution flows
3. Read key files listed above for implementation details
