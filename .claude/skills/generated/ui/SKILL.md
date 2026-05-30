---
name: ui
description: "Skill for the Ui area of TextPolish. 49 symbols across 5 files."
---

# Ui

49 symbols | 5 files | Cohesion: 94%

## When to Use

- Working with code in `src/`
- Understanding how load_ui_settings, get_config_file_path, setup_ui work
- Modifying ui-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/textpolish/ui/config_interface.py` | __init__, setup_ui, apply_page_title_style, create_app_settings_section, apply_theme_background (+25) |
| `src/textpolish/ui/main_interface.py` | __init__, initUI, update_splitter_style, create_input_card, create_output_card (+1) |
| `src/textpolish/config.py` | load_ui_settings, get_config_file_path, get_config, update_level_config, save_ui_settings |
| `src/textpolish/ui/main_window.py` | __init__, initWindow, center_window, initThemeListener, add_config_interface |
| `src/textpolish/utils/icon.py` | get_icon_path, load_icon, set_window_icon |

## Entry Points

Start here when exploring this area:

- **`load_ui_settings`** (Method) — `src/textpolish/config.py:414`
- **`get_config_file_path`** (Method) — `src/textpolish/config.py:438`
- **`setup_ui`** (Method) — `src/textpolish/ui/config_interface.py:530`
- **`apply_page_title_style`** (Method) — `src/textpolish/ui/config_interface.py:598`
- **`create_app_settings_section`** (Method) — `src/textpolish/ui/config_interface.py:622`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `load_ui_settings` | Method | `src/textpolish/config.py` | 414 |
| `get_config_file_path` | Method | `src/textpolish/config.py` | 438 |
| `setup_ui` | Method | `src/textpolish/ui/config_interface.py` | 530 |
| `apply_page_title_style` | Method | `src/textpolish/ui/config_interface.py` | 598 |
| `create_app_settings_section` | Method | `src/textpolish/ui/config_interface.py` | 622 |
| `apply_theme_background` | Method | `src/textpolish/ui/config_interface.py` | 747 |
| `apply_title_label_style` | Method | `src/textpolish/ui/config_interface.py` | 770 |
| `apply_scroll_area_style` | Method | `src/textpolish/ui/config_interface.py` | 792 |
| `setup_save_button` | Method | `src/textpolish/ui/config_interface.py` | 841 |
| `apply_save_button_style` | Method | `src/textpolish/ui/config_interface.py` | 898 |
| `load_ui_settings` | Method | `src/textpolish/ui/config_interface.py` | 987 |
| `create_title_settings_section` | Method | `src/textpolish/ui/config_interface.py` | 1062 |
| `create_text_settings_section` | Method | `src/textpolish/ui/config_interface.py` | 1068 |
| `initWindow` | Method | `src/textpolish/ui/main_window.py` | 22 |
| `center_window` | Method | `src/textpolish/ui/main_window.py` | 59 |
| `initThemeListener` | Method | `src/textpolish/ui/main_window.py` | 87 |
| `add_config_interface` | Method | `src/textpolish/ui/main_window.py` | 110 |
| `get_icon_path` | Method | `src/textpolish/utils/icon.py` | 17 |
| `load_icon` | Method | `src/textpolish/utils/icon.py` | 38 |
| `set_window_icon` | Method | `src/textpolish/utils/icon.py` | 76 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `__init__ → Save_config` | cross_community | 8 |
| `Add_rule → Save_config` | cross_community | 6 |
| `Main → Get_icon_path` | cross_community | 6 |
| `__init__ → Update_remove_button_style` | cross_community | 5 |
| `__init__ → Apply_rule_widget_style` | cross_community | 5 |
| `__init__ → Get_icon_path` | intra_community | 5 |
| `On_rule_changed → Save_config` | cross_community | 4 |
| `__init__ → Clear_rules` | cross_community | 4 |
| `__init__ → Apply_title_label_style` | intra_community | 4 |
| `Add_rule → Update_remove_button_style` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Textpolish | 1 calls |

## How to Explore

1. `gitnexus_context({name: "load_ui_settings"})` — see callers and callees
2. `gitnexus_query({query: "ui"})` — find related execution flows
3. Read key files listed above for implementation details
