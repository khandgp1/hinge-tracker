# 73 — Photo Library Version Grouping & Comparison Sheet

## Goal

Implement **Photo Stacks & Version Grouping** within the **Photo Selector Gallery** (`#lineupGalleryView` in `#profileView`), enabling users to group multiple crops, color treatments, or variations of an image into unified stacks, inspect them in a dedicated **Version Comparison Sheet**, and select the optimal variant for their 6-photo profile lineup without grid clutter.

---

## Architectural & UX Specifications

### 1. Gallery Grid Presentation & Badges
- **Stack Thumbnail**:
  - Displays the active **Cover Version** image for each photo stack.
  - **Frosted Glass Version Pill**: Positioned in the bottom-left corner (`⧉ <count>`, e.g., `⧉ 3`).
    - Styled with iOS-inspired blur (`rgba(0, 0, 0, 0.6)`, `backdrop-filter: blur(8px)`, white text, pill radius).
    - Only visible when the item has 2 or more versions.
  - **Numbered Selection Badge (`1`–`6`)**: Positioned in the top-right corner.
    - Active when any version from this stack is currently selected in `pendingGallerySelection`.
    - Shows index `1`–`6`.
- **Interaction Logic**:
  - **Standalone Photos (1 Version)**: Tapping the thumbnail directly toggles selection into `pendingGallerySelection` (1–6).
  - **Stacked Photos (2+ Versions)**: Tapping the thumbnail opens the **Version Comparison Sheet** (`#versionComparisonSheet`), allowing the user to review all variants before choosing one for the lineup.

---

### 2. Version Comparison Sheet (`#versionComparisonSheet`)
- **Container**: Semi-modal / bottom sheet overlay with backdrop, smooth sliding transition, and dismiss on backdrop click or close button.
- **Top Bar**:
  - Left: Close icon button (`✕`).
  - Center: Title `"Photo Versions"` + count indicator (e.g. `"2 of 3"`).
  - Right: `"Done"` text button.
- **Hero Preview**:
  - Full 4:5 aspect ratio preview displaying the currently inspected variant.
  - Smooth visual transition when scrubbing between variants.
- **Variant Label & Status**:
  - Editable tag badge (e.g., `"Version 1 — Original"`, `"Version 2 — Tight Crop"`).
  - Tap-to-edit inline text input or edit button to update the variant label.
  - Primary Cover badge (`★ Cover`) if this variant is the stack's cover image.
- **Horizontal Thumbnail Scrubber**:
  - Leading `+ Add Version` tile with hidden file input to upload new variants directly to this stack from device.
  - Miniature scrollable thumbnail strip of all versions in the stack.
  - Highlighted border on the currently active preview variant.
- **Management Action Bar**:
  - **Set as Cover**: Designates this variant as the stack's primary gallery cover image.
  - **Detach**: Separates this variant into its own standalone photo stack in the gallery.
  - **Delete**: Permanently removes this variant from the stack (with confirmation, disabled if only 1 version remains).
- **Lineup Selection Button**:
  - Full-width action button at the bottom:
    - `"Select for Lineup"`: Assigns this variant to the next open slot (`1`–`6`).
    - `"Use in Slot #X"`: If this stack is already in the lineup, swaps this variant into slot `X`.
    - `"Remove from Lineup"`: Deselects the stack if already active.

---

### 3. Stack Creation & Organize Mode
- **Pathway 1: In-Sheet Upload (`+ Add Version`)**:
  - Uploading via the scrubber's `+ Add Version` tile compresses the image via canvas (matching existing 1200px max, 0.85 JPEG) and appends it to the open stack.
- **Pathway 2: Gallery Header Organize / Merge Mode**:
  - A `"Group"` / `"Organize"` button in the `#lineupGalleryView` top nav header.
  - Tapping toggles **Organize Mode**:
    - Top title changes to `"Select photos to group"`.
    - Header shows `"Cancel"` and `"Merge (X)"` (disabled until >= 2 items are selected).
    - Grid thumbnails display selection checkboxes.
    - Tapping items checks/unchecks them for merging.
    - Tapping `"Merge"` bundles all selected items into a single stack, setting the first selected photo as the default cover version, and exits Organize Mode.

---

### 4. Lineup Sandbox Decoupling & Compatibility
- The **Lineup Builder Sandbox** (`#lineupSandboxView`) and Hinge Live Feed remain cleanly decoupled from version management.
- Lineup slots strictly receive the resolved `src` string of the chosen version.
- `activeLineupSlots` maintains its exact `string[6]` format for 100% backward compatibility with Coach sync, Firestore listeners, and profile rendering.

---

### 5. Data Architecture, Persistence & Migration
- **Schema**:
  ```typescript
  interface PhotoVersion {
    id: string;              // "v_<timestamp>_<rand>"
    src: string;             // relative path or base64 data URI
    label: string;           // "Original", "Crop A", etc.
    createdAt: number;
  }

  interface GalleryStackItem {
    id: string;              // "stack_<timestamp>_<rand>"
    coverVersionId: string;  // ID of version used as cover
    versions: PhotoVersion[];
    createdAt: number;
  }
  ```
- **Storage Keys**:
  - LocalStorage: `hinge_gallery_stacks` (stores `GalleryStackItem[]`).
  - Firestore: `settings/profile_lineup.galleryStacks`.
- **Auto-Migration**:
  - If `hinge_gallery_stacks` is absent or empty, initialize from `customGalleryPhotos` and `DEFAULT_LINEUP_PHOTOS` (`profile/01.jpg`–`05.jpg`), wrapping each into a single-version `GalleryStackItem`.

---

## Proposed Changes

### 1. Markup in `index.html`
- Add **"Organize"** button (`#lineupGalleryOrganizeBtn`) and merge action button (`#lineupGalleryMergeBtn`) in `#lineupGalleryModal` / `#lineupGalleryView` header.
- Add `#versionComparisonSheet` overlay container with header, hero preview, label badge, thumbnail strip with `+ Add Version` tile, management actions, and lineup selection button.

### 2. CSS in `index.html`
- Styles for `.lineup-version-pill` (frosted glass blur in bottom-left of thumbnail).
- Styles for `#lineupGalleryView.is-organize-mode` (checkbox overlays, active highlight).
- Styles for `#versionComparisonSheet` (bottom sheet animation, hero 4:5 image container, thumbnail scrubber, action buttons, editable label pill).

### 3. JavaScript in `index.html`
- Data store `galleryStacks = []` with loading, LocalStorage caching, and Firestore synchronization.
- Migration utility `migrateLegacyPhotosToStacks()` to initialize default/custom photos into stack items.
- Updated `renderGalleryGrid()` to render stack covers with `.lineup-version-pill` and handle tap routing (open comparison sheet for stacks vs. toggle lineup selection for single photos).
- Organize mode state (`isOrganizeMode`, `organizeSelectedStackIds = Set()`) with merge handler `mergeSelectedStacks()`.
- Version Comparison Sheet controller:
  - `openVersionComparisonSheet(stackId)`
  - `closeVersionComparisonSheet()`
  - `renderVersionSheet(stackId, activeVersionIndex)`
  - `setStackCoverVersion(stackId, versionId)`
  - `detachVersionFromStack(stackId, versionId)`
  - `deleteVersionFromStack(stackId, versionId)`
  - `updateVersionLabel(stackId, versionId, newLabel)`
  - `handleVariantUpload(stackId, file)`
  - `selectVersionForLineup(stackId, versionId)`

---

## Implementation Checklist

- [x] **Step 1: Data Structures & Migration Logic**
  - [x] Define `GalleryStackItem` and `PhotoVersion` structures in `index.html`.
  - [x] Implement `migrateLegacyPhotosToStacks()` to convert existing `DEFAULT_LINEUP_PHOTOS` and `customGalleryPhotos` into stack format.
  - [x] Implement persistence helpers (`saveGalleryStacks()`, `loadGalleryStacks()`, Firestore sync).

- [x] **Step 2: Gallery Grid Markup & Organize Mode Header**
  - [x] Add `#lineupGalleryOrganizeBtn` and `#lineupGalleryMergeBtn` to `#lineupGalleryModal` header.
  - [x] Add organize mode title and cancel handlers.

- [x] **Step 3: Gallery Grid Thumbnail Rendering with Stack Pills**
  - [x] Update `renderGalleryGrid()` to render stack cover thumbnails.
  - [x] Add `.lineup-version-pill` for stacks with 2+ versions (`⧉ <count>`).
  - [x] Wire thumbnail click behavior: open comparison sheet if >= 2 versions, else toggle lineup selection.
  - [x] Add organize mode checkbox overlays and merge selection behavior.

- [x] **Step 4: Version Comparison Sheet Markup & CSS**
  - [x] Add `#versionComparisonSheet` HTML overlay markup (Header, Hero Preview, Editable Label, Scrubber, Action Bar, Lineup Select Button).
  - [x] Add CSS styling for bottom sheet slide-in, hero preview, thumbnail scrubber, frosted glass badges, and action buttons.

- [x] **Step 5: Version Comparison Sheet Interactions & Management**
  - [x] Implement `openVersionComparisonSheet()` and `renderVersionSheet()`.
  - [x] Implement scrubbing between versions with active highlight.
  - [x] Implement inline label editing (`updateVersionLabel`).
  - [x] Implement `+ Add Version` file upload (`handleVariantUpload`).
  - [x] Implement `setStackCoverVersion()`.
  - [x] Implement `detachVersionFromStack()`.
  - [x] Implement `deleteVersionFromStack()`.
  - [x] Implement `selectVersionForLineup()` to update `pendingGallerySelection` and sync seamlessly.

- [x] **Step 6: Organize & Merge Flow Implementation**
  - [x] Implement `toggleOrganizeMode()`.
  - [x] Implement `mergeSelectedStacks()` to bundle multiple photos into a single stack.
  - [x] Connect header Merge button and status counter.

- [x] **Step 7: Verification & Testing**
  - [x] Test uploading variants into an existing photo.
  - [x] Test merging two or more existing photos into a stack.
  - [x] Test switching between variants in the comparison sheet and selecting for lineup.
  - [x] Test detaching and deleting variants.
  - [x] Verify 6-photo lineup selection proceeds smoothly into `#lineupSandboxView` without breaking existing profile flow.
