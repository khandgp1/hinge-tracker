# 65 — Add Popcorn Emoji (🍿) Template and Detection Support

## Goal

Add native detection for the popcorn emoji (**🍿**) in chat screenshots—specifically in Sakshi's chat (`test_chats/Sakshi_Test/Sakshi_chat.jpg`) where the final sent message concludes with `"idc how many Jurassic Parks come out .. best movies 🍿"`—ensuring it is accurately detected, corridor-aligned, and merged into message text across both sent (purple) and received (grey) chat bubbles.

---

## Design Decisions

1. **Template Asset Sourcing & Dimensions**:
   - Extract the 28×28 iOS popcorn template directly from [`test_chats/Sakshi_Test/Sakshi_chat.jpg`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/test_chats/Sakshi_Test/Sakshi_chat.jpg) at ($x=349..377, y=1097..1125$) to preserve Apple Color Emoji native rendering, retina pixel density, and anti-aliasing.
   - Save to [`assets/emojis/popcorn.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/assets/emojis/popcorn.png).

2. **Template Matching & Cross-Bubble Background Handling**:
   - Existing face emojis (`😄`, `😏`) rely on circular masking (`circle_mask`) to swap purple sent backgrounds (`#D7C4DA` / `#701A51`) with grey received backgrounds (`#EBEBEB` / `#F0F0F0`).
   - Popcorn (`🍿`) is bucket-shaped (rectangular with flared top kernels) rather than circular.
   - For popcorn, create or derive a foreground/alpha mask (non-background pixels) or evaluate both native purple template and a grey-background variant (`popcorn_grey.png` or dynamically generated) so matching produces high confidence ($\ge 0.85$) on both sent and received bubbles without false corner mismatches.

3. **Text Line Alignment & Bubble Grouping**:
   - In `parse_chat_images()`, OCR currently yields two text lines in Sakshi's bubble:
     - Line 1: `"idc how many Jurassic Parks come"`
     - Line 2: `"out .. best movies"`
   - The popcorn emoji is horizontally positioned to the right of `"out .. best movies"` in the same vertical corridor ($y \approx 1104$, $h \approx 22$).
   - Trailing emoji alignment attaches `🍿` to Line 2: `"out .. best movies 🍿"`.
   - The existing bubble grouping aggregates adjacent lines within the same sent bubble, producing the complete message:
     `"idc how many Jurassic Parks come out .. best movies 🍿"`.

4. **Frontend & Deduplication Compatibility**:
   - Frontend text rendering in [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html) supports UTF-8 emoji strings natively.
   - Deduplication in `index.html` uses `.replace(/[^a-z0-9]/g, '')`, ensuring message deduplication against existing Firestore history works transparently.

---

## Proposed Changes

### 1. Template Asset Generation: [`assets/emojis/popcorn.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/assets/emojis/popcorn.png)
- Extract the 28×28 pixel region from `test_chats/Sakshi_Test/Sakshi_chat.jpg` containing the popcorn emoji ($x=349..377, y=1097..1125$).
- Save as [`assets/emojis/popcorn.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/assets/emojis/popcorn.png).
- Optionally generate a grey-background complementary asset [`assets/emojis/popcorn_grey.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/assets/emojis/popcorn_grey.png) for received bubble matching.

### 2. Backend Template Registration: [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)
- Register `"🍿"` in `EMOJI_TEMPLATES`:
  ```python
  "🍿": {
      "file": os.path.join(BASE_DIR, "assets", "emojis", "popcorn.png"),
      "base_width": 591,
      "base_size": 28,
      "threshold": 0.82
  }
  ```
- In `detect_emojis(img)`:
  - Ensure background swapping accommodates non-circular shapes (using foreground color-distance masking or a dedicated grey template file) so template cross-correlation scores remain above threshold in both sent purple and received grey bubbles.

---

## Implementation Checklist

- [x] **Step 1: Extract and Save Popcorn Emoji Template Asset**
  - [x] Extract the 28×28 popcorn emoji from `test_chats/Sakshi_Test/Sakshi_chat.jpg`.
  - [x] Save to `assets/emojis/popcorn.png` and verify dimensions (28×28×3).
  - [x] Generate corresponding grey-background variant or mask for received bubble detection (`assets/emojis/popcorn_grey.png`).

- [x] **Step 2: Update `server.py` Emoji Configuration**
  - [x] Register `"🍿"` in `EMOJI_TEMPLATES` in `server.py`.
  - [x] Verify `detect_emojis()` produces score $\ge 0.85$ on `Sakshi_chat.jpg` (scored `1.0`).
  - [x] Ensure non-circular masking works cleanly without edge degradation via `file_grey` pairing.

- [x] **Step 3: Verification & Regression Testing**
  - [x] Test `parse_chat_images()` on `Sakshi_chat.jpg`: verify last message parses as `"idc how many Jurassic Parks come out .. best movies 🍿"`.
  - [x] Run regression check on `test_chats/Tess_Test/` (verify `😄` detection is preserved).
  - [x] Run regression check on `test_chats/Priya_Test/` (verify `😏` detection is preserved).
  - [x] Verify live `/api/parse-chat` HTTP endpoint output with popcorn emoji.
