# CRC Workbook Preservation and Update Procedure

## Map the template first

Inspect and render the workbook before authoring. `office_audit.py inspect` inventories native package parts, sheets, actual extents, formulas, merges, validations, charts, and styles without printing cell values. Inspect actual labels and formulas privately through the spreadsheet editor.

Build a job-specific adapter: metadata inputs; student-table boundaries; sequence, surname, given-name, ID, mark-input, result, and override columns; linked CLO rows; summaries; and the source of grading thresholds. Discover protection requirements. Do not assume the example adapter applies to another CRC revision.

Some templates use `Course Information` as the metadata source, `Grade Sheet` for roster inputs, and a formula-linked `CLO sheet`. Change authoritative inputs once and preserve links. Do not paste over formula-driven CLO names/IDs.

## Extend capacity safely

When authorized, insert extra student rows before summaries. Match appropriate nearby row styles, heights, and formula patterns. Fill sequences and translate formulas through the last student. Preserve IDs as text.

Update dependencies affected by insertion: student averages/counts/percentages, linked CLO rows, distribution and review references, names, filters, validations, conditional formats, print areas, chart references and drawing anchors. Absolute references move with Excel row insertions; copying formulas is a different operation. Student-only ranges must end at the new last student, before summaries.

Shared-formula children may have an empty `<f>` element inherited from a master. Resolve it before translating; it is not a blank cell. Do not replace formulas with cached values or rewrite unrelated formulas.

## Replace students and authorized inputs

Write source-derived surname, given names, and text ID to mapped columns. Replace the entire old roster, clearing leftover students when the new population is smaller. Clear old **entered** marks and approved manual overrides when authorized; retain weights, maximum scores, formulas, validation, and unrelated review text.

Unused shared strings or unrelated hidden caches may still contain historical IDs. A roster refresh is not a forensic privacy scrub. Preserve those parts unless sanitization is requested, and keep the full workbook private.

## Missing marks versus zeros

Read existing grading logic and ask about empty-result behavior if a change is not authorized. Never assume every course uses S/US or a 60-point threshold.

For an approved blank-result rule on numeric marks, use presence checks such as `COUNT(mark_range)=0`, distinguishing empty inputs from genuine zeros. Adapt these examples to the real template:

```excel
=IF(COUNT(E6:H6)=0,"",SUM(E6:H6))
=IF(COUNT(E6:H6)=0,"",EXISTING_LETTER_LOGIC)
=IF(COUNT('Grade Sheet'!E6)=0,"",'Grade Sheet'!E6)
=IF(COUNT(E6:E65)=0,"",AVERAGE(E6:E65))
=IF(COUNT(E66)=0,"",E66/E5)
```

`EXISTING_LETTER_LOGIC` is explanatory notation, not a formula to paste. Retain the real grading scale, weights, rounding, and conditions. Decide how partial marks behave: a nonempty range need not mean fully graded. Extend numeric blank handling to affected summaries when required. Avoid blanket error suppression that hides broken references.

## Preserve native features

Do not assume library round-trips preserve everything. Compare before/after parts and native structures: charts, images, hidden/very-hidden sheets, validations, comments, protection, print settings, custom XML, add-ins, external links, and names.

If the engine cannot retain a feature, use a narrower supported edit or carefully merge only authorized cells and structural changes into an original-package copy. Do not silently drop features. Invalidate/rebuild calculation metadata after changes. Refresh affected formula/chart caches, or explicitly require Excel recalculation and disclose stale previews.

Legacy signed chart-axis IDs and sparse hidden caches extending to distant cells can break preview engines. Normalize only a disposable tool copy if needed, preserving native originals in the deliverable. These are conditional troubleshooting measures, not routine edits to all charts or hidden sheets.

## Verify the saved workbook

- Compare every ID and name against the verified source, exact section counts, and unique IDs.
- Reopen and confirm linked rows, first/last students, summaries, section, term, and student count.
- Recalculate affected results. In disposable copies, test all blanks, real zeros, both sides of the actual grade boundary, maximum marks, and the last added student. Restore inputs before previews; never save test marks into outputs.
- Render changed metadata/student regions, long names, final rows, summaries, and affected charts. Check clipping, missing rows, blank-vs-zero behavior, and displaced summaries.
- Compare styling, widths, row conventions, formulas, and native features outside the approved changes. `office_audit.py compare` supports this review; it does not automatically establish a PASS.

Name specific unverified Excel features rather than claiming native Excel validation when only another engine was used.
