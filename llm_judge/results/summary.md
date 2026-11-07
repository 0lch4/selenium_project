# LLM-as-a-Judge results

Backend: `cli`, model: `claude-opus-5-5`, runs per view: 3, date: 2026-11-07 16:46 UTC

PASS verdict: mean of medians ≥ 3.5 and no dimension < 2. Cells: median (± spread = max − min across runs).

| Dimension | login | repo_home | issues_list | new_issue |
|---|---|---|---|---|
| visual_hierarchy | 4 (±0) | 4 (±0) | 4 (±0) | 4 (±0) |
| consistency | 4 (±1) | 4 (±0) | 5 (±0) | 5 (±1) |
| system_status | 4 (±0) | 4 (±0) | 4 (±0) | 3 (±1) |
| language_clarity | 4 (±0) | 3 (±1) | 4 (±0) | 4 (±1) |
| error_prevention | 3 (±0) | 4 (±0) | 4 (±0) | 3 (±1) |
| efficiency | 4 (±1) | 5 (±0) | 4 (±1) | 3 (±1) |
| minimalism | 4 (±0) | 4 (±0) | 5 (±1) | 4 (±0) |
| accessibility | 3 (±0) | 3 (±0) | 3 (±0) | 3 (±0) |
| **mean** | **3.75** | **3.88** | **4.12** | **3.62** |
| **verdict** | **PASS** | **PASS** | **PASS** | **PASS** |

## login

- strength: The login form is focused and centred, with a clear full-width primary 'Sign In' button.
- strength: The username field gets focus automatically and shows a visible focus ring, so the user can start typing straight away.
- strength: Recovery and other paths ('Forgot password?', passkey, 'Register now.') are easy to find and placed in the expected spots.
- [high] (accessibility) Make unfocused input borders lighter so they reach at least 3:1 against the dark background. Darken the button blue, or check that its white text reaches 4.5:1.
- [medium] (consistency) Style the 'Password' label the same way as the username label (bold, with a required asterisk). Use one capitalisation style everywhere, for example 'Remember this device' and 'Sign in'.
- [medium] (error_prevention) Add a show/hide toggle to the password field so users can check what they typed.
- [low] (minimalism) Hide the page and template render times (and possibly the version) from anonymous users in the footer.
- [low] (visual_hierarchy) Make the 'Sign In' heading larger, or centre the card vertically a little more, to balance the empty space below the form.

## repo_home

- strength: The file list shows each item's last commit message, and the latest commit (hash, author, message) sits right above it. This makes the typical task fast.
- strength: The repository navigation follows familiar Git platform conventions: an active Code tab, counters, a branch selector, and Watch/Star/Fork buttons.
- strength: 'Go to file' (T) and 'Search code' (S) show visible keyboard shortcut hints, which speeds up navigation.
- [high] (accessibility) Increase contrast for secondary text (commit messages, timestamps), counter badges and control borders in the dark theme to at least 4.5:1 for text and 3:1 for UI component boundaries.
- [medium] (language_clarity) Replace the bare 'Escape' button in the README header with a descriptive label or tooltip (e.g. 'Show escaped characters'), or hide it unless ambiguous characters are actually present.
- [medium] (accessibility) Add visible text labels or tooltips and aria-labels to the icon-only buttons (the compare icon next to the branch selector, RSS, the README edit pencil).
- [low] (system_status) Visually set the latest-commit row apart from the file rows (e.g. a 'Latest commit' label or a tinted background), and show absolute dates alongside relative times like 'now'.
- [low] (minimalism) Remove the star, watcher and fork counts that duplicate the header buttons from the sidebar, and hide the page/template render timings from regular users.

## issues_list

- strength: The layout follows familiar GitHub-style conventions: state toggle, filter dropdowns and coloured label pills.
- strength: A clean, minimal issue list where titles and labels are scannable at a glance.
- strength: The Issues tab, its counter and the Open/Closed counts clearly show where the user is and what state the issues are in.
- [high] (accessibility) Raise the contrast of secondary metadata text, the search placeholder and the white-on-green label text to at least 4.5:1. Enlarge the row checkboxes, or their hit area, to 24×24px.
- [medium] (system_status) Show active filters as removable chips (e.g. 'Label: bug ×') and make the selected Open/Closed segment more visually distinct.
- [medium] (efficiency) Make the label pills in rows visibly clickable so they filter the list, and consider quick filters such as 'Open bugs' next to the state toggle.
- [low] (error_prevention) Add tooltips to the disabled Milestone/Project dropdowns explaining why they are disabled (e.g. 'No milestones in this repository').
- [low] (language_clarity) Use a more specific search placeholder, e.g. 'Search issues by title or content…'.

## new_issue

- strength: A familiar two-column issue form that matches GitHub conventions, with all metadata on one page
- strength: The title field has focus on load and the 'Create Issue' button is clearly placed
- strength: Clear location context: repo breadcrumb and active Issues tab with counter
- [high] (error_prevention) Add a persistent visible 'Title' label with a required asterisk. Disable 'Create Issue', or show an inline message, while the title is empty.
- [high] (accessibility) Increase the contrast of placeholder text, the sidebar empty-state text and the primary button (aim for at least 4.5:1). Enlarge the gear-icon targets to at least 24×24px.
- [medium] (efficiency) Make the sidebar headers ('Labels', etc.) fully clickable and add an explicit 'Add label' affordance instead of relying on the gear icon alone.
- [low] (language_clarity) Change the 'Leave a comment' placeholder to 'Describe the issue…', add a tooltip explaining 'No Branch/Tag Specified', and make the empty-state capitalisation consistent.
- [low] (system_status) Add a 'New issue' page heading above the form.
