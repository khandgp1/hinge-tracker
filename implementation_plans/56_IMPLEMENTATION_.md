# 56 — Fix Coach & Client Dialogue Drawer Scrolling

## Goal

Resolve the bug preventing the Coach & Client Dialogue sheet (`#expertBottomSheet` / `#expertSheetBody`) from scrolling, ensuring that coaching conversations with multiple messages scroll smoothly via mouse wheel, trackpad, and mobile touch swipe gestures.

---

## Root Cause Analysis

1. **Inline Display Override (`display: block` vs `display: flex`)**:
   - In [`openChatForMatch(match)`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html), line 2138 sets `sheet.style.display = 'block'`.
   - In CSS, `.expert-sheet` is defined as a flex column container:
     ```css
     .expert-sheet {
       display: flex;
       flex-direction: column;
       ...
     }
     ```
   - When overridden with `display: block`, the child `.expert-sheet-body`'s `flex: 1` rule is disabled.
   - In standard block layout, `.expert-sheet-body` with `height: auto` expands to fit the full combined height of all messages (e.g., 1649px) rather than being constrained to the visible sheet height (~304px).
   - Because `body.clientHeight == body.scrollHeight`, the element calculates 0 internal overflow and never triggers its `overflow-y: auto` scrollbar. The overflowing content is simply clipped by `.expert-sheet { overflow: hidden; }`, and the input bar is pushed offscreen.

2. **Missing `min-height: 0` on Scrollable Flex Child**:
   - In CSS Flexbox, flex items default to `min-height: auto` (`min-content`). Without `min-height: 0`, a flex child can resist shrinking below content height in various mobile and desktop browser engines.

3. **Stale Touch Coordinates in Boundary Listener**:
   - In `expertSheetBody.addEventListener('touchmove')`, the gesture delta is calculated as `deltaY = currentY - expertTouchStartY` without updating the reference coordinate on subsequent move events.
   - If a user reverses direction during a swipe gesture, `deltaY` is evaluated against the initial touchstart position rather than the instantaneous movement direction, causing gesture lockup.

4. **Missing Scroll-to-Bottom on Drawer Expansion**:
   - When expanding the drawer via `toggleExpertSheet()`, the view should automatically scroll to the bottom of the feed so recent advice is immediately visible.

---

## Proposed Changes

### [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Fix ([`.expert-sheet-body`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html#L867-L877))**:
   - Add `min-height: 0;` to ensure `.expert-sheet-body` reliably shrinks to the available flex space.

2. **JS Fix ([`openChatForMatch`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html#L2135-L2145))**:
   - Change `sheet.style.display = 'block';` to `sheet.style.display = 'flex';` to preserve the flexbox column structure.

3. **JS Fix ([`toggleExpertSheet`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html#L1850-L1865))**:
   - Add auto-scroll to `expertSheetBody.scrollHeight` with a short timeout when expanding the drawer (`sheetState === 'open'`).

4. **JS Fix (Touch Boundary Listeners)**:
   - Update `expertSheetBody` and `chatBody` touchmove listeners to track continuous delta coordinates (`expertTouchLastY` / `chatTouchLastY`) on each move event.

---

## Verification Plan

### Automated / Browser Verification
1. Add 10+ coaching messages to a test match in Firestore.
2. Open the match chat and expand the coach drawer.
3. Verify via DevTools / DOM evaluation:
   - `sheet.style.display === 'flex'`
   - `expertSheetBody.clientHeight < expertSheetBody.scrollHeight`
   - `expertSheetBody.scrollHeight > 1000px`, `expertSheetBody.clientHeight ≈ 304px`
4. Test scrolling:
   - Mouse wheel upward and downward.
   - Touch drag gestures from bottom to top and top to bottom.
5. Purge test messages to leave database clean.

---

## Progress Checklist

- [x] **Step 1:** Add `min-height: 0;` to `.expert-sheet-body` in `index.html`.
- [x] **Step 2:** Update `openChatForMatch()` to set `sheet.style.display = 'flex'`.
- [x] **Step 3:** Add auto-scroll to bottom in `toggleExpertSheet()` upon expansion.
- [x] **Step 4:** Update touchmove listeners to track incremental delta Y.
- [x] **Step 5:** Verify scrolling behavior across wheel and touch interactions in browser.
