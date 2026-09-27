# 53 — Bottom Navigation: Graceful "Not Available" Toast & Badge Removal (with Profile Tab Temporarily Disabled)

## Goal

Enhance the bottom menu bar in `index.html`:
1. **Remove Notification Badge**: Remove the `9` notification number badge (`<span class="nav-badge">9</span>`) from the Heart icon.
2. **Graceful Notice Notification**: When a user taps any of the inactive/unsupported menu items:
   - The H (Discover)
   - The Star (Standouts)
   - The Heart (Likes You)
   - The Profile icon (Temporarily disabled)
   Trigger a sleek, non-intrusive in-app toast displaying: **"This feature is not available yet"**.
3. **Refined Toast Component & Micro-Interactions**:
   - Add a sleek neutral dark toast style (`app-toast info`) with an informational circle icon and smooth entrance/exit.
   - Add subtle tap micro-interactions (`:active { transform: scale(0.92); }`) to the navigation items for tactile mobile responsiveness.

---

## Architectural & UI Design

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Bottom Navigation Bar                         │
│                                                                        │
│    [  H  ]       [  ★  ]       [  ♥  ]       [  💬  ]      [ (Profile) ]
│   (Discover)   (Standouts)   (Likes You)     (Matches)      (Settings)  │
│        │             │             │             │               │     │
│        └─────────────┼─────────────┴─────────────┼───────────────┘     │
│                      │                           │                     │
│                      ▼                           ▼                     │
│             showToast(                          Switch to              │
│       "This feature is not available yet",      Matches tab            │
│                 'info'                          (Active)               │
│             )                                                          │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Badge Removal
In `index.html`:
- Remove `<span class="nav-badge">9</span>` inside the Heart navigation item.
- The Heart icon will render clean and uncluttered, matching the Star and H icons.

### 2. Navigation Item IDs & Semantics
Assign descriptive IDs and accessible button roles to the left 3 navigation items:
- `id="navDiscoverBtn"` (`role="button"`, `aria-label="Discover"`)
- `id="navStandoutsBtn"` (`role="button"`, `aria-label="Standouts"`)
- `id="navLikesBtn"` (`role="button"`, `aria-label="Likes You"`)

### 3. Toast Notification Enhancements
In `index.html`:
- **CSS**: Define `.app-toast.info`:
  - Background: Glassmorphic dark charcoal `rgba(28, 28, 30, 0.94)`
  - Border: 1px subtle border `rgba(255, 255, 255, 0.12)`
  - Icon stroke: Soft slate/silver `#98989f`
  - Typography: Clean iOS system font, 13.5px, medium weight
  - Shadow: Deep elevation shadow `0 8px 24px rgba(0, 0, 0, 0.4)`
- **JS**: Update `showToast(message, type = 'error', durationMs = 5000)`:
  - If `type === 'info'`, render an informational circle icon:
    ```html
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="8" x2="12" y2="12"></line>
      <line x1="12" y1="8" x2="12.01" y2="8"></line>
    </svg>
    ```
  - Default duration for info notices set to 2500ms for a swift, non-intrusive feel.

### 4. Event Handling (Including Temporary Profile Disable)
Bind click listeners to `navDiscoverBtn`, `navStandoutsBtn`, `navLikesBtn`, and `navProfileBtn`:
```javascript
const unavailableNotice = () => showToast('This feature is not available yet', 'info', 2500);

if (navDiscoverBtn) navDiscoverBtn.addEventListener('click', unavailableNotice);
if (navStandoutsBtn) navStandoutsBtn.addEventListener('click', unavailableNotice);
if (navLikesBtn) navLikesBtn.addEventListener('click', unavailableNotice);

// Temporarily disable profile tab navigation
if (navProfileBtn) {
  navProfileBtn.addEventListener('click', unavailableNotice);
}
```
*(Matches tab `navChatBtn` remains active as the sole primary view).*

---

## Files to Modify

### [MODIFIED] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Remove `<span class="nav-badge">9</span>` from heart icon.
- Add `id="navDiscoverBtn"`, `id="navStandoutsBtn"`, `id="navLikesBtn"` with appropriate accessibility attributes to the 3 nav elements.
- Add `.nav-item:active` tactile scale effect in CSS.
- Add `.app-toast.info` styling in CSS.
- Support `type === 'info'` in `showToast()` with info icon.
- Add event listeners on Discover, Standouts, Likes, and Profile buttons triggering `showToast('This feature is not available yet', 'info', 2500)`.

---

## Verification Plan

### Browser / UI Verification
1. Open `http://localhost:8080/` in the browser.
2. Check the bottom navigation bar:
   - Confirm the purple `9` badge on the Heart icon is completely gone.
   - Confirm Heart icon is cleanly rendered and horizontally aligned with the other icons.
3. Click the **H** icon:
   - Verify tactile tap response.
   - Verify smooth presentation of toast: *"This feature is not available yet"*.
   - Verify toast automatically dismisses after ~2.5 seconds.
4. Click the **Star** icon:
   - Verify toast displays *"This feature is not available yet"*.
5. Click the **Heart** icon:
   - Verify toast displays *"This feature is not available yet"*.
6. Click the **Profile** icon:
   - Verify toast displays *"This feature is not available yet"*.
   - Verify the profile page does not open.
7. Click the **Matches** (speech bubble) icon:
   - Verify it continues operating as the active view without showing the toast.

---

## Progress Checklist

- [x] **Step 1:** Add IDs (`navDiscoverBtn`, `navStandoutsBtn`, `navLikesBtn`) and remove `<span class="nav-badge">9</span>` in `index.html`.
- [x] **Step 2:** Add `.app-toast.info` CSS and `.nav-item:active` micro-interaction styles.
- [x] **Step 3:** Update `showToast()` to support `'info'` type with appropriate info icon.
- [x] **Step 4:** Attach click event listeners for the left 3 nav items (Discover, Standouts, Likes).
- [x] **Step 5:** Test in browser across all navigation buttons to confirm expected behavior.
