# Implementation Plan 21 - Even Split for Hinge Chat vs Expert Chat with Mobile Keyboard

Ensure that when the mobile soft keyboard opens (`.keyboard-active`), the available visible screen area is divided evenly (50/50 split) between the Hinge chat feed (`#chatBody`) and the Expert coach sheet (`#expertBottomSheet`).

## User Review Required

> [!IMPORTANT]
> **50/50 Flex Split Strategy**: When `.keyboard-active` is present on `.chat-overlay` and `.expert-sheet` is expanded (`.open` or `.half`), `.expert-sheet`'s fixed `height: 40vh` / `flex-basis: 40vh` and `flex-shrink: 0` will be overridden to `flex: 1 1 0%; height: auto; flex-shrink: 1;`. Both `#chatBody` and `#expertBottomSheet` will receive equal flex grow (`flex: 1`), sharing the available height above the soft keyboard equally.

---

## Proposed Changes

### Core Application Layout & Styling

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Keyboard-Active Layout Rule**:
   - Add `.chat-overlay.keyboard-active .expert-sheet.open`, `.chat-overlay.keyboard-active .expert-sheet.half`, and `.chat-overlay.keyboard-active .expert-sheet.full` rules:
     - Set `height: auto;`
     - Set `flex: 1 1 0%;`
     - Set `min-height: 140px;` (to keep header + input bar + messages visible and functional)
   - Ensure `#chatBody` maintains `flex: 1 1 0%; min-height: 120px;` when keyboard is active.

2. **Auto-Scroll Behavior**:
   - Ensure `updateVisualViewport()` scrolls both `#chatBody` and `#expertSheetBody` to the bottom when the soft keyboard is triggered.

---

## Progress Checklist

- [x] **1. CSS Layout Rule Updates**
  - [x] Add `.keyboard-active` styles for `.expert-sheet.open`, `.half`, and `.full`.
  - [x] Set balanced flex properties (`flex: 1 1 0%`) and minimum heights on both chat sections.
- [x] **2. Verification & Testing**
  - [x] Test layout when keyboard opens with Expert sheet collapsed vs open.
  - [x] Verify both Hinge chat feed and Expert chat feed remain scrollable and equally visible.
