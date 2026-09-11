# Implementation Plan - Mobile Soft Keyboard Sticky Viewport (Option 2)

Implement **Option 2 (Sticky Viewport Docking with `VisualViewport` API)** to ensure both the **Aubrey Chat stream**, the **Coach & Client dialogue**, and the **Coach Input Box** remain 100% visible simultaneously when the soft keyboard opens on mobile devices.

## User Review Required

> [!IMPORTANT]
> **Dynamic Viewport Resizing via `window.visualViewport`**: On mobile devices (iOS Safari & Android Chrome), soft keyboard activation reduces the visible viewport height. By binding `.chat-overlay` to `window.visualViewport.height`, the app container resizes dynamically to fit exact visible space above the keyboard, preserving visual access to both chat streams.

---

## Proposed Changes

### Core Application Layout & Logic

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Viewport & Flex Adjustments**:
   - Add CSS variable support: `.chat-overlay { height: var(--vh-height, 100vh); }`.
   - Ensure `.chat-body` and `.expert-sheet` maintain proportional flex height (e.g., 50%/50% or 55%/45%) inside the visible keyboard viewport when `#expertBottomSheet.open` is active.

2. **JavaScript `VisualViewport` API Integration**:
   - Add event listeners for `window.visualViewport` `resize` and `scroll` events.
   - Dynamically compute `--vh-height` as `${window.visualViewport.height}px` whenever the keyboard is active or viewport resizes.
   - Add `focus` listener on `#expertInput`:
     - When input is focused on touch/mobile devices, trigger viewport adjustment and auto-scroll both `#chatBody` and `#expertSheetBody` to their latest messages.
   - Add `blur` listener on `#expertInput`:
     - Reset `--vh-height` to `100vh` on keyboard dismissal.

---

## Progress Checklist

- [x] **1. Visual Viewport CSS & Logic**
  - [x] Add `--vh-height` CSS binding to `.chat-overlay`.
  - [x] Implement `window.visualViewport` `resize` and `scroll` handler in `index.html`.
- [x] **2. Mobile Focus & Auto-Scroll Logic**
  - [x] Add `focus` and `blur` event listeners to `#expertInput`.
  - [x] Implement dual auto-scroll for `#chatBody` and `#expertSheetBody` upon keyboard trigger.
- [x] **3. Verification & Testing**
  - [x] Test mobile soft keyboard opening on touch/mobile view.
  - [x] Verify simultaneous visibility of Aubrey Chat, Coach Dialogue, and Coach Input Box above keyboard fold.
