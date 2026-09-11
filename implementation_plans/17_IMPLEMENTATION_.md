# Implementation Plan - Coach & Client Dialogue Shift+Enter & Mobile Newline Support

Enable multiline input support in the Coach & Client Dialogue sheet, supporting newlines for both Desktop (`Shift+Enter`) and Mobile virtual keyboards (`Enter`/Return key), while maintaining instant send (`Enter`) on desktop and Send button support.

## Mobile & Desktop Keyboard Behavior Breakdown
- **Desktop (Hardware Keyboard)**:
  - `Enter` (without Shift): Submits the message immediately.
  - `Shift+Enter`: Inserts a newline into the textarea without sending.
- **Mobile / Touch Devices (Virtual Keyboard)**:
  - `Enter` / `Return` key on soft keyboard: Inserts a newline (since mobile keyboards do not have a physical Shift key).
  - Tapping the **Send Button** (`#expertSendBtn`): Submits the message.
- **Input Growth**: `<textarea>` auto-expands height dynamically up to 100px as content grows, then scrolls.
- **Message Rendering**: Chat bubbles use `white-space: pre-wrap;` to accurately display line breaks.

---

## Progress Checklist

- [x] **1. HTML Structure Update**
  - [x] Replace `<input id="expertInput">` with `<textarea id="expertInput" rows="1" enterkeyhint="enter">` in `index.html`.
- [x] **2. CSS Styling & Layout**
  - [x] Style `.expert-input-field` for multiline textarea (remove resize handles, set max-height to 100px, auto overflow-y, padding/font adjustments).
  - [x] Update `.expert-bubble` with `white-space: pre-wrap;` and `word-break: break-word;`.
- [x] **3. JavaScript Event & Mobile Detection Logic**
  - [x] Detect touch/mobile environment (`'ontouchstart' in window || navigator.maxTouchPoints > 0`).
  - [x] Add `keydown` event listener to `expertInput`:
    - On Desktop: `Enter` sends message, `Shift+Enter` creates newline.
    - On Mobile/Touch: `Enter` creates newline; sending is triggered via the Send button.
  - [x] Implement auto-resizing height function for `expertInput` on `input` events and reset height upon sending.
- [x] **4. Verification & Testing**
  - [x] Test Desktop `Shift+Enter` creating newlines & `Enter` sending message.
  - [x] Test Mobile/Touch return key creating newlines.
  - [x] Test message bubble rendering for multiline text.
