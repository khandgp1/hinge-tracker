# 59 — Stitch Profile 2 and Register Preset in Dropdown

## Goal

Stitch the 10-frame scrolling screenshot sequence in `test_chats/profile_2/` (`profile_2_1.jpg` through `profile_2_10.jpg`) into a single continuous, high-resolution dating profile image (`profile_02.png`), fix natural sorting in `stitch.py`, and register the new profile as `Profile 2` in the Profile Tab dropdown switcher in `index.html`.

---

## Design Decisions (from `/grill-me` alignment)

1. **Output File & Location**:
   - Save the stitched composite as [`profile_02.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/profile_02.png) in the workspace root directory, matching the existing [`profile_01.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/profile_01.png).

2. **UI Registration & Display Label**:
   - Register the new preset in `PROFILES` inside [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html):
     ```javascript
     {
       id: 'profile_02',
       name: 'Profile 2',
       image: 'profile_02.png'
     }
     ```
   - Labeled as `"Profile 2"` to maintain clean, consistent numbering with `"Profile 1"`.

3. **Cropping & Header Handling**:
   - **Seamless Profile View**: Auto-crop static top app header (~219px status bar + Hinge "Cancel / Done / Edit / View" header) so the profile cards start right beneath the web app's simulated device header, identical to how Profile 1 is presented.
   - Do not re-attach top header or bottom footer (`keep_header=False`, `keep_footer=False`), blending seams smoothly with 20px alpha gradient.

4. **Stitcher Script Enhancements**:
   - Update `load_and_sort_images()` in [`stitch.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py) to use natural numeric sorting (e.g. `profile_2_1.jpg` before `profile_2_2.jpg` before `profile_2_10.jpg`), preventing alphabetical misordering where `10` sorts before `2`.

---

## Proposed Changes

### 1. [`stitch.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/stitch.py)
- Import `re`.
- Add a natural sort helper `natural_sort_key(s)`.
- Use `files.sort(key=natural_sort_key)` when loading files from a directory, and sort explicit inputs if provided.

### 2. Generate [`profile_02.png`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/profile_02.png)
- Execute `stitch.py` with:
  ```bash
  python3 stitch.py -i test_chats/profile_2 -o profile_02.png --no-header --no-footer --blend-height 20
  ```
- Validate image dimensions (width 591px, height ~5374px) and visual fidelity.

### 3. [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Update `const PROFILES` array:
  ```javascript
  const PROFILES = [
    {
      id: 'profile_01',
      name: 'Profile 1',
      image: 'profile_01.png'
    },
    {
      id: 'profile_02',
      name: 'Profile 2',
      image: 'profile_02.png'
    }
  ];
  ```

---

## Verification Plan

### Automated / CLI Verification
1. Run `stitch.py` on `test_chats/profile_2` and ensure natural sorting correctly orders frames 1 through 10.
2. Verify `profile_02.png` exists, is non-empty, and has valid dimensions matching frame width (591px).

### Browser / Functional Verification
1. Open active browser at `http://localhost:8080/`.
2. Navigate to the **Profile** tab.
3. Open the profile dropdown menu in the header.
4. Verify both **Profile 1** and **Profile 2** appear in the list.
5. Select **Profile 2**:
   - Verify the header title updates to "Profile 2".
   - Verify the profile image updates to `profile_02.png`.
   - Verify smooth scrolling of the full stitched profile.
6. Verify Firestore document `settings/profile` updates to `{ activeProfileId: 'profile_02' }`.
7. Switch back to **Profile 1** to confirm seamless bidirectional switching.
