#!/usr/bin/env python3
"""
Hinge Tracker Local Server & High-Performance Vision Backend
-------------------------------------------------------------
Serves static frontend files and exposes a native Apple Vision & OpenCV
screenshot parsing endpoint at POST /api/parse-screenshot.
"""

import os
import sys
import json
import base64
import tempfile
import subprocess
import email.parser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np

# Directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VISION_BIN = os.path.join(BASE_DIR, "bin", "vision_ocr")


def compute_ahash(img_bgr: np.ndarray) -> str:
    """Compute 8x8 average perceptual luminance hash for deduplication."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (8, 8), interpolation=cv2.INTER_AREA)
    avg = np.mean(resized)
    bits = (resized > avg).flatten()
    hash_val = 0
    for b in bits:
        hash_val = (hash_val << 1) | int(b)
    return f"{hash_val:016x}"


def run_vision_ocr(image_path: str) -> Dict[str, Any]:
    """Execute native Swift Apple Vision OCR binary."""
    if not os.path.exists(VISION_BIN):
        # Auto-compile if missing
        print("[SERVER] Compiling bin/vision_ocr using swiftc...")
        os.makedirs(os.path.dirname(VISION_BIN), exist_ok=True)
        swift_src = os.path.join(BASE_DIR, "vision_ocr.swift")
        subprocess.run(["swiftc", "-O", swift_src, "-o", VISION_BIN], check=True)

    result = subprocess.run([VISION_BIN, image_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Vision OCR failed: {result.stderr}")
    return json.loads(result.stdout)


def parse_screenshot_image(img_bgr: np.ndarray) -> List[Dict[str, Any]]:
    """
    Parse Hinge matches from an image:
    1. Runs native Apple Vision OCR.
    2. Detects bottom navigation boundary.
    3. Finds horizontal divider lines.
    4. Centrally crops circular avatars.
    5. Excludes banners, headers, and truncated bottom rows.
    """
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Save to temporary file for Vision CLI
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
        cv2.imwrite(tmp_path, img_bgr)

    try:
        ocr_data = run_vision_ocr(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 1. Detect bottom navigation bar boundary
    bottom_boundary = h
    for y in range(h - 1, int(h * 0.75), -1):
        samples = []
        for x in range(int(w * 0.1), int(w * 0.9), 12):
            b, g, r = img_bgr[y, x]
            samples.append((r, g, b))
        avg_r = np.mean([s[0] for s in samples])
        avg_g = np.mean([s[1] for s in samples])
        avg_b = np.mean([s[2] for s in samples])
        # Dark or purple bottom nav
        if (avg_g < 90 and (avg_r > 65 or avg_b > 65)) or (avg_r < 50 and avg_g < 50 and avg_b < 50):
            bottom_boundary = y

    # 2. Divider line detection across [25%, 95%] width
    x_start = int(w * 0.25)
    x_end = int(w * 0.95)
    step_x = 4

    raw_candidates = []
    scan_start = int(h * 0.08)
    scan_end = bottom_boundary - 15

    for y in range(scan_start, scan_end):
        samples = gray[y, x_start:x_end:step_x]
        mean = np.mean(samples)
        std = np.std(samples)
        if std < 5.0 and 225 <= mean <= 252:
            above = gray[max(0, y - 2), x_start:x_end:step_x * 2]
            below = gray[min(h - 1, y + 2), x_start:x_end:step_x * 2]
            diff_above = np.mean(above) - mean
            diff_below = np.mean(below) - mean
            if diff_above >= 1.5 and diff_below >= 1.5:
                raw_candidates.append(y)

    # Cluster divider lines within 20px
    clustered = []
    for y in raw_candidates:
        if len(clustered) == 0 or y > clustered[-1] + 20:
            clustered.append(y)

    # Filter by minimum row distance (18% of width)
    min_row_dist = round(w * 0.18)
    filtered_dividers = []
    for y in clustered:
        if len(filtered_dividers) == 0 or y - filtered_dividers[-1] >= min_row_dist:
            filtered_dividers.append(y)

    # Add bottom boundary as final row end if sufficient height
    if len(filtered_dividers) > 0 and (bottom_boundary - filtered_dividers[-1]) >= round(w * 0.20):
        filtered_dividers.append(bottom_boundary)

    # 3. Form match rows and extract avatars + names
    matches = []
    avatar_size = round(w * 0.175)
    avatar_x = round(w * 0.05)
    min_row_h = round(w * 0.20)
    max_row_h = round(w * 0.40)

    for i in range(len(filtered_dividers) - 1):
        top = filtered_dividers[i]
        bot = filtered_dividers[i + 1]
        row_h = bot - top

        # Exclude partial or oversized rows
        if row_h < min_row_h or row_h > max_row_h:
            continue

        # Avatar presence check (discard text headers like "Your turn")
        avatar_y = top + round((row_h - avatar_size) / 2)
        if avatar_y + avatar_size > h:
            continue

        avatar_patch = gray[avatar_y:avatar_y + avatar_size, avatar_x:avatar_x + avatar_size]
        if np.std(avatar_patch) < 15:
            continue

        # Find match name from Apple Vision OCR observations
        match_name = f"Match {len(matches) + 1}"
        for obs in ocr_data.get("observations", []):
            by = obs["box"]["pixelY"]
            bx = obs["box"]["pixelX"]
            text = obs["text"].strip()
            # Bounding box must align with row
            if top <= by <= top + int(row_h * 0.6) and 0.20 * w <= bx <= 0.45 * w:
                clean = text.split("•")[0].strip()
                if not clean.startswith(("When", "reply", "Great", "I can", "someone", "ummm", "ahh", "who", "You")):
                    words = [w_str for w_str in clean.split() if w_str.isalpha()]
                    if words:
                        match_name = words[0]
                        break

        # Crop circular avatar with transparent alpha channel
        avatar_crop = img_bgr[avatar_y:avatar_y + avatar_size, avatar_x:avatar_x + avatar_size]
        mask = np.zeros((avatar_size, avatar_size), dtype=np.uint8)
        cv2.circle(mask, (avatar_size // 2, avatar_size // 2), avatar_size // 2, 255, -1)

        b, g, r = cv2.split(avatar_crop)
        bgra = cv2.merge([b, g, r, mask])

        # Encode to PNG base64
        _, png_bytes = cv2.imencode(".png", bgra)
        base64_str = base64.b64encode(png_bytes.tobytes()).decode("utf-8")
        avatar_data_url = f"data:image/png;base64,{base64_str}"

        # Compute perceptual hash
        ahash = compute_ahash(avatar_crop)

        matches.append({
            "name": match_name,
            "avatar": avatar_data_url,
            "avatarHash": ahash,
            "row": [top, bot],
            "rowHeight": row_h
        })

    return matches


class HingeTrackerHandler(SimpleHTTPRequestHandler):
    """Extends SimpleHTTPRequestHandler with API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            resp = {
                "status": "ok",
                "engine": "Native Apple Vision + OpenCV",
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        # Default static file handler
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/parse-screenshot":
            try:
                content_type = self.headers.get("Content-Type", "")
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                image_bytes_list = []

                if "multipart/form-data" in content_type:
                    # Parse multipart body
                    parser = email.parser.BytesFeedParser()
                    # Feed MIME headers + body
                    header_bytes = f"Content-Type: {content_type}\r\n\r\n".encode("utf-8")
                    parser.feed(header_bytes + body)
                    msg = parser.close()

                    for part in msg.walk():
                        if part.get_content_disposition() == "form-data":
                            filename = part.get_filename()
                            if filename or "image" in part.get_content_type():
                                payload = part.get_payload(decode=True)
                                if payload:
                                    image_bytes_list.append(payload)

                elif "application/json" in content_type:
                    payload = json.loads(body.decode("utf-8"))
                    if "image" in payload:
                        raw_b64 = payload["image"].split(",")[-1]
                        image_bytes_list.append(base64.b64decode(raw_b64))
                    elif "images" in payload:
                        for img_item in payload["images"]:
                            raw_b64 = img_item.split(",")[-1]
                            image_bytes_list.append(base64.b64decode(raw_b64))
                else:
                    # Raw image binary
                    image_bytes_list.append(body)

                if not image_bytes_list:
                    self.send_error(400, "No image files received in request.")
                    return

                # Decode primary image
                nparr = np.frombuffer(image_bytes_list[0], np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is None:
                    self.send_error(400, "Failed to decode image data.")
                    return

                # Parse matches
                matches = parse_screenshot_image(img)

                resp = {
                    "success": True,
                    "count": len(matches),
                    "matches": matches,
                    "engine": "Native Apple Vision + OpenCV"
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                err_resp = {"success": False, "error": str(e)}
                self.wfile.write(json.dumps(err_resp).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        # Support CORS preflight
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run(port: int = 8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, HingeTrackerHandler)
    print(f"[SERVER] Hinge Tracker Server running at http://localhost:{port}/")
    print(f"[SERVER] Engine: Native Apple Vision + OpenCV (Swift & Python)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
