# 38 — Profile Tab View Integration

## Goal

Add a new **Profile** view to Hinge Tracker that is displayed when tapping the bottom-right profile avatar icon in the bottom navigation bar. The view will display a non-sticky "Profile" header (matching the typography and divider style of the "Matches" header) followed by the full-length stitched profile image (`profile_01.png`), with persistent bottom navigation tab switching and independent scroll state preservation.

---

## User Design Choices (from Interview)

1. **Navigation Style**: Persistent bottom navigation bar — the bottom bar remains docked at the bottom, allowing seamless switching between the **Matches** tab and the **Profile** tab.
2. **Profile Header**: Contains the "Profile" title with typography and divider line identical to the existing "Matches" header, **but not sticky** (it scrolls naturally out of view with the profile image).
3. **Active Nav Tab Indicator**:
   - When on the Profile tab: the profile avatar has an active white ring border (`2px solid #ffffff`), and the chat bubble icon turns inactive grey (`#888888`).
   - When on the Matches tab: the chat bubble icon is white (`#FFFFFF`), and the profile avatar has no ring border.
4. **Transition & Scroll Behavior**: Instant switch between tabs with independent scroll positions preserved.

---

## Proposed Changes

### `index.html`

#### 1. HTML Layout Structure
- Wrap the current matches view (`.sticky-header-wrapper` and `.matches-list`) inside a tab container or give it a dedicated container ID `matchesView`.
- Add a new container `#profileView` with class `profile-view`:
  - Contains a non-sticky header:
    ```html
    <div class="profile-header-wrapper">
      <div class="header">
        <div class="header-title">Profile</div>
      </div>
      <div class="divider-line"></div>
    </div>
    ```
  - Contains the profile content container displaying `profile_01.png`:
    ```html
    <div class="profile-content">
      <img src="profile_01.png" alt="Profile" class="profile-image" id="profileImage">
    </div>
    ```
- Add IDs or semantic attributes to bottom nav items:
  - Chat icon: `id="navChatBtn"` (tab: `matches`)
  - Profile avatar: `id="navProfileBtn"` (tab: `profile`)

#### 2. CSS Styling
- Add styles for `.profile-view`:
  - `display: none` by default; `display: block` when active.
  - Max-width matching app container (`390px`), centered, with bottom padding (`padding-bottom: 74px`) so the end of the profile isn't obscured by the bottom navigation bar.
- Add styles for `.profile-header-wrapper`:
  - Identical padding and typography to `.sticky-header-wrapper`, but `position: static` (not sticky) so it scrolls out of view naturally.
- Add styles for `.profile-image`:
  - `width: 100%`, `height: auto`, `display: block`, `user-select: none`.
- Add styles for active bottom navigation states:
  - Active profile avatar: `border: 2px solid #ffffff` with smooth border transitions.
  - Active chat icon vs inactive chat icon: dynamically toggle SVG fill (`#FFFFFF` vs `#888888`).

#### 3. JavaScript Tab Navigation & Scroll Management
- Maintain active tab state (`currentTab = 'matches' | 'profile'`).
- Add click listeners to `navChatBtn` and `navProfileBtn`.
- Save `window.scrollY` for the current tab before switching, and restore the stored `scrollY` for the incoming tab.
- Update DOM visibility: toggle `display` between `matchesView` and `profileView`.
- Update bottom navigation visual state:
  - Toggle white border on the profile avatar.
  - Toggle fill color (`#FFFFFF` vs `#888888`) on the chat bubble SVG.

---

## Progress Checklist

- [x] **Step 1:** Add the `#profileView` container with non-sticky "Profile" header and `profile_01.png` image to `index.html`.
- [x] **Step 2:** Add CSS rules for `.profile-view`, `.profile-header-wrapper`, `.profile-image`, and active navigation styling.
- [x] **Step 3:** Implement tab switching logic with independent scroll preservation and nav item active state updates.
- [x] **Step 4:** Verify tab switching between Matches and Profile tabs in desktop and mobile viewports.
- [x] **Step 5:** Verify that the "Profile" header scrolls naturally with the profile image, while the "Matches" header remains sticky.
- [x] **Step 6:** Verify chat overlay interaction (opening Aubrey's chat from Matches, closing it, and ensuring bottom nav behavior remains robust).

---

## Verification Plan

### Automated / Browser Verification
1. Launch local dev server or preview `index.html` in browser subagent.
2. Verify:
   - Initial load displays the Matches tab with chat icon active (white) and profile avatar inactive (no ring).
   - Tapping the bottom-right profile avatar switches to the Profile view immediately.
   - Profile avatar gains white circular ring border, and chat icon changes to `#888888`.
   - "Profile" header title is visible and scrolls off-screen as the user scrolls down through `profile_01.png`.
   - Bottom navigation remains docked at the bottom with 74px clearance.
   - Scrolling halfway down the profile, tapping the chat icon returns to Matches at its scroll position, and tapping profile returns to the profile's previous scroll position.
   - Opening Aubrey's chat overlay continues to function as expected and closes cleanly back to Matches.
