# Implementation Plan 12 - Complete Top-to-Bottom Liked Photo Crop Preview

This plan details expanding the crop bounds of Aubrey's liked photo card asset from `Aubrey_Chat.png` to encompass the absolute top-most border of the photo card (y=304) down to the bottom card border (y=730), capturing 100% of the original image card (429x426 px).

## User Directives & Technical Requirements

> [!IMPORTANT]
> - **Pre-update Preview**: Show the proposed candidate image (`assets/aubrey_liked_photo_candidate.png`) to the user for approval **before** replacing `assets/aubrey_liked_photo.png` or updating `index.html`.
> - **Full Bounds (y=304..730)**: Include the complete top wall/background space above Aubrey's head (starting at y=304, immediately below timestamp) through the bottom of her hoodie (y=730).

---

## Technical Architecture & Crop Region

```
+-------------------------------------------------+
|  Aubrey Chat Feed Item (Right Aligned 78% Width)|
|                                                 |
|  +-------------------------------------------+  |
|  |  [ True Top Card Boundary (y=304) ]       |  |  (Full background space)
|  |   Aubrey Liked Photo Image                |  |
|  |   (Complete photo card bounds 429x426)    |  |
|  |                                           |  |
|  |                             [ Native Pill |  (HTML overlay covers
|  |                               Badge ]     |   baked-in text area)
|  +-------------------------------------------+  |
+-------------------------------------------------+
```

---

## Proposed Changes

### Assets & Web Application

#### [NEW / PREVIEW] [`assets/aubrey_liked_photo_candidate.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/assets/aubrey_liked_photo_candidate.png)
- Candidate crop extracted from `Aubrey_Chat.png` using bounds y=304..730, x=131..560 (429x426 px).

#### [MODIFY] `assets/aubrey_liked_photo.png`
- Upon user approval of the candidate image, overwrite `assets/aubrey_liked_photo.png` with `assets/aubrey_liked_photo_candidate.png`.

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Verify `index.html` displays the updated full card image and `.liked-photo-pill` position cleanly.

---

## Implementation Checklist

- [x] **Step 1: Candidate Image Review**
  - [x] Extract candidate image `assets/aubrey_liked_photo_candidate.png` (y=304..730, 429x426 px) and present preview to user.

- [x] **Step 2: Asset Overwrite & HTML/CSS Update**
  - [x] Copy candidate image to `assets/aubrey_liked_photo.png`.
  - [x] Verify `.liked-photo-container` in `index.html`.

- [x] **Step 3: Verification**
  - [x] Confirmed complete 429x426 px uncropped card asset applied to `assets/aubrey_liked_photo.png`.

---

## Verification Plan

### Automated / Browser Verification
- Verify candidate image dimensions: 429x426 px.
- User review of preview image before updating `index.html`.
