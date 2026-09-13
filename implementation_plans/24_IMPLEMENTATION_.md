# Implementation Plan 24 - Replace Textarea with Contenteditable to Suppress iOS Form Accessory Bar

Replace the Expert `<textarea>` element with a custom `contenteditable="true"` element (`-webkit-user-modify: read-write-plaintext-only`) to suppress iOS Safari's default Form Accessory Bar (`< > ✓`) and dock the input box directly on top of the virtual keyboard.

## User Review Required

> [!IMPORTANT]
> **Form Accessory Bar Suppression via Contenteditable**:
> Switching to a `contenteditable` container removes iOS Safari's automatic form navigation toolbar (`< > ✓`). The input box will sit directly flush against the soft keyboard keys.

---

## Proposed Changes

### Core Application Layout & Logic

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **HTML & CSS Updates**:
   - Replaced `<textarea id="expertInput">` with `<div id="expertInput" class="expert-input-field" contenteditable="true" role="textbox" aria-multiline="true" data-placeholder="Ask coach for advice..."></div>`.
   - Updated `.expert-input-field` CSS to support `-webkit-user-modify: read-write-plaintext-only;` and pseudo-element placeholder display via `:empty::before`.

2. **JavaScript Input Handler**:
   - Updated `sendExpertMessage()` to get and clear text via `innerText` / `textContent`.
   - Updated `keydown` and `input` event listeners to handle height auto-resize and `Enter` sending.

---

## Progress Checklist

- [x] **1. Contenteditable Implementation**
  - [x] Replace `<textarea>` tag with `contenteditable` div.
  - [x] Add CSS placeholder handling (`data-placeholder`) and plain text enforcement.
- [x] **2. JavaScript Refactoring**
  - [x] Update message retrieval to use `innerText`.
  - [x] Test message sending and newline behavior.
- [x] **3. Verification & Testing**
  - [x] Verify iOS Form Accessory Bar (`< > ✓`) is completely suppressed.
  - [x] Verify input box sits flush on top of keyboard.
