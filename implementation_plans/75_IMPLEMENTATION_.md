# 75 — 1:1 Square Photo Cropping in Photo Versions

## Goal

Implement a native-fidelity **1:1 Square Photo Cropper** accessible directly from the **Photo Versions Sheet** (`#versionComparisonSheet`), inspired by Hinge's iOS photo editing experience. Users can tap a **"Crop"** button on any version in their stack, enter a dedicated **"Edit Photo"** screen with a 1:1 square viewport, pan/drag, pinch/wheel zoom, subtle zoom slider, rule-of-thirds grid lines, and save the result as a new version in the stack (non-destructive) labeled e.g. `"Version X — Square Crop"` for side-by-side comparison and lineup selection.

---

## Architectural & UX Specifications

### 1. Entry Point in Photo Versions Sheet
- Add a dedicated **"Crop"** button (`#versionCropBtn`) to the `.version-actions-bar` in `#versionComparisonSheet` alongside **Set Cover**, **Download**, **Detach**, and **Delete**.
- Action bar updated with balanced sizing and high-contrast iconography.
- Tapping "Crop" loads the currently previewed photo into the 1:1 Square Photo Cropper modal (`#photoCropModal`).

### 2. "Edit Photo" Modal Screen (`#photoCropModal`)
- **Container**: Full-screen modal overlay with iOS-native styling:
  - Top bar:
    - Left: `"Cancel"` text button in Hinge plum (`#7b2046`).
    - Center: `"Edit Photo"` title (17px, bold).
    - Right: `"Done"` text button in Hinge plum (`#7b2046`, bold).
- **1:1 Square Crop Viewport (`#photoCropViewportContainer`)**:
  - Exact 1:1 aspect ratio box (width: `min(350px, calc(100vw - 32px))`).
  - Dark/subtle neutral background with rounded border radius (12px) matching modern iOS Hinge.
  - Image element dynamically positioned with GPU-accelerated CSS transforms.
  - **Rule-of-Thirds Grid (`.photo-crop-grid`)**:
    - Semi-transparent 3x3 grid lines (`rgba(255, 255, 255, 0.45)` with subtle shadow/border) visible during interaction/editing to guide portrait framing and eye-level alignment.
- **Controls & Adjustments**:
  - **Pan Gesture**: Direct touch-drag (mobile) or mouse-drag (desktop).
  - **Pinch-to-Zoom**: Native two-finger pinch-to-zoom on touch screens.
  - **Wheel-Zoom**: Smooth trackpad/mouse scroll wheel zoom on desktop.
  - **Subtle Zoom Slider (`#photoCropZoomSlider`)**:
    - Placed underneath the crop square with zoom-out and zoom-in icons for quick, accessible scaling.
    - Synchronized with touch/wheel zoom in real time.
  - **Aspect-Fill Boundary Clamping**:
    - Minimum scale constrained so the photo always completely fills the 1:1 square (zero letterboxing, black bars, or empty gaps).
    - Pan offsets clamped so image edges never pull inside the crop boundary.

### 3. Non-Destructive Version Generation & Persistence
- When the user taps **"Done"**:
  - An offscreen HTML5 canvas extracts the exact cropped region mapped from natural source pixels to a crisp 1080×1080 JPEG (`quality: 0.88`).
  - Generates a new `PhotoVersion`:
    ```javascript
    {
      id: "v_<timestamp>_<rand>",
      src: croppedDataUrl,
      label: `Version ${stack.versions.length + 1} — Square Crop`,
      createdAt: Date.now()
    }
    ```
  - Appends the new version to `stack.versions`.
  - Saves to `localStorage` (`hinge_gallery_stacks`) and synchronizes with Firestore.
  - Closes the Edit Photo modal and switches the active version in `#versionComparisonSheet` to the newly cropped variant.
  - Triggers thumbnail update in `#lineupGalleryGrid`.

---

## Implementation Checklist

- [x] **Step 1: Modal Markup & Action Bar Button in `index.html`**
  - [x] Add `#versionCropBtn` to `.version-actions-bar`.
  - [x] Add `#photoCropModal` with header (Cancel, Edit Photo, Done), 1:1 square crop viewport with 3x3 grid, and zoom slider bar.

- [x] **Step 2: CSS Styles in `index.html`**
  - [x] Style `.crop-modal-overlay`, `.photo-crop-header`, and plum navigation buttons (`#7b2046`).
  - [x] Style `#photoCropViewportContainer` with 1:1 aspect ratio, overflow hidden, and rounded corners.
  - [x] Style 3x3 rule-of-thirds grid overlay lines.
  - [x] Style `.photo-crop-zoom-bar` and slider controls.

- [x] **Step 3: Interactive Pan, Zoom & Clamping Controller**
  - [x] Implement `openPhotoCropModal(imageSrc)`.
  - [x] Implement aspect-fill minimum zoom and boundary clamping math.
  - [x] Implement single-finger / mouse drag pan handlers.
  - [x] Implement two-finger pinch zoom and wheel zoom handlers.
  - [x] Implement zoom slider change synchronization.

- [x] **Step 4: Canvas 1:1 Export & Stack Version Creation**
  - [x] Implement `savePhotoCrop()` extracting 1080×1080 slice to JPEG data URL.
  - [x] Append new version to `stack.versions` labeled `"Version X — Square Crop"`.
  - [x] Persist via `saveGalleryStacks(true)` and update UI.

- [x] **Step 5: Testing & Verification**
  - [x] Verify crop launching from single-version and multi-version photos.
  - [x] Test pan and pinch/wheel zoom on mobile and desktop viewports.
  - [x] Verify aspect-fill clamping prevents empty edges (700 coordinate test cases passed).
  - [x] Verify saved crop creates a new version without modifying the original.
  - [x] Verify selection into profile lineup slots.
