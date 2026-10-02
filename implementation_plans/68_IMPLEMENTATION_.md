# 68 — Restore and Fix Unread Number Badge on Collapsed Coach Dialogue

## Goal

Ensure the numeric unread badge (`#expertBadge`) on the collapsed **Coach & Client Dialogue** bottom sheet accurately displays the number of unread messages both upon opening a chat and in real time:
- Calculates unread count from Firestore dialogue history based on the user's last read timestamp (`clientLastReadCoachAt` for client, `coachLastReadCoachAt` for coach).
- Resolves the bug where `!isInitialLoad` skipped showing the badge when navigating into a match from the match list.
- Supports bidirectional role tracking (counts coach advice for client; counts client messages for coach).
- Automatically clears the badge and resets the count when the user expands the dialogue bottom sheet.

---

## Root Cause Analysis

In [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html#L2050-L2066):
1. **Initial Load Omission**:
   ```javascript
   if (!isInitialLoad && sheetState === 'collapsed') {
     const addedCoachDocs = snapshot.docChanges().filter(c => c.type === 'added' && c.doc.data().sender === 'coach');
     ...
   }
   ```
   When tapping into a chat, `isInitialLoad` is `true`. The code bypassed evaluating unread messages on initial load, meaning the badge only ever incremented if a message arrived while the user was *already* sitting on that chat screen with the sheet collapsed.
2. **Role Hardcoding**:
   Checking `doc.data().sender === 'coach'` meant the badge never worked in Coach View (`?role=coach`) when clients asked questions.
3. **Disconnected from Firestore Read State**:
   The count was tracked via a volatile JS variable (`coachUnreadCount`) instead of checking timestamps against `clientLastReadCoachAt` or `coachLastReadCoachAt`.

---

## Proposed Changes

### 1. Update `initCoachListener(match)` in [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Determine target sender and last read timestamp:
  ```javascript
  const otherRole = currentRole === 'coach' ? 'client' : 'coach';
  const lastReadAt = currentRole === 'coach' ? match.coachLastReadCoachAt : match.clientLastReadCoachAt;
  ```
- Filter unread messages across both initial snapshot and subsequent updates:
  ```javascript
  const unreadDocs = snapshot.docs.filter(doc => {
    const d = doc.data();
    return d.sender === otherRole && getMillis(d.ts) > getMillis(lastReadAt);
  });
  ```
- Update badge display:
  - If `sheetState === 'collapsed'` and `unreadDocs.length > 0`:
    - Show `#expertBadge` with `badge.textContent = unreadDocs.length;`
    - `badge.style.display = 'inline-block';`
  - Otherwise (if `sheetState === 'open'` or `unreadDocs.length === 0`):
    - `badge.textContent = '0';`
    - `badge.style.display = 'none';`

### 2. Badge Dismissal in `toggleExpertSheet()`
- When transitioning to `'open'`:
  - `badge.style.display = 'none';`
  - `badge.textContent = '0';`
  - Call `markCoachDialogueAsRead(currentActiveMatch)` to persist read state in Firestore.

---

## Implementation Checklist

- [x] **Step 1: Fix Unread Count Calculation in `initCoachListener`**
  - [x] Remove `!isInitialLoad` restriction so unread messages are counted upon entering the chat.
  - [x] Implement bidirectional sender check (`otherRole`).
  - [x] Evaluate unread count using `getMillis(doc.data().ts) > getMillis(lastReadAt)`.
  - [x] Display `#expertBadge` with numeric count when `sheetState === 'collapsed'`.

- [x] **Step 2: Sheet Expansion & Dismissal Handling**
  - [x] Verify `toggleExpertSheet()` resets badge to `0` and hides it when opened.
  - [x] Confirm `markCoachDialogueAsRead()` updates Firestore timestamp so re-entering chat maintains clean read state.

- [x] **Step 3: Verification & Cross-Role Testing**
  - [x] Send advice as coach: open client chat screen -> verify numeric badge (e.g., `1`) appears on collapsed drawer.
  - [x] Expand drawer: verify badge clears.
  - [x] Test real-time message arrival while drawer is collapsed.
  - [x] Test coach view receiving client messages.
