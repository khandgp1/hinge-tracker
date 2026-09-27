# 52 — Clean Start: Empty Matches & Chats, Disabled Auto-Seeding, Empty State UI & Reset CLI

## Goal

Provide a clean start across the Hinge Tracker application:
1. **Disable Auto-Seeding**: Remove the automatic seeding of demo matches (`defaultMatchesData`) and demo chats (`aubreyChatData`) in `index.html`, allowing the app to start with 0 matches and 0 chats.
2. **Empty State UI**: Implement a clean, modern empty state for the Matches list when 0 matches exist, complete with an icon, "No matches yet" heading, descriptive subtext, and an "Import Matches" action button that opens the screenshot file picker.
3. **Database Purge**: Clear all current match documents in the Firestore `matches` collection and all chat subcollections (`chats/{match}/messages`), while keeping `coachDialogue` intact.
4. **Reusable Reset CLI**: Create `reset_db.py` to allow the user or developer to instantly wipe all matches and chats anytime via command line (with interactive confirmation or `--yes` flag) without touching coach dialogue.

---

## Architectural Changes & Design

```
┌────────────────────────────────────────────────────────┐
│                      Firestore                         │
│  - matches/ (Purged -> 0 docs)                         │
│  - chats/{match}/messages (Purged -> 0 docs)           │
│  - coachDialogue/ (PRESERVED intact)                   │
└──────────────────────────┬─────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│        index.html         │ │        reset_db.py        │
│ - matchesData: []         │ │ - CLI utility             │
│ - snap.empty: NO seed     │ │ - Wipes matches & chats   │
│ - Render empty state      │ │ - Preserves coachDialogue │
│ - "Import Matches" button │ │ - --yes flag for non-int. │
└───────────────────────────┘ └───────────────────────────┘
```

### 1. `index.html` Adjustments
- **Initial State**: Change `let matchesData = [...defaultMatchesData];` to `let matchesData = [];` so memory starts clean. Keep `defaultMatchesData` and `aubreyChatData` definitions as archived reference constants if needed, but do not assign them as default state.
- **`initFirestoreMatches()`**:
  - Remove the branch that auto-seeds `defaultMatchesData` when `snap.empty`.
  - In `matchesCol.onSnapshot`:
    - When `snapshot.empty` is true, explicitly set `matchesData = []` and call `renderMatchesList()`.
    - When docs exist, map docs to `matchesData` and call `renderMatchesList()`.
- **`renderMatchesList()`**:
  - Check `if (matchesData.length === 0)`:
    - Render an empty state card with an icon (e.g. user/message silhouette), "No matches yet" title, "Tap + or import a screenshot to add your matches" subtitle, and an "Import Matches" button styled consistently with the app's aesthetic.
    - Wire button click to trigger `matchesFileInput.click()`.
- **`initFirestoreChat(match)`**:
  - Remove the auto-seed check `if (match.name === 'Aubrey') { seed aubreyChatData }`.
  - Ensure opening any match with 0 messages displays the existing clean chat empty state ("You matched with {name} / Start the chat with {name}" and "Upload Chat Screenshots" button).

### 2. `reset_db.py` CLI Utility
- A standalone, robust script using Python's standard `urllib.request` communicating directly with the Firestore REST API using the project's Firebase credentials:
  - Fetches all documents in `matches`.
  - Deletes all messages in `chats/{match_name}/messages`.
  - Deletes all match documents in `matches`.
  - Explicitly skips/preserves `coachDialogue`.
  - Supports `--yes` / `-y` flag to bypass interactive confirmation for automated execution.
  - Reports summary of deleted documents.

---

## Files to Modify & Create

### [NEW] [reset_db.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/reset_db.py)
* CLI utility to purge all matches and chats from Firestore with safety checks, preserving `coachDialogue`.

### [MODIFIED] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
* Remove auto-seeding from `initFirestoreMatches()` and `initFirestoreChat()`.
* Add empty state UI to `renderMatchesList()` when `matchesData.length === 0`.
* Handle empty snapshot in `onSnapshot` to render empty state immediately.

---

## Verification Plan

### Automated Verification
1. Run `python3 reset_db.py --yes` to execute the database wipe.
2. Verify via Firestore REST API that:
   - `GET /matches` returns 0 documents (`documents` key not present or empty).
   - `GET /coachDialogue` still contains all existing coach conversation documents.

### Browser / UI Verification
1. Open or refresh `index.html` in the browser.
2. Verify:
   - The Matches tab displays the "No matches yet" empty state with the "Import Matches" button.
   - Clicking "Import Matches" opens the file chooser.
   - No auto-seeding occurs (console logs do not show `[Firestore] Seeding default matches...`).
   - The Coach Dialogue bottom sheet remains populated with prior advice messages.
3. Test adding a match (via screenshot import or test script) to ensure adding matches still works properly and seamlessly transitions from empty state to the match list.

---

## Progress Checklist

- [x] **Step 1:** Create `reset_db.py` CLI script to safely purge all matches and chat messages while preserving `coachDialogue`.
- [x] **Step 2:** Execute `python3 reset_db.py --yes` to wipe the remote Firestore database clean.
- [x] **Step 3:** Update `index.html` to disable auto-seeding in `initFirestoreMatches()` and `initFirestoreChat()`.
- [x] **Step 4:** Implement the Matches tab empty state in `renderMatchesList()` and style it cleanly in `index.html`.
- [x] **Step 5:** Handle empty snapshot in `matchesCol.onSnapshot` so the UI immediately reflects 0 matches.
- [x] **Step 6:** Verify in browser that the app starts with 0 matches, 0 chats, shows the new empty state, and preserves coach dialogue.
