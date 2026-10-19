# Course File Toolkit

Share this folder or ZIP with colleagues. It contains the `course-file-manager` skill, a practical framework, an intake form, an example job record, and Python helpers for roster import and verification. It contains no real templates, student data, passwords, or account access.

## Start using it

1. Extract the ZIP. Keep `SKILL.md` with its `references`, `assets`, `agents`, and `scripts` folders.
2. Open a Codex chat with access to your course folder. Ask it to install the local skill at `skills/course-file-manager` for your user, or copy that folder to your configured skills location. Current documentation lists `~/.agents/skills` for user skills and `.agents/skills` for a project. Existing installations can have a configured directory. Do not overwrite an existing same-named skill without checking it.
3. Start a new chat or restart Codex if it is not detected. Invoke `$course-file-manager` in Codex. Use the client-supported skill selector when installed in ChatGPT.
4. Provide your course root, completed template, semester/campus, and schedule link or exports. Sign in to your university portal yourself if necessary. The assistant should inspect before editing and ask only about unresolved choices.

Example prompt:

> Use $course-file-manager to prepare my course files. My course root is [folder], my completed template is [folder], my semester/campus is [term/campus], and my schedule is [link or file]. Copy missing folders, correct checklist sections, and replace old CRC students with current names and IDs. Preserve the templates. Ask before clearing old marks or changing blank-result behavior if I have not already specified those choices.

Without installed skills, supply `skills/course-file-manager/SKILL.md` and supporting files and ask the assistant to follow them. The skill cannot create missing file/browser access or bypass sign-in. Provided roster exports work when live access is unavailable.

## Contents

| File | Purpose |
| --- | --- |
| `skills/course-file-manager/SKILL.md` | Agent instructions |
| `skills/course-file-manager/references/framework.md` | Workflow and acceptance conditions |
| `skills/course-file-manager/assets/intake.md` | Instructor inputs |
| `skills/course-file-manager/assets/job.example.json` | Private job record and example CRC adapter |
| `skills/course-file-manager/scripts/roster_tools.py` | Normalize CSV/XLSX rosters, validate counts/IDs, compare records |
| `skills/course-file-manager/scripts/office_audit.py` | Inspect DOCX/XLSX packages and compare native features |
| `skills/course-file-manager/scripts/file_inventory.py` | Verify exact copies, including empty folders |
| `plugin.json` | Portable metadata for hosts supporting local plugins |

Helpers require Python 3.10+ and only its standard library. They do not log in, message students, or edit CRC workbooks. The skill directs an assistant through template-specific authoring; each university template must be mapped. Appropriate document/spreadsheet editing and rendering capabilities are needed for full verification.

This folder also uses a portable plugin layout. Plugin installation depends on the host and your organization's configuration; this ZIP is not a published marketplace listing. Direct skill-folder installation remains available for local Codex use.

## Sharing and privacy

Keep real templates, exports, student work, rosters, backups, credentials, and outputs outside this toolkit. Do not add the private job directory to the ZIP. Examples/tests use fictional records. Colleagues must use their own authorized accounts and destinations. Sharing the package does not share your PeopleSoft or OneDrive access.

## References

Local skill guidance follows the [official OpenAI skills documentation](https://learn.chatgpt.com/docs/build-skills), checked 19 October 2026. The optional plugin layout follows [OpenAI plugin packaging guidance](https://developers.openai.com/plugins/build/plugins). Follow your organization's current host configuration if installation differs.
