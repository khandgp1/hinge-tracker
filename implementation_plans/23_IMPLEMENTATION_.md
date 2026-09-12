# Implementation Plan 23 - Native-Style Input Accessory Bar Docking for Mobile Web

Replicate native iOS `inputAccessoryView` behavior in the mobile web browser so the Expert input bar attaches synchronously and seamlessly to the soft keyboard without layout jitter or redundant system toolbars.

## User Review Required

> [!IMPORTANT]
> **Native-Style Input Docking Architecture**:
> To emulate native `inputAccessoryView` in Mobile Safari/Chrome:
> 1. Use zero-delay `visualViewport` hardware-accelerated transforms (`transform: translateY(...)`) or fixed bottom positioning locked to `window.visualViewport`.
> 2. Lock parent scroll containers during input focus to prevent iOS web view rubber-banding and scroll shifts.
> 3. Suppress all default iOS browser form accessory bars so the custom Expert input bar acts as the sole, native-feeling input toolbar.

---

## Proposed Changes

### Core Application Layout & Logic

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Synchronous Viewport Transformer**:
   - Refactored `updateVisualViewport()` to use `requestAnimationFrame` with 60fps frame-synced GPU-accelerated viewport transforms matching `window.visualViewport.height` and `offsetTop`.
   - Bound to `visualViewport.onresize` and `visualViewport.onscroll` with passive event listeners for stutter-free frame lock.

2. **Native Focus & Gesture Handling**:
   - Added viewport body position locks during text field focus to block iOS web view rubber-banding and scroll shifts.
   - Enhanced input field focus to trigger immediate dock alignment.

---

## Progress Checklist

- [x] **1. Native Input Accessory Bar Docking Engine**
  - [x] Implement `requestAnimationFrame` synced `visualViewport` transform positioning.
  - [x] Lock input toolbar directly to top edge of soft keyboard fold.
- [x] **2. Viewport Lock & Gesture Polish**
  - [x] Prevent web view rubber-banding during keyboard focus.
  - [x] Smooth 60fps transitions when keyboard opens/closes.
- [x] **3. Verification & Testing**
  - [x] Verify input bar attaches seamlessly like native `inputAccessoryView`.
  - [x] Verify message streams in both chats remain scrollable and legible.
