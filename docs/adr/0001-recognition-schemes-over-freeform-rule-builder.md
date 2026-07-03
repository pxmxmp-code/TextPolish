# Recognition schemes over a freeform rule builder

TextPolish will support flexible title recognition through built-in numbering schemes first, with advanced regex rules kept as an expert fallback. This keeps common cases such as hierarchical numeric numbering (`1`, `1.1`, `1.1.1`) configurable without requiring regex, while avoiding the complexity of a general rule-builder UI.

The formatter recognizes numbering that already exists in the source text and applies configured title styles; it does not generate Word or WPS automatic numbering. Built-in numbering schemes take precedence over advanced regex rules so broad custom expressions do not shadow predictable common formats.

**Consequences**: The first implementation should add hierarchical numeric numbering with a configurable starting title level, require non-empty title text after the number, keep advanced regex to whole-line title recognition, and show recognition results in the settings test area. It should not add automatic Word/WPS numbering, more title levels, regex capture-group styling, or a general rule-builder UI.
