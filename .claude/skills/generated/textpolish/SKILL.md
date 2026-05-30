---
name: textpolish
description: "Skill for the Textpolish area of TextPolish. 40 symbols across 5 files."
---

# Textpolish

40 symbols | 5 files | Cohesion: 83%

## When to Use

- Working with code in `src/`
- Understanding how main, load_config, import_config_from_file work
- Modifying textpolish-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/textpolish/config.py` | __init__, _default_recognition_rules, _coerce_recognition_rule, _load_recognition_rules_data, _migrate_legacy_patterns_to_rules (+18) |
| `src/textpolish/core/html_generator.py` | convert_to_html, _process_line, _is_title_level, _process_special_format, _wrap_numbers_with_western_font (+4) |
| `src/textpolish/app.py` | create_application, create_main_window, run, main |
| `src/textpolish/ui/config_interface.py` | import_config, refresh_all_configs, export_config |
| `src/textpolish/utils/icon.py` | set_app_icon |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `src/textpolish/app.py:76`
- **`load_config`** (Method) — `src/textpolish/config.py:525`
- **`import_config_from_file`** (Method) — `src/textpolish/config.py:712`
- **`initialize_from_project_config`** (Method) — `src/textpolish/config.py:744`
- **`load_from_app_config`** (Method) — `src/textpolish/config.py:762`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `main` | Function | `src/textpolish/app.py` | 76 |
| `load_config` | Method | `src/textpolish/config.py` | 525 |
| `import_config_from_file` | Method | `src/textpolish/config.py` | 712 |
| `initialize_from_project_config` | Method | `src/textpolish/config.py` | 744 |
| `load_from_app_config` | Method | `src/textpolish/config.py` | 762 |
| `import_config` | Method | `src/textpolish/ui/config_interface.py` | 1932 |
| `refresh_all_configs` | Method | `src/textpolish/ui/config_interface.py` | 1979 |
| `update_style` | Method | `src/textpolish/config.py` | 464 |
| `update_patterns` | Method | `src/textpolish/config.py` | 470 |
| `add_pattern` | Method | `src/textpolish/config.py` | 485 |
| `remove_pattern` | Method | `src/textpolish/config.py` | 491 |
| `toggle_pattern` | Method | `src/textpolish/config.py` | 497 |
| `save_config` | Method | `src/textpolish/config.py` | 504 |
| `reset_to_default` | Method | `src/textpolish/config.py` | 564 |
| `export_config_to_file` | Method | `src/textpolish/config.py` | 699 |
| `export_config` | Method | `src/textpolish/ui/config_interface.py` | 1897 |
| `get_enabled_patterns` | Method | `src/textpolish/config.py` | 569 |
| `classify_line` | Method | `src/textpolish/config.py` | 627 |
| `convert_to_html` | Method | `src/textpolish/core/html_generator.py` | 21 |
| `get_style_dict` | Method | `src/textpolish/config.py` | 654 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Load_config → _serialize_config` | cross_community | 6 |
| `Load_config → _match_recognition_rule` | cross_community | 6 |
| `Main → Get_icon_path` | cross_community | 6 |
| `Reset_to_default → _default_recognition_rules` | cross_community | 5 |
| `Reset_to_default → _coerce_recognition_rule` | cross_community | 5 |
| `__init__ → _default_recognition_rules` | intra_community | 5 |
| `__init__ → _coerce_recognition_rule` | intra_community | 5 |
| `Import_config → _default_recognition_rules` | intra_community | 4 |
| `Import_config → _coerce_recognition_rule` | intra_community | 4 |
| `Import_config → _serialize_config` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Ui | 1 calls |

## How to Explore

1. `gitnexus_context({name: "main"})` — see callers and callees
2. `gitnexus_query({query: "textpolish"})` — find related execution flows
3. Read key files listed above for implementation details
