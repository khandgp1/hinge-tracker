# Implementation Plan - Scrolling Screenshot Stitcher (Python)

This document details the finalized implementation plan for a Python-based utility that automatically stitches multiple overlapping web or mobile app screenshots into a single, continuous, high-resolution image.

## Key Design Choices (Finalized via /grill-me)
- **Tech Stack**: Python 3 using OpenCV (`cv2`), `numpy`, and Pillow (`PIL`).
- **UI Masking**: Automated static region detection (identifying invariant top/bottom rows across consecutive frames) supplemented by optional `--crop-top` and `--crop-bottom` CLI overrides.
- **Registration & Blending**: 1D Normalized Cross-Correlation (NCC) to compute vertical displacement $\Delta y$ with linear alpha cross-fade blending across overlap boundaries to eliminate visual seams.
- **CLI Interface**: Flexible command-line tool (`stitch.py`) accepting directory paths (`--input ./screenshots/`) or explicit image paths (`img1.png img2.png`), with configurable output path (`--output stitched.png`).

---

## Technical Architecture & Algorithm Flow

```
+--------------------------+
|  Load & Order Images     | (Sort filenames / CLI arguments)
+------------+-------------+
             |
             v
+--------------------------+
| Static Region Detection  | (Auto-detect invariant header/footer rows)
+------------+-------------+
             |
             v
+--------------------------+
|  Central Region Crop     | (Apply top/bottom insets)
+------------+-------------+
             |
             v
+--------------------------+
| 1D NCC Registration      | (Compute vertical scroll displacement Δy)
+------------+-------------+
             |
             v
+--------------------------+
| Canvas & Alpha Blending  | (Stitch strips with gradient cross-fade)
+------------+-------------+
             |
             v
+--------------------------+
|  Save Output Image       | (PNG / JPEG output)
+--------------------------+
```

---

## Implementation Checklist

- [x] **Step 1: Setup & Dependency Configuration**
  - [x] Create `stitch.py` script template.
  - [x] Ensure `opencv-python`, `numpy`, and `Pillow` are installed and declared in project.

- [x] **Step 2: CLI Argument Parser**
  - [x] Implement support for directory input (`--input`, `-i`) or positional image list.
  - [x] Implement options: `--output` / `-o` (default `stitched.png`), `--crop-top`, `--crop-bottom`, `--auto-crop` (default enabled), `--blend-height`.

- [x] **Step 3: Image Loading & Static Header/Footer Detection**
  - [x] Load image sequence and validate dimensions.
  - [x] Implement `detect_static_margins(img1, img2)` comparing top rows and bottom rows for zero variance / identical pixel rows across frames.

- [x] **Step 4: Vertical Scroll Registration (1D NCC)**
  - [x] Convert images to grayscale.
  - [x] Slice lower overlap band of `img[k]` and search across upper region of `img[k+1]`.
  - [x] Compute `cv2.matchTemplate(..., cv2.TM_CCOEFF_NORMED)` to determine exact Y-displacement $\Delta y$ with peak confidence threshold.

- [x] **Step 5: Image Canvas Assembly & Alpha Seam Blending**
  - [x] Allocate master canvas of height $Y_{total} = H_0 + \sum \Delta y_k$.
  - [x] Place initial image onto canvas.
  - [x] For subsequent images, blend overlap strip using linear alpha gradient ($0.0 \to 1.0$) across seam region.

- [x] **Step 6: Verification & Test Suite**
  - [x] Test CLI execution with mock scroll frames or real website screenshots.
  - [x] Verify seamless visual transition and correct text alignment without ghosting.

---

## Verification Plan

### Automated / Synthetic Testing
- Generate synthetic test images (e.g. text/image tall canvas split into 3 overlapping scroll viewports).
- Run `python stitch.py --input ./synthetic_frames/ -o test_stitched.png`.
- Assert output pixel dimensions match expected total unrolled height.

### Manual Verification
- Execute script on actual scrolling screenshots.
- Audit visual output for pixel-perfect vertical alignment and invisible seams.
