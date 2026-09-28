# 55 — Universal Coach & Client Dialogue for All Matches

## Goal

Expand the Coach & Client Dialogue bottom sheet drawer so that every match card in Hinge Tracker has its own isolated, real-time coaching conversation backed by Firestore at `chats/{matchName}/coachDialogue`, starting fresh across all matches.

---

## Architecture & Data Strategy

1. **Firestore Data Model**:
   - Path: `chats/{matchName}/coachDialogue`
   - Scoped per match directly under `chats/{matchName}`.
   - Document Schema:
     - `sender`: `'coach' | 'client'`
     - `name`: `'DA' | 'Me'`
     - `text`: string
     - `ts`: `firebase.firestore.FieldValue.serverTimestamp()`
2. **Legacy Cleanup**:
   - Purge the legacy 5 test messages in top-level `coachDialogue`.
3. **Database Maintenance Tooling**:
   - Update `reset_db.py` to support collectionGroup query or `chats/*/coachDialogue` deletion, with options/flags to either wipe or preserve coach dialogue during database resets.
4. **Frontend Architecture (`index.html`)**:
   - Enable the coach bottom sheet drawer (`#expertBottomSheet`) for **all** matches upon click.
   - Scope real-time listener to active match: `currentCoachChatUnsubscribe`.
   - Dynamic unread badge:
     - Badge starts hidden (`display: none`).
     - When drawer is collapsed and new messages from `sender === 'coach'` arrive, display dynamic unread count.
     - When drawer is opened, reset badge to hidden.
   - Send handler writes directly to `chats/{currentActiveMatch.name}/coachDialogue`.
   - Clean teardown on `closeChat()`: unsubscribe coach listener, clear feed, collapse drawer.

---

## Files to Modify

### 1. [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Hide hardcoded badge `#expertBadge` by default (`style="display: none;"`).
- Update `initCoachListener(match)` to subscribe to `chats/{match.name}/coachDialogue` and manage `currentCoachChatUnsubscribe`.
- Update `sendExpertMessage()` to write to the active match's subcollection.
- Update `openChatForMatch(match)` to activate the coach sheet for every match.
- Update `closeChat()` to unsubscribe and clean up the coach sheet.
- Update `toggleExpertSheet()` to dismiss the unread badge when opened.

### 2. [reset_db.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/reset_db.py)
- Update reset script to recognize `chats/*/coachDialogue` subcollections.
- Add `--wipe-coach` CLI flag and interactive prompt options.

---

## Verification Plan

### Automated / API Verification
1. Run a script to verify the legacy `coachDialogue` collection is purged.
2. Test writing a message to `chats/{matchName}/coachDialogue` via Firestore REST API and verifying query response.

### Browser / Functional Verification
1. Open the web app on `http://localhost:8080/`.
2. Click on a match (e.g., Aubrey, Lauren, or another match).
3. Confirm the Coach & Client Dialogue drawer is present and collapsed at the bottom.
4. Expand the drawer: verify clean, minimalist empty feed ready for typing.
5. Send a coach message; verify it persists to Firestore and displays in the feed.
6. Close chat and open a different match; verify coach dialogue is scoped to the second match and doesn't bleed between matches.
7. Verify keyboard docking and toggle interactions.

---

## Progress Checklist

- [x] **Step 1:** Purge legacy top-level `coachDialogue` Firestore records.
- [x] **Step 2:** Update `reset_db.py` to support per-match `coachDialogue` paths and optional flags.
- [x] **Step 3:** Implement universal per-match coach listener, unread badge logic, and sending in `index.html`.
- [x] **Step 4:** Verify multi-match coach chat isolation, persistence, and drawer behavior in browser.
- [x] **Step 5:** Finalize and mark implementation complete.
