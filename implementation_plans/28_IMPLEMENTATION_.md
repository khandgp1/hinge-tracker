# Implementation Plan 28 – True 50/50 Mobile Split for Dual Chat View

## Overview
When both the Aubrey Hinge chat and the Coach & Client dialogue sheet are open simultaneously on mobile, the screen space was intended to divide evenly into a 50/50 split. However, because `.chat-body` has 68px of vertical padding (`padding-top: 52px` to clear the floating back button + `padding-bottom: 16px`) while `.expert-sheet` has 0px padding, CSS Flexbox's `flex-basis: 0%` calculation adds the 68px padding back on top of the allocated space. This results in an uneven **54% / 46%** split (455.5px vs 388.5px on an 844px mobile viewport), shortchanging the Coach sheet by 67px.

This plan updates the CSS sizing for dual chat mode so that both panes receive an exact **50.00% / 50.00%** split (422px each on an 844px height screen).

---

## User Review Required

> [!IMPORTANT]
> - **Dual Chat Open State**: When `#expertBottomSheet` is expanded (`.sheet-open`), both `#chatBody` and `#expertBottomSheet` are assigned `height: 50%` and `flex: 0 0 50%` with `box-sizing: border-box`.
> - **Collapsed State Preserved**: When collapsed, `#expertBottomSheet` retains its 56px bottom bar height, and `#chatBody` expands to fill the full remaining height.
> - **Keyboard Active State Preserved**: When keyboard is active, the dedicated 35% / 65% keyboard ratio remains intact for typing comfort.

---

## Proposed Changes

### Styling & Layout

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Update `.chat-overlay.sheet-open .chat-body`**:
   - Add `height: 50%;` and `flex: 0 0 50%;` (and `box-sizing: border-box;`).
   - Retain `padding-top: 52px;` to safely clear the floating back button.

2. **Update `.chat-overlay.sheet-open .expert-sheet.open` and `.half`**:
   - Set `height: 50%;` and `flex: 0 0 50%;` (and `box-sizing: border-box;`).
   - Ensure `transition: height 0.3s cubic-bezier(0.16, 1, 0.3, 1), flex-basis 0.3s cubic-bezier(0.16, 1, 0.3, 1)` remains smooth when expanding and collapsing.

---

## Verification Plan

### Automated / Browser Verification
- Launch mobile emulation (390 × 844 px).
- Open Aubrey chat from match list.
- Expand Coach dialogue sheet.
- Inspect bounding client rects:
  - Verify `#chatBody.getBoundingClientRect().height` === 422.0 px (50.00%).
  - Verify `#expertBottomSheet.getBoundingClientRect().height` === 422.0 px (50.00%).
  - Verify sum of both heights === total overlay height (844.0 px).
- Collapse Coach sheet:
  - Verify sheet height transitions smoothly back to 56 px.
  - Verify top `.chat-header` reappears and `#chatBody` fills the screen.
- Activate keyboard input:
  - Verify layout shifts appropriately to keyboard mode without breaking.

---

## Progress Checklist

- [ ] **1. CSS Updates in `index.html`**
  - [ ] Update `.chat-overlay.sheet-open .chat-body` with `height: 50%; flex: 0 0 50%;`.
  - [ ] Update `.chat-overlay.sheet-open .expert-sheet.open`, `.expert-sheet.half` with `height: 50%; flex: 0 0 50%;`.
- [ ] **2. Verification & Measurement**
  - [ ] Measure computed DOM heights in mobile viewport (390 × 844 px).
  - [ ] Confirm exact 50.00% / 50.00% ratio.
  - [ ] Verify collapse/expand transitions and floating back button functionality.
