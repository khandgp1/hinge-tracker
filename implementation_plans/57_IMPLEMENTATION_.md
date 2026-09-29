# 57 — Remove Add Matches and Chat Screenshot Upload from Coach View

## Goal

Remove match addition/importing and chat screenshot uploading capabilities from the Coach view (`?role=coach`), providing a clean, read-only oversight experience while preserving the coach's ability to participate in Coach & Client Dialogue.

---

## Design Decisions (from `/grill-me` alignment)

1. **Role Scope & Identification**:
   - The role is determined by URL parameter `?role=coach` and persisted in `sessionStorage` (`hinge_tracker_role`) across page refreshes and navigation.
   - `currentRole === 'coach'` triggers coach-restricted UI behavior.

2. **Matches View Restrictions**:
   - **Header**: Hide the `+` import button (`#importMatchesBtn`) in the top navigation header when in coach view.
   - **Empty State**: In the "No matches yet" empty state, retain the title and subtitle but omit the "Import Matches" button (`#emptyMatchesImportBtn`).

3. **Chat View Restrictions**:
   - **Header**: Hide the screenshot upload button (`#chatUploadBtn`) in the chat header when in coach view.
   - **Header Alignment**: Ensure `.chat-header-spacer` preserves balanced spacing so the match name remains centered between the back button and the right boundary.
   - **Empty State**: In the empty chat state ("You matched with [Name]" / "Start the chat with [Name]"), omit the "Upload Chat Screenshots" button (`#emptyStateUploadBtn`).

4. **Defensive Guards**:
   - Guard file inputs (`#matchesFileInput`, `#chatFileInput`) and ingestion triggers so coaches cannot upload images even if triggered programmatically or via debug helpers.

---

## Proposed Changes

### [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Role Persistence & Initialization**:
   - Check `new URLSearchParams(window.location.search).get('role')` or fallback to `sessionStorage.getItem('hinge_tracker_role')`.
   - If `role === 'coach'`, persist to `sessionStorage`.
   - Add a body or root class (e.g. `role-coach`) for clean CSS-driven visibility control where appropriate.

2. **Matches View Updates**:
   - If `currentRole === 'coach'`, hide `#importMatchesBtn`.
   - In `renderMatches()` empty state generator: conditionally omit `<button class="matches-import-action-btn" id="emptyMatchesImportBtn">` if `currentRole === 'coach'`.

3. **Chat Header & Empty State Updates**:
   - In chat header, if `currentRole === 'coach'`, hide `#chatUploadBtn` and render or display a `.chat-header-spacer` on the right side.
   - In `initMatchChatListener()` empty snapshot generator: conditionally omit `<button class="chat-upload-action-btn" id="emptyStateUploadBtn">` if `currentRole === 'coach'`.

4. **Action Guards**:
   - In `#importMatchesBtn` click listener and `#chatUploadBtn` click listener, return early if `currentRole === 'coach'`.
   - In `processScreenshotFile()`, return early if `currentRole === 'coach'`.

---

## Verification Plan

### Automated / Browser Verification
1. **Client Mode Check (`/` without `?role=coach`)**:
   - Navigate to `http://localhost:8080/`.
   - Verify `#importMatchesBtn` is visible in Matches header.
   - Open a match; verify `#chatUploadBtn` is visible in Chat header.
   - Verify empty states include the respective upload buttons.
2. **Coach Mode Check (`/?role=coach`)**:
   - Navigate to `http://localhost:8080/?role=coach`.
   - Verify `#importMatchesBtn` is hidden from the Matches header.
   - Open a match; verify `#chatUploadBtn` is hidden and match title is properly centered.
   - Check empty match list and empty chat states: verify upload buttons are absent.
   - Verify Coach & Client Dialogue drawer functions normally (coach can send advice messages and view existing chat).
3. **Session Persistence**:
   - Refresh the page and verify coach mode remains active if persisted in session.

---

## Progress Checklist

- [x] **Step 1:** Add role detection persistence and `role-coach` body class logic in `index.html`.
- [x] **Step 2:** Conditionally hide `#importMatchesBtn` and omit `#emptyMatchesImportBtn` in Coach view.
- [x] **Step 3:** Conditionally hide `#chatUploadBtn`, apply `.chat-header-spacer`, and omit `#emptyStateUploadBtn` in Coach view.
- [x] **Step 4:** Add execution guards to upload handlers for `currentRole === 'coach'`.
- [x] **Step 5:** Verify both Client and Coach modes using browser subagent / automated testing.
