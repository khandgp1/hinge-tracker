# Implementation Plan 34 – Hide Matches List Screen When Chat Overlay Is Open

## Overview
When viewing a conversation in mobile view, opening the virtual keyboard shrinks `#chatOverlay`'s height to the visual viewport height, revealing the underlying Matches list screen behind the coach drawer and through the translucent iOS keyboard (showing "You matched with Isadora" and "Anshara").

This update implements **Solution 1**: cleanly removing the underlying main screens (`.matches-list`, `.sticky-header-wrapper`, and `.bottom-nav`) from the rendering tree via CSS whenever `body.chat-open` is active.

---

## Current vs Proposed Behavior

### Current Behavior
- When Aubrey's chat is opened, `body.chat-open` is applied, but the underlying elements remain active in the DOM.
- When the keyboard opens, `#chatOverlay` is cropped to `window.visualViewport.height`.
- Elements from `#matchesList` (Isadora, Anshara) show through the gap above the keyboard and through the frosted-glass keyboard keys.

### Proposed Behavior
- When Aubrey's chat is opened, `body.chat-open` hides `.matches-list`, `.sticky-header-wrapper`, and `.bottom-nav` (`display: none !important;`).
- Behind `#chatOverlay`, there is only a solid `#ffffff` canvas.
- When the keyboard opens, no text, match cards, or profile pictures can bleed through or show behind the keyboard.
- When returning from chat, `closeChat()` removes `body.chat-open`, instantly restoring the match list, header, and bottom navigation bar, and restoring the user's previous scroll position via the existing `window.scrollTo(0, scrollRestoreY)`.

---

## User Review Required

> [!IMPORTANT]
> - **Zero Visual Changes to Normal Browsing**: When browsing the Matches list, everything appears and functions identically.
> - **Zero Visual Changes to Normal Chat**: When Aubrey chat is active, the chat screen continues to display Aubrey's messages, floating back button, and Coach Alex dialogue.
> - **Underlying Page Hidden**: Hiding the underlying page prevents ghosting, text bleed-through, and any background rubber-banding or touch chaining.
> - **Clean Scroll Restoration**: Tapping back (`closeChat`) seamlessly restores the Matches list and scrolls back to the exact pre-chat scroll position.

---

## Proposed Changes

### Styling

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
Add CSS rules under `body.chat-open` (around line 30):

```css
body.chat-open .matches-list,
body.chat-open .sticky-header-wrapper,
body.chat-open .bottom-nav {
  display: none !important;
}
```

---

## Verification Plan

### Mobile Device & Browser Testing
1. **Match List Baseline**:
   - Verify all match cards, header, and bottom navigation bar display properly.
   - Scroll down to the middle of the list.
2. **Open Chat Overlay**:
   - Tap on Aubrey's row to open chat.
   - Inspect DOM to verify `.matches-list`, `.sticky-header-wrapper`, and `.bottom-nav` are hidden (`display: none`).
3. **Keyboard Focus Test**:
   - Open the Coach Alex dialogue drawer.
   - Tap into `#expertInput` ("Ask coach for advice...") to open the virtual keyboard.
   - Verify that **no** match text ("You matched with Isadora") or avatars ("Anshara") appear in the gap above the keyboard or behind the translucent keyboard keys.
4. **Close Chat & Scroll Restoration**:
   - Tap the back button (`#chatFloatingBackBtn` or `#chatBackBtn`).
   - Confirm the Matches list, header, and bottom nav reappear immediately.
   - Verify the list returns to the exact scroll position where Aubrey was tapped.

---

## Progress Checklist
- [x] Create Implementation Plan 34 (`implementation_plans/34_IMPLEMENTATION_.md`)
- [x] Add `body.chat-open` hiding rules for `.matches-list`, `.sticky-header-wrapper`, and `.bottom-nav` in `index.html`
- [x] Verify CSS code changes and rules via verification script
- [ ] Manual verification on user's mobile device / browser (CDP browser automation encountered connection error)
