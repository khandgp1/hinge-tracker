# 35 — Coach & Client Dialogue: Firebase Real-Time Chat

## Goal

Replace the current hardcoded/simulated coach bottom sheet with a live, persistent,
two-user conversation backed by Firebase Firestore. DA (coach) and the client each
open the app on separate devices; messages sync in real time with no backend code
required beyond the Firebase JS SDK.

---

## Design Decisions (already aligned)

| Concern | Decision |
|---|---|
| Persistence | Firebase Firestore |
| Role identification | URL param `?role=coach` = DA; no param = client |
| Message alignment | Coach (DA) always **left**, Client always **right** |
| Typing indicator | None |
| UI placement | Keep existing bottom-sheet drawer inside Aubrey chat view |
| Aubrey context for DA | DA sees Aubrey chat thread (read-only) above the dialogue |

---

## Manual Steps Required From You

> **PAUSE POINT 1 — Create Firebase project**
> 1. Go to https://console.firebase.google.com
> 2. Click **Add project** -> name it `hinge-tracker-coach` (or similar)
> 3. Disable Google Analytics (not needed)
> 4. Once created, click **Web** (`</>`) to add a web app
> 5. Register app name `hinge-coach`, skip Firebase Hosting
> 6. Copy the **firebaseConfig** object shown — you'll paste it in Step 3

> **PAUSE POINT 2 — Enable Firestore**
> 1. In the Firebase console sidebar -> **Build -> Firestore Database**
> 2. Click **Create database**
> 3. Choose **Start in test mode** (we can lock it down later)
> 4. Pick any region (us-east1 is fine)
> 5. Confirm — Firestore is now live

> **PAUSE POINT 3 — Paste firebaseConfig into index.html**
> After I add the placeholder block in `index.html`, you paste your copied
> `firebaseConfig` object into that block, then commit and push to GitLab.

---

## Proposed Changes

### index.html

**Phase A — Firebase setup:**
- Add Firebase JS SDK v9 compat CDN scripts (`app`, `firestore`) in `<head>`
- Add `firebaseConfig` placeholder block + init code (you fill in at PAUSE POINT 3)

**Phase B — Role detection:**
- On page load: `new URLSearchParams(window.location.search).get('role')`
- `'coach'` -> `currentRole = 'coach'`, `currentName = 'DA'`
- default -> `currentRole = 'client'`, `currentName = 'Me'`

**Phase C — Firestore message model:**
```
Collection: coachDialogue
Fields per doc:
  sender:  'coach' | 'client'
  name:    'DA' | 'Me'
  text:    string
  ts:      serverTimestamp()
```

**Phase D — Real-time listener:**
- Replace static `expertDialogueData` array + `renderExpertChat()` with a
  Firestore `onSnapshot` on `coachDialogue` ordered by `ts asc`
- Each snapshot update re-renders the feed instantly on both devices

**Phase E — Send logic:**
- `sendExpertMessage()` calls `addDoc` to write to Firestore
- Remove the simulated auto-reply `setTimeout` entirely

**Phase F — DA coach view: Aubrey context:**
- If `role === 'coach'`, render the Aubrey chat thread (read-only, condensed)
  above the coach dialogue feed inside the bottom sheet, with a subtle divider
  labeled "Aubrey Thread (context)"

**Phase G — Visual identity:**
- Coach (DA) bubbles: left-aligned, warm amber/gold color
- Client bubbles: right-aligned, existing style
- Sender label above each bubble: `DA` or `Me`
- Input placeholder:
  - Coach: `"Type advice for client..."`
  - Client: `"Ask your coach..."`

---

## Checklist

### Manual (You)
- [ ] Create Firebase project in console (PAUSE POINT 1)
- [ ] Enable Firestore in test mode (PAUSE POINT 2)
- [ ] Copy firebaseConfig object
- [ ] Paste firebaseConfig into index.html placeholder (PAUSE POINT 3)
- [ ] Push to GitLab Pages
- [ ] Share DA's URL: `[your-gitlab-pages-url]?role=coach`

### Code (AI)
- [ ] Add Firebase SDK CDN tags to `<head>`
- [ ] Add firebaseConfig placeholder block + Firebase init
- [ ] Add role detection logic on page load
- [ ] Replace `expertDialogueData` array + static render with Firestore `onSnapshot`
- [ ] Update `sendExpertMessage()` to use `addDoc`
- [ ] Remove simulated auto-reply `setTimeout`
- [ ] Add Aubrey context block (read-only) for coach role
- [ ] Update bubble alignment + colors for coach vs client roles
- [ ] Update input placeholder text based on role
- [ ] Update sender labels (`DA` / `Me`)

---

## Verification Plan

1. Open app normally (client view) on Device A -> send a message
2. Open `?role=coach` on Device B (or incognito) -> message appears in real time
3. DA replies from coach view -> message appears on client view in real time
4. Refresh both pages -> full conversation history persists (Firestore)
5. DA's view shows Aubrey chat thread above the dialogue (read-only)
