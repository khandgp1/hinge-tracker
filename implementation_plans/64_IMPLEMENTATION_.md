# 64 — Store Image Uploads Locally for Debugging

## Goal

Store all incoming image uploads (match list screenshots and chat screenshots) to a local debug directory on the server before parsing, so that uploaded screenshots can be easily inspected, reproduced in offline test scripts, and debugged when OCR or parsing issues occur.

---

## Requirements & Scope

1. **Upload Endpoints Covered**:
   - `POST /api/parse-screenshot`: Match list screenshots (typically multipart `screenshot` or raw binary).
   - `POST /api/parse-chat`: Chat screenshot images (JSON payload with base64 images & file metadata, or multipart form data).

2. **Storage Location & Organization**:
   - Base directory: `debug_uploads/` in the workspace root.
   - Subdirectories:
     - `debug_uploads/screenshots/`: for match list screenshots from `/api/parse-screenshot`.
     - `debug_uploads/chats/` (or `debug_uploads/chats/<match_name>/`): for chat screenshot batches from `/api/parse-chat`.
   - Ensure the directory is created automatically if it doesn't already exist.

3. **File Naming & Formats**:
   - Use timestamps and sanitized original filenames to avoid collisions and preserve ordering:
     - For screenshots: `YYYYMMDD_HHMMSS_<original_name_or_screenshot>.png`
     - For chats: `YYYYMMDD_HHMMSS_<match_name>_<index>_<original_name>.png` (or `.jpg`)
   - If an uploaded image is raw bytes or base64 without extension, detect format from image headers or default to `.png`.

4. **Metadata Logging (Optional / Contextual)**:
   - Save a small companion metadata JSON (e.g. `YYYYMMDD_HHMMSS_meta.json`) or log entry recording:
     - Timestamp
     - Endpoint (`/api/parse-screenshot` or `/api/parse-chat`)
     - Match name (if provided)
     - Original client filename(s) and `lastModified` timestamp(s)
     - Saved file paths on disk

5. **Git Hygiene & Privacy**:
   - Add `debug_uploads/` to `.gitignore` so uploaded debug images are not committed to source control.

6. **Server Console Output**:
   - Log the saved paths to stdout so the developer can immediately see where images were stored during active sessions:
     - `[DEBUG] Saved 1 screenshot upload to debug_uploads/screenshots/...`
     - `[DEBUG] Saved 3 chat uploads for 'Sakshi' to debug_uploads/chats/...`

---

## Detailed Implementation Details

### 1. Update `.gitignore`
Add:
```gitignore
# Debug Uploads
debug_uploads/
```

### 2. Helper Functions in [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)
Define helper function to save uploaded image bytes safely:
```python
DEBUG_UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_uploads")

def save_debug_upload(
    image_bytes: bytes,
    category: str = "screenshots",
    prefix: str = "",
    filename: Optional[str] = None
) -> str:
    """
    Saves uploaded image bytes to debug_uploads/<category>/ with timestamped filename.
    Returns the absolute path of the saved file.
    """
    ...
```

### 3. Hook into `do_POST` in [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)
- For `POST /api/parse-screenshot`:
  - After extracting `image_bytes_list`, iterate and save each image to `debug_uploads/screenshots/`.
  - Log saved file path(s) to console.
- For `POST /api/parse-chat`:
  - After extracting `image_bytes_list`, match metadata/filenames with images if present.
  - Save to `debug_uploads/chats/` (or `debug_uploads/chats/<match_name>/`).
  - Optionally write accompanying `meta.json` with client timestamps and file details.
  - Log saved file path(s) to console.

---

## Verification & Testing Plan

1. **Verify Directory & Git Ignore**:
   - Check that `debug_uploads/` is ignored by git (`git status` does not show it as untracked).
2. **Verify `/api/parse-screenshot`**:
   - Send a test match screenshot via web UI or curl to `POST /api/parse-screenshot`.
   - Confirm file is written to `debug_uploads/screenshots/` and opens properly as a valid image.
3. **Verify `/api/parse-chat`**:
   - Upload chat screenshots via the web UI chat modal (e.g. Sakshi or Aubrey chat screenshots).
   - Confirm files are saved in `debug_uploads/chats/` with match name and timestamp.
   - Verify parsing continues to work seamlessly without errors or delays.

---

## Progress Checklist

- [x] Add `debug_uploads/` to `.gitignore`
- [x] Implement `save_debug_upload()` helper function in `server.py`
- [x] Hook upload saving into `POST /api/parse-screenshot` handler in `server.py`
- [x] Hook upload saving into `POST /api/parse-chat` handler in `server.py`
- [x] Test saving with `curl` or browser upload on `/api/parse-screenshot`
- [x] Test saving with browser upload on `/api/parse-chat`
- [x] Validate image integrity and console logging
