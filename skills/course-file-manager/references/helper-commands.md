# Helper Commands

Resolve `scripts` relative to the installed skill folder. Run commands with an available Python 3.10+ runtime. The helpers use only the standard library. They read source files and can write new reports; they do not edit course documents, access accounts, or send student data anywhere.

## Roster normalization

```text
python scripts/roster_tools.py normalize sources/section-001.xlsx --section 001 --course DEMO100 --campus EX --term "Fall 2026-2027" --class-number CLASS_A --expected-count 2 --out job/section-001.json
```

`--expected-count` must come from the class page. `--sheet` selects a workbook sheet if the first visible one is not the roster. CSV/TSV input is supported; `--encoding` defaults to UTF-8 with optional BOM. Use `--id-header`, `--name-header`, `--last-header`, and `--given-header` when automatic English header detection is insufficient. Names without a comma need separate surname/given-name columns; the helper does not infer name structure from spaces. For a legitimate mononym or a different naming convention, obtain an explicit mapping and use the editor rather than inventing a second component.

The output contains private student records, source checksum, class identity, counts, and a canonical SHA-256 roster digest. The helper cannot know which class was on screen. `identity_verified_by_helper` therefore remains false. Record independent portal identity verification in the private job map, never by altering this flag to imply the parser performed it.

Duplicate IDs, incomplete records, ambiguous headers, Excel errors, and a count mismatch stop normalization. A populated footer can require a cleaner export rather than silent row deletion. Text IDs retain leading zeros. If Excel already stored an ID numerically, the helper cannot recover leading zeros that the source no longer contains.

```text
python scripts/roster_tools.py compare job/export.json job/independently-captured.json
```

Comparison validates both documents' internal digests and identity, then compares every record by ID. A different source order is reported separately and is not a missing-student error. Exit code 0 means equivalent records, 1 means different records, and 2 means invalid input. The two files should come from genuinely independent capture if used as a source-accuracy check.

## Office audits

```text
python scripts/office_audit.py inspect original.xlsx --out job/original-audit.json
python scripts/office_audit.py compare original.xlsx staged.xlsx --out job/diff.json
```

Supports XLSX and DOCX. Reports hash package parts and cell values instead of printing their text. They still belong in the private job directory. XLSX comparison lists changed value/formula/style cell addresses, names, visibility, merges, row/column settings, validation, and protection. DOCX inspection records text and formatting digests for the main story, headers, and footers. Part changes such as charts, drawings, images, styles, links, and custom XML remain visible in the package comparison.

An expected edit will produce a difference; the report does not decide whether a change is authorized. Shared-formula relocation and recalculation caches can change representation without changing meaning. Review the differences against the adapter and render relevant regions. These audits do not replace spreadsheet recalculation or visual inspection.

## Exact folder copies

```text
python scripts/file_inventory.py template --out job/template-inventory.json
python scripts/file_inventory.py copied-section --compare job/template-inventory.json
```

The inventory includes empty folders and streams file SHA-256 hashes. Store its report outside the inventoried folder. Comparison expects an exact copy and reports extra/missing/changed files and folders. Run before personalizing checklists and CRCs; afterward, compare non-targeted materials or assess expected differences explicitly. It does not copy files or delete unexpected files. Linked folders require review to avoid traversing unintended locations.

New report paths must not already exist. Keep previous reports and use a fresh filename on reruns. Reading OneDrive placeholders can hydrate files through the normal sync client. Local verification does not establish cloud synchronization.
