# 37 — Fix Stray Purple Header Border Artifact in Stitched Profile Screenshots

## Goal

Remove the slight purple / dark horizontal artifact appearing at the very top of `profile_01.png`, ensuring stitched screenshots start cleanly on the white profile card body.

---

## Root Cause Summary

1. In Hinge's navigation header, the active tab indicator is a purple bar located at rows **214–216** of the original screenshots (`profile/*.jpg`), followed by a 1px divider border at row **217**.
2. Rows **218+** are the clean white background of the first profile card.
3. In `stitch.py`, `detect_static_margins` uses a strict pixel difference threshold of `< 3.0`.
4. Due to JPEG compression ringing and anti-aliasing around the purple bar's edge, row 215 has a mean difference of `5.3`, causing the loop to stop prematurely at row 215 (or 216).
5. The uncropped rows 216 (purple underline) and 217 (divider line) are left at the top of Frame 0, creating a visible purple stripe at row 0 of `profile_01.png`.

---

## Proposed Changes

### `stitch.py`

#### 1. Header Boundary Edge Cleanup in `detect_static_margins`
- Adjust the detection threshold / boundary logic in `detect_static_margins` so that JPEG edge compression noise (diffs between 3.0 and 10.0) on sharp static header dividers does not cause premature truncation before the header divider ends.
- Alternatively, include a 2px safety trim (`header_padding = 2`) on detected static headers so that 1–2px anti-aliased navigation divider borders are cleanly cropped with the header rather than left attached to the body.

#### 2. Re-generate `profile_01.png`
- Re-run `python3 stitch.py -i profile -o profile_01.png`.
- Verify row 0 through 5 are completely free of purple or dark border artifacts and start on the clean white background.

---

## Progress Checklist

- [x] **Step 1:** Update `detect_static_margins` / `stitch_sequence` in `stitch.py` to cleanly cut through header divider lines and anti-aliasing boundaries.
- [x] **Step 2:** Verify that `synthetic_frames/` continues to stitch without regression.
- [x] **Step 3:** Re-run `python3 stitch.py -i profile -o profile_01.png`.
- [x] **Step 4:** Inspect the top rows of `profile_01.png` to confirm no purple pixels remain.

---

## Verification Plan

### Automated / Command-Line Tests
1. `python3 stitch.py -i synthetic_frames -o test_synthetic.png`
   - Verify code exits 0 and output dimensions and colors remain valid.
2. `python3 stitch.py -i profile -o profile_01.png`
   - Verify code exits 0 and inspect rows 0–5 of `profile_01.png`.
   - Verify RGB color values are in the white range (`> 245` across channels) with zero purple pixels (`(R > 50, B > 50, G < 70)`).
3. Clean up temporary test files (`test_synthetic.png`).
