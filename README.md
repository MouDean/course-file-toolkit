# Course File Toolkit

Reusable AI-assistant instructions and verification tools for preparing university course files across multiple sections.

Faculty course files often repeat the same syllabus, instructional materials, checklist, and comprehensive course review workbook. The section details and student roster must change, while the institution's document formatting and spreadsheet formulas need to stay intact. This toolkit organizes that work into an inspect, collect, update, verify, and save workflow.

## What it does

- Guides an assistant through copying a completed course-file folder into the instructor's verified sections.
- Updates section labels in Word checklists while preserving their formatting.
- Collects currently enrolled student names and IDs from an authorized PeopleSoft session or supplied CSV/XLSX exports.
- Defines a template-specific process for refreshing CRC workbooks, extending student rows and linked formulas, and handling previous marks with the instructor's approval.
- Supplies read-only helpers for complete roster comparisons, Office package audits, and exact folder-copy verification.

**This is an assistant workflow toolkit, not a one-click student information system integration.** The Python helpers do not edit CRC workbooks, grade students, sign in, change enrollment, or submit marks. A capable assistant must inspect and map each university's template before authoring changes.

## Quick start for instructors

1. Download this repository using **Code > Download ZIP**, or clone it.
2. Follow [START_HERE.md](START_HERE.md) to install the `course-file-manager` skill in your assistant's supported local skill directory.
3. Supply your own completed section template, destination folder, semester/campus, and teaching schedule or exports.
4. Start with:

```text
Use $course-file-manager to prepare my course files.
Course root: [my folder]
Completed template: [my section folder]
Term and campus: [my term/campus]
Schedule: [my signed-in portal link or exported schedule]
Requested work: [folder copies, checklists, CRC metadata and/or rosters]
Preserve my university's templates. Ask about unresolved decisions before
clearing old marks, extending rows, or changing blank-result behavior.
```

If you are not using installed skills, provide [SKILL.md](skills/course-file-manager/SKILL.md) and its supporting folder to your assistant. The [framework](skills/course-file-manager/references/framework.md) can also be followed manually.

## Portable across universities

Section lists, course codes, academic terms, campus labels, filenames, spreadsheet addresses, and grading rules are configurable. The [example job record](skills/course-file-manager/assets/job.example.json) shows the information to capture; its cell addresses are illustrative and must be verified against the real workbook. Names are never split by guessing at spaces, and IDs remain text so leading zeros are preserved when present in the source.

PeopleSoft guidance describes class-identity checks and export handling. Other student systems can be used through authorized exports or a supported browser workflow, provided the same identity, count, and record checks are performed. An enrollment roster is not an attendance report.

## Try the helpers with fictional data

Requires **Python 3.10+**. No third-party Python packages are needed for the helpers or tests.

```bash
python skills/course-file-manager/scripts/roster_tools.py normalize skills/course-file-manager/assets/roster.synthetic.csv --section 001 --course DEMO100 --campus EX --term "Example Term" --class-number CLASS_A --expected-count 2 --out private-job/section-001.json
python -B -m unittest discover -s tests -v
```

The first command writes a new local report; choose a fresh report filename on reruns. Never place real student data in a public repository. See [helper commands](skills/course-file-manager/references/helper-commands.md) for roster comparisons, Office audits, and folder inventories.

## Project structure

```text
skills/course-file-manager/
  SKILL.md          Assistant workflow and stage routing
  agents/           Skill display metadata
  assets/           Intake form, example job record, fictional roster
  references/       Framework and template-preservation procedures
  scripts/          Standard-library verification helpers
tests/              Synthetic-only regression tests
```

## Verification and limits

The initial helper suite has **15 tests** covering incomplete and duplicate rosters, counts, leading-zero IDs, numeric IDs, Unicode names, shared strings, incorrect Excel dimensions, roster order, source identity, report overwrite refusal, document formatting digests, native workbook parts, and empty folders. [VALIDATION.md](VALIDATION.md) records the scope. GitHub Actions runs the suite on supported Python versions.

These tests do not certify compatibility with every institutional template or prove native Excel recalculation. Real jobs still require inspecting the supplied workbook, preserving its native features, testing affected formulas in a disposable copy, and reviewing changed document regions. Document/spreadsheet editing and rendering capabilities depend on the assistant environment.

## Privacy and contributions

Only fictional examples belong in this project. Do not contribute university templates without permission, student names/IDs, work samples, grades, attendance, account details, credentials, screenshots of live systems, or private job files. The [.gitignore](.gitignore) is a convenience, not a data-loss prevention system; review every change before publishing.

Contributions are welcome: export adapters, clearer instructor guidance, synthetic regression cases, and template-preservation checks. Read [CONTRIBUTING.md](CONTRIBUTING.md). Report privacy-sensitive issues using [SECURITY.md](SECURITY.md), without posting live records.

## Background and credit

Created by [codebea](https://github.com/codebea) from a practical faculty course-file preparation workflow. The project demonstrates workflow design, reusable agent instructions, source-data validation, Office-format preservation checks, and Python testing. It is an independent project and is not endorsed by a university, Oracle, Microsoft, GitHub, or OpenAI.

## License

MIT. See [LICENSE](LICENSE).
