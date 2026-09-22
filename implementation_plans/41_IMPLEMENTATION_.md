# 41 — OCR Accuracy & Partial Row Filtering Refinement

## Goal

Refine the screenshot parsing engine in Hinge Tracker to fix OCR misrecognitions (**"Meredith"** misread as *"Anmaradith"* and **"Bem"** misread as *"Ram"*) and completely exclude truncated/partial match rows at the bottom of the screenshot (**"Bonnie"** cut off by the navigation bar, previously appearing as *"Match 5"*).

---

## User Review Required

> [!IMPORTANT]
> **Partial Row Exclusion**: Rows truncated at the bottom of the screen by the navigation bar (less than $20\%$ of image width in height) are now automatically discarded, ensuring only complete, untruncated match entries with visible names and complete avatars are imported.

---

## Root Causes & Solutions

### 1. Partial Row Truncation (Excluding Bonnie)
- **Problem**: Bonnie's row begins at divider line $y = 853$ and is cut off by the purple bottom navigation bar at $y = 923$, leaving only $70\text{px}$ ($0.15 \times \text{width}$, or $\approx 61\%$ of a full $114\text{px}$ row).
- **Solution**: Set the minimum row height to $\text{min\_row\_h} = \text{round}(w \times 0.20)$. This cleanly keeps full rows (height $\approx 114\text{px} \ge 94\text{px}$) while automatically excluding truncated partial rows like Bonnie ($70\text{px} < 94\text{px}$).

### 2. "Meredith" Character Splitting & Heart Removal
- **Problem**:
  1. A rigid binary cutoff (`val < 125`) destroyed the anti-aliased diagonal strokes of the capital `'M'`, splitting it into two vertical bars (`|  |`) that Tesseract read as `'An'`.
  2. The wide crop extended into the purple heart icon (💜), adding trailing OCR noise.
- **Solution**:
  1. Dynamically find the inter-word white gap ($> 10\text{px}$) and stop the crop *before* the purple heart icon begins.
  2. Preserve anti-aliased grayscale with contrast stretching rather than harsh thresholding, keeping the capital `'M'` strokes solid and connected.

### 3. "Bem" Contour Preservation & Single-Line PSM
- **Problem**: The lower loop of `'B'` thinned out under binary thresholding, and Tesseract's default multi-line PSM (`PSM.AUTO`) misclassified it as `'R'`.
- **Solution**:
  1. Retain anti-aliasing to keep the lower `'B'` loop closed.
  2. Set Tesseract's page segmentation mode to single text line (`tessedit_pageseg_mode: '7'`).

---

## Proposed Changes

### `index.html`

#### 1. Update Minimum Row Height Threshold
- In `analyzeScreenshotImage`:
  - Change row height validation from `rowH < Math.round(w * 0.14)` to:
    ```javascript
    const minRowH = Math.round(w * 0.20); // Requires full untruncated row
    if (rowH < minRowH || rowH > Math.round(w * 0.40)) {
      continue;
    }
    ```

#### 2. Dynamic Name Boundary Detection (Exclude Heart Icons)
- Scan the name row horizontally from the first dark character pixel.
- Trace character clusters and stop the crop at the first gap $> 10\text{px}$:
  - For **Meredith**, stops at $x \approx 105\text{px}$ (before the heart at $122\text{px}$).
  - For **Bem**, stops at $x \approx 57\text{px}$ (before the heart at $72\text{px}$).

#### 3. Anti-Aliased Grayscale Name Preprocessing
- Instead of hard binary thresholding (`val < 125 ? 0 : 255`), apply contrast-stretched grayscale with color suppression:
  - Preserves subpixel font curvature and stroke connections.
  - Cleans any background tint while leaving text crisp.

#### 4. Configure Tesseract Single-Line PSM
- Set Tesseract parameter:
  ```javascript
  await worker.setParameters({
    tessedit_pageseg_mode: '7' // Single text line
  });
  ```

---

## Progress Checklist

- [x] **Step 1:** Update the row height threshold in `analyzeScreenshotImage` to `Math.round(w * 0.20)` to exclude truncated rows.
- [x] **Step 2:** Implement dynamic inter-word gap detection to truncate name crops before badge/heart icons.
- [x] **Step 3:** Update name canvas preprocessing to use contrast-stretched anti-aliased grayscale rather than hard thresholding.
- [x] **Step 4:** Set Tesseract's `tessedit_pageseg_mode: '7'` (single text line mode).
- [x] **Step 5:** Verify with the user's test screenshot (`media_1789926022466.jpg`) in the browser:
  - Exactly 4 matches detected (Lauren, Mukta, Meredith, Bem).
  - Bonnie is completely excluded.
  - "Meredith" is spelled correctly.
  - "Bem" is spelled correctly.
- [x] **Step 6:** Verify backward compatibility with `hinge_view.jpeg` (all 7 rows detected).
- [x] **Step 7:** Document verification results in `walkthrough.md`.

---

## Verification Plan

### Automated / Browser Verification
1. Load `index.html` in browser.
2. Trigger `window.processScreenshotFile` with `media_1789926022466.jpg`.
3. Inspect review modal:
   - Confirm only 4 cards appear: **Lauren**, **Mukta**, **Meredith**, **Bem**.
   - Confirm Bonnie is excluded.
   - Confirm "Meredith" is spelled correctly without "Anmaradith".
   - Confirm "Bem" is spelled correctly without "Ram".
4. Trigger `window.processScreenshotFile` with `hinge_view.jpeg`.
   - Confirm all 7 default matches are detected and flagged as duplicates.
