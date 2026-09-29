# 58 — Multiple Dating Profiles Support with Top Title Dropdown

## Goal

Add the capability to support multiple dating profiles in the **Profile Tab** with an interactive top title dropdown menu, extensible preset architecture, and real-time cross-device Firestore synchronization between client and coach.

---

## Design Decisions (from `/grill-me` alignment)

1. **Scope & Behavior**:
   - **Profile Tab Only**: Matches, chat threads, and coach dialogues remain shared. The profile selector operates solely within the Profile tab to showcase different dating profile personas/variations.
   - When a profile is selected, the profile image (`#profileImage`) and header title update accordingly.

2. **Preset Infrastructure**:
   - Extensible preset configuration array:
     ```javascript
     const PROFILES = [
       { id: 'profile_01', name: 'Profile 1', image: 'profile_01.png' }
     ];
     ```
   - Pre-populated with the current preset (`Profile 1` using `profile_01.png`). Adding future profiles (e.g., `Profile 2` with `profile_02.png`) only requires adding an entry to this array.

3. **Header & Dropdown UI Interaction**:
   - **Header Trigger**: The Profile tab header title displays the active profile name accompanied by an iOS-style chevron (`Profile 1 ▾`).
   - **Dropdown Popover**:
     - Tapping the header trigger opens a smooth, iOS/Hinge-styled popover menu centered below the title.
     - Chevron smoothly rotates 180° when expanded.
     - Displays list of profile options; the active profile displays a checkmark indicator.
     - Selecting an option updates the active profile, immediately reflects on screen, syncs to Firestore, and closes the dropdown.
     - Tapping outside, clicking the trigger again, or pressing `Escape` dismisses the dropdown.

4. **Cross-Device Persistence & Real-Time Sync**:
   - Persists the selected profile ID in Firestore document `settings/profile` (`{ activeProfileId: 'profile_01', updatedAt: firebase.firestore.FieldValue.serverTimestamp() }`).
   - No URL query parameters used.
   - Subscribes via `onSnapshot` real-time listener so that any change made on a client device instantly updates the coach device (and vice versa).
   - If the Firestore document does not exist yet or is offline, defaults gracefully to the first preset (`PROFILES[0]`).
   - Both **Client** and **Coach** roles are permitted to switch the profile.

---

## Proposed Changes

### [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

1. **CSS Styling**:
   - Add styles for `.profile-header-title-container`:
     - Centered flex row with cursor pointer, subtle hover/active highlight, user-select none.
     - Accessible focus and tap targets.
   - Add styles for `.profile-dropdown-arrow`:
     - Inline SVG chevron with smooth `transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)`.
     - Inverted rotation (`rotate(180deg)`) when `.is-open`.
   - Add styles for `.profile-dropdown-menu`:
     - Positioned absolute below header, centered horizontally with `transform: translateX(-50%)`.
     - Rounded corners (14px), subtle border (`border: 1px solid rgba(0,0,0,0.08)`), clean drop-shadow (`0 10px 30px rgba(0,0,0,0.12)`), white background (or translucent backdrop blur).
     - Z-index elevated above profile content (`z-index: 100`).
     - Animation: scale/fade in transition.
   - Add styles for `.profile-dropdown-item`:
     - Clean list item with active state styling, checkmark icon alignment, and hover/active states.
   - Add backdrop overlay `.profile-dropdown-backdrop` to handle dismiss on outside tap.

2. **Profile Header HTML**:
   - Update `#profileView .header` in `index.html`:
     ```html
     <div class="profile-header-wrapper">
       <header class="header">
         <div class="profile-title-btn" id="profileDropdownTrigger" role="button" aria-haspopup="true" aria-expanded="false">
           <h1 class="header-title" id="profileHeaderTitle">Profile 1</h1>
           <svg class="profile-dropdown-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
             <polyline points="6 9 12 15 18 9"></polyline>
           </svg>
         </div>
         <div id="profileDropdownMenu" class="profile-dropdown-menu" style="display: none;">
           <!-- Dynamically rendered profile list -->
         </div>
       </header>
       <div id="profileDropdownBackdrop" class="profile-dropdown-backdrop" style="display: none;"></div>
       <div class="divider-line"></div>
     </div>
     ```

3. **JavaScript Logic**:
   - Define `PROFILES` array containing the initial preset.
   - Helper `getActiveProfile()` and `setActiveProfile(profileId, syncToFirestore = true)`.
   - Function `renderProfileDropdown()` to populate the dropdown menu dynamically based on `PROFILES` and highlight the active profile with a checkmark.
   - Dropdown toggle logic: open, close, backdrop click handler, Escape key handler.
   - Firestore sync:
     - `initProfileSync()`: Set up `db.collection('settings').doc('profile').onSnapshot(...)`.
     - When snapshot updates, invoke `setActiveProfile(activeProfileId, false)` to update DOM without cyclical writes.
     - On user selection, call `db.collection('settings').doc('profile').set({ activeProfileId: profileId, updatedAt: ... }, { merge: true })`.

---

## Verification Plan

### Browser / Functional Verification
1. **Initial Rendering**:
   - Open `http://localhost:8080/`.
   - Switch to the Profile tab.
   - Verify the top title displays `Profile 1` with a downward chevron.
   - Verify `profile_01.png` is displayed cleanly.
2. **Dropdown Interaction**:
   - Click the title `Profile 1 ▾`.
   - Verify the menu opens smoothly, the chevron rotates up, and `Profile 1` is displayed with a checkmark.
   - Click outside or press `Escape`; verify menu closes and chevron resets.
3. **Cross-Device / Multi-Tab Real-Time Sync**:
   - Open a second window/tab (e.g. `http://localhost:8080/?role=coach`).
   - Switch to Profile tab in both windows.
   - Switch profile or verify Firestore listener updates the header title and displayed image simultaneously on both tabs.
4. **Code Extensibility Test**:
   - Verify that adding a secondary profile entry to the `PROFILES` array dynamically adds the row to the dropdown and allows toggling back and forth.

---

## Progress Checklist

- [x] Add CSS styling for profile dropdown trigger, chevron animation, and menu popover in `index.html`
- [x] Update `#profileView` header HTML with dropdown trigger container and menu
- [x] Implement `PROFILES` registry and dropdown rendering / toggling logic
- [x] Implement Firestore `settings/profile` real-time listener and update logic
- [x] Test dropdown interactions, dismiss behaviors, and cross-tab/cross-role real-time sync
