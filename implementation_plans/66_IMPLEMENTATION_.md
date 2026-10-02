# 66 — Bidirectional Coach Message Unread Dot on Match List

## Goal

Provide a real-time unread indicator on the match list when new messages are exchanged between coach and client. Specifically:
- When the **coach** sends advice, the **client** sees a sleek berry/plum dot badge overlaid on the top-right corner of that match's avatar on the match list.
- When the **client** asks a question, the **coach** (in coach view) sees the unread dot badge on that match's avatar.
- The indicator clears automatically when the user expands and reviews the **Coach & Client Dialogue** bottom sheet (or immediately if already open).
- Unread status is synced in real-time via Firestore across devices, scoped to new messages sent forward.

---

## Design Decisions

1. **Avatar Dot Badge Visual Placement & Aesthetics**:
   - Wrap the match avatar in a relative container (`.avatar-wrap`) within `.match-row`.
   - Place a circular badge dot (`.coach-unread-dot`) positioned at the top-right corner of the avatar (`top: 1px; right: 1px;`).
   - Dimensions: ~14px × 14px, colored with Hinge brand plum/berry (`#701A51`), with a 2.5px solid white border (`#ffffff`) and a subtle drop shadow (`0 1px 4px rgba(112, 26, 81, 0.35)`).
   - Animation: Smooth CSS entrance animation (`unreadDotPop 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275)`) so the dot pops cleanly into view when a message arrives without aggressive flashing.

2. **Bidirectional Role-Based Tracking**:
   - **Client View** (`currentRole !== 'coach'`):
     - Displays the unread dot if `match.lastCoachMessageAt` > `match.clientLastReadCoachAt` (or `lastCoachMessageAt` exists and `clientLastReadCoachAt` is unset).
   - **Coach View** (`currentRole === 'coach'`):
     - Displays the unread dot if `match.lastClientMessageAt` > `match.coachLastReadCoachAt` (or `lastClientMessageAt` exists and `coachLastReadCoachAt` is unset).

3. **Firestore Metadata Schema on Matches**:
   - Stored directly on each match document in `db.collection('matches')`:
     - `lastCoachMessageAt`: Timestamp (set when coach sends advice)
     - `lastClientMessageAt`: Timestamp (set when client sends a question)
     - `clientLastReadCoachAt`: Timestamp (set when client opens/views coach dialogue)
     - `coachLastReadCoachAt`: Timestamp (set when coach opens/views coach dialogue)
   - Because [`initFirestoreMatches()`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html#L2593) already subscribes to `matchesCol.orderBy('createdAt', 'desc').onSnapshot()`, any update to these fields automatically and instantly triggers [`renderMatchesList()`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html#L2208) across all open browser sessions and tabs.

4. **Dismissal & Read Trigger Behavior**:
   - When expanding the Coach & Client Dialogue bottom sheet (`toggleExpertSheet()` transitions `sheetState` to `'open'`):
     - Call `markCoachDialogueAsRead(currentActiveMatch)`.
     - Updates `clientLastReadCoachAt` (or `coachLastReadCoachAt`) in Firestore for that match document.
   - If a new message arrives in real-time while the user *already* has the sheet expanded for that active match (`sheetState === 'open'`), immediately update the read timestamp so returning to the match list shows the conversation as read.
   - Matches without new timestamps (historical messages) are treated as read by default, ensuring no false-positive badge spam on older chats.

---

## Proposed Changes

### 1. UI Styling: [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Add CSS rules for `.avatar-wrap` and `.coach-unread-dot`:
  ```css
  .avatar-wrap {
    position: relative;
    display: inline-flex;
    flex-shrink: 0;
    margin-right: 16px;
  }
  .coach-unread-dot {
    position: absolute;
    top: 1px;
    right: 1px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background-color: #701A51;
    border: 2.5px solid #ffffff;
    box-shadow: 0 1px 4px rgba(112, 26, 81, 0.35);
    z-index: 2;
    pointer-events: none;
    animation: unreadDotPop 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }
  @keyframes unreadDotPop {
    0% { transform: scale(0); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
  }
  ```

### 2. Match Rendering: [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Update `renderMatchesList()`:
  - Check whether `item` has an unread coach message for the current role:
    ```javascript
    function hasUnreadCoachMessage(match) {
      if (!match) return false;
      if (currentRole === 'coach') {
        if (!match.lastClientMessageAt) return false;
        if (!match.coachLastReadCoachAt) return true;
        const msgTime = match.lastClientMessageAt.toMillis ? match.lastClientMessageAt.toMillis() : new Date(match.lastClientMessageAt).getTime();
        const readTime = match.coachLastReadCoachAt.toMillis ? match.coachLastReadCoachAt.toMillis() : new Date(match.coachLastReadCoachAt).getTime();
        return msgTime > readTime;
      } else {
        if (!match.lastCoachMessageAt) return false;
        if (!match.clientLastReadCoachAt) return true;
        const msgTime = match.lastCoachMessageAt.toMillis ? match.lastCoachMessageAt.toMillis() : new Date(match.lastCoachMessageAt).getTime();
        const readTime = match.clientLastReadCoachAt.toMillis ? match.clientLastReadCoachAt.toMillis() : new Date(match.clientLastReadCoachAt).getTime();
        return msgTime > readTime;
      }
    }
    ```
  - In match row HTML, wrap `.avatar` with `.avatar-wrap` and conditionally render `<div class="coach-unread-dot" title="New coach advice"></div>`.

### 3. Firestore Read/Write Updates: [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- In `sendExpertMessage()`:
  - When coach sends advice: update match doc in `matches` with `lastCoachMessageAt: firebase.firestore.FieldValue.serverTimestamp()`.
  - When client sends text: update match doc in `matches` with `lastClientMessageAt: firebase.firestore.FieldValue.serverTimestamp()`.
- Add helper function `markCoachDialogueAsRead(match)`:
  - Sets `clientLastReadCoachAt: firebase.firestore.FieldValue.serverTimestamp()` when role is client.
  - Sets `coachLastReadCoachAt: firebase.firestore.FieldValue.serverTimestamp()` when role is coach.
- Call `markCoachDialogueAsRead(currentActiveMatch)`:
  - Inside `toggleExpertSheet()` when opening the sheet.
  - Inside `initCoachListener()` snapshot callback if `sheetState === 'open'`.

---

## Implementation Checklist

- [x] **Step 1: CSS & Match List Avatar Badge**
  - [x] Add `.avatar-wrap` and `.coach-unread-dot` styles with smooth scale-in animation in `index.html`.
  - [x] Update `renderMatchesList()` to wrap avatars in `.avatar-wrap` and evaluate `hasUnreadCoachMessage(match)`.

- [x] **Step 2: Firestore Timestamps & Read Status Sync**
  - [x] Implement `markCoachDialogueAsRead(match)` targeting the active match doc in `matches` collection.
  - [x] Update `sendExpertMessage()` to record `lastCoachMessageAt` (for coach) or `lastClientMessageAt` (for client).
  - [x] Hook `markCoachDialogueAsRead` into `toggleExpertSheet()` when opening the sheet.
  - [x] Auto-mark as read in `initCoachListener()` when `sheetState === 'open'` upon receiving messages.

- [x] **Step 3: Verification & Multi-Session Testing**
  - [x] Test client view (`http://localhost:8080/`) and coach view (`http://localhost:8080/?role=coach`).
  - [x] Send advice as coach: verify unread berry dot appears on client's match list avatar in real-time.
  - [x] Open chat & expand coach dialogue sheet on client: verify unread dot disappears.
  - [x] Send question as client: verify unread dot appears on coach's match list avatar.
  - [x] Open coach dialogue sheet on coach: verify unread dot disappears.
  - [x] Verify historical chats without timestamps remain clean with no erroneous badges.
