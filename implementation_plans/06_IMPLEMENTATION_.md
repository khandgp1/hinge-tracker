# Implementation Plan 06 - Aubrey Chat View Overlay

This plan details the implementation of a new Chat View overlay for `Aubrey` in `index.html` that opens when the Aubrey row is clicked in the Matches list.

## User Review Required

> [!NOTE]
> - **View Style**: Fullscreen overlay with a sticky header bar featuring a back button (`<`) and title (`Aubrey`), with vertically scrollable chat content displaying `Aubrey_Chat.png`.
> - **Interactivity**: Clicking the `Aubrey` row opens the view overlay. Tapping the back button (or header bar) closes the overlay and returns to the matches list.
> - **Other Rows**: Clicking on non-Aubrey match rows will remain inactive.

---

## Technical Architecture & Design System

```
+------------------------------------------+
|  Matches View (Default)                  |
|  - List of matches                       |
|  - Click 'Aubrey' row ----------------+  |
+---------------------------------------|--+
                                        |
                                        v
+------------------------------------------+
|  Aubrey Chat View (Overlay)              |
|  +------------------------------------+  |
|  | [<]  Aubrey                        |  |  (Sticky Top Header)
|  +------------------------------------+  |
|  |                                    |  |
|  | [ Aubrey_Chat.png Image ]          |  |  (Scrollable Chat Body)
|  | (Full-width, vertical scroll)      |  |
|  |                                    |  |
|  +------------------------------------+  |
+------------------------------------------+
```

---

## Proposed Changes

### Web Application

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **HTML Structure**:
   - Add a `<div id="chatOverlay" class="chat-overlay">` element containing:
     - Header bar (`.chat-header`): Back arrow icon/button (`#chatBackBtn`), chat user name (`Aubrey`).
     - Content container (`.chat-content`): `<img>` displaying `Aubrey_Chat.png`.

2. **CSS Styling**:
   - Style `.chat-overlay` as fixed position covering `max-width: 390px` (or full width inside mobile container), `z-index: 200`, `top: 0`, `left: 50%`, `transform: translateX(-50%)`, background `#ffffff`, `height: 100vh`, `overflow-y: auto`.
   - Add smooth display/transition states (`.chat-overlay.active`).
   - Style `.chat-header` with sticky position (`top: 0`), clean iOS header styling, border-bottom divider, back chevron button, bold centered or left-aligned title.
   - Style `.chat-content img` to render full width (`width: 100%`, `display: block`, `height: auto`).

3. **JavaScript Logic**:
   - Update `matchesData` or match row renderer to attach event listeners or data attributes.
   - Add click listener for row: if `item.name === 'Aubrey'`, show `#chatOverlay`.
   - Add click listener for `#chatBackBtn` to hide `#chatOverlay`.

---

## Implementation Checklist

- [x] **Step 1: HTML & CSS for Chat Overlay**
  - [x] Add `#chatOverlay` structure to `index.html`.
  - [x] Add CSS for `.chat-overlay`, `.chat-header`, `.chat-back-btn`, and `.chat-content`.

- [x] **Step 2: JavaScript Interaction Logic**
  - [x] Update row click event handler in `index.html` to detect clicks on Aubrey.
  - [x] Add open/close functions for the chat overlay view.

- [x] **Step 3: Verification**
  - [x] Test clicking `Aubrey` row to open chat overlay view.
  - [x] Verify `Aubrey_Chat.png` renders sharply and scrolls smoothly.
  - [x] Test clicking back button to return to Matches list.
  - [x] Verify clicking other rows does not trigger overlay.

---

## Verification Plan

### Automated / Browser Verification
- Serve `index.html` and inspect UI interactions:
  - Click `Aubrey` row.
  - Verify chat overlay opens with top header bar and scrollable `Aubrey_Chat.png`.
  - Click back button and confirm return to matches list.
