# Implementation Plan - Fix Mobile Keyboard Background Leak & Full-Screen Backdrop

Fix the mobile soft keyboard background leakage issue where the base "Matches" view bleeds through behind the chat overlay. Ensure `.chat-overlay` remains 100% opaque and full-screen (`100vh`) at all times while correctly elevating inner chat views above the virtual keyboard.

## User Review Required

> [!IMPORTANT]
> **Full-Screen Opaque Backdrop**: `.chat-overlay` will remain locked at `height: 100vh;` (or `100%`) regardless of soft keyboard state. Soft keyboard height changes will be handled purely via internal bottom padding/margin on inner components (`.expert-sheet`), ensuring the background matches list is 100% masked out at all times.

---

## Proposed Changes

### Core Application Layout & Logic

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Backdrop & Layout Enforcements**:
   - Restore `.chat-overlay` CSS to `height: 100%` / `100vh;` fixed overlay.
   - Remove outer height variable `--vh-height` binding on `.chat-overlay`.
   - Ensure `.chat-overlay` background is 100% opaque (`background: #ffffff;`).

2. **Inner Viewport Padding & Keyboard Handling**:
   - In `updateVisualViewport()`:
     - Calculate keyboard height: `keyboardHeight = winHeight - vpHeight`.
     - When `keyboardHeight > 100`, apply `padding-bottom: ${keyboardHeight}px` (or flex offset) to `.expert-sheet` or `.chat-overlay` internal wrapper.
     - Keep `.chat-overlay` outer dimensions at full window height (`100%`).
     - Trigger auto-scroll on `#chatBody` and `#expertSheetBody` to maintain recent message visibility.
   - On `blur` of `#expertInput`:
     - Reset inner padding/offset back to `0px`.

3. **Prevent Background Body Scroll**:
   - In `openChatOverlay()`: set `document.body.style.overflow = 'hidden'`.
   - In `closeChatOverlay()`: reset `document.body.style.overflow = ''`.

---

## Progress Checklist

- [x] **1. CSS Full-Screen Backdrop Restoration**
  - [x] Lock `.chat-overlay` height to fixed `100%`/`100vh`.
  - [x] Remove outer `--vh-height` container resizing.
- [x] **2. Internal Keyboard Offset & Scroll Handling**
  - [x] Update `updateVisualViewport()` to set internal `padding-bottom` for keyboard offset instead of shrinking the parent overlay frame.
  - [x] Update `blur` & `focus` event listeners on `#expertInput`.
- [x] **3. Verification & Manual Testing**
  - [x] Verify matches view is 100% hidden behind chat overlay when soft keyboard opens.
  - [x] Verify Coach input box and chat stream remain visible above keyboard fold.
