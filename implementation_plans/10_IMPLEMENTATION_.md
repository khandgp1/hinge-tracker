# Implementation Plan 10 - Restore Full Uncropped Liked Photo Card with Overlay Coverage

This plan details re-extracting Aubrey's liked photo card asset (`assets/aubrey_liked_photo.png`) to preserve the complete uncropped vertical photo height from `Aubrey_Chat.png`, and positioning the native HTML/CSS `.liked-photo-pill` badge to cover any underlying original text.

## User Directives & Technical Requirements

> [!IMPORTANT]
> - **Full Uncropped Photo Height**: Re-extract `assets/aubrey_liked_photo.png` from `Aubrey_Chat.png` without cropping out the bottom portion of the photo.
> - **Overlay Text Coverage**: Position the native HTML/CSS overlay badge (`.liked-photo-pill`) so it sits directly over the baked-in text area at the bottom-right corner, covering it completely with a clean vector text pill.

---

## Technical Architecture

```
+-------------------------------------------------+
|  Aubrey Chat Feed Item (Right Aligned 78% Width)|
|                                                 |
|  +-------------------------------------------+  |
|  |                                           |  |
|  |   [ Aubrey Liked Photo Image ]            |  |
|  |   (Full vertical card height ~428x428)    |  |
|  |                                           |  |
|  |                             [ Native Pill |  (HTML overlay covers
|  |                               Badge ]     |   baked-in text area)
|  +-------------------------------------------+  |
+-------------------------------------------------+
```

---

## Proposed Changes

### Web Application Assets & HTML/CSS

#### [MODIFY] `assets/aubrey_liked_photo.png`
- Re-crop `assets/aubrey_liked_photo.png` from `Aubrey_Chat.png` using full card height bounds (y: 418 to 846, x: 131 to 559).

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Adjust `.liked-photo-pill` CSS positioning (`position: absolute; bottom: 12px; right: 12px;` or `-8px` / `-4px` offset) to perfectly mask the underlying baked-in text while displaying the sharp native vector text badge.

---

## Implementation Checklist

- [x] **Step 1: Re-extract Full Uncropped Photo Asset**
  - [x] Extract full card crop (y=418..846, x=131..559) from `Aubrey_Chat.png` to `assets/aubrey_liked_photo.png`.

- [x] **Step 2: HTML & CSS Overlay Alignment in `index.html`**
  - [x] Adjust `.liked-photo-container` and `.liked-photo-pill` CSS in `index.html` for pixel-perfect overlay coverage.

- [x] **Step 3: Verification**
  - [x] Extracted 428x428 full height card asset and verified CSS overlay badge position.

---

## Verification Plan

### Automated / Browser Verification
- Serve `index.html` and inspect UI:
  - Verify `assets/aubrey_liked_photo.png` displays full photo height.
  - Verify the blush pill badge cleanly covers the bottom-right text area without text leakage or awkward overhangs.
