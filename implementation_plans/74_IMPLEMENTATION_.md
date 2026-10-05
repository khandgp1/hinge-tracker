# 74 — Split Tap Targets & Native Gesture Shielding for Photo Gallery Versions

## Goal

Provide a smooth, frictionless user experience for opening the **Photo Version Comparison Sheet** across both laptop (desktop trackpad/mouse) and iPhone (iOS Safari):
1. **Split Tap Targets (Option 1)**: Decouple the two competing user actions on gallery thumbnails so that:
   - **Tapping the photo** always toggles selection for the 6-photo lineup (`1`–`6`).
   - **Tapping the version pill** (in the bottom-left corner) always opens the **Photo Versions Sheet**, available on both multi-version stacks and single-version photos.
2. **Eliminate OS Gesture Collisions**:
   - Suppress native iOS Safari Share Sheets / image preview popups caused by holding or dragging images.
   - Suppress native desktop context menus on two-finger or right clicks.
   - Remove fragile long-press timer hacks that interfered with scrolling and native touches.

---

## Architectural & UX Specifications

### 1. Gallery Thumbnail Interaction Model
- **Primary Target (Image Card Body)**:
  - Tapping/clicking anywhere on the photo thumbnail toggles photo selection in/out of `pendingGallerySelection` (up to 6 photos).
  - Works identically for single-version photos and multi-version stacks.
  - In **Organize Mode**, tapping the photo toggles the organize/merge checkbox selection as before.
- **Secondary Target (Frosted Glass Version Pill in Bottom-Left)**:
  - **Multi-Version Stacks (`versions.length >= 2`)**:
    - Frosted glass pill displays `⧉ <count>` (e.g., `⧉ 3`).
    - Interactive button with `pointer-events: auto`, cursor pointer, subtle hover brightening, and `:active` scale bounce (`transform: scale(0.92)`).
    - Tapping this pill stops event propagation (`e.stopPropagation()`) and directly opens `#versionComparisonSheet` for this stack.
  - **Single-Version Photos (`versions.length === 1`)**:
    - Displays a subtle, frosted pill or icon button (e.g., `⧉` or `+` / versions icon) in the bottom-left corner.
    - Tapping this pill directly opens `#versionComparisonSheet` for that photo, allowing the user to immediately view it and tap `+ Add Version` to upload variations or crops.
    - Designed with clean, unobtrusive opacity that brightens on hover/tap.

### 2. Native Gesture & Event Shielding
- **iOS Callout & Drag Prevention**:
  - Add `-webkit-touch-callout: none;` to `.lineup-photo-thumb` and `.lineup-photo-thumb img`.
  - Add `-webkit-user-select: none; user-select: none;` across gallery thumbnails.
  - Add `-webkit-user-drag: none;` and `draggable="false"` on thumbnail `<img>` elements.
  - Prevents iOS Safari from capturing touches as image saves, drags, or Share Sheet launches.
- **Laptop / Desktop Context Menu Shielding**:
  - Add `contextmenu` listener on gallery thumbnails with `e.preventDefault()`.
  - Optional secondary shortcut: If the user right-clicks on a photo card, it can smoothly open the Version Comparison Sheet rather than popping up the browser's context menu.
- **Removal of Fragile Long-Press Timer Delays**:
  - Remove the 500ms `setTimeout` long-press listener from the grid items.
  - Eliminates latency, touch cancelation during scroll, and unintended double-triggers.

---

## Proposed Changes

### 1. CSS in `index.html`
- Update `.lineup-photo-thumb img`:
  - Add `-webkit-touch-callout: none;`
  - Add `-webkit-user-select: none; user-select: none;`
  - Add `-webkit-user-drag: none;`
  - Add `pointer-events: none;` so touches and clicks register cleanly on the parent container.
- Update `.lineup-version-pill`:
  - Change `pointer-events: none;` to `pointer-events: auto;`.
  - Add `cursor: pointer;`, `transition: transform 0.15s ease, background-color 0.15s ease;`.
  - Add `:hover` and `:active` styles (`transform: scale(0.92);`).
  - Add styling for single-version pill variant (`.lineup-version-pill.is-single`), keeping it elegant and uncluttered.
- Update `.lineup-photo-thumb`:
  - Add `-webkit-touch-callout: none;`

### 2. JavaScript in `index.html`
- Update `renderGalleryGrid()`:
  - Render the `.lineup-version-pill` for all stacks (with version count for >= 2, or subtle `⧉ +` version icon for single photos).
  - In thumbnail click listener:
    - Normal thumb click strictly handles lineup selection (or organize selection when in Organize Mode).
    - Attach an explicit click handler on `.lineup-version-pill` that stops propagation (`e.stopPropagation()`) and calls `openVersionComparisonSheet(stack.id)`.
  - Add `contextmenu` handler on thumbnails:
    - Calls `e.preventDefault()`.
    - Opens `openVersionComparisonSheet(stack.id)` as an intuitive desktop power shortcut.
  - Clean up touchstart/touchend/mousedown/mouseup long-press timer boilerplate.

---

## Implementation Checklist

- [x] **Step 1: CSS Hardening & Pill Interactive Styling**
  - [x] Add `-webkit-touch-callout: none;`, `user-select: none;`, and `-webkit-user-drag: none;` to thumbnail containers and images in `index.html`.
  - [x] Enable `pointer-events: auto;` and interactive states (`cursor: pointer;`, hover, `:active` scale) on `.lineup-version-pill`.
  - [x] Add styling for single-version pill affordance (`.is-single`) so users have an obvious 1-tap entry to add/manage versions on any photo.

- [x] **Step 2: Gallery Grid Markup & Split Tap Handlers**
  - [x] Update `renderGalleryGrid()` in `index.html` to generate version pills for both multi-version and single-version stacks.
  - [x] Wire `.lineup-version-pill` click listener with `e.stopPropagation()` and direct invocation of `openVersionComparisonSheet(stack.id)`.
  - [x] Update thumbnail `onclick` handler so tapping the photo image consistently toggles lineup selection (`toggleGalleryPhotoSelection`) regardless of version count.

- [x] **Step 3: Native Context Menu & Gesture Suppression**
  - [x] Add `contextmenu` event listener with `e.preventDefault()` on gallery items.
  - [x] Allow desktop right-click / two-finger click to open `openVersionComparisonSheet(stack.id)` smoothly without browser menu popups.
  - [x] Remove legacy 500ms long-press timer event listeners (`touchstart`, `mousedown`, etc.).

- [x] **Step 4: Verification & Cross-Platform Testing**
  - [x] Test tapping photo card body on single-version photos (verifies 1-tap lineup selection).
  - [x] Test tapping photo card body on multi-version photos (verifies 1-tap lineup selection without opening sheet).
  - [x] Test tapping the version pill on both single-version and multi-version photos (verifies 1-tap version sheet launch).
  - [x] Verify right-click / two-finger click on desktop opens versions cleanly without native browser menu.
  - [x] Verify long-press or touch interactions on mobile do not trigger native iOS Share Sheet.
