# Implementation Plan 16: Concept A (Floating Bottom Sheet Overlay) Integration

Integrate **Concept A: Floating Bottom Sheet Overlay** into the Aubrey Chat View in [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html).

## Progress Checklist
- [x] Add HTML structure for `#expertBottomSheet` floating container inside `#chatOverlay`
- [x] Add CSS for dark glassmorphism design (`backdrop-filter: blur(16px)`), snap-point height transitions (`collapsed` 56px, `half` 50%, `full` 85%), drag handle, and badge
- [x] Seed targeted Expert & Client coaching dialogue dataset focused on analyzing Aubrey's phone number text
- [x] Add JavaScript interactivity for bottom sheet toggling (collapsed -> half -> full) and swipe/tap handling
- [x] Implement message input & send functionality inside the drawer ("Ask coach for advice...")
- [x] Perform visual and interactive verification in browser

## Resolved Design Decisions
1. **Initial State**: Starts collapsed as a bottom peek bar (`56px` high) displaying "Coach & Client Dialogue" with a badge indicator (`2 unread`).
2. **Snap Points**: Supports 3 states: Collapsed (`56px`), Half (`50%` screen height), and Full (`85%` screen height).
3. **Interactivity**: Includes a bottom input pill ("Ask coach for advice...") inside the sheet so the client can ask questions and receive dynamic responses.
4. **Pre-Seeded Content**: Contains 2-3 coaching messages evaluating Aubrey's last message ("ummmmmmm how's those eyes are gonna get you in trouble...") and advising on texting strategy.

## Proposed Changes

### UI Overlay & Styling

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **HTML Markup**:
   - Insert `#expertBottomSheet` inside `#chatOverlay`:
     ```html
     <div id="expertBottomSheet" class="expert-sheet collapsed">
       <div id="expertSheetHeader" class="expert-sheet-header">
         <div class="expert-drag-handle"></div>
         <div class="expert-header-content">
           <div class="expert-avatar-stack">
             <span class="expert-icon">🎓</span>
           </div>
           <div class="expert-title-group">
             <span class="expert-title">Coach & Client Dialogue</span>
             <span class="expert-subtitle">Real-time Advice</span>
           </div>
           <span class="expert-unread-badge">2</span>
           <button id="expertExpandBtn" class="expert-toggle-btn" aria-label="Toggle drawer">
             <svg class="chevron-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"></polyline></svg>
           </button>
         </div>
       </div>

       <div id="expertSheetBody" class="expert-sheet-body">
         <div id="expertChatFeed" class="expert-chat-feed"></div>
       </div>

       <div class="expert-input-bar">
         <input id="expertInput" type="text" class="expert-input-field" placeholder="Ask coach for advice..." autocomplete="off">
         <button id="expertSendBtn" class="expert-send-btn" aria-label="Send">
           <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
         </button>
       </div>
     </div>
     ```

2. **CSS Styling**:
   - Styling for `.expert-sheet`: Dark glassmorphism (`background: rgba(18, 18, 22, 0.88)`, `backdrop-filter: blur(20px)`, `border-top: 1px solid rgba(255, 255, 255, 0.15)`).
   - Transitions for smooth snapping (`transition: height 0.35s cubic-bezier(0.16, 1, 0.3, 1)`).
   - State classes:
     - `.expert-sheet.collapsed` -> `height: 56px;`
     - `.expert-sheet.half` -> `height: 50vh;`
     - `.expert-sheet.full` -> `height: 85vh;`
   - Styled message bubbles for Expert (amber/purple gradient accent avatar + dark card) vs Client (purple bubble).

3. **JavaScript Integration**:
   - Seed data array `expertDialogueData`:
     ```javascript
     const expertDialogueData = [
       { sender: 'expert', name: 'Coach Alex', text: 'Great work getting her phone number! She responded warmly to your humor.', time: '12:03 AM' },
       { sender: 'expert', name: 'Coach Alex', text: 'Recommendation: Wait until tomorrow morning before texting her number to keep the momentum smooth.', time: '12:04 AM' }
     ];
     ```
   - Render logic `renderExpertChat()` and click toggle handler `toggleExpertSheet()`.
   - Event handlers for typing and sending a message into the Expert dialogue feed.

## Verification Plan

### Manual Verification
- Open [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html) in browser.
- Open Aubrey chat view.
- Verify bottom peek bar is displayed with dark glassmorphism styling and "2" unread badge.
- Click header or toggle button: verify drawer expands smoothly to 50% screen height.
- Click expand button again: verify drawer expands to 85% height.
- Type a question in "Ask coach for advice..." and click Send: verify message appears in the coach feed and scrolls into view.
- Click back button to return to Matches list; re-open Aubrey chat to verify clean state reset.
