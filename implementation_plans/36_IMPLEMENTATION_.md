# 36 — Make stitch.py Robust for Variable-Height and Profile Screenshots

## Goal

Fix `stitch.py` so it handles images whose cropped heights differ (such as real-world screenshots in `profile/`), resolving the NumPy broadcast error `operands could not be broadcast together with shapes (1060,591) (1041,591)`, while preserving existing functionality for `synthetic_frames/`.

---

## Root Cause Summary

1. **Height-blind slicing in `find_vertical_displacement`:**
   Lines 172–173 sliced `gray_upper[dy:h_up, :]` and `gray_lower[0:h_up - dy, :]`. When `h_low < h_up - dy`, Python truncated the `gray_lower` slice to `h_low`, while `gray_upper` had `h_up - dy` rows. Comparing the two arrays caused a broadcast shape mismatch.
2. **Asymmetric margin propagation:**
   In `stitch_sequence`, `detect_static_margins` is called on adjacent pairs sequentially. When pair 1–2 detected a 239 px top crop while pair 0–1 detected 215 px, the crop was never propagated backward to frame 0, causing frame 0 and frame 1 to have different body heights.

---

## Proposed Changes

### `stitch.py`

#### 1. Robust Overlap Slicing (`find_vertical_displacement`)
- Calculate the valid overlap height dynamically for each candidate shift `dy`:
  ```python
  overlap_h = min(h_up - dy, h_low)
  ```
- Skip iterations where `overlap_h < min_overlap_px`.
- Slice both upper and lower grayscale images strictly to `overlap_h`:
  ```python
  overlap_upper = gray_upper[dy:dy + overlap_h, :]
  overlap_lower = gray_lower[0:overlap_h, :]
  ```
- This guarantees identical shapes `(overlap_h, w)` regardless of whether `h_up == h_low`, `h_up > h_low`, or `h_up < h_low`.

#### 2. Margin Normalization across Sequence (`stitch_sequence`)
- In `stitch_sequence`, after detecting pairwise margins, propagate the detected static header and footer margins across all frames (or compute the uniform sequence margin) so that screenshots from the same screen capture session are cropped consistently.
- Still respect user-specified `--crop-top` and `--crop-bottom` overrides if provided.

#### 3. Pre-displacement Resizing Check
- Ensure any width scaling happens consistently before displacement calculation if images have varying widths.

---

## Progress Checklist

- [x] **Step 1:** Update `find_vertical_displacement` in `stitch.py` with dynamic `overlap_h` bounds slicing.
- [x] **Step 2:** Normalize margin detection in `stitch_sequence` across all frames for consistent header/footer removal.
- [x] **Step 3:** Verify backward compatibility by running `python3 stitch.py -i synthetic_frames -o test_synthetic.png`.
- [x] **Step 4:** Verify fix by running `python3 stitch.py -i profile -o profile_01.png` on the user's 9 profile screenshots.
- [x] **Step 5:** Clean up temporary test artifacts.

---

## Verification Plan

### Automated / Command-Line Tests
1. `python3 stitch.py -i synthetic_frames -o test_synthetic.png`
   - Expected: Exits with code 0, outputs stitched image matching previous dimensions without regression.
2. `python3 stitch.py -i profile -o profile_01.png`
   - Expected: Exits with code 0, successfully calculates displacements for all 9 frames (0 through 8), blends seams, and outputs `profile_01.png`.
3. Check image properties of `profile_01.png` (dimensions, valid PNG file).
