# Drill 03 — Prefix search and exact output formatting

> Prefix search, two shapes, and exact output formatting.
>
> Two different prefix shapes appear in ICF and candidates confuse them (T17). Both are here.

**Target: 12 minutes.** Traps exercised: T4, T17, T18, T13.

Implement `Catalog` in `solution.py`.

**Shape A — global search over entity names, size-ranked:**

- `add_file(name: str, size: int) -> bool`
  `False` if a file with that name already exists, else `True`.
- `search_files(prefix: str) -> list[str]`
  The **top 10** files whose *name* starts with `prefix`, ordered by size **descending**,
  ties by name **ascending**. Format `"<name>(<size>)"`. `[]` if nothing matches.
  An empty prefix matches every file.

**Shape B — prefix filter over the fields of one record, lexicographic:**

- `set_tag(name: str, field: str, value: str) -> str`
  Sets a tag on a file. Returns `""`. If the file doesn't exist, returns `""` and does
  nothing. Overwrites an existing field.
- `scan_tags(name: str, prefix: str) -> str`
  Fields of `name` starting with `prefix`, sorted by **field name ascending**, rendered as
  `"<field>(<value>), <field>(<value>)"`. `""` if the file or matching fields don't exist.
  An empty prefix matches every field.

### Example

```
add_file("report.pdf", 300)   -> True
add_file("report.txt", 300)   -> True
add_file("readme.md", 900)    -> True
add_file("report.pdf", 10)    -> False
search_files("re")            -> ['readme.md(900)', 'report.pdf(300)', 'report.txt(300)']
search_files("zzz")           -> []
set_tag("readme.md", "owner", "amy")   -> ""
set_tag("readme.md", "org", "acme")   -> ""
set_tag("readme.md", "lang", "en")     -> ""
scan_tags("readme.md", "o")   -> "org(acme), owner(amy)"
scan_tags("readme.md", "")    -> "lang(en), org(acme), owner(amy)"
scan_tags("ghost.md", "o")    -> ""
```

Run: `./run d03`
