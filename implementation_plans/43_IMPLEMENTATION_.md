# 43 — Remote Mobile Vision OCR via HTTPS Static Tunnel & Graceful Error Handling

## Goal

Enable high-precision Apple Vision screenshot importing directly from a mobile device running the GitHub Pages web app. This plan:
1. **Removes the client-side Tesseract.js fallback** entirely to guarantee consistent, high-accuracy parsing exclusively via the native macOS Vision backend.
2. **Implements graceful offline error handling** with a sleek floating toast notification when the server cannot be reached.
3. **Integrates a persistent HTTPS tunnel (ngrok static domain)** via a unified launcher (`python3 server.py --tunnel`) so GitHub Pages can securely communicate with your Mac over HTTPS.
4. **Configures static domain support** via a lightweight config file (`config.js`) committed to Git, enabling zero-configuration access from mobile Safari while retaining `localStorage` overrides.

---

## User Review Required

> [!NOTE]
> **Static Domain Configured**:
> Your permanent ngrok domain is configured as:
> **`https://subplot-sarcastic-yesterday.ngrok-free.dev`**
>
> Your ngrok authtoken has been provided and will be configured in your local environment.
> We will configure this directly in `config.js` so GitHub Pages permanently points to your Mac backend with zero manual setup on your phone.

> [!NOTE]
> **No More Inconsistent Client OCR**:
> When your Mac server is offline or unreachable, the web app will no longer attempt client-side browser OCR (which caused misspelled names, split letters, and missing avatars). Instead, it will immediately display a friendly floating error toast notifying you to turn on the Mac server.

---

## Architecture & Communication Flow

```
Mobile Safari (GitHub Pages)
https://<username>.github.io/hinge-tracker/
               │
               │ HTTPS POST /api/parse-screenshot
               ▼
   Ngrok Secure Tunnel (Static Domain)
   https://subplot-sarcastic-yesterday.ngrok-free.dev/
               │
               ▼ Forwarded to port 8080
    server.py (Mac Python Server)
               │
               ▼ Process image & extract crops
       bin/vision_ocr (Swift + Apple Vision)
               │
               ▼ Return JSON { success: true, matches: [...] }
```

---

## Proposed Changes

### Configuration
#### [NEW] [config.js](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/config.js)
- Exposes `window.APP_CONFIG = { API_BASE_URL: "https://<your-static-domain>.ngrok-free.app" };`
- Loaded before `index.html` main scripts.
- Resolves the API URL with the following priority:
  1. `localStorage.getItem('hinge_api_url')` (manual override or URL param)
  2. If opened from `localhost` or `127.0.0.1`, defaults to `""` (same-origin local server)
  3. `window.APP_CONFIG.API_BASE_URL` (the static ngrok domain)

### Frontend
#### [MODIFY] [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- **Remove Tesseract.js**: Remove `<script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>` from `<head>`.
- **Remove Fallback Pipeline**: Delete client-side `analyzeScreenshotImage` and canvas slicing routines that produced degraded OCR results.
- **Graceful Error Toast**:
  - Implement a mobile-friendly toast component (`showToast(message, type)`).
  - When `POST /api/parse-screenshot` fails, times out, or throws a network error:
    - Close the import loading state / modal.
    - Show a clean floating error toast: `"Backend unreachable. Make sure your Mac server is running (python3 server.py --tunnel)."`.
- **API Base URL Integration**: Update `fetch('/api/parse-screenshot')` to prepend the resolved API base URL.
- **URL Parameter Auto-Registration**: Support `?server=https://...` query parameter to allow easy one-tap URL overrides stored in `localStorage`.

### Backend & Unified Launcher
#### [MODIFY] [server.py](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)
- Add `--tunnel` CLI flag to `server.py`:
  - When `--tunnel` is specified, checks for `ngrok` installation (or installs/downloads if needed).
  - Reads the configured static domain from `config.js` or CLI argument `--domain`.
  - Spawns `ngrok http 8080 --domain=<static-domain>` as a coordinated subprocess.
  - Automatically shuts down both server and tunnel cleanly on Ctrl+C.
  - Prints startup banner with local URL, tunnel HTTPS URL, and API health status.

---

## Progress Checklist

- [x] **Step 1:** Create `config.js` with base configuration structure and dynamic endpoint resolution helper.
- [x] **Step 2:** Update `index.html` to load `config.js`, remove Tesseract.js script imports, and remove client-side OCR fallback logic.
- [x] **Step 3:** Implement floating error toast notification in `index.html` and wire it to catch network/server failures during screenshot parsing.
- [x] **Step 4:** Ensure CORS headers in `server.py` accept cross-origin requests from GitHub Pages and ngrok headers (e.g. `ngrok-skip-browser-warning`).
- [x] **Step 5:** Add `--tunnel` flag and automatic subprocess management to `server.py`.
- [x] **Step 6:** Test unified server launch with tunnel, verify endpoint with `curl`, and test simulated network failure toast in web UI.

---

## Verification Plan

### Automated / CLI Verification
1. **Unified Server & Tunnel Launch**:
   ```bash
   python3 server.py --help
   ```
2. **Cross-Origin Health Check via HTTPS**:
   ```bash
   curl -I https://<static-domain>.ngrok-free.app/api/health
   ```
   - Verify `Access-Control-Allow-Origin: *` is present.
   - Verify HTTP 200 with JSON `{ "status": "ok", "engine": "Native Apple Vision + OpenCV" }`.

### Mobile & Browser Verification
1. **Local Mode**:
   - Open `http://localhost:8080/`.
   - Verify screenshot import works seamlessly without external dependencies.
2. **Offline Error Toast**:
   - Stop `server.py`.
   - Attempt to upload/import a screenshot on `index.html`.
   - Verify the loading overlay closes cleanly and the floating error toast displays `"Backend unreachable. Make sure your Mac server is running..."`.
   - Confirm NO browser console errors regarding Tesseract or fallback processing.
3. **Remote Mobile Mode via GitHub Pages**:
   - Open GitHub Pages app on phone with Mac server running.
   - Tap **Import Matches** and upload a Hinge screenshot.
   - Verify that the review modal displays the extracted names and high-resolution avatars processed by Apple Vision.
