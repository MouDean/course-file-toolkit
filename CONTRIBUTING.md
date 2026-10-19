# Contributing

Useful contributions include export parsing improvements, institutional terminology, clearer setup guidance, and tests that catch missing students or formatting loss. Keep the workflow configurable rather than assuming one course, campus, or grading scheme.

1. Fork the repository and create a branch for a focused change.
2. Add a fictional fixture or regression case when changing helper behavior. Never use live student records, university documents, or account sessions.
3. Run `python -B -m unittest discover -s tests -v` with Python 3.10 or later.
4. Check that local Markdown links still resolve and examples run as documented.
5. Open a pull request describing the problem, resulting behavior, and validation.

The Python helpers use only the standard library. Avoid new dependencies unless there is a concrete need. Preserve text IDs and observed name components; do not infer names from cultural assumptions or split on spaces. Reject incomplete or ambiguous roster data instead of silently dropping rows.

For workbook-authoring guidance, preserve the institution's template and keep changes within the instructor's request. Do not turn this project into automatic enrollment editing, grading, or student messaging.

Before publishing, inspect the entire diff for private paths, identifiers, names, credentials, screenshots, and output files. Synthetic records should be visibly fictional. An ignored file is not a substitute for reviewing a commit.
