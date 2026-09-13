# Implementation Plan 32 – Prevent iOS Keyboard Auto-Zoom & Lock 50/50 Dual Chat Viewport

## Overview
When focusing `#expertInput` on mobile Safari, Aubrey's top chat was pushed completely off-screen and only the Coach Dialogue was visible. 

Investigation identified two interrelated root causes:
1. **iOS Safari Auto-Zoom**: `#expertInput` had `font-size: 13.5px`. Mobile Safari automatically zooms and pans the page downward when focusing any input with font size under 16px, pushing the top chat out of the viewport.
2. **Layout vs Visual Viewport Disconnect**: `#chatOverlay` was fixed to `100dvh` and used `padding-bottom: ${offset}px`. When Safari scrolled/panned the visual viewport down, `#chatOverlay` remained pinned at layout `top: 0`, leaving Aubrey's top chat in the hidden area above the screen.

This plan resolves both issues so that when the keyboard opens, the viewport remains un-zoomed and `#chatOverlay` matches the visible viewport precisely, cleanly presenting the 50/50 split between Aubrey chat and Coach Dialogue.

---

## User Review Required

> [!IMPORTANT]
> - **Input Font Size Updated to 16px**: `.expert-input-field` font size is increased from `13.5px` to `16px`. This is the standard iOS threshold that completely disables Safari's native auto-zoom.
> - **Direct Viewport Docking**: When the keyboard opens, `#chatOverlay` height and top are locked directly to `window.visualViewport.height` and `window.visualViewport.offsetTop` rather than adding large bottom padding.
> - **50/50 Split Maintained**: Aubrey's chat pane and the Coach Dialogue sheet each cleanly occupy 50% of the visible space above the soft keyboard.

---

## Proposed Changes

### Styling & Layout

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Update Input Font Size**:
   ```css
   .expert-input-field {
     flex: 1;
     min-height: 38px;
     max-height: 100px;
     background: rgba(255, 255, 255, 0.08);
     border: 1px solid rgba(255, 255, 255, 0.15);
     border-radius: 19px;
     padding: 8px 14px;
     color: #ffffff;
     font-size: 16px; /* Prevents iOS Safari auto-zoom */
     font-family: inherit;
     ...
   }
   ```

2. **Disable Transition During Keyboard Mode**:
   ```css
   .chat-overlay.keyboard-active .expert-sheet {
     transition: none;
   }
   ```

3. **Update `syncVisualViewport()` in JavaScript**:
   ```javascript
   function syncVisualViewport() {
     vpScheduled = false;
     if (!window.visualViewport) return;
     const chatOverlay = document.getElementById('chatOverlay');
     if (!chatOverlay || !chatOverlay.classList.contains('active')) return;

     const vpHeight = window.visualViewport.height;
     const vpOffsetTop = window.visualViewport.offsetTop || 0;
     const winHeight = window.innerHeight;
     const keyboardHeight = Math.max(0, winHeight - vpHeight - vpOffsetTop);

     if (keyboardHeight > 100 || document.activeElement === expertInput) {
       chatOverlay.classList.add('keyboard-active');
       chatOverlay.style.top = `${vpOffsetTop}px`;
       chatOverlay.style.height = `${vpHeight}px`;
       chatOverlay.style.paddingBottom = '0px';
     } else {
       chatOverlay.classList.remove('keyboard-active');
       chatOverlay.style.top = '0px';
       chatOverlay.style.height = '';
       chatOverlay.style.paddingBottom = '0px';
     }

     window.scrollTo(0, 0);
     chatOverlay.scrollTop = 0;

     const chatBody = document.getElementById('chatBody');
     const expertSheetBody = document.getElementById('expertSheetBody');
     if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
     if (expertSheetBody) expertSheetBody.scrollTop = expertSheetBody.scrollHeight;
   }
   ```

4. **Reset Viewport Styles on Blur and Close**:
   In `closeChat()` and `expertInput` blur handler, ensure `chatOverlay.style.top = ''` and `chatOverlay.style.height = ''` are reset.

---

## Verification Plan

### Mobile Viewport & Device Testing
1. **Open Mobile View**:
   - Access `http://localhost:8089/index.html` on iPhone / mobile emulation.
   - Tap into Aubrey match.
   - Open Coach Dialogue drawer.
2. **Keyboard Focus Test**:
   - Tap into `#expertInput` ("Ask coach for advice...").
   - Confirm Safari does **not** auto-zoom in.
   - Confirm Aubrey chat pane is fully visible at the top (50% of the visible area).
   - Confirm Coach Dialogue is fully visible below it (50% of the visible area).
   - Confirm Coach input bar is docked directly above the keyboard.
3. **Keyboard Dismissal Test**:
   - Tap outside or blur the input.
   - Confirm the overlay returns cleanly to full height and default sheet proportions.

---

## Progress Checklist

- [x] **1. CSS Updates in `index.html`**
  - [x] Set `.expert-input-field` font-size to `16px`.
  - [x] Add `transition: none` to `.chat-overlay.keyboard-active .expert-sheet`.
- [x] **2. JavaScript Viewport Docking in `index.html`**
  - [x] Update `syncVisualViewport()` to lock `chatOverlay.style.top` and `chatOverlay.style.height` to `visualViewport`.
  - [x] Add `window.scrollTo(0, 0)` and `chatOverlay.scrollTop = 0` clamping.
  - [x] Ensure cleanup on `closeChat()` and blur.
- [ ] **3. Verification**
  - [ ] Verify both Aubrey chat and Coach chat share 50/50 visible space when keyboard is open.
  - [ ] Verify zero unwanted auto-zoom on input focus.
