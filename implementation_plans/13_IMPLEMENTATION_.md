# Implementation Plan 13 - Complete Text Bubble Overlap Alignment

This plan details adjusting the native HTML text bubble overlay (`.liked-photo-pill`) in `index.html` so that it completely and seamlessly overlaps the baked-in text bubble in `assets/aubrey_liked_photo.png`.

## User Directives & Technical Requirements

> [!IMPORTANT]
> - **100% Complete Overlap**: The HTML text bubble badge (`.liked-photo-pill`) must completely cover and obscure the underlying baked-in text bubble present in `assets/aubrey_liked_photo.png`. No edges, text, or shadows of the underlying baked-in text bubble should peek out.
> - **Preserve Native Hinge Typography**: Maintain Georgia italic 14px font, `#f7ebe6` background, and 20px border radius while tuning padding and positioning (`bottom`/`right`/`min-width`).
> - **Pure CSS Approach**: Achieve complete overlap via CSS styling adjustments in `index.html`.

---

## Technical Architecture & Overlap Analysis

```
+-------------------------------------------------------------+
| .liked-photo-container (max-width: 78%)                     |
|                                                             |
| +---------------------------------------------------------+ |
| |                                                         | |
| |   assets/aubrey_liked_photo.png (429x426 px)            | |
| |                                                         | |
| |   [ Underlying Baked-in Text Bubble in Image ]          | |
| |                                                         | |
| +---------------------------------------------------------+ |
|                        ===================================  |
|                       | HTML Overlay .liked-photo-pill    | | (Covers 100% of underlying
|                       | "You liked Aubrey's photo."       | |  baked-in bubble)
|                        ===================================  |
+-------------------------------------------------------------+
```

---

## Proposed Changes

### Web Application & CSS Styling

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Update `.liked-photo-pill` CSS rule to expand bounds and adjust offsets:
  - Increase horizontal and vertical padding (e.g., `padding: 10px 20px;`).
  - Set `min-width` / `bottom` / `right` position offsets so all 4 bounding edges of the underlying image bubble are obscured.

---

## Implementation Checklist

- [x] **Step 1: CSS Overlap Alignment in `index.html`**
  - [x] Adjust `.liked-photo-pill` padding, `bottom`, `right`, and `min-width` CSS in `index.html`.
  - [x] Test layout in browser preview to verify 100% overlap.

- [x] **Step 2: Verification**
  - [x] Verify using browser subagent/python pixel testing that zero trace of the underlying image text bubble is visible around or behind the top HTML bubble.

---

## Verification Plan

### Automated / Browser Verification
- Launch local HTTP server and view `index.html` in browser subagent.
- Open Aubrey chat overlay.
- Inspect the liked photo card and confirm 100% complete overlap.
