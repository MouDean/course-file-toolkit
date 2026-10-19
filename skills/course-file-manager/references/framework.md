# Course File Preparation Framework

This framework gives instructors and assistants a repeatable way to prepare section course files without redesigning their university templates. It supports an entire semester setup or a narrow correction to existing files.

## The working record

Each job has its own private directory containing intake choices, a section map, source exports, backups, staged outputs, and a verification report. Keep it separate from the reusable skill package.

The section map links **course + term + campus + section + class number** to a destination folder and its checklist and CRC file. Store the displayed enrollment count and roster extraction date. A folder name alone is not enough to identify a class. Preserve leading zeros and suffixes in identifiers.

Suggested job states are `inspected`, `sources_verified`, `staged`, `validated`, and `saved`. Track them per section so a blocked section is visible and a rerun does not overwrite completed work blindly.

## Workflow and acceptance conditions

| Stage | Work | Evidence required before continuing |
| --- | --- | --- |
| Inspect | Read the template, schedule, files, and requested scope | Authoritative section map; destination collisions; discovered checklist/CRC fields; sufficient disk space |
| Collect | Retrieve each section's currently enrolled students | Correct course, term, campus, section, class number, filter and displayed count; all rows present; unique IDs within the section |
| Copy | Duplicate approved shared materials and empty folders | Same relative paths, directories, file sizes and SHA-256 hashes; originals preserved |
| Update | Correct fields and populate student tables | Correct metadata; source-derived names/IDs; approved mark-clearing and row-extension behavior |
| Validate | Reopen, recalculate and visually inspect staged files | Exact roster comparison; counts reconcile; formulas cover all rows; native features/layout preserved |
| Save | Replace or rename authorized destinations | Inputs unchanged since staging; backups exist; saved files reopen and pass key checks |

Complete only requested stages. Existing approvals remain valid within the same scope. Ask only when a meaningful policy or mapping decision cannot be resolved from supplied files and conversation.

## Definition of a successful section

The folder, Word checklist, CRC filename, and displayed workbook section agree. Semester and campus are correct if updating them is in scope. IDs and name components exactly match the authoritative roster; no records are dropped, duplicated, truncated, or assigned to another section. The Grade Sheet and linked CLO sheet cover the same students, with enough rows and no displaced summaries.

Old entered marks and status overrides are cleared only when authorized. Real zeros remain valid marks. When blank-result behavior is requested, no ungraded student receives a calculated failure solely because inputs are empty. Existing grading boundaries, weights, and rounding still apply.

The original design remains intact: tabs and visibility, styles, column widths, row conventions, merged cells, images, charts, protection, print settings, validation, and conditional formats. Required row growth may move summaries and chart anchors; it must not change their meaning. Updated ranges and caches must agree with the new layout.

## When to stop a dependent action

Stop editing an affected section if class identity is uncertain, the roster is incomplete, IDs are duplicated, a destination collides with another class, workbook mapping is ambiguous, a native feature would be lost, or the source changed during work. Resolve the cause or ask one specific question. Continue independent work where safe. Never silently skip a failed section and claim the whole batch is complete.

For a locked workbook, ask the instructor to close that file and retry the blocked save after verifying its hash. Do not terminate their Excel session. For OneDrive placeholders or unavailable content, allow normal hydration or ask for affected files; do not replace materials with links or remove videos on your own.

## Saving and recovery

Keep an untouched backup of each file that will be modified. Record its SHA-256 hash, original path, destination, and proposed changes. Before saving, verify the source still matches that hash. Write a temporary file beside the target and replace atomically when supported. Refuse unexpected existing filenames.

Keep a private journal recording sections committed and pending. If a save fails partway, report which sections were saved. Recover only affected files from backups with the instructor's authorization; do not roll back unrelated work or delete backups automatically.

## Shareable versus private materials

Share this framework, SKILL.md, synthetic examples, and reusable scripts. Do not share real rosters, student work, exports, private paths, teacher identifiers, tokens, screenshots, or backups. Examples use fictional records. Successful synthetic tests demonstrate helper behavior, not compatibility with every university workbook.

## A colleague's starting prompt

> Use $course-file-manager. My course folder is [folder], my completed template section is [section], and my teaching schedule is [signed-in portal link or exported schedule]. Prepare [requested stages] for verified sections in [term/campus]. Preserve the university templates. Ask about old marks, extra rows, or grading behavior if those choices are not already clear.

In a client without installed skills, supply SKILL.md and supporting files and ask the assistant to follow them. File/browser access still depends on that client's capabilities.
