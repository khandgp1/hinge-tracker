# 46 — Real Chat Accuracy Testing & Refinement Workflow

## Goal

Establish a fast, repeatable testing and refinement workflow to diagnose and fix real-world chat screenshot ingestion accuracy errors (stitching alignment, bubble classification, noise rejection, multiline merging) one issue at a time using actual user screenshots and immediate ground-truth verification.

---

## Aligned Workflow & Protocol

1. **Test Screenshot Repository**:
   - Screenshots are dropped into `test_chats/` in the workspace root (e.g. `test_chats/aubrey_01.png`, `test_chats/aubrey_02.png`).
2. **Issue Reporting & Feedback**:
   - The user provides the screenshot(s) and describes what went wrong (e.g., misclassified bubble, duplicate message, cut-off text, or noise artifact).
3. **Targeted Pipeline Diagnosis & Direct Code Fix**:
   - We inspect the screenshot and trace the exact breakdown point:
     - `stitch.py`: Seam calculation, displacement offset, or auto-crop logic.
     - Native Vision OCR: Character/box detection and line coordinates.
     - `server.py` (`parse_chat_images`): Color sampling (BGR margin thresholds), bubble categorization, grouping logic, or noise rejection regex.
   - We update the parser code directly and test against the screenshot to verify the fix.
4. **Clean Iterative Testing (`reset_chat.py`)**:
   - A dedicated Python CLI tool allows wiping chat messages in Firestore and resetting the match preview text instantly without polluting the production app UI:
     ```bash
     python reset_chat.py <MatchName>   # e.g., python reset_chat.py Aubrey
     python reset_chat.py --all         # wipes messages across all matches
     ```
   - Enables re-uploading and verifying fixes cleanly in the app.

---

## Key Refinement Targets

- **Stitching Quality**:
  - Prevent duplicate or truncated message bubbles across overlapping seams.
  - Accurate header/footer auto-cropping on different device aspect ratios.
- **Bubble Color & Sender Classification**:
  - Sent vs. Received color sampling margin (purple `#701A51` vs. grey `#EFEFEF` vs. white background).
  - Robust positioning heuristics (`px` relative to canvas width) for ambiguous bubbles.
- **Multiline & Multi-Bubble Grouping**:
  - Grouping adjacent lines belonging to the same bubble without merging distinct back-to-back bubbles.
- **Noise Rejection vs. Legitimate Short Messages**:
  - Preserving real short messages (e.g., "ok", "yes", "haha", "lol") while strictly rejecting UI artifacts ("5G", battery %, status bar timestamps, input bar placeholders).
- **Special Elements**:
  - Liked photo cards and prompt comment cards.
  - Date / timestamp headers and status indicators ("Sent", "Delivered", "Read").

---

## Status & Progress Log

- [x] **Setup**: Created `reset_chat.py` CLI utility for instant Firestore chat resets.
- [x] **Setup**: Created `test_chats/` workspace directory.
- [x] **Issue 1 Resolved: Header Bar Chrome Exclusion (`Signals`, `Chat`, `Profile`)**:
  - **Problem**: Header elements leaked into chat messages and middle seam when stitching.
  - **Fix**: Updated `stitch.py` to auto-crop the full 224px header across transient clock shifts, and added dynamic `header_cutoff` in `server.py`.

- [x] **Issue 2 Resolved: Missing Message & Client Sender Misclassification**:
  - **Problem in `Sydney_result_2.png`**:
    1. `'Nope, just grew up there'` was absent from the UI.
    2. `'do you think i'd pickup on it in person ..'` and `'references are overrated anyways tbh...'` were classified as `received` (grey / the woman) instead of `sent` (client).
  - **Root Cause**:
    1. `'Nope, just grew up there'` was skipped during the previous upload because `python3 reset_chat.py --Sydney` had failed to delete the old Firestore records due to the leading hyphens, triggering client-side deduplication.
    2. Sent bubbles in this chat use a soft lavender/lilac tint (`#D7C4DA`, BGR: `[218, 196, 215]`), where $R - G \approx 19$ and $B - G \approx 22$. The previous check required strict dark magenta (`R > G + 20`), causing long multiline bubbles that stretch leftward (`px < 0.4 * w`) to fall into the `received` fallback.
  - **Fix in `server.py`**:
    - Broadened color detection to `R > G + 7 and B > G + 7` to handle both soft lilac and deep purple sent bubbles.
    - Added right-anchor alignment check (`px + pw > w * 0.82 and not is_grey`).
    - Evaluated timestamps before bubble checks to preserve chronological headers.
- [x] **Issue 4 Resolved: Punctuation Precision (`..` vs `.`) & Contraction Restoration (`i'd` vs `id`)**:
  - **Problem**: `'do you think i'd pickup on it in person ..'` was missing the apostrophe in `i'd` (rendered as `id`) and lost a trailing period in `..` (rendered as `.`).
  - **Root Cause**:
    1. Low pixel density ($591\text{px}$ canvas) caused adjacent $2\times 2\text{px}$ period dots to blur together at the seam, leading Apple Vision to read a single dot.
    2. In San Francisco iOS font, the curly apostrophe sits directly against the dot of the letter `i` (`i’d`), causing optical collision into `id`.
  - **Fix in `server.py`**:
    - **1.5× Bicubic Super-Sampling**: Automatically upscales images $< 900\text{px}$ wide prior to OCR, giving tiny punctuation marks distinct $4\times 4\text{px}$ clusters with whitespace separation. Coordinates are normalized back seamlessly.
    - **Contraction Restoration**: Added colloquial pattern restoration for `id + [verb]` $\rightarrow$ `i'd` alongside `im`, `dont`, `cant`, `didnt`, etc.
    - **Bottom Boundary Cutoff**: Discarded partial text slices within $30\text{px}$ of the bottom canvas edge.
  - **Verification**:
    - Live server returns exact text: `'do you think i'd pickup on it in person ..'` with apostrophe and both dots intact.
    - Total messages verified at 11 clean items. Sydney's chat cleared for re-test.
