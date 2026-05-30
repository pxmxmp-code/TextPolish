---
name: ui
description: "Skill for the Ui area of TextPolish. 87 symbols across 5 files."
---

# Ui

87 symbols | 5 files | Cohesion: 90%

## When to Use

- Working with code in `src/`
- Understanding how create_rule_widget, update_remove_button_style, apply_rule_widget_style work
- Modifying ui-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/textpolish/ui/config_interface.py` | _combo_text, _mapped_combo_value, _update_rule_count_label, _literal_from_exact_pattern, _detect_rule_template (+61) |
| `src/textpolish/config.py` | update_recognition_rules, load_ui_settings, get_config_file_path, get_config, update_level_config (+2) |
| `src/textpolish/ui/main_interface.py` | __init__, initUI, update_splitter_style, create_input_card, create_output_card (+1) |
| `src/textpolish/ui/main_window.py` | __init__, initWindow, center_window, initThemeListener, add_config_interface |
| `src/textpolish/utils/icon.py` | get_icon_path, load_icon, set_window_icon |

## Entry Points

Start here when exploring this area:

- **`create_rule_widget`** (Method) — `src/textpolish/ui/config_interface.py:451`
- **`update_remove_button_style`** (Method) — `src/textpolish/ui/config_interface.py:546`
- **`apply_rule_widget_style`** (Method) — `src/textpolish/ui/config_interface.py:589`
- **`load_rules`** (Method) — `src/textpolish/ui/config_interface.py:729`
- **`clear_rules`** (Method) — `src/textpolish/ui/config_interface.py:742`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `create_rule_widget` | Method | `src/textpolish/ui/config_interface.py` | 451 |
| `update_remove_button_style` | Method | `src/textpolish/ui/config_interface.py` | 546 |
| `apply_rule_widget_style` | Method | `src/textpolish/ui/config_interface.py` | 589 |
| `load_rules` | Method | `src/textpolish/ui/config_interface.py` | 729 |
| `clear_rules` | Method | `src/textpolish/ui/config_interface.py` | 742 |
| `add_rule` | Method | `src/textpolish/ui/config_interface.py` | 748 |
| `remove_rule` | Method | `src/textpolish/ui/config_interface.py` | 763 |
| `on_rule_changed` | Method | `src/textpolish/ui/config_interface.py` | 777 |
| `save_config_silent` | Method | `src/textpolish/ui/config_interface.py` | 791 |
| `update_recognition_rules` | Method | `src/textpolish/config.py` | 583 |
| `setup_ui` | Method | `src/textpolish/ui/config_interface.py` | 839 |
| `load_config` | Method | `src/textpolish/ui/config_interface.py` | 939 |
| `create_rule_widget` | Method | `src/textpolish/ui/config_interface.py` | 953 |
| `save_config_silent` | Method | `src/textpolish/ui/config_interface.py` | 1019 |
| `refresh_test_results` | Method | `src/textpolish/ui/config_interface.py` | 1052 |
| `apply_card_style` | Method | `src/textpolish/ui/config_interface.py` | 1084 |
| `load_ui_settings` | Method | `src/textpolish/config.py` | 671 |
| `get_config_file_path` | Method | `src/textpolish/config.py` | 695 |
| `setup_ui` | Method | `src/textpolish/ui/config_interface.py` | 1381 |
| `apply_panel_style` | Method | `src/textpolish/ui/config_interface.py` | 1447 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Add_rule → _template_options` | cross_community | 6 |
| `Load_config → _serialize_config` | cross_community | 6 |
| `Load_config → _match_recognition_rule` | cross_community | 6 |
| `Main → Get_icon_path` | cross_community | 6 |
| `Load_config → _clear_layout` | intra_community | 5 |
| `Load_rules → _literal_from_exact_pattern` | intra_community | 4 |
| `Add_rule → _literal_from_exact_pattern` | intra_community | 4 |
| `Add_rule → _set_rule_pattern_text` | cross_community | 4 |
| `Load_config → _target_value` | intra_community | 4 |
| `InitWindow → Get_icon_path` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Textpolish | 3 calls |

## How to Explore

1. `gitnexus_context({name: "create_rule_widget"})` — see callers and callees
2. `gitnexus_query({query: "ui"})` — find related execution flows
3. Read key files listed above for implementation details
