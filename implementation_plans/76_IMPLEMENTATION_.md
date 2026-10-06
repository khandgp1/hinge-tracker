# 76 — 1:1 Square Photos for Profile Lineup & Photo Gallery Selector

## Goal

Align the photo display aspect ratio across the **Profile Lineup Sandbox** (Grid Reorder & Live Feed) and the **Photo Gallery Selector** to a native **1:1 square ratio**, matching the 1:1 cropping capability introduced in Plan 75.

---

## Architectural & UX Specifications

### 1. Photo Selection Grid (`#lineupGalleryGrid`)
- Update `.lineup-photo-thumb` aspect ratio from `4 / 5` to `1 / 1`.
- Retain 3-column responsive layout (`repeat(3, 1fr)`).
- Ensure thumbnail image retains `object-fit: cover`, cleanly center-cropping any non-square photos while displaying 1:1 cropped versions at exact 1:1 pixel fidelity.
- Badges (`.lineup-badge-number`), version pills (`.lineup-version-pill`), and the `+ Upload Photo` leading tile fit seamlessly within the square tile.

### 2. Profile Lineup Grid View (`#lineupGridView`)
- Update `.lineup-slot-photo-wrapper` aspect ratio from `4 / 5` to `1 / 1`.
- Retain the 2-column card layout (`repeat(2, 1fr)`).
- Keep `.lineup-slot-photo` styled with `object-fit: cover` and `width: 100%; height: 100%`.
- Reorder controls bar (`.lineup-slot-controls`) remains underneath each square photo card with arrow buttons and slot index label.
- Slot interaction model preserved: arrows handle reordering, while photo changes/crops remain accessed via the top-bar "Photos" button.

### 3. Profile Lineup Live Feed View (`#lineupFeedView`)
- Update `.lineup-feed-card-photo` aspect ratio from `4 / 5` to `1 / 1`.
- Retain the rounded card presentation (`border-radius: 16px`, 16px side margins) with `object-fit: cover`.
- Feed badges (`#1 / 6` and primary photo indicator) position cleanly over the square cards.

---

## Proposed Changes

### 1. CSS Updates in `index.html`
- Update `.lineup-photo-thumb`:
  - `aspect-ratio: 1 / 1;`
- Update `.lineup-slot-photo-wrapper`:
  - `aspect-ratio: 1 / 1;`
- Update `.lineup-feed-card-photo`:
  - `aspect-ratio: 1 / 1;`

---

## Verification Plan

- [x] Check Photo Gallery Grid (`#lineupGalleryGrid`): verify tiles are 1:1 square, badges and version pills render properly, and the `+ Upload Photo` tile is balanced.
- [x] Check Lineup Grid View (`#lineupGridView`): verify slot photo containers are 1:1 square and reorder controls work smoothly.
- [x] Check Lineup Live Feed View (`#lineupFeedView`): verify cards display 1:1 square photos with rounded corners and proper margins.
- [x] Verify both 1:1 cropped versions and original non-square photos render properly with center-crop.
