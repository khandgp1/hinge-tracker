# 39 — Screenshot Match Importer for Matches View

## Goal

Add a client-side screenshot import flow for the **Matches** view in Hinge Tracker. Users can upload a screenshot of their Hinge matches list, automatically slice and crop avatar thumbnails, extract names via in-browser OCR, deduplicate entries (via dual Name + Avatar visual fingerprinting), review matches in an iOS-style review sheet, and append new matches to the active list with persistent storage in `localStorage`.

---

## User Design Choices (from Interview)

1. **Selection Model**: Auto-detect rows and present a staged multi-select review modal where users can check/uncheck which women to import.
2. **Review Card Content**: Minimal checklist showing the cropped avatar thumbnail and extracted name, defaulting preview text to `"You matched with [Name]"`.
3. **Execution Environment**: 100% client-side inside the web app (`index.html`) using HTML5 Canvas for avatar slicing and client-side OCR for text extraction.
4. **Deduplication Strategy**: Dual check on **both Name and Avatar Image similarity**. True duplicates (same name + same photo) are automatically filtered out into an "Already Added" non-selectable list. Different women sharing the same first name are recognized as distinct new matches.
5. **Entry Point**: A clean top-right `+` button in the sticky "Matches" header bar, styled according to iOS navigation bar aesthetics.
6. **Data Persistence**: Browser `localStorage` so imported matches persist across sessions and page refreshes.
7. **Match Interaction**: Tapping on an imported match opens a personalized starter chat view showing her name, circular avatar, and a `"Start the chat with [Name]"` placeholder.

---

## Proposed Changes

### `index.html`

#### 1. Header & Import Modal Markup
- **Sticky Header**: Add an import button (`#importMatchesBtn`) with an iOS-style `+` icon positioned at the top right of the sticky header in `#matchesView`.
- **Hidden File Input**: Add `<input type="file" id="matchesFileInput" accept="image/*" style="display:none">`.
- **Review Modal (`#importReviewModal`)**:
  - Modal backdrop with smooth fade/slide-up animation.
  - Header with title "Import Matches" and a "Cancel" button.
  - Loading state indicator (spinner + "Analyzing screenshot & detecting matches...").
  - Content container `#importReviewList`:
    - "New Matches" checklist section with avatar thumbnails, detected names, and checkboxes.
    - "Already in Matches" section displaying recognized duplicates with an "Already Added" badge (disabled, cannot duplicate).
  - Bottom action bar with dynamic button: `Import X New Matches`.

#### 2. OCR Library Integration
- Include Tesseract.js via CDN (`https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js`) for fast client-side text recognition of names in the match rows.

#### 3. CSS Styling
- Styles for `#importMatchesBtn` in `.sticky-header-wrapper`:
  - Aligned to top-right with touch-friendly padding and active feedback.
- Styles for `#importReviewModal` and sheet:
  - Bottom-sheet layout on mobile (`max-width: 390px`, rounded top corners `16px`, backdrop filter).
  - Modern checklist items: circular avatar (48px), bold name, customized checkbox accent.
  - "Already Added" row styling (opacity 0.5, "Already Added" pill badge, no checkbox).
  - Primary import button styled consistently with Hinge black/dark buttons.

#### 4. JavaScript Engine: Slicing, OCR, Deduplication, & Storage
- **Canvas Slicer**:
  - Load user-selected image onto an off-screen `<canvas>`.
  - Calculate row offsets based on Hinge's standard aspect ratio and geometry (calibrated from `hinge_view.jpeg`: row spacing ~152px per 1280h, avatar diameter ~108px at x=31px).
  - Extract circular avatar image crops as data URLs.
- **Name Extraction (OCR)**:
  - Isolate the name region next to each avatar (x = avatar_x + avatar_width + padding) and run OCR on the first text line.
- **Deduplication Engine**:
  - Compute a visual fingerprint for each avatar (8×8 downscaled pixel luminance hash).
  - Compare name and visual hash against existing items in `matchesData`.
  - Classify as duplicate if name matches AND avatar hash distance is below threshold; otherwise mark as new.
- **State & `localStorage` Sync**:
  - Load custom matches from `localStorage.getItem('hinge_custom_matches')` on boot and prepend to `matchesData`.
  - On confirming import, push new matches to `matchesData` and save to `localStorage`.
  - Re-render `#matchesList`.
- **Tap Interaction for Imported Matches**:
  - Extend match click handler so tapping any imported match opens `#chatOverlay` configured for her name and avatar, displaying a clean `"Start the chat with [Name]"` screen.

---

## Progress Checklist

- [x] **Step 1:** Add the `+` import button to the Matches header, hidden file input, and `#importReviewModal` markup in `index.html`.
- [x] **Step 2:** Include Tesseract.js script tag and add CSS styles for the header button, review sheet, checklist items, and duplicate badges.
- [x] **Step 3:** Implement offscreen Canvas row slicing and circular avatar cropping logic.
- [x] **Step 4:** Implement OCR name extraction and dual-key deduplication (Name + Avatar visual hash).
- [x] **Step 5:** Build review modal rendering with dynamic checkbox counters and import confirmation.
- [x] **Step 6:** Implement `localStorage` persistence and re-rendering of the Matches list.
- [x] **Step 7:** Connect click handling for newly imported matches to open the personalized starter chat view.
- [x] **Step 8:** Verify end-to-end import with `hinge_view.jpeg` in the browser, verifying avatar cropping, deduplication, review modal interaction, and chat opening.

---

## Verification Plan

### Automated / Browser Subagent Verification
1. Open `index.html` via local web server / browser.
2. Verify `+` button in the sticky Matches header is visible and responsive.
3. Simulate selecting `hinge_view.jpeg` into the file input.
4. Verify the review modal appears showing detected match rows.
5. Verify deduplication correctly identifies existing matches (e.g., Aubrey, Divya) and prevents duplicate additions.
6. Verify checking/unchecking items updates the "Import X Matches" button count.
7. Confirm import and verify the new matches appear in `#matchesList` with avatar images and `"You matched with [Name]"` preview text.
8. Refresh page to confirm `localStorage` persistence.
9. Click an imported match to verify the personalized chat view opens correctly.
