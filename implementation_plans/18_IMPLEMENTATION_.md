# Implementation Plan - Concept A Docked Bottom Pane Layout

Transform **Concept A** from an obscuring floating overlay into a **Docked Bottom Pane** layout. When expanded, the bottom pane docks into the layout and dynamically resizes the top main chat (Aubrey Chat) view so the latest chat messages remain fully visible without overlap.

## User Review Required

> [!IMPORTANT]
> **Layout Shift to Flex Container**: Instead of fixing `.expert-sheet` over top of the Aubrey chat screen, the main chat container and bottom pane will now live within a flex column layout where expanding the pane resizes the main chat viewport from 100% to ~60% height.

---

## Proposed Changes

### UI & Documentation

#### [MODIFY] [`UI_CONCEPTS.md`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/UI_CONCEPTS.md)
- Update Concept A title and description from "Floating Bottom Sheet Overlay" to "Docked Bottom Pane".
- Update the layout comparison table to highlight dynamic main chat viewport resizing.

---

### Core Application Layout & Logic

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Layout System Updates**:
   - Update main chat wrapper (`.chat-view` / main container) and `.expert-sheet` to operate within a flex column layout.
   - Update `.expert-sheet`:
     - **Collapsed state**: `height: 50px; flex: 0 0 50px;` (summary header bar).
     - **Open/Expanded state**: `height: 40vh; flex: 0 0 40vh;` (docked pane).
     - Smooth transitions (`transition: height 0.3s ease, flex 0.3s ease`).
   - Update Aubrey main chat container (`.chat-messages`):
     - `flex: 1 1 auto; overflow-y: auto; transition: height 0.3s ease;`

2. **JavaScript State & Scroll Controls**:
   - Simplify sheet state logic from 3 states (`collapsed`, `half`, `full`) to 2 states (`collapsed` and `open`).
   - Add auto-scroll helper on toggle: when pane expands or collapses, trigger `scrollToBottom()` on main chat container to maintain focus on the latest messages.
   - Maintain independent scrolling inside `.expert-sheet-body`.

---

## Progress Checklist

- [x] **1. UI Concepts Document Update**
  - [x] Update `UI_CONCEPTS.md` descriptions for Concept A (Docked Bottom Pane).
- [x] **2. CSS Layout Restructuring**
  - [x] Convert `.expert-sheet` from fixed overlay to docked flex item.
  - [x] Configure smooth 0.3s flex/height transitions for both main chat and bottom pane.
- [x] **3. JS Interaction & Auto-Scroll**
  - [x] Implement 2-state toggle (`collapsed` vs `open`).
  - [x] Add dynamic auto-scroll to main chat on pane expansion/collapse.
- [x] **4. Manual Verification**
  - [x] Verify latest Aubrey chat messages remain visible when bottom pane opens.
  - [x] Verify independent scrolling in both top and bottom panes.
