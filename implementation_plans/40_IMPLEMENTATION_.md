# 40 — Dynamic Screenshot Row & Avatar Parser Overhaul

## Goal

Overhaul the screenshot parsing engine in Hinge Tracker to replace hardcoded coordinate slicing with **content-aware dynamic row detection**. The new engine will automatically detect row divider lines, filter out dynamic UI banners (such as "You're over the limit" purple banners and "Your turn" collapsible headers), accurately center circular avatar crops on each woman's face, and isolate the name line to eliminate garbled OCR output.

---

## Background & Root Cause

The initial implementation in `39_IMPLEMENTATION_.md` used fixed coordinate percentages (`startY = 0.0953 * h`, `stepY = 0.11875 * h`), which caused severe failures on real Hinge screenshots:
1. **Banner Displacement**: Variable top banners (e.g. the purple "over the limit" banner) pushed the true first match row down to $y \approx 400\text{px}$, causing the parser to slice the "Matches" heading and banner text as avatars.
2. **Vertical Drift**: Fixed stepping cut across row dividers, slicing body parts in half.
3. **Garbled OCR**: Because row boxes were misaligned, OCR read banner paragraphs and phone numbers, returning gibberish like `"LHigioTHYUuballotiln"` and `"NETdalHygHUWNIVE"`.

---

## Proposed Changes

### `index.html`

#### 1. Divider Line & Row Boundary Detection Algorithm
Replace static `startY` and `stepY` loops with a multi-step image analyzer:
- **Bottom Navigation Detection**: Scan upward from the bottom of the canvas to locate the top edge of the bottom navigation bar (identifies dark/purple/colored bar boundary).
- **Divider Line Scanner**: Scan $x \in [25\%, 95\%]$ across all vertical lines. Detect horizontal lines characterized by uniform light gray values ($225 \le \text{gray} \le 252$, $\text{std} < 4.0$) with contrast against white row backgrounds above and below.
- **Row Clustering**: Group adjacent divider scan lines into distinct row dividers $y_0, y_1, y_2, \dots$.

#### 2. Row Content Filtering (Banner & Header Rejection)
- Discard rows with non-white backgrounds (e.g., the purple warning banner with $\text{RGB} \approx 118, 64, 120$).
- Discard rows where the height is outside valid Hinge match row proportions ($0.18 \times \text{width} \le \text{height} \le 0.38 \times \text{width}$).
- **Avatar Presence Check**: Measure color variance/standard deviation in the avatar region ($x \in [0.03w, 0.22w]$). If the patch is plain white or solid color ($\text{std} < 15$), it is a text section header (like "Your turn (14)") and is discarded.

#### 3. True Avatar Centering & Circular Crop
- For each verified match row $[y_{\text{top}}, y_{\text{bot}}]$:
  - $\text{avatar\_size} = \text{round}(w \times 0.175)$
  - $\text{avatar\_x} = \text{round}(w \times 0.05)$
  - $\text{avatar\_y} = y_{\text{top}} + \text{round}\left(\frac{(y_{\text{bot}} - y_{\text{top}}) - \text{avatar\_size}}{2}\right)$
- Generate circular clipped avatars centered directly on each woman's face.

#### 4. Name Line Isolation & OCR Preprocessing
- Restrict the name crop area vertically to the top 40% of the row text area ($y = y_{\text{top}} + 0.16 \times \text{row\_h}$, $\text{height} = 0.36 \times \text{row\_h}$), completely excluding message previews (e.g. *"Great, my number is..."*) and action buttons (e.g. *"[Start chat]"*).
- Apply high-contrast thresholding to eliminate background noise and separate attached icons (such as purple verification hearts 💜).
- Extract only alphabetic characters from the first word of the recognized line.

#### 5. Deduplication & Review Modal
- Compute 8×8 perceptual luminance hashes from the correctly cropped avatars.
- Cross-reference with existing matches in `matchesData`.
- Present clean, properly cropped avatars and names in the review checklist.

---

## Progress Checklist

- [x] **Step 1:** Implement dynamic bottom navigation and horizontal divider line detection in `analyzeScreenshotImage` in `index.html`.
- [x] **Step 2:** Add row validation logic to reject banners (purple over-the-limit cards) and section headers (empty avatar slots).
- [x] **Step 3:** Implement row-centered avatar cropping ($\text{avatar\_y}$ relative to row dividers).
- [x] **Step 4:** Implement isolated name line cropping and high-contrast preprocessing for OCR to eliminate garbled text and ignore purple heart icons.
- [x] **Step 5:** Verify with the user's provided test screenshot (`media_1789926022466.jpg`) to ensure all 5 women (Lauren, Mukta, Meredith, Bem, Bonnie) are detected with correctly centered avatars and names.
- [x] **Step 6:** Verify with the original `hinge_view.jpeg` screenshot to ensure backward compatibility across different Hinge layouts.
- [x] **Step 7:** Document before/after verification in `walkthrough.md`.

---

## Verification Plan

### Automated / Browser Verification
1. Load `index.html` in the browser.
2. Trigger `window.processScreenshotFile` with `media_1789926022466.jpg`.
3. Verify that the review modal displays:
   - Exactly the real match rows (Lauren, Mukta, Meredith, Bem, Bonnie).
   - Zero banner crops (no "Matches", no purple banner text).
   - Clean, centered circular avatars.
   - Clean recognized names without OCR gibberish.
4. Trigger `window.processScreenshotFile` with `hinge_view.jpeg` to verify the original 6–7 rows are detected and flagged as duplicates.
