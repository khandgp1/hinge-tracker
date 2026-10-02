# Regression Guard & Code Editing Quality Rules

Follow these rules for all code changes, edits, and feature implementations in this repository:

## 1. Mandatory `git diff` Audit
- Before declaring any task complete or reporting completion to the user, you MUST run `git diff` across all modified files.
- Inspect the diff line-by-line to verify:
  - No unrelated lines, HTML tags, comments, styles, or functions were deleted or modified.
  - Replacement chunks did not inadvertently swallow adjacent code at selection boundaries.
  - All opening and closing tags/braces (`<div>...</div>`, `{...}`, `</script>`, etc.) remain balanced and intact.

## 2. Core Navigation & UI Protection
- In [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html), never remove, alter, or disrupt:
  - Bottom navigation bar elements (`#navStandoutsBtn`, `#navLikesBtn`, `#navChatBtn`, `#navProfileBtn` and their child icons/images).
  - Header elements and triggers (`#importMatchesBtn`, `#profileDropdownTrigger`, title headings).
  - Main view containers (`#matchesView`, `#chatOverlay`, dialogue drawers).
- When any edit touches the DOM structure around navigation or layout containers, verify that all 4 navigation icons remain present and functional.

## 3. Surgical Edits
- Keep `TargetContent` in replacement tools strictly focused on the exact lines requiring changes.
- Avoid including adjacent container tags in replacement blocks unless the container itself is intentionally being redesigned.
