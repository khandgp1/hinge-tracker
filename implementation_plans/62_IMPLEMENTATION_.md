# 62 — Remove Preview Snippet from Match List

## Goal

Completely remove the preview snippet line (`.preview-text`) from all match rows in the main Match list, displaying only the match's avatar and name vertically centered within the existing 91px row height.

---

## Design Decisions (from `/grill-me` alignment)

1. **Scope — Main Match List Only**:
   - Completely remove the preview snippet line (`.preview-text`) from match cards in the main Match list view.
   - Retain the `"You matched"` subtitle in the Import Review modal as-is for screenshot import confirmation.

2. **Row Height & Vertical Alignment**:
   - Keep the existing spacious **91px** row height (`height: 91px` on `.match-row`).
   - Remove `margin-bottom: 3px` from `.name-row` so the match name sits perfectly vertically centered next to the 63px circular avatar.

3. **Row Accessories**:
   - Keep the row completely minimal: only the avatar and the name.
   - No right-side chevrons, timestamps, or unread badges.

4. **Typography**:
   - Preserve current match name typography (**21px**, font-weight **600**, letter-spacing **-0.01em**, color `#000000`).

---

## Proposed Changes

### [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

#### 1. CSS Spacing Update (`.name-row`)
- In `.name-row` (around line 146):
  ```css
  .name-row {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 0;
  }
  ```
- This ensures `.match-info` vertically centers `.name-row` cleanly within the 91px row without bottom bias.

#### 2. Match Row Template (`renderMatchesList()`)
- In `renderMatchesList()` (around line 2245):
  ```javascript
  container.innerHTML = matchesData.map((item) => `
    <div class="match-row" data-name="${item.name}">
      <img class="avatar" src="${item.image}" alt="${item.name}">
      <div class="match-info">
        <div class="name-row">
          <span class="name">${item.name}</span>
        </div>
      </div>
    </div>
    <div class="divider-line"></div>
  `).join('');
  ```

---

## Implementation Checklist

- [x] **Step 1: CSS Spacing Adjustment**
  - [x] Update `.name-row` in `index.html` to eliminate the bottom margin (`margin-bottom: 0;`).

- [x] **Step 2: Template Update in `renderMatchesList()`**
  - [x] Remove the `.preview-text` element from the template string inside `renderMatchesList()`.

- [x] **Step 3: Verification & Regression Testing**
  - [x] Verify the Match list view at `http://localhost:8080/`:
    - [x] Rows show only avatar and match name.
    - [x] Name is vertically centered with respect to avatar and the 91px row.
    - [x] Clicking a match row still opens the chat view properly.
  - [x] Verify that the Import Review modal (`matchesFileInput` flow) still displays the `"You matched"` subtitle as expected.
