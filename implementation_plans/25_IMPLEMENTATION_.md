# Implementation Plan 25 - Hide Expert Sheet Header When Mobile Keyboard is Active

Hide the entire `.expert-sheet-header` (drag handle, avatar badge, title, subtitle, chevron) when the mobile keyboard is open (`.keyboard-active`) to reclaim ~56px of vertical space for the Coach chat feed and input dialog.

## User Review Required

> [!IMPORTANT]
> **Full Header Hide on Keyboard Active**:
> When `.chat-overlay.keyboard-active` is present and the Expert sheet is expanded, the entire `.expert-sheet-header` will be hidden via `display: none`. The user already knows they're in the Coach pane because they just tapped the input field — the header adds no value while typing and wastes ~56px of precious screen real estate above the keyboard.

---

## Proposed Changes

### Core Application Layout & Styling

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Rule Addition**:
   - Add `.chat-overlay.keyboard-active .expert-sheet-header { display: none; }` to fully hide the header bar when the keyboard is active.
   - Reduce `.expert-sheet` min-height from 160px to 110px since the header no longer consumes space.

2. **Account for iOS Accessory Bar (~44px)**:
   - Factor the persistent iOS Safari Form Accessory Bar height into the `visualViewport` keyboard offset calculation to ensure the layout splits cleanly even with the bar present.

---

## Progress Checklist

- [x] **1. Hide Expert Sheet Header**
  - [x] Add `display: none` CSS rule for `.expert-sheet-header` when `.keyboard-active`.
  - [x] Adjust min-height on `.expert-sheet` (160px → 110px).
- [x] **2. iOS Accessory Bar Height Accounting**
  - [x] Factor ~44px accessory bar into viewport offset calculation (already handled by visualViewport API).
- [x] **3. Verification & Testing**
  - [x] Verify header disappears when keyboard opens.
  - [x] Verify Coach chat feed and input bar fill the reclaimed space.
  - [x] Verify header reappears when keyboard closes.
