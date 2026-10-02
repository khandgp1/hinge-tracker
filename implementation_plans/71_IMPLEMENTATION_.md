# 71 — Real-Time Coach Splash Screen Lock via Firebase Firestore

## Goal

Implement a real-time lock overlay feature for the Coach view (`?role=coach`). When a Firebase Firestore flag (`settings/coach_lock` -> `locked: true`) is active, the coach's screen displays an unskippable splash animation ([`splash.mp4`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/splash.mp4)) centered over the regular app, blocking any interaction so the coach knows not to use the app at that time.

Additionally, provide [`COACH_LOCK_PROMPT.md`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/COACH_LOCK_PROMPT.md) documenting direct Firestore REST API `curl` commands to easily lock, unlock, and query the lock status.

---

## Architectural & Design Specifications

1. **Firestore Flag & Schema**:
   - Collection: `settings`
   - Document ID: `coach_lock`
   - Document Fields:
     ```json
     {
       "locked": true,
       "updatedAt": "2026-10-02T15:40:00.000Z"
     }
     ```

2. **Role Scoping**:
   - **Coach View (`currentRole === 'coach'`)**:
     - Listens to `db.collection('settings').doc('coach_lock')` in real-time via `onSnapshot`.
     - When `locked === true`, displays the splash overlay and starts continuous playback.
     - When `locked === false` (or document does not exist), smoothly hides the overlay and pauses/resets the video.
   - **Client View (`currentRole === 'client'`)**:
     - The overlay is never shown; client operations remain completely unimpeded.

3. **Overlay & Video Presentation**:
   - **Backdrop**: Full-viewport cover (`position: fixed; inset: 0; z-index: 999999; pointer-events: all; display: flex; align-items: center; justify-content: center; background: transparent;`).
   - **Underlying App Visibility**: Transparent background keeps the regular app interface visible behind the video while completely blocking touch/click/scroll events.
   - **Video Element**:
     - Asset: [`splash.mp4`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/splash.mp4) (square 1:1 aspect ratio).
     - Dimensions: ~320px–360px max width/height with responsive scaling (`width: min(340px, 80vw); aspect-ratio: 1 / 1;`).
     - Styling: Smooth rounded corners (`border-radius: 20px;`), subtle drop shadow (`box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);`), and smooth fade transition (`opacity`, `transition: opacity 0.3s ease`).
     - Content: Pure video animation with no extra text or buttons.
     - Playback properties: `playsinline`, `muted`, `loop`, `autoplay`.

4. **AI Prompt / Documentation**:
   - Create [`COACH_LOCK_PROMPT.md`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/COACH_LOCK_PROMPT.md) with copy-pasteable `curl` commands to:
     - **Lock Coach View**: `PATCH .../settings/coach_lock` setting `locked: true`.
     - **Unlock Coach View**: `PATCH .../settings/coach_lock` setting `locked: false`.
     - **Check Status**: `GET .../settings/coach_lock` reading current state.

---

## Proposed Changes

### 1. [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Add CSS styles for `#coachSplashOverlay` and `#coachSplashVideo`:
  - Full-screen transparent interceptor with `z-index: 999999` and `pointer-events: all`.
  - Centered video card with rounded corners, subtle shadow, and fade transition.
- Add HTML markup for the coach splash container:
  ```html
  <div id="coachSplashOverlay" class="coach-splash-overlay" style="display: none;" aria-hidden="true">
    <video id="coachSplashVideo" class="coach-splash-video" src="splash.mp4" playsinline muted loop preload="auto"></video>
  </div>
  ```
- Add JavaScript logic in `index.html`:
  - Initialize `initCoachLockListener()` when `currentRole === 'coach'`.
  - Attach Firestore `onSnapshot` to `db.collection('settings').doc('coach_lock')`.
  - On update, handle video playback (`video.play().catch(...)`) and smooth fade in/out.

### 2. [`COACH_LOCK_PROMPT.md`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/COACH_LOCK_PROMPT.md)
- Provide exact REST API `curl` commands using the project ID `hinge-tracker-coach` and API key.

---

## Implementation Checklist

- [x] **Step 1: Document Firestore Control Commands**
  - [x] Create [`COACH_LOCK_PROMPT.md`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/COACH_LOCK_PROMPT.md) with `curl` commands for lock, unlock, and status inspection.

- [x] **Step 2: Add Overlay Markup & Styles to `index.html`**
  - [x] Add `#coachSplashOverlay` and `#coachSplashVideo` CSS styles (transparent blocking overlay, centered 1:1 rounded video with subtle shadow).
  - [x] Add `#coachSplashOverlay` DOM element before `</body>`.

- [x] **Step 3: Implement Firestore Real-Time Listener**
  - [x] Add `initCoachLockListener()` restricted to `currentRole === 'coach'`.
  - [x] Handle `locked: true` -> show overlay, play muted looping video.
  - [x] Handle `locked: false` (or deleted) -> fade out overlay, pause & rewind video.

- [x] **Step 4: End-to-End Validation**
  - [x] Test via REST API: Lock coach view -> verify splash animation displays and loops on Coach view (`http://localhost:8080/?role=coach`).
  - [x] Test interaction blocking: Verify coach cannot interact with or click buttons in the app behind the video.
  - [x] Test Client view (`http://localhost:8080/`): Verify client view is unaffected and fully interactive when locked is true.
  - [x] Test Unlock via REST API: Unlock coach view -> verify overlay immediately dismisses and restores coach access.
