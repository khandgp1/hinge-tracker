# 72 — 6-Photo Profile Lineup Builder & Sandbox

## Goal

Refine the **Profile Lineup Builder & Photo Selector** in the **Profile Tab** (`#profileView`):
1. **Full-Screen Photo Selection Experience**: Replace the modal drawer/sheet with a dedicated full-screen view (`#lineupGalleryView`), complete with an iOS-style top navigation bar (Cancel button, title, and Next button) and a sticky bottom action bar (counter + large "Continue to Lineup" button).
2. **Zero Pre-Selection on Fresh Open**: Do not auto-select photos when tapping the `+` button in the Profile header. Fresh openings start cleanly at `0 of 6 selected`. When reopening from inside the Lineup Builder via "Photos" / "Edit Selection", retain the user's current 6 selections for seamless adjusting.
3. **Dedicated Photo Library**: Replace previous stock photos with the 5 user-provided library photos (`profile/01.jpg`–`05.jpg/png`).
4. **Leading Upload Tile**: Place the `+ Upload Photo` tile as the very first tile in the gallery grid (index 0) like an iOS Camera / Add action.
5. **Auto-Selection on Upload**: When a user uploads a new custom photo from device, automatically select it and assign the next badge number if fewer than 6 photos are selected.
6. **Lineup Builder Sandbox**: Retain the dual-mode 2x3 Grid Reorder and Hinge-style Live Feed Preview, backed by Firestore synchronization (`settings/profile_lineup`) and localStorage persistence.

---

## Architectural & UX Specifications

### 1. Header Action & Entry
- **Location**: Profile tab header (`#profileView .profile-header-wrapper header.header`), right side `#openLineupBuilderBtn`.
- **Trigger**: Tapping `+` resets selection to `0 of 6 selected` and opens `#lineupGalleryView` in full-screen mode.

---

### 2. Full-Screen Photo Selector View (`#lineupGalleryView`)
- **View Container**: Full-screen overlay (`position: fixed; inset: 0; background: var(--bg-dark); z-index: 1200; display: flex; flex-direction: column;`). No bottom drawer or sheet styling.
- **Top Navigation Bar**:
  - Left: "Cancel" text button (`#lineupGalleryCancelBtn`) to dismiss and return to the profile tab (or back to lineup sandbox if editing).
  - Center: Title `"Select 6 Photos"`.
  - Right: "Next" text button (`#lineupGalleryNextBtn`), disabled until 6 photos are selected.
- **Photo Grid (`#lineupGalleryGrid`)**:
  - 3-column scrollable grid with 4:5 aspect ratio tiles.
  - **Tile 1 (Leading)**: `+ Upload Photo` tile with dashed border, camera/plus icon, and hidden file input.
  - **Tiles 2–6**: The 5 user library photos (`profile/01.jpg`, `profile/02.jpg`, `profile/03.jpg`, `profile/04.png`, `profile/05.jpg`).
  - **Tiles 7+**: Any previously uploaded custom photos.
- **Selection State & Badges**:
  - Numbered accent badges (`1` through `6`) on selected thumbnails.
  - Tapping an unselected photo assigns the next number (up to 6).
  - Tapping a selected photo deselects it and re-indexes remaining badges.
- **Sticky Bottom Action Bar**:
  - Counter text: `"X of 6 selected"`.
  - Full-width button: `"Continue to Lineup"` (`#lineupContinueBtn`), disabled until exactly 6 photos are selected.

---

### 3. Dual-Mode Lineup Builder View (`#lineupSandboxView`)
- **Full-Screen Overlay**: Displays the chosen 6 photos in order.
- **Header**:
  - Left: Back chevron button (`#lineupBackBtn`) to return to the active profile tab.
  - Center: `"Profile Lineup"`.
  - Right: `"Photos"` button (`#lineupEditPhotosBtn`) to reopen the photo selector with current 6 selections retained.
- **Mode Toggle**:
  - Segmented control for **Grid Reorder** vs **Live Feed Preview**.
- **Mode A (Grid Reorder)**:
  - 2x3 cards with `#1`–`#6` badges, "Primary" marker on Slot 1, and prev/next arrow buttons to swap positions.
- **Mode B (Live Feed)**:
  - Vertical scrollable cards simulating the native Hinge dating profile feed.

---

### 4. Firestore & Local Storage Persistence
- Collection: `settings`, Doc: `profile_lineup`.
- Real-time `onSnapshot` ensures Client and Coach (`?role=coach`) stay synchronized.
- LocalStorage caching for fast offline/local boot.

---

## Proposed Changes

### 1. `profile/` Assets
- Populate `profile/01.jpg`, `profile/02.jpg`, `profile/03.jpg`, `profile/04.png`, `profile/05.jpg` from attached media.
- Clean up unused `profile/06.jpg`–`10.jpg`.

### 2. Markup in `index.html`
- Transform `#lineupGalleryModal` from modal sheet into full-screen `#lineupGalleryView` with top nav header (Cancel, Title, Next) and sticky footer (Counter, Continue).

### 3. CSS in `index.html`
- Update styles for `#lineupGalleryView`, full-screen container, leading upload tile, selection badges, top nav bar, and sticky footer.

### 4. JavaScript in `index.html`
- Set `DEFAULT_LINEUP_PHOTOS` to the 5 new library images.
- Reset `pendingGallerySelection = []` when opening via header `+` button.
- Retain current selection when tapping "Photos" (`#lineupEditPhotosBtn`) from the Lineup Builder.
- Render `+ Upload Photo` tile as the first item before library photos.
- Auto-select uploaded photos if selection count is under 6.
- Wire both `#lineupContinueBtn` and `#lineupGalleryNextBtn` to launch Lineup Builder with the 6 selected photos.

---

## Implementation Checklist

- [x] **Step 1: Replace Library Images in `profile/`**
  - [x] Copy 5 attached photos to `profile/01.jpg`–`05.jpg/png`.
  - [x] Clean up old `profile/06.jpg`–`10.jpg`.

- [x] **Step 2: Update Photo Selector Markup in `index.html`**
  - [x] Convert `#lineupGalleryModal` to full-screen `#lineupGalleryView` / overlay.
  - [x] Add top navigation bar with Cancel, Title ("Select 6 Photos"), and Next button.
  - [x] Add sticky bottom footer with counter and Continue button.

- [x] **Step 3: Update CSS for Full-Screen Photo Selector**
  - [x] Full viewport layout (`position: fixed; inset: 0; max-width: 390px; height: 100dvh; display: flex; flex-direction: column; z-index: 220;`).
  - [x] Modern iOS-style header with subtle border-bottom and clean typography.
  - [x] Scrollable grid with leading upload tile and 4:5 aspect ratio photo tiles.
  - [x] Sticky bottom footer with glass blur and prominent CTA button.

- [x] **Step 4: Update JavaScript Logic**
  - [x] Update `DEFAULT_LINEUP_PHOTOS` array to `['profile/01.jpg', 'profile/02.jpg', 'profile/03.jpg', 'profile/04.png', 'profile/05.jpg']`.
  - [x] Open from header `+`: clear `pendingGallerySelection = []` (`0 of 6 selected`).
  - [x] Open from Lineup Builder "Photos": retain `pendingGallerySelection = [...activeLineupSlots]`.
  - [x] Render `+ Upload Photo` tile as first tile.
  - [x] Automatically select uploaded image if selection < 6.
  - [x] Sync Next / Continue button disabled states and click handlers.

- [x] **Step 5: Testing & Verification**
  - [x] Open `+` button: verify full-screen presentation, 0 photos selected, 5 user photos shown with leading upload tile.
  - [x] Select photos: verify badges 1–5, Next/Continue disabled until 6th photo added.
  - [x] Upload 6th photo: verify auto-selected as #6, Continue enabled.
  - [x] Navigate to Lineup Builder: test Grid reordering, Live Feed preview, and Firestore sync.
  - [x] Tap "Photos" from Lineup Builder: verify current 6 selections are preserved.
