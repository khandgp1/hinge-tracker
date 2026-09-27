# 47 — Top Liked Photo Card Auto-Extraction & Chat Reflection

## Goal

Automatically detect, crop, and reflect the top liked photo card from uploaded chat screenshots (such as Sydney or any uploaded match) in the chat feed, mirroring Aubrey's chat layout with 100% native fidelity. If a comment was sent with the like (e.g., "ure Chinese??"), display that comment inside the photo card's cream pill badge instead of creating a redundant separate message bubble.

---

## Confirmed Design Decisions (via `/grill-me` Alignment)

1. **Scope & Behavior**:
   - Ingested chat screenshots with a top photo card (e.g., `Sydney_1.jpg`) will automatically extract the photo card and render it as a `liked_photo` item in the chat feed, exactly matching Aubrey's chat.
2. **Detection Mechanism**:
   - In `server.py` (`parse_chat_images`), analyze the region between the top navigation/timestamp and the first message bubble.
   - Detect large non-white photo card components (width ~50–85% of screen width, height > 180px, aspect ratio ~1:1, right-anchored / centered).
   - Works deterministically whether Vision OCR detected a text pill ("liked photo") or pure image content.
3. **Comment vs. Like Pill Binding**:
   - If a text observation is anchored within or at the bottom edge of the photo card (e.g. "ure Chinese??"), bind it as the photo card's `text` property (`type: 'liked_photo'`, `text: 'ure Chinese??'`).
   - Suppress emitting this comment as a separate standalone `sent` message bubble so it is not duplicated.
   - If no comment is attached (like Aubrey), `text` remains empty or defaults to `"You liked {matchName}'s photo."`.
4. **Visual Presentation & Badge Styling**:
   - **Uniform Cream Badge**: Use the established Aubrey cream serif badge (`#f7ebe6`, Georgia italic, rounded pill, subtle drop shadow) for both comments and "You liked..." notices.
   - **Responsive Multiline Support**: Update `.liked-photo-pill` CSS to allow `max-width: 92%`, `white-space: normal`, and neat centering so multiline comments wrap cleanly within the card without horizontal overflow.
5. **Chat Positioning**:
   - The photo card is positioned chronologically after the opening timestamp header (e.g., "Sat, Sep 19 5:51 PM") and immediately before the subsequent conversation messages.
6. **Data Persistence**:
   - `index.html` already supports storing and syncing `liked_photo` items in Firestore (`chats/{matchName}/messages`) with base64 image payloads and deduplication.

---

## Technical Architecture & Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                   Chat Screenshots (e.g., Sydney)                │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ Upload via API
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               server.py (parse_chat_images)                     │
│                                                                  │
│  1. Run Vision OCR to get text observations & bounding boxes     │
│  2. Identify Opening Context:                                    │
│     - Top chrome cutoff & initial timestamp (y ~ 200..320)       │
│     - First conversation text bubble (y ~ 700..850)              │
│  3. Detect Top Photo Card:                                       │
│     - Threshold non-white region in top zone                     │
│     - Locate ~420x420 card (x ~ 140..560, y ~ 320..740)          │
│  4. Comment Association:                                         │
│     - Check if text box (e.g. "ure Chinese??") overlaps card     │
│       bottom area (y > card_y2 - 80)                             │
│     - If found: set card_text = text; mark text box consumed     │
│  5. Crop Card:                                                   │
│     - Encode cropped card region to base64 JPEG data URL         │
│     - Insert into grouped messages after initial timestamp       │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ Returns JSON messages
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Frontend (index.html)                        │
│                                                                  │
│  - Render .liked-photo-container:                                │
│    - <img> displaying extracted photo card                       │
│    - .liked-photo-pill displaying card text or                   │
│      "You liked [MatchName]'s photo."                            │
│  - Real-time Firestore sync & deduplication                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Proposed Changes

### Backend Engine

#### [MODIFY] [server.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)

1. **Enhanced Photo Card & Comment Detection**:
   - In `parse_chat_images`, before or during bubble grouping:
     - Scan the zone between the top header/initial timestamp and the conversational messages.
     - Extract connected component bounding box for non-background pixels (`gray < 248`) where `width > 0.5 * w` and `height > 180`.
     - Check if any OCR observation falls within the bottom 25% of this card box. If so, capture its text as `card_comment` and exclude that observation from being classified as a standalone `sent` bubble.
     - Crop the card bounds `stitched[y1:y2, x1:x2]`, encode as base64 JPEG (`quality: 88`), and insert `{ "type": "liked_photo", "text": card_comment, "image": photo_url }`.
   - Maintain compatibility with existing `"liked" in lower and "photo" in lower` pills (e.g. Aubrey).

---

### Web Application Frontend

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Pill Template Binding**:
   - In `renderChatMessages` (lines ~1835-1841):
     ```javascript
     } else if (item.type === 'liked_photo') {
       const pillText = item.text || `You liked ${matchName}'s photo.`;
       return `
         <div class="liked-photo-container">
           <img src="${item.image}" alt="Liked Photo" class="liked-photo-img">
           <div class="liked-photo-pill">${pillText}</div>
         </div>
       `;
     }
     ```
2. **Pill CSS Enhancement**:
   - Update `.liked-photo-pill` styles:
     - Add `max-width: 90%`.
     - Change `white-space: nowrap` to `white-space: normal` with `word-break: break-word` and `display: inline-block` to accommodate longer comments gracefully.

---

## Implementation Checklist

- [x] **Task 1: Backend Photo Card & Comment Detection in `server.py`**
  - [x] Detect ~1:1 square photo card component in top chat region
  - [x] Bind attached comment text to photo card (`liked_photo`)
  - [x] Prevent duplicate emission of attached comment as a separate `sent` bubble
  - [x] Preserve standard "liked photo" pill fallback for Aubrey
- [x] **Task 2: Frontend Rendering & Responsive CSS in `index.html`**
  - [x] Bind dynamic `item.text` in `.liked-photo-pill` with fallback to `"You liked ${matchName}'s photo."`
  - [x] Update `.liked-photo-pill` CSS for multiline wrapping and responsive sizing
- [x] **Task 3: Automated Backend & Regression Verification**
  - [x] Verify `Sydney_1.jpg` + `Sydney_2.jpg` extraction (photo card + "ure Chinese??", no duplicate bubble)
  - [x] Verify `Aubrey_Chat.png` regression test (photo card + "You liked Aubrey's photo.")
  - [x] Verify live `POST /api/parse-chat` endpoint on port 8080 returning 11 messages with photo card base64 image
- [ ] **Task 4: End-to-End Firestore & Browser Verification**
  - [x] Reset Sydney's chat using `reset_chat.py`
  - [ ] User browser verification on `http://localhost:8080/`

