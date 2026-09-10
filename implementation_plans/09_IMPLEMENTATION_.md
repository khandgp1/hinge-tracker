# Implementation Plan 09 - Native Hinge Overlapping Liked Photo Badge Design

This plan details updating the liked photo card in `index.html` to replicate native Hinge's overlapping pill badge layout, where the "You liked Aubrey's photo." badge floats over the bottom-right corner of the photo and extends downwards.

## User Directives & Technical Requirements

> [!IMPORTANT]
> - **Clean Photo Asset**: Crop `assets/aubrey_liked_photo.png` to contain the crisp photo card image.
> - **Native Vector Pill Badge**: Render the badge as a native HTML element (`.liked-photo-pill`) with Georgia italic serif font, blush background (`#f7ebe6`), and subtle drop shadow.
> - **Overlapping Position**: Set `.liked-photo-container` to `overflow: visible;` and position `.liked-photo-pill` with `position: absolute; bottom: -12px; right: -4px;` so it hangs gracefully over the photo's bottom-right edge.

---

## Technical Architecture

```
+-------------------------------------------------+
|  Aubrey Chat Feed Item (Right Aligned 78% Width)|
|                                                 |
|  +-------------------------------------------+  |
|  |                                           |  |
|  |   [ Aubrey Liked Photo Image ]            |  |
|  |   (Rounded 16px card)                     |  |
|  |                                           |  |
|  +-------------------------------------------+  |
|                                [ You liked   |  (Badge hangs -12px
|                                  Aubrey's    |   below bottom edge)
|                                  photo. ]    |
+-------------------------------------------------+
```

---

## Proposed Changes

### Web Application Assets & HTML/CSS

#### [MODIFY] `assets/aubrey_liked_photo.png`
- Re-crop `assets/aubrey_liked_photo.png` to contain strictly the photo card image.

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Styling**:
   - Update `.liked-photo-container`:
     `position: relative; max-width: 78%; margin: 8px 4px 24px auto; overflow: visible;`
   - Update `.liked-photo-img`:
     `width: 100%; height: auto; display: block; border-radius: 16px;`
   - Update `.liked-photo-pill`:
     `position: absolute; bottom: -12px; right: -4px; background: #f7ebe6; color: #111111; font-family: Georgia, "Times New Roman", serif; font-style: italic; font-size: 14px; padding: 8px 16px; border-radius: 20px; box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12); z-index: 5; white-space: nowrap;`

2. **JavaScript Data Feed (`aubreyChatData`)**:
   - Update `renderAubreyChat()` to output:
     ```html
     <div class="liked-photo-container">
       <img src="assets/aubrey_liked_photo.png" alt="Liked Photo" class="liked-photo-img">
       <div class="liked-photo-pill">You liked Aubrey's photo.</div>
     </div>
     ```

---

## Implementation Checklist

- [x] **Step 1: Clean Photo Asset Crop**
  - [x] Crop `assets/aubrey_liked_photo.png` to contain the photo image.

- [x] **Step 2: HTML & CSS Overlapping Badge Implementation in `index.html`**
  - [x] Update `.liked-photo-container`, `.liked-photo-img`, and `.liked-photo-pill` CSS in `index.html`.
  - [x] Update `renderAubreyChat()` to render the native `.liked-photo-pill` HTML badge inside the container.

- [x] **Step 3: Verification**
  - [x] Verify in browser subagent that the badge overlaps the bottom-right corner of the photo card and extends downwards.

---

## Verification Plan

### Automated / Browser Verification
- Serve `index.html` and inspect UI:
  - Open Aubrey chat view overlay.
  - Verify `assets/aubrey_liked_photo.png` is right-aligned (78% width).
  - Verify the blush text pill hangs over the bottom-right corner extending below the photo edge.
