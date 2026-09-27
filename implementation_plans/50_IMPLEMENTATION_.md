# 50 — Multi-Paragraph Chat Bubble Continuity & Accurate Message Grouping

## Goal

Fix the issue where multi-paragraph text messages within a single Hinge chat bubble (such as the 3-paragraph message in `Tess_3.jpg`) are split into multiple separate bubbles. Implement color-aware vertical bubble continuity checking in `server.py`, harden top photo card detection against large text bubbles, and support paragraph newlines in `index.html`.

---

## Detailed Root Cause Analysis

### 1. Hardcoded Vertical Gap Threshold (`gap < 25`)
In `server.py`:
```python
if grouped and grouped[-1]["type"] == item["type"] and item["type"] in ("sent", "received"):
    prev_box = grouped[-1]["box"]
    curr_box = item["box"]
    gap = curr_box["pixelY"] - (prev_box["pixelY"] + prev_box["pixelHeight"])
    if gap < 25:
        grouped[-1]["text"] += " " + item["text"]
        grouped[-1]["box"]["pixelHeight"] = (curr_box["pixelY"] + curr_box["pixelHeight"]) - prev_box["pixelY"]
        continue
```
* **Normal line wraps within a paragraph**:
  Text lines sit ~11–13px apart vertically (`gap = 11..13px < 25px`), so lines merge correctly.
* **Paragraph breaks within the same bubble**:
  An empty line / paragraph break in Hinge creates a vertical gap of **~46px to 50px**.
  Because `46px > 25px`, the grouping logic prematurely terminates the bubble and starts a new one, turning 1 message into 3 separate bubbles.

### 2. Lack of Visual Canvas Continuity Detection
In Hinge:
* **Between separate bubbles**: The app's white canvas background (`rgb(255, 255, 255)` or `> 250` across all RGB channels) runs continuously between the bubbles.
* **Between paragraphs in the same bubble**: The vertical gap is completely filled by the bubble's background color (e.g. lavender `[213, 196, 210]` or grey `[237, 237, 237]`).
Relying solely on a 1D pixel distance cannot differentiate between two separate bubbles that are close together versus a single bubble with a paragraph break.

### 3. Photo Card False-Positive on Tall Bubbles
In `server.py` (`parse_chat_images` lines 308–327):
* Connected components search for any non-white region (`gray < 248`) where `cw > w * 0.45` and `ch > 180` and `area > 30000`.
* A large 7-line bubble like the one in `Tess_3.jpg` (width = 457px, height = 359px, area = 160,766px) fits these dimensions.
* Without a color variance or photo texture check, the parser misidentifies large solid-color text bubbles as photo cards and strips out words (e.g. consuming `"shots."` as the card comment).

### 4. Frontend CSS White-space Handling
In `index.html`:
* `.bubble` has `word-break: break-word;` but lacks `white-space: pre-line;` or `white-space: pre-wrap;`.
* Without this, joining paragraphs with `\n\n` in the JSON response would collapse into single spaces in the browser DOM.

---

## Architecture & Algorithm Redesign

```
  ┌────────────────────────────────────────────────────────┐
  │ haha I'm open to it but no.                            │
  │                                                        │ ── Gap = 46px
  │ [ Vertical corridor sampled at bubble fill color ]     │    Color = [213, 196, 210] (NOT white)
  │                                                        │    -> CONTINUOUS BUBBLE (append "\n\n")
  │ I have a photographer friend and I                     │
  │ always enjoy helping him out.                          │ ── Gap = 11px (< 25px) -> same paragraph
  │ Selecting locations, setting up his                    │ ── Gap = 11px (< 25px) -> same paragraph
  │ shots.                                                 │ ── Gap = 12px (< 25px) -> same paragraph
  │                                                        │
  │ [ Vertical corridor sampled at bubble fill color ]     │ ── Gap = 49px (NOT white)
  │                                                        │    -> CONTINUOUS BUBBLE (append "\n\n")
  │ sweathouz is the last place I sent him.                │
  │ looks artsy. what do you think?                        │ ── Gap = 13px (< 25px) -> same paragraph
  └────────────────────────────────────────────────────────┘
                              │
                    [ White Canvas Gap ]                     ── White background (R,G,B > 250)
                              │                                 -> SEPARATE BUBBLES
  ┌────────────────────────────────────────────────────────┐
  │ Next Bubble...                                         │
  └────────────────────────────────────────────────────────┘
```

### Proposed Bubble Grouping Rules
1. **Intra-paragraph merge (`gap < 25`)**:
   Merge with space: `grouped[-1]["text"] += " " + item["text"]`.
2. **Inter-paragraph continuity check (`25 <= gap <= 75`)**:
   Sample vertical pixels between `prev_box` bottom and `curr_box` top in the x-range overlapping both boxes.
   - If the sampled pixels match the bubble's color (sent purple or received grey) and are **not white canvas** (`mean_rgb < 250`), merge with a paragraph break:
     `grouped[-1]["text"] += "\n\n" + item["text"]`.
   - If white canvas is detected between the boxes, do not merge; emit as a separate bubble.
3. **Photo Card Detection Guard**:
   Exclude candidate components from being treated as photo cards if:
   - They consist of uniform flat bubble color (low color standard deviation across the inner card area).
   - They lack an associated photo pill or image variance typical of photos.

---

## Proposed Changes

### 1. Backend Server (`server.py`)

#### [MODIFY] [server.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)
* **Add bubble continuity helper function**:
  `is_continuous_bubble(stitched, prev_box, curr_box, msg_type)`:
  Inspects the vertical strip between `prev_box['pixelY'] + prev_box['pixelHeight']` and `curr_box['pixelY']`. Checks that pixels remain non-white and retain bubble chromaticity.
* **Update Grouping Loop**:
  - For `gap < 25`: merge with `" "`
  - For `25 <= gap <= 75`: test `is_continuous_bubble()`. If true, merge with `"\n\n"` and update bounding box height.
* **Guard Top Photo Card Detection**:
  - Verify that the detected component has photographic texture (e.g. `np.std(card_interior) > 20`) or has a valid photo pill rather than a solid bubble background.

### 2. Frontend Styles (`index.html`)

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
* Add `white-space: pre-line;` to `.bubble`:
  ```css
  .bubble {
    padding: 11px 15px;
    font-size: 15px;
    line-height: 1.35;
    max-width: 80%;
    letter-spacing: -0.01em;
    word-break: break-word;
    white-space: pre-line;
  }
  ```
  This preserves the paragraph breaks visually inside the bubble while retaining normal responsive word wrapping.

---

## Verification Plan

### Automated Verification
1. Run `parse_chat_images` in Python directly on `test_chats/Tess_3.jpg`:
   - Verify that the message starting with `"haha I'm open to it but no."` and ending with `"what do you think?"` is parsed as **ONE single sent message** containing all 3 paragraphs joined by `\n\n`.
   - Verify that `"shots."` is properly included in the text and not consumed as a photo card comment.
   - Verify the total message count matches expectations (no phantom split messages).
2. Regression check on existing chat test files:
   - `test_chats/Tess_1.jpg`
   - `test_chats/Aubrey_1.jpg`
   - `test_chats/Sydney_1.jpg`
   - Confirm no regression on liked photos, timestamps, or system pills.

### Visual & Browser Verification
1. Open `http://localhost:8080/` in browser or view rendered modal.
2. Ingest `test_chats/Tess_3.jpg` and verify the single purple bubble renders with clean paragraph spacing matching native Hinge.

---

## Progress Checklist

- [x] **Step 1:** Add bubble continuity detection (`is_continuous_bubble`) and paragraph break handling (`\n\n`) to `server.py`.
- [x] **Step 2:** Guard photo card connected component detection against large solid-color text bubbles in `server.py`.
- [x] **Step 3:** Add `white-space: pre-line;` to `.bubble` in `index.html`.
- [x] **Step 4:** Execute automated parsing verification script on `Tess_3.jpg` and verify all 3 paragraphs remain in a single message with `"shots."` intact.
- [x] **Step 5:** Run regression tests across `Tess_1.jpg`, `Aubrey_1.jpg`, and `Sydney_1.jpg`.
- [x] **Step 6:** Review rendered output and verify UI appearance.
