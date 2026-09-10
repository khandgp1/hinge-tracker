# Implementation Plan 14: Remove Priority Like Banner & Send Message Bar

Remove the "Your Priority Like helped you stand out" top banner and the "Send a message" bottom bar from the chat view in [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html).

## Progress Checklist
- [x] Remove Priority Like banner item from `aubreyChatData` JS array
- [x] Remove `.chat-input-bar` element from `#chatOverlay` HTML markup
- [x] Adjust `.chat-body` CSS padding-bottom from `84px` to `16px`
- [x] Verify chat overlay layout visually

## User Review Required
> [!NOTE]
> Removing the bottom input bar frees up vertical space in the chat view. `.chat-body` bottom padding will be adjusted to `16px` so message content fits flush with the view.

## Open Questions
- None. Requirements are clear.

## Proposed Changes

### UI / Chat Overlay Component

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Remove Priority Like Banner**:
   - In `aubreyChatData`, remove the initial item:
     ```javascript
     {
       type: "banner",
       title: "Your Priority Like<br>helped you stand out"
     },
     ```

2. **Remove "Send a message" Bottom Input Bar**:
   - Delete the `<div class="chat-input-bar">` block:
     ```html
     <!-- Fixed Bottom Input Footer -->
     <div class="chat-input-bar">
       <div class="chat-input-pill">
         <span class="chat-input-placeholder">Send a message</span>
         ...
       </div>
     </div>
     ```

3. **Adjust CSS Layout**:
   - Update `.chat-body` CSS rule to set `padding: 16px;` (reducing `padding-bottom` from `84px` to `16px`).

## Verification Plan

### Automated Tests
- N/A (UI layout structure)

### Manual Verification
- Open [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html) in browser.
- Click on the "Aubrey" match row to open `#chatOverlay`.
- Verify the top of the chat starts with the timestamp / photo without any "Your Priority Like helped you stand out" banner.
- Verify the bottom of the chat contains no "Send a message" bar.
