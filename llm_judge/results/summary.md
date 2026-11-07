# LLM-as-a-Judge results

Backend: `cli`, model: `claude-opus-5-5`, runs per view: 3, date: 2026-11-07 13:47 UTC

PASS verdict: mean of medians ≥ 3.5 and no dimension < 2. Cells: median (± spread = max − min across runs).

| Dimension | login | repo_home | issues_list | new_issue |
|---|---|---|---|---|
| visual_hierarchy | 4 (±0) | 4 (±0) | 4 (±0) | 4 (±0) |
| consistency | 3 (±1) | 4 (±1) | 5 (±0) | 5 (±0) |
| system_status | 4 (±0) | 4 (±0) | 4 (±0) | 4 (±0) |
| language_clarity | 4 (±1) | 3 (±0) | 4 (±0) | 3 (±1) |
| error_prevention | 3 (±0) | 4 (±0) | 4 (±0) | 3 (±0) |
| efficiency | 5 (±1) | 5 (±0) | 4 (±1) | 4 (±1) |
| minimalism | 4 (±0) | 4 (±0) | 4 (±0) | 4 (±0) |
| accessibility | 3 (±0) | 3 (±0) | 3 (±0) | 3 (±0) |
| **mean** | **3.75** | **3.88** | **4** | **3.75** |
| **verdict** | **PASS** | **PASS** | **PASS** | **PASS** |

## login

- strength: A short, focused form with autofocus and one clear main 'Sign In' button
- strength: Recovery, passkey and registration links sit right where users expect them
- strength: Clear labels that state either a username or an email address is accepted
- [high] (consistency) Mark the Password field as required with the same red asterisk as the username field, or add a note that all fields are required.
- [medium] (accessibility) Make the input borders and checkbox outline in the dark theme at least 3:1 against the background, and make sure the white text on the blue Sign In button reaches 4.5:1 by darkening the blue.
- [medium] (error_prevention) Add a show/hide password toggle, and a short hint next to 'Remember This Device' saying not to use it on shared computers.
- [low] (minimalism) Hide the page and template render times and the version number from users who aren't logged in.
- [low] (accessibility) Enlarge the 'Remember This Device' checkbox's clickable area to at least 24×24 px, for example by making the whole label clickable with padding.

## repo_home

- strength: The latest commit (author, hash, message 'Dodaj docs/INSTALL.md') appears directly above the file list, so the task needs almost no navigation
- strength: It follows familiar Git platform conventions: tab bar with counters, branch selector, and a commits/branches/tags strip
- strength: Shortcuts for efficiency are shown: 'Go to file' (T) and 'Search code' (S)
- [medium] (accessibility) Increase the contrast of secondary grey text (commit messages, 'now' timestamps, 'Manage Topics', counter badges) to at least 4.5:1 against the dark background.
- [medium] (language_clarity) Replace the 'Escape' button label with a descriptive one (e.g. 'Show escaped characters') or add an icon with a visible tooltip/explanation.
- [medium] (language_clarity) Add a visible text label or tooltip to the icon-only compare button next to the branch selector (e.g. 'Compare').
- [low] (system_status) Show absolute dates next to or instead of the relative 'now' (e.g. on the latest commit row) so the last commit time is unambiguous.
- [low] (minimalism) Hide developer-oriented footer metrics (Page/Template render time) for regular users.

## issues_list

- strength: Follows Git platform conventions closely: Open/Closed toggle with counters, a filter bar and colour-coded label pills make the view instantly familiar
- strength: The task is quick to do: the list defaults to open issues, 'bug' badges are visible at a glance and the Label filter is one click away
- strength: Clear navigation status: active Issues tab with a counter, the repo breadcrumb and a highlighted Open state
- [high] (accessibility) Raise the contrast of the metadata text, disabled filters and label pills (for example, darken the green 'enhancement' background or use dark text) to reach at least 4.5:1. Enlarge row checkboxes and their click areas to at least 24×24 px.
- [medium] (system_status) When filters are applied, show active filter chips (e.g. 'label: bug ×') above the list. Add a tooltip to the disabled Milestone/Project filters explaining why they are unavailable (e.g. 'No milestones in this repository').
- [medium] (language_clarity) Tell apart the 'Labels' management button and the 'Label' filter, for example by renaming the button to 'Manage labels' or using an icon. Make the search placeholder more specific, e.g. 'Search issues by title, #number…'.
- [low] (efficiency) Make label badges in rows act as clickable filters, with a visible cue. Consider saved or quick filters (e.g. 'Open bugs') for frequent queries.
- [low] (minimalism) Hide the developer render timings in the footer and the repository tabs that have no content (Packages, Projects, Wiki) to cut visual noise.

## new_issue

- strength: A familiar two-column layout, consistent with GitHub, that groups content (left) and metadata (right) logically
- strength: The title field is focused automatically, and the full editor (toolbar, Preview, file upload) is on one screen
- strength: Clear repository context: the active 'Issues' tab with its counter and the breadcrumb 'judge-demo / web-shop'
- [high] (error_prevention) Mark the Title field as required (for example a visible label 'Title *'). Disable the 'Create Issue' button, or show a validation message inline, while the title is empty.
- [high] (language_clarity) Change the body placeholder from 'Leave a comment' to 'Describe the issue (Markdown supported)'. Add persistent visible labels above the Title and Description fields.
- [medium] (accessibility) Increase the contrast of the placeholder and secondary text ('No labels', 'No Milestone') to at least 4.5:1. Make the whole Labels/Milestone/Assignees header clickable so targets are at least 24×24 px.
- [medium] (system_status) Add a page heading 'New Issue', or extend the breadcrumb to 'judge-demo / web-shop / Issues / New', so the current step is clear.
- [low] (minimalism) Move the 'No Branch/Tag Specified' selector lower in the sidebar or hide it under advanced options. Hide the footer performance metrics outside debug mode.
