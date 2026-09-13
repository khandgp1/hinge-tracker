# Implementation Plan 26 – 50/50 Chat / Coach Split (No Keyboard)

When the expert (coach) sheet is expanded on mobile with **no keyboard open**, the Hinge chat pane and the Coach dialog should occupy equal halves of the screen. Currently the coach sheet takes a fixed `40vh`, which doesn't produce a true 50/50 split because the chat header (~54px) eats into the chat body's share.

## User Review Required

> [!IMPORTANT]
> **Layout Change:** The expanded coach sheet will switch from a fixed `40vh` height to a flex-based `50 1 0%` split, giving both panes equal weight. The chat header (~54px) sits outside both flex regions so the _body_ areas won't be pixel-identical, but the overall visual impression will be a balanced 50/50 divide.

> [!NOTE]
> The **keyboard-active** split (35% chat / 65% coach) remains **unchanged** — this plan only affects the no-keyboard expanded state.

---

## Proposed Changes

### Core Layout CSS

#### [MODIFY] [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **Give `.chat-body` an explicit flex value for equal splitting:**
   - Change `.chat-body { flex: 1; }` → `.chat-body { flex: 50 1 0%; }` so it participates in a weighted flex split with the expert sheet.

2. **Switch `.expert-sheet.open` / `.expert-sheet.half` from fixed `40vh` to flex-based 50/50:**
   - Remove `height: 40vh; flex-basis: 40vh;` and replace with `height: auto; flex: 50 1 0%;` so both panes get equal flex weight.

3. **Keep `.expert-sheet.full` at 75vh** — no change needed; "full" is an intentionally larger state.

4. **Preserve the existing keyboard-active overrides** (lines 482–510) — these already set their own flex values (`35 1 0%` / `65 1 0%`) which take precedence via higher specificity.

---

## Verification Plan

### Manual Verification
- Open the app on a mobile viewport (390px) or device.
- Tap into Aubrey's chat, expand the coach sheet.
- Confirm the Hinge chat body and the coach sheet visually occupy equal halves of the screen below the chat header.
- Open the keyboard (tap into the coach input field) and confirm the 35/65 keyboard-active split still works as before.
- Collapse the sheet and confirm it returns to the 56px collapsed bar.

---

## Progress Checklist

- [x] **1. Update `.chat-body` flex value**
  - [x] Change `flex: 1` → `flex: 50 1 0%` in the base `.chat-body` rule.
- [x] **2. Update `.expert-sheet.open` / `.expert-sheet.half` to flex-based 50/50**
  - [x] Replace `height: 40vh; flex-basis: 40vh;` with `height: auto; flex: 50 1 0%;`.
- [x] **3. Verify keyboard-active split unchanged**
  - [x] Confirm 35/65 keyboard-active split still works (no CSS changes needed there).
- [ ] **4. Visual verification**
  - [ ] Confirm 50/50 split on mobile with no keyboard.
  - [ ] Confirm collapsed state still works (56px bar).
  - [ ] Confirm full state still works (75vh).
