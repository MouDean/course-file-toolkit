# Package Validation

Checked 19 October 2026.

- Codex's bundled skill validator accepted the skill's name, frontmatter, description, and instructions.
- Local reference links, JSON examples, plugin metadata, and UI YAML were checked.
- Fifteen synthetic helper tests passed. They cover incomplete/duplicate rosters, count mismatches, leading-zero and numeric IDs, Unicode and multiword names, explicit non-English headers, wrong XLSX dimensions, shared strings, blank enrollment, reordered rosters, altered names, identity mismatches, tampered digests, report overwrite refusal, DOCX formatting digests, native workbook-part differences, and exact folder copies with empty directories.
- Package text was checked for the original instructor's personal paths, institutional URL, course code, teacher identifier, and sampled real student IDs. No real course files, exports, credentials, rosters, or private job data are included.

Run the tests from this folder with:

```text
python -B -m unittest discover -s tests -v
```

These checks validate the bundled helpers and package structure. They do not certify another instructor's workbook, portal access, or native Excel behavior. The skill requires inspecting, mapping, and verifying each real template during the actual job. Its scripts do not perform workbook authoring automatically.
