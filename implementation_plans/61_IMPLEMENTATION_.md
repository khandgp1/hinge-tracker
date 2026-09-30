# 61 — Add Smirk Emoji (😏) Template and Detection Support

## Goal

Add native detection for the smirking face emoji (**😏**) in chat screenshots (such as Priya's reply `"Thank you 😏"` in `test_chats/Priya_Chat_2.jpg`), ensuring it is accurately detected and merged into message text in both received (grey) and sent (purple) bubbles.

---

## Design Decisions (from `/grill-me` alignment)

1. **Asset Sourcing**:
   - Extract the 28x28 iOS smirk template directly from [`test_chats/Priya_Chat_2.jpg`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/test_chats/Priya_Chat_2.jpg) ($x=227..255, y=863..891$) to preserve native iOS rendering, pixel density, and anti-aliasing.
   - Save the asset to [`assets/emojis/smirk.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/assets/emojis/smirk.png).

2. **Multi-Bubble Color Support (Grey & Purple)**:
   - In [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py), support circular masking during template matching so that the circular emoji face matches cleanly regardless of whether the bubble background is grey (received) or purple/lavender (sent).

3. **Text Merging**:
   - When detected adjacent to a message line, attach with a standard single-space separator (e.g. `"Thank you 😏"`).

---

## Proposed Changes

### 1. Template Asset Generation: [`assets/emojis/smirk.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/assets/emojis/smirk.png)
- Extract the 28x28 pixel region from `test_chats/Priya_Chat_2.jpg` containing the smirk emoji.
- Save as [`assets/emojis/smirk.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/assets/emojis/smirk.png).

### 2. Backend Template Registration & Masked Matching: [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)
- In `EMOJI_TEMPLATES`:
  ```python
  "😏": {
      "file": os.path.join(BASE_DIR, "assets", "emojis", "smirk.png"),
      "base_width": 591,
      "base_size": 28,
      "threshold": 0.82
  }
  ```
- In `detect_emojis(img)`:
  - Generate a circular mask for scaled templates so template matching evaluates the emoji face pixels rather than the corner background pixels.
  - Utilize masked template matching (`cv2.TM_CCORR_NORMED` with mask or circular foreground weighting) to enable high-confidence matching in both sent and received bubbles.

---

## Implementation Checklist

- [x] **Step 1: Extract and Save Smirk Template Asset**
  - [x] Extract the 28x28 smirk emoji from `test_chats/Priya_Chat_2.jpg`.
  - [x] Save to `assets/emojis/smirk.png` and verify dimensions (28x28x3).

- [x] **Step 2: Update `server.py` Emoji Configuration & Matching**
  - [x] Register `"😏"` in `EMOJI_TEMPLATES` in `server.py`.
  - [x] Update `detect_emojis()` to support circular masking for cross-color bubble detection (grey and purple).
  - [x] Verify `detect_emojis()` finds `😏` with high confidence on `Priya_Chat_2.jpg`.

- [x] **Step 3: End-to-End Verification**
  - [x] Test `parse_chat_images([img1, img2], match_name='Priya')` to confirm message 7 is parsed as `"Thank you 😏"`.
  - [x] Verify live `/api/parse-chat` HTTP endpoint returns `"Thank you 😏"`.
  - [x] Run regression check across other test chats (`Sydney`, `Sakshi`, `Tess`).
