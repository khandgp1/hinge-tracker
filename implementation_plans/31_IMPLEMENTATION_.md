# Implementation Plan 31 – 50/50 Split for Top Chat & Coaching Chat When Mobile Keyboard is Open

## Overview
On mobile view, when the virtual keyboard is active (`.keyboard-active`), the remaining visual viewport space above the keyboard is currently divided into a **35% / 65% split** (35% for the top Hinge/Aubrey chat pane, 65% for the Coach & Client Dialogue pane).

The user requested changing this layout so that the **top chat** (`#chatBody`) and the **coaching chat** (`#expertBottomSheet`) share a clean **50/50 split** of the remaining vertical space above the virtual keyboard.

---

## Current vs Proposed Layout

### Current Keyboard-Active Layout (Plan 22 Legacy)
- Top Chat (`.chat-overlay.keyboard-active .chat-body`):
  - `flex: 35 1 0%`
  - `min-height: 70px`
- Coaching Chat (`.chat-overlay.keyboard-active .expert-sheet.open, ...`):
  - `flex: 65 1 0%`
  - `min-height: 110px`

### Proposed 50/50 Keyboard-Active Layout
- Top Chat (`.chat-overlay.keyboard-active .chat-body`, `.chat-overlay.sheet-open.keyboard-active .chat-body`):
  - `flex: 50 1 0%` (equal flex weight `1 1 0%`)
  - `min-height: 70px`
  - `height: auto`
- Coaching Chat (`.chat-overlay.keyboard-active .expert-sheet.open, .chat-overlay.keyboard-active .expert-sheet.half, .chat-overlay.keyboard-active .expert-sheet.full`):
  - `flex: 50 1 0%` (equal flex weight `1 1 0%`)
  - `min-height: 70px`
  - `height: auto`

Both panes have `flex-basis: 0%` and identical `flex-grow` (`50` or `1`), ensuring they divide 100% of the available vertical space after the keyboard offset (`chatOverlay.style.paddingBottom`) exactly 50/50.

---

## User Review Required

> [!IMPORTANT]
> - **No Keyboard State Unaffected**: When the keyboard is closed, the existing 45% (Aubrey chat) / 55% (Coach sheet) layout remains unchanged.
> - **Header Invisibility Preserved**: The expert sheet header remains hidden during keyboard typing to avoid eating into the coach feed's 50% share.
> - **Smooth Auto-Scroll**: When the keyboard triggers, both the top chat feed and the coach dialogue feed will automatically scroll to their bottom boundaries to keep recent messages visible.

---

## Proposed Changes

### Styling & Layout

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

Update lines ~542–564 in `index.html`:

```css
/* Reclaim Space & 50% / 50% Flex Split when Keyboard is Active */
.chat-overlay.keyboard-active .chat-header {
  height: 42px;
  padding: 6px 14px;
}

.chat-overlay.keyboard-active .chat-body,
.chat-overlay.sheet-open.keyboard-active .chat-body {
  height: auto;
  flex: 50 1 0%;
  min-height: 70px;
  padding: 10px 14px 10px;
  padding-top: 48px;
}

.chat-overlay.keyboard-active .expert-sheet.open,
.chat-overlay.keyboard-active .expert-sheet.half,
.chat-overlay.keyboard-active .expert-sheet.full {
  height: auto;
  flex: 50 1 0%;
  flex-basis: 0%;
  flex-shrink: 1;
  min-height: 70px;
}
```

---

## Verification Plan

### Automated / Browser Verification
1. **Emulate Mobile Viewport**:
   - Open browser subagent or dev server at viewport 390 × 844 px.
   - Navigate to Aubrey chat.
   - Expand Coach & Client dialogue sheet.
2. **Keyboard Activation Test**:
   - Focus `#expertInput` or simulate keyboard active (`paddingBottom: 300px` or VisualViewport resize).
   - Check computed heights of `#chatBody` and `#expertBottomSheet`:
     - Both elements should measure within a few pixels of each other (50% / 50% of the remaining height above the keyboard).
3. **Feed Usability & Scrolling**:
   - Verify messages in both `#chatFeed` and `#expertChatFeed` are visible and readable.
   - Verify both panes scroll independently without layout snapping or rubber-banding.
4. **Keyboard Dismissal**:
   - Blur `#expertInput`.
   - Verify the layout smoothly returns to standard no-keyboard dimensions (45% chat / 55% coach).

---

## Progress Checklist

- [x] **1. CSS Layout Updates in `index.html`**
  - [x] Update `.chat-overlay.keyboard-active .chat-body` to `flex: 50 1 0%`.
  - [x] Update `.chat-overlay.keyboard-active .expert-sheet` rules to `flex: 50 1 0%` and `min-height: 70px`.
  - [x] Align `.chat-overlay.sheet-open.keyboard-active .chat-body` selector for consistent specificity.
- [ ] **2. Verification & Validation**
  - [ ] Simulate keyboard opening and verify 50/50 vertical division of remaining space.
  - [ ] Verify both chat feeds scroll and display messages correctly.
  - [ ] Verify keyboard blur returns layout to default proportions without artifacts.
