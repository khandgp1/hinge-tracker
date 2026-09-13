# Implementation Plan 30 – Fix Coach Dialogue Swipe-Up Overscroll & White Screen on Mobile

## Overview
When the Coach & Client Dialogue sheet is open in mobile view, swiping up on the coach dialogue when it is already at the bottom causes a white screen or gap to appear beneath/around the bottom sheet instead of remaining solidly resting at the bottom.

This implementation plan diagnoses the root cause of the mobile rubber-band/scroll-chaining behavior and details the necessary CSS and JavaScript fixes to lock the viewport and contain scrolling within the sheet.

---

## Root Cause Analysis

1. **Scroll Chaining (`overscroll-behavior` missing)**:
   - `.expert-sheet-body` has `-webkit-overflow-scrolling: touch` but does **not** specify `overscroll-behavior: contain` (or `overscroll-behavior-y: contain`).
   - When the user swipes up and the feed is already at its bottom boundary (`scrollTop + clientHeight >= scrollHeight`), mobile browsers (especially iOS Safari and Chrome Mobile) chain the scroll gesture to parent elements (`.chat-overlay`, `body`, and `window`).

2. **Chat Overlay Missing Overflow & Overscroll Restraints**:
   - `.chat-overlay` has `position: fixed`, but lacks `overflow: hidden` and `overscroll-behavior: none`.
   - If the overlay container absorbs any scroll or shifts, its white background (`background: #ffffff`) or the page underneath is exposed below the dark coach drawer (`rgba(18, 18, 22, 0.95)`).
   - `.chat-overlay` uses `height: 100vh` rather than dynamic `100dvh` / `100%`, which can cause layout shifts when mobile browser address bars respond to gestures.

3. **Incomplete Body Scroll Locking on Mobile WebKit**:
   - When Aubrey chat opens, `document.body.style.overflow = 'hidden'` is applied. On iOS Safari, `overflow: hidden` on `body` **does not** prevent touch drag and rubber-banding of the document.
   - The underlying page (with 10+ match items totaling >1000px height) scrolls behind the overlay or rubber-bands upward, exposing a white background.
   - (Note: `expertInput` focus previously added `document.body.style.position = 'fixed'`, but this was not active during normal sheet browsing).

4. **Non-Scrollable Chrome propagating drags**:
   - Touches initiated on `.expert-sheet-header`, `.expert-drag-handle`, or `.expert-input-bar` (which are non-scrollable) immediately scroll the window/overlay if not prevented.

---

## User Review Required

> [!IMPORTANT]
> - **Zero Visual Changes to Layout**: The 45% (Aubrey chat) / 55% (Coach drawer) split, colors, typography, buttons, and animations remain identical.
> - **Smooth In-Drawer Scrolling Preserved**: Inside `.expert-sheet-body`, normal flick-scrolling between messages continues to work with native momentum.
> - **Solid Pinning at Boundaries**: When swiping up while already at the bottom (or down at the top), the drawer stays strictly anchored without rubber-banding or exposing white screen background.

---

## Proposed Changes

### Styling & Layout

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Overscroll Behavior & Viewport Locking**:
   - Add `overscroll-behavior: none;` to `html, body`.
   - Add `body.chat-open` rules:
     ```css
     body.chat-open {
       position: fixed;
       width: 100%;
       height: 100%;
       overflow: hidden;
     }
     ```
   - Update `.chat-overlay`:
     - Add `overflow: hidden;`
     - Add `overscroll-behavior: none;`
     - Support dynamic viewport: `height: 100%; height: 100dvh;`
   - Update `.chat-body` and `.expert-sheet-body`:
     - Add `overscroll-behavior: contain;`
     - Add `overscroll-behavior-y: contain;`
   - Update `.expert-sheet`:
     - Add `overscroll-behavior: contain;`

2. **JavaScript Viewport & Touch Event Handlers**:
   - In Aubrey match click handler:
     - Add `document.body.classList.add('chat-open');`
     - Record current scroll position to restore smoothly if needed.
   - In `closeChat()`:
     - Remove `document.body.classList.remove('chat-open');`
     - Reset `document.body.style.position = '';`
   - Guard non-scrollable touchmoves:
     - Add `touchmove` listeners on `#expertSheetHeader`, `.expert-drag-handle`, and `.expert-input-bar` with `{ passive: false }` calling `e.preventDefault()` so drag gestures on header/input do not pull the page.
     - Add bounce guard on `.expert-sheet-body` if needed to strictly block chained overscroll on mobile Safari.

---

## Verification Plan

### Mobile Viewport Emulation & Testing
1. **Viewport & Dimensions**:
   - Open mobile emulation (390 × 844 px).
   - Open Aubrey chat.
   - Open Coach dialogue drawer (`.sheet-open`).
2. **Swipe-Up Boundary Test**:
   - Ensure Coach dialogue is scrolled to bottom (default state).
   - Perform rapid upward swipe / touch drag on `#expertSheetBody`.
   - Verify `window.scrollY` remains `0`.
   - Verify `#chatOverlay.scrollTop` remains `0`.
   - Verify no white gap or screen appears underneath `#expertBottomSheet`.
3. **Header Drag Test**:
   - Perform upward and downward touch drag on `#expertSheetHeader`.
   - Verify page behind does not scroll or bounce.
4. **Chat Feed Functionality**:
   - Add multiple messages so feed overflows.
   - Verify smooth scrolling inside `#expertSheetBody` between top and bottom messages.
   - Verify smooth scrolling inside `#chatBody`.
5. **Close & Navigation**:
   - Close chat via back button.
   - Verify match list scrolls normally with no stuck body scroll locks.

---

## Progress Checklist

- [x] **1. CSS Updates in `index.html`**
  - [x] Add `overscroll-behavior: none` to `html, body`.
  - [x] Add `body.chat-open` style rules with fixed positioning.
  - [x] Add `overflow: hidden`, `overscroll-behavior: none`, `height: 100dvh` to `.chat-overlay`.
  - [x] Add `overscroll-behavior: contain` to `.chat-body`, `.expert-sheet`, and `.expert-sheet-body`.
- [x] **2. JavaScript Updates in `index.html`**
  - [x] Update match click listener to toggle `body.chat-open`.
  - [x] Update `closeChat()` to clean up `body.chat-open`.
  - [x] Add touch event guards on header and input bar to prevent scroll propagation.
- [x] **3. Verification & Validation**
  - [x] Test swipe-up at bottom of coach dialogue; verify no white screen.
  - [x] Test swipe gestures across headers and inputs.
  - [x] Confirm normal scrolling works within chat feed and matches list after exit.
