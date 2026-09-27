# 45 — 100% Automated Chat Screenshot Upload, Stitching & Ingestion

## Goal

Enable users to upload chat conversation screenshots directly within any open match's chat view (Aubrey, Isadora, or any imported match) with **100% zero-friction, end-to-end automation**. The previous manual review/editing modal is completely eliminated. When screenshots are selected, they are stitched via `stitch.py`, parsed into native Hinge message bubbles via Apple Vision OCR and OpenCV color analysis with strict noise filtering, directly written to Firebase Firestore, and rendered instantly in the chat feed with a sleek in-chat floating progress indicator.

---

## Confirmed Design Decisions (via `/grill-me` Alignment)

1. **100% End-to-End Automation (No Review Modal)**:
   - The manual review modal, text editing inputs, sender toggles, and checkboxes are completely removed.
   - The ingestion pipeline runs autonomously from file selection to live chat rendering.
2. **In-Chat Progress Feedback**:
   - When the user selects screenshots, a subtle floating pill appears at the top of the chat view:
     - Mini spinner + `"Stitching & adding messages..."`.
   - Once ingestion finishes, the pill smoothly transitions to a checkmark or dismisses automatically.
3. **Multi-Screenshot Processing**: **Stitch-First Pipeline**.
   - Multiple overlapping screenshots are automatically merged using `stitch.py` (`stitch_chat_frames`).
   - Automatically detects and crops static status bars, navigation headers, and input bars, eliminating duplicate overlapping content.
4. **Bubble Classification & Strict Noise Rejection**:
   - **Sent Messages**: Right-aligned purple bubbles (`#701A51` / dark magenta).
   - **Received Messages**: Left-aligned grey bubbles (`#EFEFEF`) with the match's avatar.
   - **Timestamps**: Centered text lines matching date/time patterns.
   - **Liked Photo Cards**: Automatically cropped as Base64 JPEG assets with the `.liked-photo-pill` badge.
   - **Strict Filtering**: Automatically discards input bar placeholders ("Send a message..."), top status bar clock/battery artifacts, priority banners, and partial cutoffs (< 3 characters).
5. **UI Trigger Location**:
   - Top right corner of `.chat-header` (`#chatUploadBtn` camera/screenshot icon).
   - "Upload Chat Screenshots" action button inside empty chat states.
6. **Data Persistence & Real-time Sync**:
   - Messages are written directly to Firebase Firestore under `chats/{matchName}/messages`.
   - Real-time `onSnapshot` automatically animates the new bubbles into the active view on both Client and Coach devices.
   - Intelligent deduplication ensures overlapping screenshots do not duplicate existing messages.
7. **Contextual Status Toasts**:
   - Completion toast: `"Added X new messages to chat!"`
   - If no new messages were found: `"No new messages detected in screenshot"`
   - If server error: `"Error analyzing screenshots: ..."`

---

## Technical Architecture & Pipeline

```
┌────────────────────────────────────────────────────────┐
│                   Mobile / Desktop UI                  │
│                                                        │
│  1. Open Match Chat ──> Tap Upload Button              │
│  2. Select 1 or more chat screenshots                  │
│  3. Floating Progress Pill: "Stitching & adding..."    │
└───────────────────────────┬────────────────────────────┘
                            │ Multi-file Base64 Payload
                            ▼
┌────────────────────────────────────────────────────────┐
│            Python Backend (server.py)                  │
│                                                        │
│  1. Multiple Images? ──> stitch.py (stitch_chat_frames)│
│     - Auto-detects & crops static header/footer        │
│     - 1D normalized cross-correlation displacement     │
│     - Linear alpha seam blend -> Single Long Image     │
│                                                        │
│  2. Apple Vision OCR (bin/vision_ocr)                  │
│     - High-precision character & box detection         │
│                                                        │
│  3. OpenCV Bubble & Layout Segmentation               │
│     - Segment bubbles by contour and color masks       │
│     - Purple hue (#701A51) ──> Sent message           │
│     - Grey hue (#EFEFEF)   ──> Received message       │
│     - Centered small text  ──> Timestamp              │
│     - Photo card bounds    ──> Extract JPEG crop       │
│     - Strict Noise Filter  ──> Strip placeholders/cuts │
└───────────────────────────┬────────────────────────────┘
                            │ Structured Clean JSON
                            ▼
┌────────────────────────────────────────────────────────┐
│            Firebase Firestore (`chats`)                │
│                                                        │
│  - Deduplicates against existing conversation history  │
│  - Writes new messages with sequential order           │
│  - Updates match preview snippet                       │
│  - onSnapshot updates live Chat & Coach view instantly │
│  - Progress Pill dismisses with success toast          │
└────────────────────────────────────────────────────────┘
```

---

## Proposed Changes

### 1. Backend Server (`server.py`)
- Keep `POST /api/parse-chat` with strict noise filtering:
  - Filter out strings with length < 3.
  - Filter out placeholder texts ("send a message", "type a message", "type advice").
  - Filter out status bar indicators ("5g", "lte", "wifi", battery percentage).
  - Crop liked photo cards above pill and encode as Base64 JPEG.

### 2. Frontend Application (`index.html`)
- **Remove Modal**: Delete `#chatImportModal` markup and associated review CSS (`.import-modal-overlay`, `.chat-import-row`, `.sender-toggle-btn`, etc.).
- **Add Floating In-Chat Progress Pill**:
  ```html
  <div id="chatUploadProgressPill" class="chat-upload-pill" style="display: none;">
    <div class="chat-pill-spinner"></div>
    <span id="chatPillText">Stitching & adding messages...</span>
  </div>
  ```
  Styled with clean glassmorphic / dark iOS pill aesthetics at the top of the chat view.
- **Direct-to-Firestore Ingestion**:
  - In `chatFileInput.addEventListener('change', ...)`:
    - Show `#chatUploadProgressPill`.
    - Fetch `/api/parse-chat`.
    - Automatically deduplicate returned messages against `currentMatchMessages`.
    - If new messages exist, batch write directly to Firestore `chats/{matchName}/messages`.
    - Update match preview text in `matches` collection.
    - Dismiss progress pill and show toast: `"Added X new messages to chat!"`.
    - Scroll chat smoothly to bottom.
    - If no new messages: dismiss progress pill and show toast: `"No new messages detected in screenshot"`.

---

## Implementation Checklist

### Step 1: Backend Parsing & Noise Filtering
- [x] Ensure `POST /api/parse-chat` in [server.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py) has strict noise rejection.
- [x] Verify multi-image stitching via `stitch_chat_frames` handles 1 to N images seamlessly (including dimension alignment across frames).

### Step 2: Remove Review Modal Markup & CSS
- [x] Remove `#chatImportModal` markup from [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html).
- [x] Remove unused review modal CSS rules from [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html).

### Step 3: Floating In-Chat Progress Pill UI
- [x] Add `#chatUploadProgressPill` markup inside `#chatOverlay` in [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html).
- [x] Add CSS for `.chat-upload-pill` and `.chat-pill-spinner` with smooth slide-down animation.

### Step 4: 100% Automated End-to-End Ingestion Flow
- [x] Rewrite `chatFileInput` change event listener to run 100% automatically without review modal.
- [x] Automatically deduplicate against `currentMatchMessages`.
- [x] Batch write new messages to Firestore `chats/{match.name}/messages`.
- [x] Smoothly scroll chat view to bottom on new messages.
- [x] Provide contextual toast feedback for success or empty detection.

### Step 5: End-to-End Verification
- [x] Test uploading screenshots in browser; verify progress pill appears and auto-dismisses.
- [x] Verify messages pop directly into the chat feed with zero user clicks or modal prompts.
- [x] Verify deduplication prevents duplicate messages if same screenshots are uploaded again.
