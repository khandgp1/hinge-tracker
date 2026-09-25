# 44 — Matches Persistence via Firebase Firestore & Real-Time Sync

## Goal

Replace client-only `localStorage` match storage with **Firebase Firestore** as the single source of truth for all matches (default demo matches and uploaded matches). 

This update provides:
1. **Real-Time Cross-Device Synchronization**: When a match is uploaded on a phone or laptop, all connected devices (including the Coach view) update instantly via Firestore `onSnapshot`.
2. **Instant Offline Caching**: Uses Firestore's built-in IndexedDB offline persistence (`enablePersistence`), ensuring matches load immediately on launch, even with poor cellular service.
3. **Automated First-Time Seeding**: On initial load, if the `matches` collection is empty, the app automatically seeds the baseline default matches (`Aubrey`, `Isadora`, `Anshara`, `Rachel`, and `Mital`) with chronological timestamps.
4. **Cross-Device Deduplication**: Newly uploaded screenshots are checked against all live Firestore records (by name and visual perceptual aHash), preventing duplicate entries across different devices.
5. **Clean Local Storage Removal**: Completely deprecates `localStorage.getItem('hinge_custom_matches')` to eliminate "two sources of truth" bugs.

---

## User Review Required

> [!NOTE]
> **No New Firebase Setup Required**:
> The app already contains a working Firebase configuration connected to the `hinge-tracker-coach` project (currently used for the coach-client chat). Matches will live in a top-level `matches` collection within this same Firestore database.

> [!NOTE]
> **Fresh Start from Firestore**:
> As agreed in the design interview, any previously uploaded matches stored exclusively in local browser `localStorage` will be cleared/ignored in favor of a clean, consistent state seeded directly into Firestore.

---

## Data Model & Collection Structure

### Collection: `matches`

Each document in `matches` represents a match entry:

```json
{
  "name": "Aubrey",
  "preview": "Start the chat with Aubrey",
  "isMatchedNotice": false,
  "image": "assets/aubrey.jpg",
  "hash": "1100000110000000100110000001100010010000101100001110000111111111",
  "createdAt": "2026-09-25T17:30:00Z"
}
```

* **`name`** *(string)*: Name of the match (e.g. `"Aubrey"`).
* **`preview`** *(string)*: Subtitle preview text (e.g. `"You matched with Isadora"` or last message snippet).
* **`isMatchedNotice`** *(boolean)*: Controls italicized/gray styling for new match notices.
* **`image`** *(string)*: Image source. For default seed matches, relative asset paths (e.g. `"assets/aubrey.jpg"`); for newly uploaded matches, compact 120×120 Base64 JPEG data URL (`"data:image/jpeg;base64,..."`).
* **`hash`** *(string)*: 64-bit perceptual luminance hash (aHash) for visual avatar deduplication.
* **`createdAt`** *(Firestore Timestamp)*: Server timestamp (`FieldValue.serverTimestamp()`) used for descending chronological ordering.

---

## Architecture & Synchronization Flow

```
Mobile Safari / Desktop Client
              │
              │ 1. Upload Screenshot & OCR Slicing
              ▼
       Native Vision Backend
              │
              │ 2. Return detected names & 120x120 Base64 avatars
              ▼
   Import Review Modal (Client)
              │
              │ 3. Deduplicate against live in-memory matches (from Firestore)
              ▼
   User Confirms "Import N Matches"
              │
              │ 4. db.batch() write to Firestore
              ▼
    Firestore Cloud Database (`matches` collection)
              │
              │ 5. onSnapshot push to all clients
              ▼
   ┌───────────────────────┬───────────────────────┐
   │                       │                       │
   ▼                       ▼                       ▼
Mobile Web App        Desktop Web App          Coach View
(Auto-renders feed)   (Auto-renders feed)  (Auto-renders feed)
```

---

## Proposed Changes

### Frontend Integration

#### [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Enable Firestore Offline Persistence**:
   - Call `db.enablePersistence({ synchronizeTabs: true }).catch(...)` right after initializing Firestore.
   - Gracefully catch `failed-precondition` (multiple tabs open) and `unimplemented` (unsupported browsers).

2. **Remove `localStorage` Match Loading**:
   - Remove `loadSavedMatches()`, `customMatches`, and reading/writing `'hinge_custom_matches'`.
   - Maintain `matchesData` in memory as the live view model populated exclusively by Firestore.

3. **Implement Auto-Seeding**:
   - Query `db.collection('matches').limit(1).get()`.
   - If empty, execute a batch write (`db.batch()`) inserting `defaultMatchesData` (`Aubrey`, `Isadora`, `Anshara`, `Rachel`, `Mital`) with staggered timestamps so `Aubrey` stays at the top.

4. **Attach Live Firestore Listener**:
   - Subscribe to `db.collection('matches').orderBy('createdAt', 'desc').onSnapshot(...)`.
   - Update `matchesData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))`.
   - Call `renderMatchesList()` automatically on every snapshot.

5. **Update Import Modal Confirmation**:
   - In `importConfirmBtn.addEventListener('click', ...)`:
     - Replace `localStorage.setItem` with a `db.batch()` write committing each checked match to `db.collection('matches')`.
     - Set `createdAt: firebase.firestore.FieldValue.serverTimestamp()`.
     - Close import modal upon commit.

6. **Cross-Device Deduplication**:
   - Ensure `isDuplicateMatch(candidateName, candidateHash)` checks against the live `matchesData` populated from Firestore.

---

## Verification Plan

### Automated / Browser Verification
- Open the web app on `http://localhost:8080` (or ngrok static tunnel).
- Open browser developer tools / console:
  1. Confirm Firestore connects cleanly without permission or index errors.
  2. Confirm first-run seeding populates the 5 default matches in Firestore.
  3. Verify the Matches feed displays the default list correctly.
  4. Perform an import of a test screenshot (`media_1789926022466.jpg` or via UI upload):
     - Verify new matches appear in the review sheet.
     - Confirm importing writes to Firestore and the feed updates immediately.
  5. Open a second browser tab (or mobile device via ngrok static domain):
     - Confirm both tabs display identical matches.
     - Upload a match in Tab 1; confirm Tab 2 updates in real time without refreshing.
  6. Refresh the page:
     - Verify all matches persist from Firestore.
     - Disconnect network / simulate offline in DevTools; verify matches still load from IndexedDB cache.

---

## Implementation Checklist

- [x] **Phase 1: Enable Firestore Offline Persistence & Clean LocalStorage**
  - [x] Add `db.enablePersistence({ synchronizeTabs: true })` in [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html).
  - [x] Remove `loadSavedMatches()` and references to `localStorage.getItem('hinge_custom_matches')`.
- [x] **Phase 2: Database Initialization & Seeding**
  - [x] Implement seed check: query `db.collection('matches')`.
  - [x] If collection is empty, write default matches (`Aubrey`, `Isadora`, `Anshara`, `Rachel`, `Mital`) in batch.
- [x] **Phase 3: Real-Time Listener & UI Rendering**
  - [x] Attach `db.collection('matches').orderBy('createdAt', 'desc').onSnapshot(...)`.
  - [x] Map snapshot documents to `matchesData` and invoke `renderMatchesList()`.
- [x] **Phase 4: Match Importer Firestore Integration**
  - [x] Update import review deduplication against live Firestore `matchesData`.
  - [x] Update `importConfirmBtn` to write selected matches to Firestore in batch with `serverTimestamp()`.
  - [x] Remove `localStorage.setItem('hinge_custom_matches', ...)`.
- [x] **Phase 5: Multi-Tab & Multi-Device Verification**
  - [x] Verify initial seed creation in Firestore.
  - [x] Verify real-time sync across two browser windows.
  - [x] Verify offline persistence via simulated offline network state.
