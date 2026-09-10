# Implementation Plan 11 - Fix Top Crop on Liked Photo Card

This plan details fixing the top crop of Aubrey's liked photo card asset (`assets/aubrey_liked_photo.png`) so the entire top portion of the photo card (including the wall/background space above Aubrey's head) is fully preserved without truncation.

## User Directives & Technical Requirements

> [!IMPORTANT]
> - **Complete Uncropped Photo Card**: Re-extract `assets/aubrey_liked_photo.png` from `Aubrey_Chat.png` starting from the true top card boundary (y=372) down to the bottom card boundary (y=846), preserving both the top and bottom of the original photo card (dimensions: ~428x474 px).
> - **Native Pill Overlay Coverage**: Retain `.liked-photo-pill` in `index.html` positioned at the bottom-right corner (`bottom: -12px; right: -4px`) to cover the original baked-in text badge area cleanly.

---

## Technical Architecture

```
+-------------------------------------------------+
|  Aubrey Chat Feed Item (Right Aligned 78% Width)|
|                                                 |
|  +-------------------------------------------+  |
|  |  [ Full Top Background (y=372) ]          |  |  (Preserves top wall/bg)
|  |   Aubrey Liked Photo Image                |  |
|  |   (Full vertical card height ~428x474)    |  |
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
- Re-crop `assets/aubrey_liked_photo.png` from `Aubrey_Chat.png` using full top-to-bottom card bounds: y=372 to 846, x=131 to 559 (428x474 px).

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Verify `.liked-photo-container` cleanly displays the new 428x474 aspect ratio image with the vector pill overlay.

---

## Implementation Checklist

- [x] **Step 1: Re-crop Full Uncropped Photo Card Asset**
  - [x] Extract crop bounds y=372..846, x=131..559 from `Aubrey_Chat.png` to `assets/aubrey_liked_photo.png`.

- [x] **Step 2: HTML & CSS Verification in `index.html`**
  - [x] Verify image container aspect ratio and overlay pill position in `index.html`.

- [x] **Step 3: Verification**
  - [x] Re-extracted complete 428x474 px photo card asset preserving full top background and bottom hoodie area.

---

## Verification Plan

### Automated / Browser Verification
- Verify file dimensions via Python: `assets/aubrey_liked_photo.png` is 428x474 px.
- Serve `index.html` and verify Aubrey chat view displays complete photo card top and bottom.
