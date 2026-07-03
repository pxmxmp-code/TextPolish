# TextPolish

This context defines the document-formatting language used by TextPolish. It keeps recognition and formatting terms precise while leaving implementation choices out.

## Language

**Existing Number Recognition**:
Recognition of numbering text that is already present in the source content, so the matching line can receive a configured document style. It does not create Word or WPS automatic numbering.
_Avoid_: automatic numbering, outline numbering generation

**Hierarchical Numeric Numbering**:
An existing-number recognition scheme where numeric segments separated by dots determine the title level, such as `1`, `1.1`, and `1.1.1`. The segment count maps to the configured title level.
_Avoid_: separate regex per numeric depth

**Number Title Boundary**:
The boundary between an existing number and its title text. For hierarchical numeric numbering, spaces, a trailing dot, or a dunhao can separate the number from the title, but the number must appear at the start of the line and be followed by non-empty title text.
_Avoid_: matching bare numbers, decimals, dates, or versions inside body text

**Recognition Precedence**:
The ordering used when more than one recognition scheme could match the same line. Built-in numbering schemes match before advanced regex rules, and a more specific numbering scheme can take precedence over a legacy single-level rule so one line receives exactly one style.
_Avoid_: competing rule results, broad regex rules shadowing built-in numbering

**Numbering Scheme**:
A user-facing recognition option for a family of existing numbering formats. Built-in numbering schemes cover common formats, while advanced regex remains a fallback for unusual cases.
_Avoid_: making every user assemble raw regex rules

**Starting Title Level**:
The title level assigned to the first depth of a hierarchical numbering scheme. Deeper numbering depths map downward from that starting level and clamp to the deepest supported title level.
_Avoid_: fixed depth-to-level mapping

**Advanced Regex Rule**:
A fallback recognition rule for uncommon or organization-specific numbering formats. In its first version, it matches a whole line and assigns one title style rather than splitting matched groups into different styles.
_Avoid_: requiring regex for common numbering schemes, using regex groups for special-format splitting
