# 77 — Cross-Device Photo Library Synchronization & Per-Stack Firestore Architecture

## Goal

Ensure the **Photo Library**, **Uploads**, **Cropping**, and **Photo Versions** are 100% reliably synchronized across devices (phone and laptop). Eliminate the silent Firestore 1MB document size limit failure by migrating from a single monolithic document to a **per-stack Firestore collection (`gallery_stacks/{stackId}`)**, applying **smart Retina-optimized image compression** (~800×800 at 0.80 quality), and setting the cropped version as the stack's **Cover photo** upon saving.

---

## Root Cause Analysis

1. **Firestore 1MB Hard Document Limit**:
   - Currently, `saveLineupToFirestoreAndLocal()` attempts to serialize all stacks, up to 5 versions per stack, 6 lineup slots, and a duplicate `customImages` array into a single Firestore document (`settings/profile_lineup`).
   - Crops were rendered to 1080×1080 at 0.88 JPEG quality (~500KB–700KB base64), and uploads to 1200px at 0.85 quality (~400KB–600KB base64).
   - Because `customGalleryPhotos` duplicated every image string, even a single crop pushed document size over 1,048,576 bytes (1 MiB).
   - Firestore rejected the write with `Transaction or write exceeds maximum size of 1048576 bytes`, which was caught and silenced in `console.warn`. The phone saved locally to `localStorage`, but Firestore never updated, meaning the laptop never saw the crop.

2. **Cover Photo Disconnect**:
   - When saving a crop, `savePhotoCrop()` only appended the version to `stack.versions` without setting `stack.coverVersionId`.
   - As a result, the gallery grid thumbnail continued to display the original uncropped photo.

---

## Architectural & UX Specifications

### 1. Per-Stack Firestore Sync (`gallery_stacks/{stackId}`)
- Instead of packing all gallery stacks into `settings/profile_lineup`, store each stack in a dedicated Firestore document:
  - Collection: `gallery_stacks`
  - Document ID: `stack.id`
  - Data shape:
    ```javascript
    {
      id: stack.id,
      coverVersionId: stack.coverVersionId,
      versions: stack.versions.map(v => ({
        id: v.id,
        src: v.src,
        label: v.label || '',
        createdAt: v.createdAt || Date.now()
      })),
      createdAt: stack.createdAt || Date.now(),
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    }
    ```
- Deletions, detaches, and merges also sync to `gallery_stacks` (e.g. `db.collection('gallery_stacks').doc(stackId).delete()`).

### 2. Lightweight Profile Lineup Document (`settings/profile_lineup`)
- Retain `settings/profile_lineup` strictly for lineup state:
  ```javascript
  {
    slots: activeLineupSlots,
    stackIds: galleryStacks.map(s => s.id),
    updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
    updatedBy: currentRole || 'client'
  }
  ```
- Remove the redundant `customImages` and monolithic `galleryStacks` arrays from `profile_lineup` writes, preventing bloat.

### 3. Smart Image Compression for Retina Screens
- **Cropping (`savePhotoCrop`)**:
  - Export canvas slice at **800×800** with **JPEG quality 0.80**.
  - Produces crisp, pixel-dense 2x Retina clarity in mobile cards (displayed at ~350px viewport) while cutting base64 payload size by **~85%** (down to ~60KB–80KB).
- **Uploads & Variants (`handlePhotoUpload` & `handleVariantUpload`)**:
  - Scale max dimension to **960px** at **JPEG quality 0.80** (~65KB–85KB base64).

### 4. Crop Application: Automatic Cover Update
- In `savePhotoCrop()`:
  - Set `stack.coverVersionId = newVersion.id`.
  - Active 6-slot lineup slots remain unchanged until the user manually chooses to apply the version to a slot (as agreed).

### 5. Real-Time Cross-Device Synchronization
- Set up a real-time listener on `db.collection('gallery_stacks').onSnapshot(...)`:
  - Merges incoming stacks into `galleryStacks` and persists to `localStorage`.
  - Dynamically refreshes UI:
    - If Photo Gallery is open (`isGalleryModalOpen`): updates `#lineupGalleryGrid` and selection indicators.
    - If Photo Versions sheet is open (`activeSheetStackId`): updates `#versionComparisonSheet` and scrubber track.
- Seamlessly handles offline fallback and ignores echo updates when `doc.metadata.hasPendingWrites` is true.

---

## Implementation Checklist

- [x] **Step 1: Smart Retina Image Compression**
  - [x] Update `savePhotoCrop()` to 800×800 canvas and JPEG quality 0.80.
  - [x] Update `handlePhotoUpload()` to max dimension 960px and JPEG quality 0.80.
  - [x] Update `handleVariantUpload()` to max dimension 960px and JPEG quality 0.80.
- [x] **Step 2: Crop Application — Auto Cover Update**
  - [x] Set `stack.coverVersionId = newVersion.id` in `savePhotoCrop()`.
  - [x] Retain lineup slot assignment until explicitly selected.
- [x] **Step 3: Per-Stack Firestore Sync Functions**
  - [x] Implement `syncStackToFirestore(stack)` saving to `gallery_stacks/{stackId}`.
  - [x] Implement `deleteStackFromFirestore(stackId)` deleting from `gallery_stacks/{stackId}`.
  - [x] Update `saveGalleryStacks(syncToFirestore, targetStackId)` to target edited stacks.
  - [x] Update `detachVersionFromStack()`, `deleteVersionFromStack()`, and `mergeSelectedStacks()` to sync affected stack documents.
  - [x] Update `setStackCoverVersion()` and inline label editing to sync stack document.
- [x] **Step 4: Streamlined Lineup Document**
  - [x] Update `saveLineupToFirestoreAndLocal()` to store only `slots`, `stackIds`, and metadata in `settings/profile_lineup` (eliminating duplicate arrays).
- [x] **Step 5: Real-Time Cross-Device Listeners**
  - [x] Implement real-time listener on `db.collection('gallery_stacks')` to propagate stacks, crops, and versions across devices in milliseconds.
  - [x] Update lineup slots listener on `db.collection('settings').doc('profile_lineup')`.
- [x] **Step 6: Syntax & Regression Validation**
  - [x] Verified full inline script syntax with Node.js (122,906 chars, 0 errors).

---

## Verification & Test Plan

1. **Crop Sync to Laptop**:
   - Perform a square crop on phone.
   - Verify Firestore `gallery_stacks/{stackId}` document is written successfully with no size warnings.
   - Verify laptop receives real-time update in milliseconds and displays the new version in the Photo Versions scrubber track.
2. **Cover Thumbnail**:
   - Verify the cropped version automatically becomes the Cover thumbnail in the Photo Gallery grid.
3. **Uploads & Variants**:
   - Upload new photo and new variant in stack; verify sync to other device.
4. **Lineup Reorder**:
   - Reorder lineup slots and verify `settings/profile_lineup` updates across devices.
