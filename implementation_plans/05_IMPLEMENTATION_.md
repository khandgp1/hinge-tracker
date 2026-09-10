# Implementation Plan 05 - Update stitch.py to Remove Top Status Bar (Time & Battery Indicator)

This plan details the updates to [stitch.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py) to remove the top status bar (containing time, battery indicator, and signal icons) above the user profile name when stitching scrolling screenshots.

## Confirmed Technical Decisions (via /grill-me)
- **Separate Header/Footer Controls**: Introduce explicit CLI options `--keep-header` (default: `False`) and `--keep-footer` (default: `True`).
- **Status Bar Removal by Default**: Setting `keep_header` default to `False` ensures `stitch_sequence()` crops out static top header margins (time & battery bar) and omits prepending the top status strip from the output.
- **Bottom Footer Retention**: Retain bottom navigation bar / footer by default (`keep_footer=True`).
- **Backward Compatibility**: Preserve `--keep-header-footer` legacy flag support by mapping it to control both header and footer flags simultaneously.

---

## Technical Architecture & Code Changes

```
Before Update:
stitch_sequence(images, ..., keep_header_footer=True)
  ├── Detects static top/bottom margins
  ├── Saves top status bar (time & battery) as header_strip
  └── Stack: [header_strip, canvas, footer_strip] (Status bar remains visible at top)

After Update:
stitch_sequence(images, ..., keep_header=False, keep_footer=True)
  ├── Detects static top/bottom margins (crops status bar out of body frames)
  ├── Saves footer_strip only
  └── Stack: [canvas, footer_strip] (Status bar completely removed)
```

---

## Proposed Changes

### Stitching Module

#### [MODIFY] [stitch.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py)
- Update `parse_args()` to include `--keep-header` (default `False`), `--keep-footer` (default `True`), `--no-header`, `--no-footer`, and handle legacy `--keep-header-footer`.
- Update `stitch_sequence()` parameter signatures: `keep_header: bool = False`, `keep_footer: bool = True`.
- Decouple top header strip saving and prepending (`if keep_header: ...`) from bottom footer strip saving and appending (`if keep_footer: ...`).
- Pass `keep_header` and `keep_footer` from `main()` to `stitch_sequence()`.

---

## Implementation Checklist

- [x] **Step 1: Update CLI Arguments & Functions in stitch.py**
  - [x] Modify `parse_args()` in [stitch.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py) to add `--keep-header` and `--keep-footer`.
  - [x] Update `stitch_sequence()` in [stitch.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py) to decouple header and footer strip logic.
  - [x] Update `main()` call signature in [stitch.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py).

- [x] **Step 2: Execution & Verification**
  - [x] Run `python3 stitch.py -i synthetic_frames_01 -o stitched.png`.
  - [x] Verify that top status bar (time & battery indicator) is removed while bottom footer is retained.

---

## Verification Plan

### Automated / Command-line Verification
- Run test stitch command:
  ```bash
  python3 stitch.py -i synthetic_frames_01 -o stitched.png
  ```
- Check output image dimension and inspect frame top boundary.
