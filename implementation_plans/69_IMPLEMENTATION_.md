# 69 — Count Unseen Client Messages in Coach & Client Dialogue Badge

## Goal

Enhance the numeric badge (`#expertBadge`) on the collapsed **Coach & Client Dialogue** bottom sheet so that it also counts **messages the client sent to the coach that have not yet been seen by the coach**:
- **On the Coach Side** (`?role=coach`):
  Counts all client dialogue messages that have not yet been seen by the coach (`d.sender === 'client' && getMillis(d.ts) > getMillis(coachLastReadCoachAt)`).
- **On the Client Side**:
  Counts both incoming coach advice waiting to be reviewed (`d.sender === 'coach' && getMillis(d.ts) > getMillis(clientLastReadCoachAt)`) **and** outgoing client dialogue messages that have not yet been seen by the coach (`d.sender === 'client' && getMillis(d.ts) > getMillis(coachLastReadCoachAt)`).
- As soon as the coach expands the dialogue drawer, `coachLastReadCoachAt` updates in Firestore, automatically clearing those messages from the unseen count on both sides.
- Strictly scoped to the dialogue stream (`coachDialogue`), completely separate from the main Hinge chat messages.

---

## Design Decisions

1. **Unseen Client Message Definition**:
   A message sent by the client (`d.sender === 'client'`) is considered "unseen by the coach" if its timestamp is strictly greater than `coachLastReadCoachAt` on the match document (or if `coachLastReadCoachAt` has not yet been initialized).

2. **Role-Based Badge Calculation**:
   - In `initCoachListener(match)`:
     ```javascript
     const activeMatchData = matchesData.find(m => m.name === match.name) || match;
     const clientLastRead = activeMatchData.clientLastReadCoachAt;
     const coachLastRead = activeMatchData.coachLastReadCoachAt;

     const unreadDocs = snapshot.docs.filter(doc => {
       const d = doc.data();
       if (currentRole === 'coach') {
         // Coach sees client messages that coach has not seen yet
         return d.sender === 'client' && getMillis(d.ts) > getMillis(coachLastRead);
       } else {
         // Client sees:
         // 1. Coach messages client hasn't reviewed yet
         const coachUnread = d.sender === 'coach' && getMillis(d.ts) > getMillis(clientLastRead);
         // 2. Client messages coach hasn't seen yet
         const clientUnseenByCoach = d.sender === 'client' && getMillis(d.ts) > getMillis(coachLastRead);
         return coachUnread || clientUnseenByCoach;
       }
     });
     ```

3. **Real-Time Cross-Device Synchronization**:
   - When the client sends a message, `lastClientMessageAt` is recorded in Firestore.
   - When the coach expands the dialogue sheet (`toggleExpertSheet`), `coachLastReadCoachAt` updates via `markCoachDialogueAsRead`.
   - The live Firestore snapshot listener on `matches` and `coachDialogue` instantly syncs across devices, reducing the badge count automatically once the coach views the dialogue.

---

## Proposed Changes

### 1. Update `initCoachListener` in [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Replace single `targetSender` filter with comprehensive unseen message evaluator:
  - Coach counts: `d.sender === 'client' && getMillis(d.ts) > getMillis(coachLastRead)`
  - Client counts: `(d.sender === 'coach' && getMillis(d.ts) > getMillis(clientLastRead)) || (d.sender === 'client' && getMillis(d.ts) > getMillis(coachLastRead))`
- Display count in `#expertBadge` when `sheetState === 'collapsed'` and `unreadDocs.length > 0`.
- Hide badge when `sheetState === 'open'` or `unreadDocs.length === 0`.

---

## Implementation Checklist

- [ ] **Step 1: Update Unseen Count Calculation in `initCoachListener`**
  - [ ] Support counting client messages unseen by coach on both client and coach sides.
  - [ ] Preserve coach advice unread counting for the client.
  - [ ] Ensure historical messages without new timestamps are handled cleanly.

- [ ] **Step 2: Verification & Live Cross-Device Testing**
  - [ ] Client sends message in dialogue: verify badge displays count on client side while sheet is collapsed.
  - [ ] Check coach side: verify badge displays count on coach side.
  - [ ] Coach expands drawer: verify badge clears on coach side.
  - [ ] Verify client side reflects that coach has seen the message (count drops accordingly).
