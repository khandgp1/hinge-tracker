# Implementation Plan 22 - Optimize Expert Input Dialog Space & Keyboard Split

Optimize the vertical space allocation when the mobile keyboard is open by reclaiming the iOS form accessory bar area (highlighted in red) for the Expert input bar and reducing top Hinge chat height.

## User Review Required

> [!IMPORTANT]
> **Input Dialog & Space Allocation**:
> 1. Reclaim the iOS input accessory bar space so the Expert input bar sits flush above the soft keyboard without redundant vertical padding.
> 2. Adjust the keyboard-active flex split ratio so the Expert chat & input dialog take up ~65% of available visible height, giving top Hinge chat a compact ~35% share.

---

## Proposed Changes

### Core Application Layout & Styling

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Accessory Bar Space Reclamation**:
   - Update `<textarea id="expertInput">` attributes (`autocorrect="off"`, `spellcheck="false"`, `inputmode="text"`, `enterkeyhint="send"`) and CSS padding to suppress default form accessory bar overhead and ensure flush keyboard docking.
   - Compact top `.chat-header` height and bottom input bar padding when keyboard is active.

2. **Adjusted Flex Ratio for Keyboard Active**:
   - Update `.chat-overlay.keyboard-active .chat-body` flex to `flex: 35 1 0%; min-height: 70px;`.
   - Update `.chat-overlay.keyboard-active .expert-sheet.open` flex to `flex: 65 1 0%; min-height: 160px;`.

---

## Progress Checklist

- [x] **1. Input Accessory Bar Space Optimization**
  - [x] Suppress redundant iOS accessory toolbar padding and compact header/input bars.
  - [x] Dock Expert input bar flush against soft keyboard fold.
- [x] **2. Flex Split Adjustment**
  - [x] Reduce top Hinge chat height allocation to ~35%.
  - [x] Expand Expert chat & input dialog space to ~65%.
- [x] **3. Verification & Testing**
  - [x] Verify input box uses reclaimed space efficiently.
  - [x] Verify both chats remain legible and scrollable.
