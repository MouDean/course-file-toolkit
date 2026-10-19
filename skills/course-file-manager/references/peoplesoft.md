# PeopleSoft Schedule and Roster Collection

Use the supplied institutional URL and authorized browser session. Do not ask for a password in chat. If sign-in or a second factor requires the instructor, identify the step and continue independent file inspection.

## Establish identity before downloading

Confirm the teaching schedule's selected term and campus. Read the actual class list rather than inferring consecutive sections. Cross-listed courses can have similar labels.

For each class, record the visible course code/title, section, campus, term, class number, and enrolled count. Open **Class Roster** and confirm the same identity. Select currently enrolled students unless the instructor needs another population. Read all rows or export the complete roster.

Bind each export to this evidence before navigating away. Do not label exports solely by download order, timestamps, number of students, or the first student's name.

## Extract all students

An export may download through a newly opened tab, so a listener on the source tab can miss it. Inspect the result before repeated clicks. An XLSX export may declare a dimension of `A1` while holding many complete rows. The bundled parser reads actual worksheet row/cell elements without trusting the dimension.

Normalize the identified export with `roster_tools.py`. Obtain the expected count from the portal, not from the same file. Where possible, independently extract the visible names/IDs and compare every pair or a SHA-256 digest of identical canonical records. Counts and first/last records alone are weaker checks; disclose that limitation when applicable.

Preserve names exactly. PeopleSoft commonly displays `Family name,Given names`; split at the first comma only for that observed convention. Preserve multiword surnames, apostrophes, hyphens, non-Latin text, and all given names. Do not split names on spaces. Retain raw names for audit. Keep IDs as text and never invent lost leading zeros.

## Enrollment and attendance are different

A roster lists enrolled students. Attendance records meetings or periods. Do not rename a roster as attendance or create events. Download attendance only if requested and an actual report exists. If a course has no lectures or the template says attendance does not apply, report the evidence and retain the note unless asked to revise it.

Do not click notification controls, email student links, change enrollment, or submit marks. If the instructor navigates elsewhere during work, leave their current user-controlled state rather than fighting their navigation.
