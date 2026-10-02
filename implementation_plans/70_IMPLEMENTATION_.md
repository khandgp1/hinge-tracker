# 70 — Align Coach & Client Dialogue Unread Badges Strictly to Incoming Messages

## Goal

Confirm and enforce that the numeric unread badge (`#expertBadge`) on the collapsed **Coach & Client Dialogue** bottom sheet strictly tracks **incoming unreviewed messages** for each respective role:
- **Client Side**: Strictly counts **Coach advice** that has not yet been reviewed by the client (`sender === 'coach' && ts > clientLastReadCoachAt`). The client does *not* see a badge for messages they sent waiting to be seen by the coach.
- **Coach Side**: Strictly counts **Client messages/questions** that have not yet been seen by the coach (`sender === 'client' && ts > coachLastReadCoachAt`).
- **Dismissal**:
  - Expanding the bottom sheet in Client View marks coach advice as read (`clientLastReadCoachAt = serverTimestamp()`) and clears the badge to `0`.
  - Expanding the bottom sheet in Coach View marks client messages as read (`coachLastReadCoachAt = serverTimestamp()`) and clears the badge to `0`.

---

## Design Specifications

1. **Role-Specific Target Filtering**:
   - For `currentRole === 'coach'`:
     - Target sender: `'client'`
     - Evaluation: `d.sender === 'client' && getMillis(d.ts) > getMillis(activeMatchData.coachLastReadCoachAt)`
   - For `currentRole === 'client'`:
     - Target sender: `'coach'`
     - Evaluation: `d.sender === 'coach' && getMillis(d.ts) > getMillis(activeMatchData.clientLastReadCoachAt)`

2. **No Outgoing / Self-Sent Message Badging**:
   - Outgoing messages sent by the current user are completely excluded from the unread badge calculation.
   - The client never sees a badge for their own messages waiting for the coach.
   - The coach never sees a badge for their own advice waiting for the client.

3. **Real-Time Cross-Device Synchronization**:
   - Firestore timestamps (`clientLastReadCoachAt` and `coachLastReadCoachAt`) persist the exact read boundary across tabs and sessions.
   - When either party expands their drawer, the corresponding timestamp updates in Firestore, resetting their badge count to `0`.

---

## Proposed Changes & Validation

### 1. Logic Verification: [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Ensure lines 2050–2075 in `initCoachListener` maintain strict incoming-only filtering:
  ```javascript
  const targetSender = currentRole === 'coach' ? 'client' : 'coach';
  const activeMatchData = matchesData.find(m => m.name === match.name) || match;
  const lastReadAt = currentRole === 'coach' ? activeMatchData.coachLastReadCoachAt : activeMatchData.clientLastReadCoachAt;

  const unreadDocs = snapshot.docs.filter(doc => {
    const d = doc.data();
    return d.sender === targetSender && getMillis(d.ts) > getMillis(lastReadAt);
  });
  ```
- Verify that `clientLastReadCoachAt` is unaffected by client sending messages so outgoing client messages do not alter coach advice unread tracking.

---

## Implementation Checklist

- [x] **Step 1: Verify and Enforce Strict Incoming-Only Filtering**
  - [x] Confirm Client View only badges incoming `coach` advice.
  - [x] Confirm Coach View only badges incoming `client` messages.
  - [x] Ensure neither view badges self-sent messages.

- [x] **Step 2: Cross-Role Verification & Dismissal Testing**
  - [x] Client View test: Send message as client -> verify badge remains 0 / hidden on client side.
  - [x] Coach View test: Verify badge displays count on coach side for the client's message.
  - [x] Coach View test: Expand coach drawer -> verify badge clears to 0 on coach side.
  - [x] Coach View test: Send advice as coach -> verify badge remains 0 / hidden on coach side.
  - [x] Client View test: Verify badge displays count on client side for the coach's advice.
