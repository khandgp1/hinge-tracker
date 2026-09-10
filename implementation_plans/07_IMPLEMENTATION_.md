# Implementation Plan 07 - Native HTML/CSS Aubrey Chat View

This plan details replacing the static `Aubrey_Chat.png` image overlay in `index.html` with a fully responsive, pixel-perfect, native HTML/CSS chat view component.

## User Decisions (Grill-Me Alignment)

> [!NOTE]
> - **Input Bar Positioning**: Fixed footer at the bottom of the chat overlay (matching native Hinge UI).
> - **Data Structure**: Messages are dynamically rendered from a JavaScript array (`aubreyChatData`), making the component modular and reusable for other matches.
> - **Performance & Sharpness**: 100% vector-sharp text rendering across all Retina / high-DPI screens.
> - **Image Assets**: Aubrey's liked photo (steamer image) will be extracted to `assets/aubrey_liked_photo.jpg`.

---

## Technical Architecture & Design System

```
+------------------------------------------+
|  Aubrey Chat Overlay View (Native HTML)  |
|  +------------------------------------+  |
|  | [<]  Aubrey                        |  |  (Fixed Top Header)
|  +------------------------------------+  |
|  |                                    |  |
|  |  [ Priority Like Banner Card ]     |  |  (Top prompt banner)
|  |                                    |  |
|  |  [ Liked Photo Card ]              |  |  (Extracted photo + pill overlay)
|  |                                    |  |
|  |  [ Dynamic Received/Sent Bubbles ] |  |  (Flexbox CSS message bubbles)
|  |  - Gray (#EFEFEF) left with avatar  |  |
|  |  - Purple (#701A51) right          |  |
|  |                                    |  |
|  +------------------------------------+  |
|  | [ Send a message ...          ||| ]|  |  (Fixed Bottom Footer Bar)
+------------------------------------------+
```

---

## Proposed Changes

### Web Application

#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **HTML Structure**:
   - Replace `<img src="Aubrey_Chat.png" ...>` inside `.chat-content` with semantic chat container elements:
     - Header: `.chat-header` (fixed top).
     - Body: `.chat-body` (scrollable container).
       - Banner: `.chat-banner` ("Your Priority Like helped you stand out").
       - Liked Content Block: `.liked-photo-card` displaying `assets/aubrey_liked_photo.jpg` and overlay badge "You liked Aubrey's photo."
       - Message Feed: `.chat-feed` rendered from JavaScript.
     - Footer: `.chat-input-bar` (fixed bottom) with placeholder "Send a message" and audio icon.

2. **CSS Styling**:
   - Add styles for `.chat-overlay`, `.chat-body`, `.bubble-received`, `.bubble-sent`, `.chat-timestamp`, `.avatar-sm`, and `.chat-input-bar`.
   - Palette: `#701A51` (sent purple), `#EFEFEF` (received gray), `#8e8e93` (timestamps), `#000000` text.

3. **JavaScript Data & Renderer**:
   - Define `aubreyChatData` containing timestamps, message type (`sent` / `received` / `match_notice`), text, and avatar flags.
   - Render chat items into `.chat-feed` on initialization or overlay show.

#### [NEW] `assets/aubrey_liked_photo.jpg`
- Extract the high-res cropped image of Aubrey in the beige hoodie with the steamer from `Aubrey_Chat.png` for use inside the liked photo card.

---

## Implementation Checklist

- [x] **Step 1: Asset Preparation**
  - [x] Crop and extract `assets/aubrey_liked_photo.jpg` from `Aubrey_Chat.png`.

- [x] **Step 2: HTML & CSS Implementation**
  - [x] Update `#chatOverlay` layout in `index.html`.
  - [x] Add CSS for chat bubbles, fixed footer input bar, banner, and timestamps.

- [x] **Step 3: JavaScript Data & Dynamic Renderer**
  - [x] Add `aubreyChatData` data array in `index.html`.
  - [x] Add rendering logic to populate the chat feed dynamically.

- [x] **Step 4: Verification & Alignment**
  - [x] Verify click interactions, smooth scrolling, fixed header & footer, and crystal-clear text quality.

---

## Verification Plan

### Automated / Browser Verification
- Serve `index.html` and inspect UI rendering using the browser tool:
  - Click `Aubrey` row to open chat view.
  - Verify crisp text, correct color values, avatars, and fixed input bar.
  - Test back button navigation.
