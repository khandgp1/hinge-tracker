# Implementation Plan 33 – 45/55 Split for Dual Chat View When Mobile Keyboard is Open

## Overview
Following the successful fix for the mobile keyboard viewport docking and auto-zoom, the user requested tuning the keyboard-active vertical proportion from 50/50 to a **45% (top chat) / 55% (bottom Coach chat) split**, matching the exact proportion used when the keyboard is closed (Plan 29).

This implementation plan details the CSS changes to adjust the keyboard-active flex distribution so that:
- **Top chat** (`#chatBody`): receives **45%** of the visible space above the keyboard.
- **Bottom Coach chat** (`#expertBottomSheet`): receives **55%** of the visible space above the keyboard.

---

## Current vs Proposed Layout (Keyboard Active)

### Current Layout (Plan 31 / 32)
- Top chat (`.chat-overlay.keyboard-active .chat-body`):
  - `flex: 50 1 0%`
  - `min-height: 70px`
- Bottom Coach chat (`.chat-overlay.keyboard-active .expert-sheet.open, ...`):
  - `flex: 50 1 0%`
  - `min-height: 70px`

### Proposed Layout (Plan 33 - 45/55 Split)
- Top chat (`.chat-overlay.keyboard-active .chat-body`, `.chat-overlay.sheet-open.keyboard-active .chat-body`):
  - `flex: 45 1 0%`
  - `min-height: 60px`
- Bottom Coach chat (`.chat-overlay.keyboard-active .expert-sheet.open, .half, .full`):
  - `flex: 55 1 0%`
  - `min-height: 80px`

Because both elements have `flex-basis: 0%`, the available height inside `#chatOverlay` (locked directly to `window.visualViewport.height`) is allocated in an exact 45% to 55% proportion.

---

## User Review Required

> [!IMPORTANT]
> - **Consistent Proportions**: The dual-chat screen maintains a consistent 45% / 55% ratio whether the keyboard is closed or open.
> - **All Previous Viewport Fixes Maintained**: The 16px input font (zero auto-zoom) and direct `window.visualViewport` docking remain intact.
> - **Smooth In-Drawer Scrolling**: Both chat bodies continue to scroll independently with momentum.

---

## Proposed Changes

### Styling & Layout

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

Update lines ~548–566 in `index.html`:

```css
/* Reclaim Space & 45% / 55% Flex Split when Keyboard is Active */
.chat-overlay.keyboard-active .chat-header {
  height: 42px;
  padding: 6px 14px;
}

.chat-overlay.keyboard-active .chat-body,
.chat-overlay.sheet-open.keyboard-active .chat-body {
  height: auto;
  flex: 45 1 0%;
  min-height: 60px;
  padding: 10px 14px;
  padding-top: 48px;
}

.chat-overlay.keyboard-active .expert-sheet.open,
.chat-overlay.keyboard-active .expert-sheet.half,
.chat-overlay.keyboard-active .expert-sheet.full {
  height: auto;
  flex: 55 1 0%;
  flex-basis: 0%;
  flex-shrink: 1;
  min-height: 80px;
}
```

---

## Verification Plan

### Mobile Viewport & Device Testing
1. **Device Testing**:
   - Access `http://<your-local-ip>:8089/index.html` on iPhone / mobile browser.
   - Open Aubrey chat and expand Coach Dialogue drawer.
   - Observe baseline 45% / 55% split without keyboard.
2. **Keyboard Focus Test**:
   - Tap into `#expertInput` ("Ask coach for advice...").
   - Confirm virtual keyboard appears with no auto-zoom.
   - Verify Aubrey chat occupies 45% of the visible area above the keyboard.
   - Verify Coach chat occupies 55% of the visible area above the keyboard.
3. **Feed Usability**:
   - Confirm both chat feeds scroll smoothly and recent messages stay pinned at the bottom.
4. **Keyboard Dismissal**:
   - Tap outside or blur the input.
   - Confirm smooth transition back to the default no-keyboard 45/55 sheet view.

---

## Progress Checklist

- [x] **1. CSS Layout Updates in `index.html`**
  - [x] Update `.chat-overlay.keyboard-active .chat-body` to `flex: 45 1 0%`.
  - [x] Update `.chat-overlay.keyboard-active .expert-sheet` rules to `flex: 55 1 0%`.
- [ ] **2. Verification & Validation**
  - [ ] Verify 45/55 proportion on iPhone with keyboard active.
  - [ ] Verify seamless transition between keyboard open and closed states.
