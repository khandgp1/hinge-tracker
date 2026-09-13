# Implementation Plan 29 – 45/55 Split for Dual Chat View (Bottom Chat Dominant)

## Overview
Currently, in dual-chat mode (when both the Aubrey Hinge chat and the Coach & Client dialogue sheet are open), the Coach drawer feels cramped and takes less space than the top chat. The user requested adjusting the split so the **bottom Coach chat takes up more space**, specifically an exact **45% (top) / 55% (bottom)** distribution.

This plan updates the CSS sizing for dual chat mode (`.chat-overlay.sheet-open`) so that:
- Top chat pane (`#chatBody`): **45%** vertical height (379.8px on an 844px mobile screen).
- Bottom Coach pane (`#expertBottomSheet`): **55%** vertical height (464.2px on an 844px mobile screen).

---

## User Review Required

> [!IMPORTANT]
> - **45% / 55% Split**: When the Coach sheet is expanded (`.sheet-open`), the top Aubrey chat pane will take **45%** of the screen, and the Coach sheet will take **55%** of the screen.
> - **Padding & Floating Back Button**: Top Aubrey chat preserves its `padding-top: 52px` so the floating circular back button has ample breathing room, while fitting strictly within the 45% box without overflowing.
> - **Collapsed & Keyboard Behaviors Preserved**:
>   - When collapsed, the Coach bar remains 56px at the bottom with standard Hinge header visible.
>   - When the user focuses an input to type, `.keyboard-active` handles the keyboard offset smoothly.

---

## Proposed Changes

### Styling & Layout

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Top Chat Pane (`.chat-overlay.sheet-open .chat-body`)**:
   - Set `height: 45%;`
   - Set `flex: 0 0 45%;`
   - Set `box-sizing: border-box;`
   - Maintain `padding-top: 52px;`

2. **Coach Drawer Sheet (`.chat-overlay.sheet-open .expert-sheet.open`, `.chat-overlay.sheet-open .expert-sheet.half`)**:
   - Set `height: 55%;`
   - Set `flex: 0 0 55%;`
   - Set `box-sizing: border-box;`
   - Ensure the 300ms transition between 56px (collapsed) and 55% (open) animates smoothly.

---

## Verification Plan

### Automated / Browser Verification
- Load mobile emulation (390 × 844 px).
- Open Aubrey chat from matches list.
- Expand Coach dialogue drawer:
  - Verify `#chatBody.getBoundingClientRect().height` === 379.8 px (**45.00%**).
  - Verify `#expertBottomSheet.getBoundingClientRect().height` === 464.2 px (**55.00%**).
  - Verify sum equals total viewport height (844.0 px).
- Verify collapse back to 56px bottom bar on pill handle click.
- Verify smooth visual transition and scrolling in both panes.

---

## Progress Checklist

- [x] **1. CSS Updates in `index.html`**
  - [x] Add `height: 45%; flex: 0 0 45%; box-sizing: border-box;` to `.chat-overlay.sheet-open .chat-body`.
  - [x] Add `height: 55%; flex: 0 0 55%; box-sizing: border-box;` to `.chat-overlay.sheet-open .expert-sheet.open`, `.expert-sheet.half`.
- [x] **2. Verification & Validation**
  - [x] Measure exact computed heights on mobile viewport (390 × 844 px).
  - [x] Confirm exact 45.00% / 55.00% split.
  - [x] Test expand/collapse transitions and touch scrolling.
