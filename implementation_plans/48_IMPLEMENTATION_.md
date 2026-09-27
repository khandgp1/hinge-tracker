# 48 — Support Received Liked Photo Cards (Inbound Match Likes)

## Goal

Correctly detect, classify, and render **inbound liked photo cards** (when a match liked the user's photo, as in `Tess_1.jpg`) versus **outbound liked photo cards** (when the user liked the match's photo, as in `Aubrey` and `Sydney`). Inbound photo cards must be horizontally centered with a bottom-left cream badge displaying `"Liked your photo"` alongside the match's avatar, masking the underlying baked-in badge cleanly. System prompts like `"Start the chat with..."` must not be classified as incoming chat bubbles.

---

## Background & Problem Analysis

In Hinge, liked photo/prompt cards take two distinct presentations based on who initiated the like:

| Attribute | Outbound / Sent Like (Aubrey, Sydney) | Inbound / Received Like (Tess) |
| :--- | :--- | :--- |
| **Photo Subject** | The match | The user |
| **Chat Alignment** | Right-aligned (`margin: 8px 4px 22px auto`) | Centered (`margin: 8px auto 22px auto`) |
| **Badge Location** | Bottom-right corner (`right: -6px; bottom: 0`) | Bottom-left corner (`left: -6px; bottom: 0`) |
| **Badge Content** | `"You liked {name}'s photo."` or user comment | `"Liked your photo"` or match comment |
| **Avatar** | None (sent by user) | Match's circular avatar attached to pill |
| **Follow-up Prompt** | None | System pill: `"Start the chat with {name}"` |

### Current Failure Points in Codebase:

1. **Hardcoded Sent Wording in `server.py` (`parse_chat_images`)**:
   - Lines 334–335 unconditionally convert any text containing `"liked"` and `"photo"` into:
     ```python
     card_comment_text = f"You liked {match_name}'s photo."
     ```
   - This overwrote `"Liked your photo"` in `Tess_1.jpg`, wrongly making it look like the user liked Tess's photo.

2. **Missing `sender` Metadata**:
   - `server.py` outputs `{ "type": "liked_photo", "text": "...", "image": "..." }` with no field indicating `sender` (`"sent"` vs `"received"`).

3. **Strictly Right-Aligned Frontend CSS in `index.html`**:
   - `.liked-photo-container` is locked to `margin: 8px 4px 22px auto` (right margin).
   - `.liked-photo-pill` is locked to `right: -6px; bottom: 0px`.
   - In `Tess_Result_1.png`, the overlay badge was placed on the bottom-right, leaving the baked-in `"Liked your photo"` badge exposed on the bottom-left.
   - No avatar element was provided for received liked photo cards.

4. **System Action Prompt Misclassified as Received Chat**:
   - `"Start the chat with Tess"` was classified as `received` because it was not purple or right-anchored, resulting in a false incoming message bubble from Tess.

---

## Technical Architecture & Design

```
┌──────────────────────────────────────────────────────────────────┐
│                   Chat Screenshot (e.g. Tess_1.jpg)              │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ POST /api/parse-screenshot
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               server.py (parse_chat_images)                     │
│                                                                  │
│  1. Detect Top Photo Card bounds (x1, y1, x2, y2, w, h)          │
│  2. Identify Directionality:                                     │
│     - Check OCR text near card bottom:                           │
│       • "liked your photo" / "liked your prompt" -> "received"   │
│       • "you liked ..." / right-anchored card -> "sent"          │
│     - Check Card Center-X:                                       │
│       • Centered (|cx - screen_w/2| < 40) -> "received"          │
│       • Right-offset (x2 near right margin) -> "sent"            │
│  3. Set Text & Sender:                                           │
│     - Inbound: text = "Liked your photo" (or comment)            │
│                sender = "received"                               │
│     - Outbound: text = "You liked {name}'s photo." (or comment)  │
│                 sender = "sent"                                  │
│  4. Filter System Prompts:                                       │
│     - If text matches r"Start the chat with":                    │
│       classify as "system_prompt" (or omit from message bubbles) │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ Returns JSON
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Frontend (index.html)                        │
│                                                                  │
│  - Render .liked-photo-container:                                │
│    • If sender === 'received' (or text includes "Liked your"):   │
│        - Add .received class (centered layout)                   │
│        - Render avatar + .liked-photo-pill at bottom-left        │
│        - Mask underlying badge completely                        │
│    • Else:                                                       │
│        - Default right-aligned layout (sent side)                │
│  - Render system prompts as clean centered pills (not bubbles)   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Proposed Changes

### Backend Engine

#### [MODIFY] [server.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)

1. **Directional Card Detection**:
   - When evaluating OCR text associated with `best_card`:
     - If `"liked your"` in `t.lower()` (e.g. `"Liked your photo"` or `"Liked your prompt"`):
       - `card_direction = "received"`
       - `card_comment_text = "Liked your photo"` (or preserve prompt text if applicable).
     - Else if `"you liked"` in `t.lower()` or `(best_card["x2"] > w * 0.88 and best_card["x1"] > w * 0.15)`:
       - `card_direction = "sent"`
       - `card_comment_text = f"You liked {match_name}'s photo."` if pure like pill, or comment.
     - Fallback based on card horizontal centering:
       - Calculate `card_center_x = (best_card["x1"] + best_card["x2"]) / 2`.
       - If `abs(card_center_x - w / 2) < w * 0.08`:
         - Default `card_direction = "received"`, `card_comment_text = "Liked your photo"`.
       - Else:
         - Default `card_direction = "sent"`, `card_comment_text = f"You liked {match_name}'s photo."`.
   - Include `"sender": card_direction` in the emitted `liked_photo` object.

2. **System Prompt Handling**:
   - In OCR bubble classification, add a rule before sent/received fallback:
     ```python
     elif re.search(r"^Start the chat with\b", text, re.IGNORECASE) or lower == "start the chat":
         msg_type = "system_prompt"
     ```
   - Either filter this out or emit as `system_prompt` so it does not become a fake message from the match.

---

### Frontend UI & Styling

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Enhancements**:
   - Add `.liked-photo-container.received`:
     ```css
     .liked-photo-container.received {
       margin: 8px auto 22px auto;
       max-width: 82%;
     }
     ```
   - Add `.liked-photo-pill-wrapper.received`:
     - Positioned at `position: absolute; bottom: 0px; left: -10px; display: flex; align-items: center; gap: 8px; z-index: 5;`.
     - Render circular match avatar thumbnail (`width: 38px; height: 38px; border-radius: 50%; box-shadow: 0 2px 6px rgba(0,0,0,0.15);`).
     - Render cream pill badge (`.liked-photo-pill.received`) with `min-width: 140px; padding: 12px 20px;` positioned on the left side to 100% cover any underlying baked-in badge.

2. **Chat Template Rendering (`renderChatMessages`)**:
   - Inspect `item.type === 'liked_photo'`:
     - Determine if received: `const isReceived = item.sender === 'received' || (item.text && item.text.toLowerCase().includes('liked your'));`
     - If `isReceived`:
       - Default text: `item.text || 'Liked your photo'`.
       - Render `.liked-photo-container.received` with match avatar and left-positioned pill.
     - Else:
       - Default text: `item.text || You liked ${matchName}'s photo.`.
       - Render `.liked-photo-container.sent` (existing right-aligned layout).
   - Inspect `item.type === 'system_prompt'`:
     - Render as a centered, subtle system prompt (or ignore if redundant).

---

## Verification & Test Plan

### Automated / Backend Tests
1. Run `parse_chat_images` on `test_chats/Tess_1.jpg`:
   - Verify `type: 'liked_photo'` has `sender: 'received'` and `text: 'Liked your photo'`.
   - Verify `"Start the chat with Tess"` is classified as `system_prompt` (not `received` message).
2. Run `parse_chat_images` on `test_chats/Sydney_Test/Sydney_1.jpg`:
   - Verify `type: 'liked_photo'` maintains `sender: 'sent'` and `text: 'ure Chinese??'`.
3. Verify Aubrey chat baseline remains unchanged.

### Visual & Browser Tests
1. Load `index.html` with Tess's parsed chat.
2. Verify:
   - The photo card is centered.
   - Tess's avatar is displayed on the bottom-left alongside `"Liked your photo"`.
   - Underlying baked-in text is 100% masked without visible seams.
   - No false `"Start the chat with Tess"` message bubble appears.
   - Aubrey and Sydney chat views remain pixel-perfect and right-aligned.

---

## Progress Checklist

- [x] **Step 1:** Update `server.py` to detect `received` vs `sent` like direction and preserve `"Liked your photo"`.
- [x] **Step 2:** Update `server.py` to classify `"Start the chat with..."` as `system_prompt`.
- [x] **Step 3:** Add CSS rules for `.liked-photo-container.received` and left-anchored pill with avatar in `index.html`.
- [x] **Step 4:** Update `renderChatMessages` in `index.html` to support received liked photo cards and system prompts.
- [x] **Step 5:** Run automated verification on `Tess_1.jpg` and `Sydney_1.jpg`.
- [ ] **Step 6:** Inspect in browser and capture before/after visual verification.
