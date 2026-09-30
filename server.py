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
import shutil
import argparse
import time
import re
import email.parser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np
from stitch import stitch_chat_frames

# Directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VISION_BIN = os.path.join(BASE_DIR, "bin", "vision_ocr")
NGROK_BIN = os.path.join(BASE_DIR, "bin", "ngrok")
DEFAULT_DOMAIN = "subplot-sarcastic-yesterday.ngrok-free.dev"

TIMESTAMP_REGEX = re.compile(
    r"^(?:"
    r"(?:Today|Yesterday)(?:,?\s+(?:at\s+)?\d{1,2}\s*:\s*\d{2}(?:\s*[AaPp]\.?[Mm]\.?)?)?"
    r"|(?:(?:Mon|Tue|Tues|Wed|Thu|Thur|Thurs|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\.?,?\s+)?"
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?"
    r"(?:,?\s+(?:at\s+)?\d{1,2}\s*:\s*\d{2}(?:\s*[AaPp]\.?[Mm]\.?)?)?"
    r"|(?:Mon|Tue|Tues|Wed|Thu|Thur|Thurs|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\.?,?\s+(?:at\s+)?\d{1,2}\s*:\s*\d{2}(?:\s*[AaPp]\.?[Mm]\.?)?"
    r"|\d{1,2}\s*:\s*\d{2}\s*[AaPp]\.?[Mm]\.?"
    r")$",
    re.IGNORECASE
)


def is_timestamp_text(text: str) -> bool:
    """Return True if text matches standard Hinge app timestamp header formats."""
    return bool(TIMESTAMP_REGEX.match(text.strip()))


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
        # Broadened threshold to handle both uncompressed Retina PNGs (mean ~221) and JPEGs (mean ~247)
        if std < 6.0 and 190 <= mean <= 253:
            above = gray[max(0, y - 2), x_start:x_end:step_x * 2]
            below = gray[min(h - 1, y + 2), x_start:x_end:step_x * 2]
            diff_above = np.mean(above) - mean
            diff_below = np.mean(below) - mean
            if diff_above >= 1.5 and diff_below >= 1.5:
                raw_candidates.append(y)

    # Cluster divider lines within 25px
    clustered = []
    for y in raw_candidates:
        if len(clustered) == 0 or y > clustered[-1] + 25:
            clustered.append(y)

    # Preserve all clustered divider lines; section headers and invalid rows are discarded by row height & avatar presence
    filtered_dividers = list(clustered)

    # Add bottom boundary as final row end if sufficient height
    if len(filtered_dividers) > 0 and (bottom_boundary - filtered_dividers[-1]) >= round(w * 0.20):
        filtered_dividers.append(bottom_boundary)

    # 3. Form match rows (via dividers or Vision text anchors fallback)
    min_row_h = round(w * 0.20)
    max_row_h = round(w * 0.40)
    avatar_size = round(w * 0.175)
    avatar_x = round(w * 0.05)

    rows = []
    if len(filtered_dividers) >= 2:
        for i in range(len(filtered_dividers) - 1):
            rows.append((filtered_dividers[i], filtered_dividers[i + 1]))
    else:
        # Fallback for borderless Hinge feeds with whitespace-separated cards
        anchors = []
        for obs in ocr_data.get("observations", []):
            text = obs.get("text", "").strip()
            box = obs.get("box", {})
            py = box.get("pixelY", 0)
            px = box.get("pixelX", 0)
            if py < scan_start or py > bottom_boundary - 40:
                continue
            if 0.18 * w <= px <= 0.50 * w:
                if text.startswith(("Start the chat", "Start chat")):
                    anchors.append(py - int(w * 0.06))
                elif not text.startswith(("Your turn", "Matches", "Hidden", "4:", "5:", "•l")):
                    clean = text.split("•")[0].strip()
                    words = [w_str for w_str in clean.split() if w_str.isalpha()]
                    if words and len(words) == 1 and len(words[0]) >= 2:
                        anchors.append(py)

        anchors.sort()
        clustered_anchors = []
        for a in anchors:
            if not clustered_anchors or a - clustered_anchors[-1] > min_row_dist * 0.8:
                clustered_anchors.append(a)

        for a in clustered_anchors:
            top = max(0, a - int(w * 0.04))
            bot = min(h, top + round(w * 0.24))
            rows.append((top, bot))

    matches = []
    for top, bot in rows:
        row_h = bot - top

        # Exclude partial or oversized rows
        if row_h < min_row_h or row_h > max_row_h:
            continue

        # Avatar presence check (discard text headers like "Your turn")
        avatar_y = top + round((row_h - avatar_size) / 2)
        if avatar_y + avatar_size > h:
            continue

        avatar_patch = gray[avatar_y:avatar_y + avatar_size, avatar_x:avatar_x + avatar_size]
        if np.std(avatar_patch) < 14:
            continue

        # Find match name from Apple Vision OCR observations
        match_name = f"Match {len(matches) + 1}"
        row_observations = sorted(ocr_data.get("observations", []), key=lambda o: o["box"]["pixelY"])
        for obs in row_observations:
            by = obs["box"]["pixelY"]
            bx = obs["box"]["pixelX"]
            text = obs["text"].strip()
            # Bounding box must align with upper half of row
            if top <= by <= top + int(row_h * 0.52) and 0.18 * w <= bx <= 0.55 * w:
                clean = text.split("•")[0].strip()
                if clean.startswith("Start the chat with "):
                    match_name = clean.replace("Start the chat with ", "").strip()
                    break
                elif not clean.startswith(("When", "reply", "Great", "I can", "someone", "ummm", "ahh", "who", "You", "Start")):
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


def is_continuous_bubble(img: np.ndarray, b1: Dict[str, Any], b2: Dict[str, Any]) -> bool:
    """
    Check if two vertically adjacent text boxes are part of the same continuous message bubble
    by verifying that the vertical gap between them is filled with the bubble background color
    rather than white canvas.
    """
    y1 = b1["pixelY"] + b1["pixelHeight"]
    y2 = b2["pixelY"]
    if y2 <= y1:
        return True
    gap = y2 - y1
    if gap > 90:
        return False

    x1 = max(b1["pixelX"], b2["pixelX"])
    x2 = min(b1["pixelX"] + b1["pixelWidth"], b2["pixelX"] + b2["pixelWidth"])
    if x2 - x1 < 20:
        cx = (b1["pixelX"] + b1["pixelWidth"] // 2 + b2["pixelX"] + b2["pixelWidth"] // 2) // 2
        x1 = max(0, cx - 15)
        x2 = min(img.shape[1], cx + 15)
    else:
        x1 += 4
        x2 -= 4

    corridor = img[y1:y2, x1:x2]
    if corridor.size == 0:
        return False

    gray = cv2.cvtColor(corridor, cv2.COLOR_BGR2GRAY)
    white_rows = (np.mean(gray >= 248, axis=1) > 0.75) | (np.mean(gray, axis=1) >= 249.0)
    return not np.any(white_rows)


EMOJI_TEMPLATES = {
    "😄": {
        "file": os.path.join(BASE_DIR, "assets", "emojis", "smile.png"),
        "base_width": 591,
        "base_size": 28,
        "threshold": 0.82
    }
}


def detect_emojis(img: np.ndarray) -> List[Dict[str, Any]]:
    """
    Detect a targeted subset of emojis in a chat screenshot using multi-scale template matching,
    Non-Maximum Suppression (NMS), and bubble color context verification.
    """
    h, w = img.shape[:2]
    detected = []

    for emoji_char, cfg in EMOJI_TEMPLATES.items():
        template_path = cfg["file"]
        if not os.path.exists(template_path):
            continue

        template = cv2.imread(template_path)
        if template is None:
            continue

        base_w = cfg.get("base_width", 591)
        base_s = cfg.get("base_size", 28)
        threshold = cfg.get("threshold", 0.82)

        # Expected target size scaled by screenshot width
        target_size = max(16, int(round(base_s * (w / float(base_w)))))

        # Search across subtle scale variations (0.95, 1.0, 1.05)
        scales = [0.95, 1.0, 1.05]
        candidate_matches = []

        for sc in scales:
            sw = int(round(target_size * sc))
            sh = int(round(target_size * sc))
            if sw >= w or sh >= h or sw < 10 or sh < 10:
                continue

            scaled_tmpl = cv2.resize(template, (sw, sh), interpolation=cv2.INTER_AREA if sc < 1.0 else cv2.INTER_CUBIC)
            res = cv2.matchTemplate(img, scaled_tmpl, cv2.TM_CCOEFF_NORMED)
            y_indices, x_indices = np.where(res >= threshold)

            for my, mx in zip(y_indices, x_indices):
                score = float(res[my, mx])
                candidate_matches.append((mx, my, sw, sh, score))

        # Sort candidates by score descending
        candidate_matches.sort(key=lambda item: item[4], reverse=True)

        # Non-Maximum Suppression (NMS) within 15px radius
        nms_boxes = []
        for mx, my, sw, sh, score in candidate_matches:
            if any(abs(mx - bx) < 15 and abs(my - by) < 15 for bx, by, _, _, _ in nms_boxes):
                continue

            # Context verification: Emoji must be inside a message bubble (purple or grey background)
            sample_pts = [
                (max(0, my + sh // 2), max(0, mx - 5)),          # Left
                (max(0, my + sh // 2), min(w - 1, mx + sw + 5)),  # Right
                (max(0, my - 5), max(0, mx + sw // 2)),          # Top
                (min(h - 1, my + sh + 5), max(0, mx + sw // 2))  # Bottom
            ]

            valid_context = False
            for sy, sx in sample_pts:
                b, g, r = [int(c) for c in img[sy, sx]]
                # Sent purple: R > G + 7 and B > G + 7
                is_purple = (r > g + 7 and b > g + 7)
                # Received grey: R, G, B within 5 of each other and 215 < B < 252
                is_grey = (abs(b - g) <= 5 and abs(g - r) <= 5 and 215 < b < 252)
                if is_purple or is_grey:
                    valid_context = True
                    break

            if not valid_context:
                continue

            nms_boxes.append((mx, my, sw, sh, score))
            detected.append({
                "emoji": emoji_char,
                "x": int(mx),
                "y": int(my),
                "w": int(sw),
                "h": int(sh),
                "score": score
            })

    return detected


def detect_pill_overlay_geometry(card_crop: np.ndarray, obs_box: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Detect the background pill geometry within the cropped photo card.
    Uses contour segmentation on the distinct #f7ebe6 pill color, falling back
    to Vision OCR text bounding box with standard Hinge horizontal padding.
    Returns proportional width percentage (e.g. 76.6) and estimated pixel width.
    """
    if card_crop is None or card_crop.size == 0:
        return None
    ch, cw = card_crop.shape[:2]
    text_w = obs_box.get("pixelWidth", 0) if obs_box else 0

    # Baseline estimate with standard Hinge horizontal padding (~19px each side)
    est_w = text_w + 38 if text_w > 0 else int(cw * 0.75)

    # Try contour detection in the lower 45% of the photo card
    sub = card_crop[int(ch * 0.55):, :]

    # Beige mask: Hinge pill background is typically #f7ebe6 (approx BGR: 230, 235, 247)
    lower = np.array([210, 215, 225])
    upper = np.array([250, 255, 255])
    mask = cv2.inRange(sub, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_w = None
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > max(80, text_w * 0.85) and w < cw * 0.98 and h > 18 and h < ch * 0.40:
            best_w = w
            break

    # Add corner-coverage buffer (~36px) so overlay's border-radius curves past the underlying pill edges
    final_w = (best_w if best_w is not None else est_w) + 36
    width_pct = min(95.0, max(45.0, round((final_w / cw) * 100, 1)))

    return {
        "widthPct": width_pct,
        "estimatedPx": int(final_w)
    }


def parse_chat_images(images: List[np.ndarray], match_name: str = "") -> Dict[str, Any]:
    """
    Parse Hinge chat messages from one or more screenshots:
    1. If multiple images, stitch them into one continuous chat image using stitch_chat_frames.
    2. Runs native Apple Vision OCR.
    3. Segments sent (purple), received (grey), timestamps, and liked photo cards.
    4. Combines multiline bubbles and extracts photo card crops.
    """
    if not images:
        raise ValueError("No images provided for chat parsing.")

    if len(images) > 1:
        stitched = stitch_chat_frames(images)
    else:
        stitched = images[0]

    h, w = stitched.shape[:2]

    # Apply 1.5x bicubic super-sampling for higher OCR precision on punctuation (. vs ..) and tiny typography
    ocr_scale = 1.5 if w < 900 else 1.0
    if ocr_scale != 1.0:
        ocr_input = cv2.resize(stitched, (int(w * ocr_scale), int(h * ocr_scale)), interpolation=cv2.INTER_CUBIC)
    else:
        ocr_input = stitched

    # Save to temporary file for Vision CLI
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
        cv2.imwrite(tmp_path, ocr_input)

    try:
        ocr_data = run_vision_ocr(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    obs = ocr_data.get("observations", [])
    if ocr_scale != 1.0:
        for o in obs:
            b = o["box"]
            b["pixelX"] = int(round(b["pixelX"] / ocr_scale))
            b["pixelY"] = int(round(b["pixelY"] / ocr_scale))
            b["pixelWidth"] = int(round(b["pixelWidth"] / ocr_scale))
            b["pixelHeight"] = int(round(b["pixelHeight"] / ocr_scale))

    obs = sorted(obs, key=lambda l: l["box"]["pixelY"])

    # Detect header tabs ('Chat' / 'Profile') to establish the top header chrome cutoff
    header_cutoff = 0
    for o in obs:
        t = o["text"].strip().lower()
        ob_box = o["box"]
        if t in ("chat", "profile") and ob_box["pixelY"] < h * 0.35:
            header_cutoff = max(header_cutoff, ob_box["pixelY"] + ob_box["pixelHeight"] + 15)

    # Detect top photo card (e.g. liked photo card with or without comment)
    top_photo_card = None
    consumed_card_obs = None
    card_comment_text = ""

    search_y1 = max(header_cutoff + 5, 80)
    for o in obs:
        py = o["box"]["pixelY"]
        ph = o["box"]["pixelHeight"]
        t = o["text"].strip()
        if py < h * 0.35 and (is_timestamp_text(t) or any(day in t for day in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Today", "Yesterday"))):
            search_y1 = max(search_y1, py + ph + 5)
            break

    search_y2 = min(h, int(search_y1 + 800))
    if search_y2 > search_y1 + 150:
        sub = stitched[search_y1:search_y2, :]
        gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
        mask = (gray < 248).astype(np.uint8)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
        best_card = None
        max_area = 0
        for i in range(1, num_labels):
            x, y, cw, ch, area = stats[i]
            if cw > w * 0.45 and ch > 180 and area > 30000 and (x + cw > w * 0.65):
                # Guard: exclude solid color text bubbles (real photos have low top color frequency & high variance)
                if cw > 50 and ch > 50:
                    patch = sub[y + 25:y + ch - 25, x + 25:x + cw - 25]
                    if patch.size > 0:
                        gray_patch = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
                        _, counts = np.unique(gray_patch, return_counts=True)
                        top_freq = np.max(counts) / counts.sum()
                        if top_freq > 0.25:
                            continue  # Solid bubble background, not a photograph
                if area > max_area:
                    max_area = area
                    best_card = {
                        "x1": int(x),
                        "y1": int(search_y1 + y),
                        "x2": int(x + cw),
                        "y2": int(search_y1 + y + ch),
                        "w": int(cw),
                        "h": int(ch)
                    }
        if best_card:
            left_margin = best_card["x1"]
            right_margin = w - best_card["x2"]
            is_centered_card = abs(left_margin - right_margin) < (w * 0.04)
            card_direction = "received" if is_centered_card else "sent"

            card_found = False
            for o in obs:
                b = o["box"]
                cx = b["pixelX"] + b["pixelWidth"] / 2
                cy = b["pixelY"] + b["pixelHeight"] / 2
                if best_card["x1"] <= cx <= best_card["x2"] and (best_card["y1"] + best_card["h"] * 0.55) <= cy <= (best_card["y2"] + 25):
                    t = o["text"].strip()
                    lower_t = t.lower()
                    if "liked your" in lower_t:
                        card_direction = "received"
                        card_comment_text = "Liked your photo"
                        card_found = True
                    elif "you liked" in lower_t:
                        card_direction = "sent"
                        card_comment_text = f"You liked {match_name}'s photo." if match_name else "You liked their photo."
                        card_found = True
                    elif "liked" in lower_t and "photo" in lower_t:
                        if is_centered_card or (b["pixelX"] < w * 0.35):
                            card_direction = "received"
                            card_comment_text = "Liked your photo"
                        else:
                            card_direction = "sent"
                            card_comment_text = f"You liked {match_name}'s photo." if match_name else "You liked their photo."
                        card_found = True
                    else:
                        card_comment_text = t
                        if b["pixelX"] < w * 0.35:
                            card_direction = "received"
                        elif b["pixelX"] > w * 0.45:
                            card_direction = "sent"
                        card_found = True
                    consumed_card_obs = o
                    break

            if not card_found and not is_centered_card:
                best_card = None

            if best_card:
                if not card_comment_text:
                    if card_direction == "received":
                        card_comment_text = "Liked your photo"
                    else:
                        card_comment_text = f"You liked {match_name}'s photo." if match_name else "You liked their photo."
                top_photo_card = best_card

    classified = []

    for o in obs:
        if consumed_card_obs is not None and o is consumed_card_obs:
            continue

        b = o["box"]
        px, py, pw, ph = b["pixelX"], b["pixelY"], b["pixelWidth"], b["pixelHeight"]
        text = o["text"].strip()
        if not text:
            continue

        # Smart contraction & punctuation restoration
        import re
        text = re.sub(r"\b([Ii])d\b(?=\s+(?:pickup|like|love|rather|prefer|think|say|tell|be|have|go|see|do|never|always|get|choose|pick|feel|know|mean|bet|hope|wonder))", r"\1'd", text)
        text = re.sub(r"\b([Ii])m\b", r"\1'm", text)
        text = re.sub(r"\b(dont)\b", "don't", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(cant)\b", "can't", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(wont)\b", "won't", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(didnt)\b", "didn't", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(couldnt)\b", "couldn't", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(wouldnt)\b", "wouldn't", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(shouldnt)\b", "shouldn't", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(thats)\b", "that's", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(whats)\b", "what's", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(youre)\b", "you're", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(theyre)\b", "they're", text, flags=re.IGNORECASE)

        lower = text.lower()
        import re

        # Filter out anything physically located within the top header chrome zone
        if header_cutoff > 0 and py < header_cutoff:
            continue

        # Header keywords, navigation icons, and tabs (filtered regardless of position in top 35% or stitched seams)
        if lower in ("chat", "profile", "signals", "signal", "<", "‹", ">", "›", "...", "•••"):
            continue
        if re.search(r"^(signals?|chat|profile|<|‹|>|›|\.{3}|•••)$", lower):
            continue
        if py < 300 and ("signals" in lower or (match_name and match_name.lower() in lower)):
            continue

        # Status bar carrier / battery / network artifacts
        if lower in ("5g", "lte", "4g", "wifi", "sos", "cancel", "done") or re.match(r"^\d{1,3}%$", lower):
            continue
        # Status bar standalone clock
        if py < 100 and re.match(r"^\d{1,2}:\d{2}$", lower):
            continue

        # Filter out bottom input placeholders or priority banners
        if "send a message" in lower or "type a message" in lower or "type advice" in lower:
            continue
        if "priority like" in lower or "helped you stand out" in lower:
            continue
        # Sliced boundary text artifacts at the very bottom canvas edge
        if py > h - 30:
            continue
        # Truncated or mangled bottom input bar / keyboard artifacts near bottom edge
        if py > h - 80 and not (re.search(r"\w{4,}", text) and (px > w * 0.3)):
            if lower in ("cancel", "send") or not re.search(r"[a-z0-9]", lower):
                continue

        sample_y = min(h - 1, max(0, py + ph // 2))
        color_l = stitched[sample_y, max(0, px - 8)].tolist()
        color_r = stitched[sample_y, min(w - 1, px + pw + 8)].tolist()

        # BGR checks:
        # Lavender / Purple sent bubble: R > G + 7 and B > G + 7 (covers deep magenta #701A51 and light lilac #D7C4DA)
        is_purple = ((color_l[2] > color_l[1] + 7 and color_l[0] > color_l[1] + 7) or
                     (color_r[2] > color_r[1] + 7 and color_r[0] > color_r[1] + 7))

        # Grey received bubble: R, G, B within 5 of each other and 215 < B < 252
        is_grey = ((abs(color_l[0] - color_l[1]) <= 5 and abs(color_l[1] - color_l[2]) <= 5 and 215 < color_l[0] < 252) or
                   (abs(color_r[0] - color_r[1]) <= 5 and abs(color_r[1] - color_r[2]) <= 5 and 215 < color_r[0] < 252))

        # Right-anchored sent bubble check: text box terminates near right margin (px + pw > w * 0.82)
        is_right_anchored = (px + pw > w * 0.82) and not is_grey

        # Strict noise rejection:
        if len(text) < 2:
            continue
        if len(text) < 3 and not (text.isalnum() and (is_purple or is_grey or is_right_anchored)):
            continue

        if is_timestamp_text(text) and not is_purple and not is_right_anchored:
            msg_type = "timestamp"
        elif re.search(r"^Start the chat with\b", text, re.IGNORECASE) or lower == "start the chat":
            msg_type = "system_prompt"
        elif "liked" in lower and "photo" in lower:
            msg_type = "liked_photo_pill"
        elif text in ("Sent", "Delivered", "Read"):
            msg_type = "status"
        elif is_purple or is_right_anchored:
            msg_type = "sent"
        elif is_grey:
            msg_type = "received"
        else:
            msg_type = "sent" if (px + pw > w * 0.7) else "received"

        classified.append({
            "type": msg_type,
            "text": text,
            "box": b
        })

    # Insert top photo card if detected
    if top_photo_card:
        crop_y1 = max(0, top_photo_card["y1"])
        crop_y2 = min(h, top_photo_card["y2"])
        crop_x1 = max(0, top_photo_card["x1"])
        crop_x2 = min(w, top_photo_card["x2"])
        crop = stitched[crop_y1:crop_y2, crop_x1:crop_x2]
        photo_url = ""
        if crop.size > 0:
            _, buf = cv2.imencode(".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
            photo_url = "data:image/jpeg;base64," + base64.b64encode(buf).decode("ascii")

        pill_overlay = detect_pill_overlay_geometry(
            crop,
            consumed_card_obs["box"] if consumed_card_obs else None
        )
        photo_item = {
            "type": "liked_photo",
            "text": card_comment_text,
            "sender": card_direction,
            "image": photo_url,
            "box": {
                "pixelX": top_photo_card["x1"],
                "pixelY": top_photo_card["y1"],
                "pixelWidth": top_photo_card["w"],
                "pixelHeight": top_photo_card["h"]
            }
        }
        if pill_overlay:
            photo_item["pillOverlay"] = pill_overlay

        classified.append(photo_item)
        classified.sort(key=lambda item: item["box"]["pixelY"])

    # Detect and merge emojis into text lines
    emojis = detect_emojis(stitched)
    for em in emojis:
        ex, ey, ew, eh, echar = em["x"], em["y"], em["w"], em["h"], em["emoji"]

        # Look for a classified text line sharing the vertical corridor
        matched_item = None
        for item in classified:
            if item["type"] not in ("sent", "received"):
                continue
            ibox = item["box"]
            iy, ih = ibox["pixelY"], ibox["pixelHeight"]
            if abs((ey + eh / 2) - (iy + ih / 2)) < max(eh, ih) * 0.75:
                matched_item = item
                break

        if matched_item:
            ibox = matched_item["box"]
            ix, iw = ibox["pixelX"], ibox["pixelWidth"]
            # Leading emoji (to the left of text)
            if ex + ew <= ix + 25:
                matched_item["text"] = f"{echar} {matched_item['text']}"
                ibox["pixelWidth"] += (ix - ex)
                ibox["pixelX"] = ex
                ibox["pixelHeight"] = max(ibox["pixelHeight"], eh)
                ibox["pixelY"] = min(ibox["pixelY"], ey)
            # Trailing emoji (to the right of text)
            elif ex >= ix + iw - 25:
                matched_item["text"] = f"{matched_item['text']} {echar}"
                ibox["pixelWidth"] = (ex + ew) - ix
                ibox["pixelHeight"] = max(ibox["pixelHeight"], eh)
                ibox["pixelY"] = min(ibox["pixelY"], ey)
        else:
            # Standalone emoji line inside a bubble
            sample_y = min(h - 1, max(0, ey + eh // 2))
            sample_x = max(0, ex - 6)
            b, g, r = [int(c) for c in stitched[sample_y, sample_x]]
            is_p = (r > g + 7 and b > g + 7)
            msg_type = "sent" if is_p else "received"
            classified.append({
                "type": msg_type,
                "text": echar,
                "box": {
                    "pixelX": ex,
                    "pixelY": ey,
                    "pixelWidth": ew,
                    "pixelHeight": eh
                }
            })
            classified.sort(key=lambda item: item["box"]["pixelY"])

    # Group adjacent bubbles
    grouped = []
    for item in classified:
        if item["type"] == "status":
            if grouped and grouped[-1]["type"] == "sent":
                grouped[-1]["status"] = item["text"]
            continue

        if item["type"] == "system_prompt":
            grouped.append(item.copy())
            continue

        if item["type"] == "liked_photo":
            grouped.append(item.copy())
            continue

        if item["type"] == "liked_photo_pill":
            # Extract photo card above pill
            pill_y = item["box"]["pixelY"]
            search_top = max(0, pill_y - 480)
            region = stitched[search_top:pill_y, :]
            gray_reg = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            non_white = np.where(gray_reg < 250)
            photo_url = ""
            if len(non_white[0]) > 0:
                card_y1 = search_top + int(non_white[0].min())
                card_y2 = search_top + int(non_white[0].max())
                card_x1 = int(non_white[1].min())
                card_x2 = int(non_white[1].max())
                crop = stitched[card_y1:card_y2, card_x1:card_x2]
                if crop.size > 0:
                    _, buf = cv2.imencode(".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
                    photo_url = "data:image/jpeg;base64," + base64.b64encode(buf).decode("ascii")

            pill_text = item["text"]
            pill_overlay = detect_pill_overlay_geometry(crop, item.get("box")) if crop.size > 0 else None
            pill_item = {
                "type": "liked_photo",
                "text": "Liked your photo" if is_recv_pill else pill_text,
                "sender": "received" if is_recv_pill else "sent",
                "image": photo_url,
                "box": item["box"]
            }
            if pill_overlay:
                pill_item["pillOverlay"] = pill_overlay
            grouped.append(pill_item)
            continue

        if grouped and grouped[-1]["type"] == item["type"] and item["type"] in ("sent", "received"):
            prev_last_box = grouped[-1].get("last_box", grouped[-1]["box"])
            curr_box = item["box"]
            gap = curr_box["pixelY"] - (prev_last_box["pixelY"] + prev_last_box["pixelHeight"])
            if gap < 25:
                grouped[-1]["text"] += " " + item["text"]
                grouped[-1]["box"]["pixelHeight"] = (curr_box["pixelY"] + curr_box["pixelHeight"]) - grouped[-1]["box"]["pixelY"]
                grouped[-1]["last_box"] = curr_box.copy()
                continue
            elif 25 <= gap <= 90 and is_continuous_bubble(stitched, prev_last_box, curr_box):
                grouped[-1]["text"] += "\n\n" + item["text"]
                grouped[-1]["box"]["pixelHeight"] = (curr_box["pixelY"] + curr_box["pixelHeight"]) - grouped[-1]["box"]["pixelY"]
                grouped[-1]["last_box"] = curr_box.copy()
                continue

        new_item = item.copy()
        new_item["last_box"] = item["box"].copy()
        grouped.append(new_item)

    # Format clean messages
    clean_messages = []
    last_type = None
    for idx, g in enumerate(grouped):
        m = {
            "id": f"msg_{idx+1}",
            "type": g["type"],
            "text": g.get("text", "")
        }
        if g["type"] == "liked_photo":
            m["image"] = g.get("image", "")
            m["sender"] = g.get("sender", "sent")
            if "pillOverlay" in g:
                m["pillOverlay"] = g["pillOverlay"]
        elif g["type"] == "sent" and "status" in g:
            m["status"] = g["status"]
        elif g["type"] == "received":
            m["showAvatar"] = (last_type != "received")

        last_type = g["type"]
        clean_messages.append(m)

    # Generate stitched thumbnail
    preview_scale = min(1.0, 390.0 / w)
    preview_w = int(w * preview_scale)
    preview_h = int(h * preview_scale)
    preview_img = cv2.resize(stitched, (preview_w, preview_h), interpolation=cv2.INTER_AREA)
    _, pbuf = cv2.imencode(".jpg", preview_img, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
    preview_b64 = "data:image/jpeg;base64," + base64.b64encode(pbuf).decode("ascii")

    return {
        "success": True,
        "count": len(clean_messages),
        "stitchedPreview": preview_b64,
        "messages": clean_messages,
        "engine": "Native Apple Vision + OpenCV + Stitch"
    }


class HingeTrackerHandler(SimpleHTTPRequestHandler):
    """Extends SimpleHTTPRequestHandler with API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, ngrok-skip-browser-warning")
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
        if self.path in ("/api/parse-screenshot", "/api/parse-chat"):
            try:
                content_type = self.headers.get("Content-Type", "")
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                image_bytes_list = []
                match_name = ""

                if "multipart/form-data" in content_type:
                    # Parse multipart body
                    parser = email.parser.BytesFeedParser()
                    # Feed MIME headers + body
                    header_bytes = f"Content-Type: {content_type}\r\n\r\n".encode("utf-8")
                    parser.feed(header_bytes + body)
                    msg = parser.close()

                    for part in msg.walk():
                        if part.get_content_disposition() == "form-data":
                            param_name = part.get_param("name", header="content-disposition")
                            if param_name == "matchName":
                                match_name = part.get_payload(decode=True).decode("utf-8").strip()
                            filename = part.get_filename()
                            if filename or "image" in part.get_content_type():
                                payload = part.get_payload(decode=True)
                                if payload:
                                    image_bytes_list.append(payload)

                elif "application/json" in content_type:
                    payload = json.loads(body.decode("utf-8"))
                    match_name = payload.get("matchName", "")
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

                if self.path == "/api/parse-screenshot":
                    # Decode primary image for match list parsing
                    nparr = np.frombuffer(image_bytes_list[0], np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if img is None:
                        self.send_error(400, "Failed to decode image data.")
                        return

                    matches = parse_screenshot_image(img)
                    resp = {
                        "success": True,
                        "count": len(matches),
                        "matches": matches,
                        "engine": "Native Apple Vision + OpenCV"
                    }
                else:
                    # /api/parse-chat
                    images = []
                    for b in image_bytes_list:
                        nparr = np.frombuffer(b, np.uint8)
                        decoded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if decoded is not None:
                            images.append(decoded)

                    if not images:
                        self.send_error(400, "Failed to decode any images.")
                        return

                    resp = parse_chat_images(images, match_name)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, ngrok-skip-browser-warning")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, ngrok-skip-browser-warning")
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
        self.send_header("Access-Control-Allow-Headers", "Content-Type, ngrok-skip-browser-warning")
        self.end_headers()


def run(port: int = 8080, enable_tunnel: bool = False, domain: str = DEFAULT_DOMAIN):
    server_address = ("", port)
    httpd = HTTPServer(server_address, HingeTrackerHandler)

    ngrok_proc = None
    if enable_tunnel:
        ngrok_bin = NGROK_BIN if os.path.isfile(NGROK_BIN) else shutil.which("ngrok")
        if not ngrok_bin:
            print("[ERROR] ngrok binary not found in bin/ngrok or system PATH.")
            print("Please ensure bin/ngrok exists or run without --tunnel.")
            sys.exit(1)

        print(f"[TUNNEL] Launching ngrok tunnel for port {port} on https://{domain}...")
        try:
            ngrok_proc = subprocess.Popen(
                [ngrok_bin, "http", str(port), f"--domain={domain}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            time.sleep(1.5)
            if ngrok_proc.poll() is not None:
                _, err_out = ngrok_proc.communicate()
                print(f"[ERROR] ngrok failed to start:\n{err_out.decode('utf-8', errors='ignore')}")
                sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to spawn ngrok: {e}")
            sys.exit(1)

    print("\n" + "=" * 66)
    print("🚀 Hinge Tracker Server Active!")
    print(f" • Local URL:   http://localhost:{port}/")
    if enable_tunnel:
        print(f" • Tunnel URL:  https://{domain}/")
        print(f" • API Health:  https://{domain}/api/health")
        print(" • Mobile:      Ready for screenshot imports from GitHub Pages!")
    print(" • Engine:      Native Apple Vision + OpenCV")
    print("=" * 66 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        httpd.server_close()
        if ngrok_proc and ngrok_proc.poll() is None:
            print("[TUNNEL] Terminating ngrok tunnel...")
            ngrok_proc.terminate()
            ngrok_proc.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hinge Tracker Server with Native Apple Vision & Tunnel")
    parser.add_argument("port", nargs="?", type=int, default=8080, help="Local port (default: 8080)")
    parser.add_argument("-t", "--tunnel", action="store_true", help="Launch ngrok HTTPS tunnel alongside server")
    parser.add_argument("-d", "--domain", type=str, default=DEFAULT_DOMAIN, help=f"Static ngrok domain (default: {DEFAULT_DOMAIN})")

    args = parser.parse_args()
    run(port=args.port, enable_tunnel=args.tunnel, domain=args.domain)
