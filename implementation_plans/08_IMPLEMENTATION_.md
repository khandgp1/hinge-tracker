# Implementation Plan 08 - Include Complete Liked Photo Card Image in Native Chat View

This plan details updating the native HTML/CSS chat view in `index.html` to include the complete uncropped liked photo card image (including the full photo and the "You liked Aubrey's photo." text pill overlay).

## User Directives & Review Required

> [!IMPORTANT]
> - **Uncropped Card Image**: Do not crop out the photo edges or text. Extract the complete card segment from `Aubrey_Chat.png` into `assets/aubrey_liked_photo.png` so it includes the full photo and the "You liked Aubrey's photo." text badge exactly as captured in the original screenshot.
> - **Clean Layout**: Display `assets/aubrey_liked_photo.png` directly inside `.liked-photo-container` in `index.html` without duplicating overlay HTML pills.

---

## Technical Architecture

```
+------------------------------------------+
|  Aubrey Chat Overlay View (Native HTML)  |
|  +------------------------------------+  |
|  | [<]  Aubrey                        |  |  (Fixed Top Header)
|  +------------------------------------+  |
|  |                                    |  |
|  |  [ Priority Like Banner Card ]     |  |  (Top prompt banner)
|  |                                    |  |
|  |  [ Sat, Aug 8 3:23 PM ]            |  |  (Timestamp)
|  |                                    |  |
|  |  [ Complete Liked Photo Card Image]|  |  (Uncropped aubrey_liked_photo.png
|  |   - Full photo + text pill         |  |   including original text badge)
|  |                                    |  |
|  |  [ Dynamic Received/Sent Bubbles ] |  |  (Flexbox CSS message bubbles)
|  |                                    |  |
|  +------------------------------------+  |
|  | [ Send a message ...          ||| ]|  |  (Fixed Bottom Footer Bar)
+------------------------------------------+
```

---

## Proposed Changes

### Web Application Assets

#### [NEW] `assets/aubrey_liked_photo.png`
- Extract the full uncropped liked photo card segment from `Aubrey_Chat.png` (including the photo and the "You liked Aubrey's photo." text overlay pill) as a clean PNG image.

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Simplify `.liked-photo-container` to render `<img src="assets/aubrey_liked_photo.png" alt="Liked Photo" class="liked-photo-img">`.
- Remove redundant HTML overlay pill tags to avoid duplicate text rendering.
- Ensure `.liked-photo-img` fills the container cleanly with `width: 100%`, `height: auto`, and `border-radius: 16px`.

---

## Implementation Checklist

- [x] **Step 1: Complete Image Asset Extraction**
  - [x] Extract `assets/aubrey_liked_photo.png` from `Aubrey_Chat.png` preserving the photo + text pill overlay intact.

- [x] **Step 2: HTML & CSS Update in `index.html`**
  - [x] Update `.liked-photo-container` markup in `index.html` to render the uncropped `assets/aubrey_liked_photo.png`.
  - [x] Adjust CSS rules for seamless full-width display.

- [x] **Step 3: Verification**
  - [x] Verify that the full image card (photo + text) displays crisp and complete under "Sat, Aug 8 3:23 PM".

---

## Verification Plan

### Automated / Browser Verification
- Serve `index.html` and inspect UI:
  - Open Aubrey chat overlay.
  - Confirm `assets/aubrey_liked_photo.png` displays the complete photo and original text pill overlay with full clarity.
