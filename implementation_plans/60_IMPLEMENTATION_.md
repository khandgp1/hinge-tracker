# 60 — Robust Chat Stitching, Scrollbar Elimination, and Photo Card OCR Optimization

## Goal

Resolve the stitching and chat ingestion failures observed with multi-screenshot uploads (specifically demonstrated by `test_chats/Priya_Chat_1.jpg` and `test_chats/Priya_Chat_2.jpg`):
1. Fix the server crash (`NameError: is_recv_pill`) in [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py).
2. Eliminate in-photo OCR noise (such as chalkboard signage like "DR TEA", "TIEC MEI") from hijacking photo card comments and creating phantom sent bubbles.
3. Prevent duplicate liked photo card generation.
4. Enhance [`stitch.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py) with smart seam placement in clean whitespace bands instead of cutting across photo cards.
5. Completely eliminate the iOS scrollbar from both displacement calculations and the final stitched visual output.
6. Cleanly trim residual header tab divider lines.

---

## Root Cause Analysis

1. **Server Crash (`is_recv_pill` undefined)**:
   - In [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py#L800-L805), `is_recv_pill` is referenced on line 801 without being defined in scope, raising an uncaught `NameError` (HTTP 500) whenever multi-image chat screenshots are parsed.

2. **OCR Signage Hijack & Duplicate Cards**:
   - Photos with background text (e.g. coffee shop or tea menus) produce Vision OCR tokens inside the photo card.
   - In [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py#L528-L560), `obs` is iterated top-to-bottom. The generic fallback branch captured background text (`TIEC MEI`) before reaching the actual liked photo pill (`You liked Priya's photo.`).
   - Consequently, unconsumed background tokens were emitted as sent message bubbles, and the unconsumed like pill triggered a second, duplicate photo card extraction downstream.

3. **Stitch Seam Cut Across Photo Card**:
   - In [`stitch.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py#L329-L346), the canvas switches to the incoming frame at `img_y + blend_height` ($y \approx 331$), slicing directly across the girls' photo, even though Frame 0 already contained the complete, intact photo card down to $y = 533$, and clean solid white rows existed at $y = 542..562$.

4. **Floating iOS Scrollbar**:
   - The iOS scrollbar (columns $w-9$ to $w-5$) appears in different vertical positions in each frame.
   - This introduces noise into 1D NCC displacement calculations and leaves fragmented gray bars on the right margin of the final stitched image.

---

## Proposed Changes

### 1. [`stitch.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py)

#### A. Scrollbar Masking & Visual Elimination
- In `find_vertical_displacement`:
  - Slice `[:, :w - 25]` when calculating Mean Absolute Difference so the moving iOS scrollbar does not distort $\Delta y$.
- In `stitch_sequence` (and helper `remove_scrollbar_strip`):
  - Inpaint / overwrite the scrollbar margin (columns $w-10$ to $w$) using the clean adjacent background column ($w-15$), guaranteeing **zero scrollbar remnants in the final stitched image**.

#### B. Smart Whitespace Seam Selection
- In `stitch_sequence`:
  - When placing `cropped_images[i]` onto the canvas overlapping `cropped_images[i-1]`, examine the overlap zone ($img\_y$ to $prev\_bottom$).
  - Instead of abruptly cutting at $img\_y$, scan for a horizontal row of uniform white background (`min(row) >= 248`) that does not intersect any photo card or text bubble.
  - Cut/blend across that neutral whitespace row, preserving photos and message bubbles intact.

#### C. Clean Header Margin Trimming
- Adjust the auto-crop static top padding buffer (from +3px to +7px when `seq_top > 0`) to cleanly eliminate the anti-aliased bottom divider of the active "Chat" tab.

---

### 2. [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)

#### A. Fix `is_recv_pill` NameError
- Define `is_recv_pill = "liked your" in pill_text.lower() or item["box"]["pixelX"] < w * 0.35` before constructing `pill_item`.

#### B. Targeted Like Pill Matching & In-Photo Text Suppression
- In `top_photo_card` detection:
  - First search for explicit like pill phrases (`"you liked"`, `"liked your"`, `"liked" ... "photo"`) within the lower half of the card.
  - If found, bind it as `card_comment_text` and mark the like pill observation as consumed.
  - Suppress/consume all other OCR observations located inside the bounding box of `best_card`, preventing background sign text (like `"DR TEA"`) from turning into message bubbles.

#### C. Prevent Duplicate Liked Photo Generation
- Ensure that if `top_photo_card` has already consumed a like pill, downstream pill classification ignores duplicate/re-detected like pills for the same card.

---

## Implementation Checklist

- [x] **Step 1: Fix `stitch.py` Scrollbar Removal & Alignment**
  - [x] Update `find_vertical_displacement` to ignore the rightmost 25px scrollbar channel.
  - [x] Add `clean_scrollbar_channel` helper in `stitch.py` to replace columns $w-10$ to $w$ with the adjacent background column.
  - [x] Verify displacement calculation on `test_chats/Priya_Chat_1.jpg` and `test_chats/Priya_Chat_2.jpg`.

- [x] **Step 2: Add Smart Seam Selection in `stitch.py`**
  - [x] Implement whitespace scan in the overlap window between adjacent frames.
  - [x] Transition between frames along the detected whitespace row rather than cutting through photos.
  - [x] Increase top auto-crop buffer slightly (+7px) to cleanly clear the Hinge tab bar divider line.
  - [x] Run test stitch and verify visual output with zero scrollbar, no seam line, and full photo fidelity.

- [x] **Step 3: Fix `server.py` Parsing & Ingestion Bugs**
  - [x] Restore `is_recv_pill` definition at line 800 to fix the `NameError`.
  - [x] Update photo card comment detector to prioritize `"liked"` / `"photo"` pills.
  - [x] Filter out in-photo OCR text within the photo card bounding box (`DR TEA`, `TIEC MEI`, etc.).
  - [x] Prevent duplicate card generation from previously consumed like pills.

- [x] **Step 4: End-to-End Verification**
  - [x] Run `python3 -c` script executing `parse_chat_images([img1, img2], match_name='Priya')`.
  - [x] Verify extracted messages:
    - 1 Photo Card ("You liked Priya's photo.") with clean cropped image.
    - No phantom "DR TEA" sent bubble.
    - No duplicate liked photo card.
    - Proper sequence of timestamps, prompts, sent bubbles, and received bubble with avatar.
  - [x] Verify final stitched image visual quality and absence of any scrollbar.
