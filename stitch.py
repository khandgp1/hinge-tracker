#!/usr/bin/env python3
"""
Scrolling Screenshot Stitcher
-----------------------------
Stitches multiple overlapping web or mobile app screenshots into a single,
continuous, high-resolution image using 1D Normalized Cross-Correlation (NCC)
and linear alpha seam blending.
"""

import os
import sys
import argparse
from typing import List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(
        description="Stitch multiple overlapping scrolling screenshots into one continuous image."
    )
    parser.add_argument(
        "-i", "--input", nargs="+",
        help="Input image files or directory containing screenshot sequence."
    )
    parser.add_argument(
        "-o", "--output", default="stitched.png",
        help="Output image path (default: stitched.png)."
    )
    parser.add_argument(
        "--crop-top", type=int, default=None,
        help="Manual pixel height to crop from the top of each frame."
    )
    parser.add_argument(
        "--crop-bottom", type=int, default=None,
        help="Manual pixel height to crop from the bottom of each frame."
    )
    parser.add_argument(
        "--no-auto-crop", action="store_true",
        help="Disable automatic static header/footer region detection."
    )
    parser.add_argument(
        "--keep-header-footer", action="store_true", default=None,
        help="Legacy flag: Re-attach both top header and bottom footer around stitched body."
    )
    parser.add_argument(
        "--keep-header", action="store_true", default=False,
        help="Re-attach top status bar header from 1st frame (default: False)."
    )
    parser.add_argument(
        "--no-header", action="store_false", dest="keep_header",
        help="Do not re-attach top status bar header (default behavior)."
    )
    parser.add_argument(
        "--keep-footer", action="store_true", default=True,
        help="Re-attach bottom footer from last frame (default: True)."
    )
    parser.add_argument(
        "--no-footer", action="store_false", dest="keep_footer",
        help="Do not re-attach bottom footer."
    )
    parser.add_argument(
        "--blend-height", type=int, default=30,
        help="Height of the alpha cross-fade seam blending zone in pixels (default: 30)."
    )
    args = parser.parse_args()
    if args.keep_header_footer is not None:
        args.keep_header = args.keep_header_footer
        args.keep_footer = args.keep_header_footer
    return args


def load_and_sort_images(inputs: Optional[List[str]]) -> List[np.ndarray]:
    """Load image paths from directory or explicit file list, sorted naturally."""
    image_paths = []
    if not inputs:
        print("Error: No input images or directory provided.", file=sys.stderr)
        sys.exit(1)

    for item in inputs:
        if os.path.isdir(item):
            valid_exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
            files = [
                os.path.join(item, f) for f in os.listdir(item)
                if f.lower().endswith(valid_exts)
            ]
            files.sort()
            image_paths.extend(files)
        elif os.path.isfile(item):
            image_paths.append(item)
        else:
            print(f"Warning: Path '{item}' not found.", file=sys.stderr)

    if len(image_paths) < 2:
        print("Error: Need at least 2 screenshots to perform stitching.", file=sys.stderr)
        sys.exit(1)

    images = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            print(f"Error: Could not read image '{path}'", file=sys.stderr)
            sys.exit(1)
        images.append(img)

    print(f"Loaded {len(images)} images for stitching.")
    return images


def detect_static_margins(
    img1: np.ndarray, img2: np.ndarray, max_header_pct: float = 0.35, max_footer_pct: float = 0.35
) -> Tuple[int, int]:
    """
    Detect static top header rows and bottom footer rows that remain identical across frames.
    Returns (top_crop_pixels, bottom_crop_pixels).
    """
    h, w = img1.shape[:2]
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) if len(img1.shape) == 3 else img1
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) if len(img2.shape) == 3 else img2

    diff = np.abs(gray1.astype(np.int16) - gray2.astype(np.int16))
    row_diffs = np.mean(diff, axis=1)

    # Check top header (from row 0 down)
    max_top_search = int(h * max_header_pct)
    top_crop = 0
    for y in range(max_top_search):
        if row_diffs[y] < 3.0:  # virtually unchanged pixel row
            top_crop = y + 1
        else:
            break

    # Check bottom footer (from row h-1 up)
    max_bottom_search = int(h * max_footer_pct)
    bottom_crop = 0
    for y in range(h - 1, h - 1 - max_bottom_search, -1):
        if row_diffs[y] < 3.0:
            bottom_crop += 1
        else:
            break

    return top_crop, bottom_crop


def find_vertical_displacement(
    img_upper: np.ndarray,
    img_lower: np.ndarray,
    min_overlap_px: int = 15
) -> Tuple[int, float]:
    """
    Compute vertical displacement Δy (in pixels) of img_lower relative to img_upper
    by searching for the 1D vertical shift that minimizes Mean Absolute Difference (MAD).
    """
    h_up, w_up = img_upper.shape[:2]
    h_low, w_low = img_lower.shape[:2]

    if w_up != w_low:
        scale = w_up / float(w_low)
        img_lower = cv2.resize(img_lower, (w_up, int(h_low * scale)))
        h_low = img_lower.shape[0]

    gray_upper = cv2.cvtColor(img_upper, cv2.COLOR_BGR2GRAY) if len(img_upper.shape) == 3 else img_upper
    gray_lower = cv2.cvtColor(img_lower, cv2.COLOR_BGR2GRAY) if len(img_lower.shape) == 3 else img_lower

    best_dy = 0
    best_diff = float('inf')

    # Search all vertical scroll shifts dy from 5px up to h_up - min_overlap_px
    max_search_dy = h_up - min_overlap_px
    for dy in range(5, max_search_dy):
        overlap_h = min(h_up - dy, h_low)
        if overlap_h < min_overlap_px:
            continue
        overlap_upper = gray_upper[dy:dy + overlap_h, :]
        overlap_lower = gray_lower[0:overlap_h, :]
        if overlap_upper.shape[0] == 0 or overlap_lower.shape[0] == 0:
            continue
        diff = np.mean(np.abs(overlap_upper.astype(np.float32) - overlap_lower.astype(np.float32)))
        if diff < best_diff:
            best_diff = diff
            best_dy = dy

    confidence = max(0.0, 1.0 - (best_diff / 50.0))
    return best_dy, float(confidence)


def blend_overlap_region(
    img1: np.ndarray, img2: np.ndarray, blend_h: int
) -> np.ndarray:
    """Apply linear alpha gradient cross-fade blending across a horizontal overlap strip."""
    h, w, c = img1.shape
    if blend_h <= 0 or blend_h > h:
        return img2

    result = img1.copy()
    alpha = np.linspace(1.0, 0.0, blend_h)[:, np.newaxis, np.newaxis]

    overlap1 = img1[-blend_h:].astype(np.float32)
    overlap2 = img2[:blend_h].astype(np.float32)

    blended = (overlap1 * alpha + overlap2 * (1.0 - alpha)).astype(np.uint8)
    result[-blend_h:] = blended
    return result


def stitch_sequence(
    images: List[np.ndarray],
    crop_top: Optional[int] = None,
    crop_bottom: Optional[int] = None,
    auto_crop: bool = True,
    keep_header: bool = False,
    keep_footer: bool = True,
    blend_height: int = 30
) -> np.ndarray:
    """Stitch a sequence of images into one continuous stitched image."""
    n = len(images)
    header_strip = None
    footer_strip = None

    # Detect or apply static cropping
    if not auto_crop:
        top_crops = [crop_top or 0] * n
        bottom_crops = [crop_bottom or 0] * n
    else:
        detected_tops = []
        detected_bottoms = []
        for i in range(n - 1):
            t_crop, b_crop = detect_static_margins(images[i], images[i + 1])
            detected_tops.append(t_crop)
            detected_bottoms.append(b_crop)

        # Normalize static margins across all frames using the median of positive detections
        # to reject transient noise (e.g. clock change in status bar or solid white content padding)
        pos_tops = [t for t in detected_tops if t > 0]
        pos_bottoms = [b for b in detected_bottoms if b > 0]
        seq_top = int(np.median(pos_tops)) if pos_tops else 0
        seq_bottom = int(np.median(pos_bottoms)) if pos_bottoms else 0

        # When a static header is auto-detected, trim 3 extra boundary pixels to cleanly
        # remove navigation divider lines, active tab underlines, and anti-aliasing edges
        if crop_top is None and seq_top > 0:
            seq_top += 3

        final_top = crop_top if crop_top is not None else seq_top
        final_bottom = crop_bottom if crop_bottom is not None else seq_bottom

        top_crops = [final_top] * n
        bottom_crops = [final_bottom] * n

    # Save header/footer if re-attaching
    if keep_header and top_crops[0] > 0:
        header_strip = images[0][:top_crops[0]].copy()
    if keep_footer and bottom_crops[-1] > 0:
        footer_strip = images[-1][-bottom_crops[-1]:].copy()

    # Crop body contents
    cropped_images = []
    for i in range(n):
        img = images[i]
        h = img.shape[0]
        t = top_crops[i]
        b = bottom_crops[i]
        body = img[t:h - b] if b > 0 else img[t:]
        cropped_images.append(body)

    # Ensure all cropped images match the width of cropped_images[0]
    w = cropped_images[0].shape[1]
    for i in range(n):
        if cropped_images[i].shape[1] != w:
            scale = w / float(cropped_images[i].shape[1])
            new_h = int(cropped_images[i].shape[0] * scale)
            cropped_images[i] = cv2.resize(cropped_images[i], (w, new_h))

    # Calculate displacements between adjacent cropped bodies
    displacements = []
    for i in range(n - 1):
        dy, score = find_vertical_displacement(cropped_images[i], cropped_images[i + 1])
        print(f"Frame {i} -> {i+1}: Vertical displacement Δy = {dy}px (confidence: {score:.3f})")
        displacements.append(dy)

    # Calculate absolute Y start positions for each frame
    y_positions = [0] * n
    for i in range(n - 1):
        y_positions[i + 1] = y_positions[i] + displacements[i]

    # Total body canvas height is the maximum bottom Y coordinate across all placed frames
    total_body_h = max(y_positions[i] + cropped_images[i].shape[0] for i in range(n))
    canvas = np.zeros((total_body_h, w, 3), dtype=np.uint8)

    # Place each cropped image onto canvas with alpha seam blending at frame tops
    for i in range(n):
        img_y = y_positions[i]
        img = cropped_images[i]
        img_h = img.shape[0]

        if i == 0:
            canvas[img_y:img_y + img_h, :] = img
        else:
            prev_y = y_positions[i - 1]
            prev_h = cropped_images[i - 1].shape[0]
            prev_bottom = prev_y + prev_h

            if img_y < prev_bottom:
                overlap_h = prev_bottom - img_y
                actual_blend = min(blend_height, overlap_h)

                # Cross-fade blend at the top of incoming image (from img_y to img_y + actual_blend)
                existing_strip = canvas[img_y : img_y + actual_blend, :]
                incoming_strip = img[0 : actual_blend, :]

                bh = min(existing_strip.shape[0], incoming_strip.shape[0])
                if bh > 0:
                    alpha = np.linspace(1.0, 0.0, bh)[:, np.newaxis, np.newaxis]
                    blended = (existing_strip[:bh].astype(np.float32) * alpha +
                               incoming_strip[:bh].astype(np.float32) * (1.0 - alpha)).astype(np.uint8)
                    canvas[img_y : img_y + bh, :] = blended

                # Place remaining body of incoming image directly onto canvas below the blend zone
                if bh < img_h:
                    canvas[img_y + bh : img_y + img_h, :] = img[bh:]
            else:
                canvas[img_y : img_y + img_h, :] = img

    # Prepend header / append footer if requested
    final_components = []
    if header_strip is not None:
        final_components.append(header_strip)
    final_components.append(canvas)
    if footer_strip is not None:
        final_components.append(footer_strip)

    if len(final_components) > 1:
        final_image = np.vstack(final_components)
    else:
        final_image = canvas

    return final_image


def main():
    args = parse_args()
    images = load_and_sort_images(args.input)

    stitched = stitch_sequence(
        images=images,
        crop_top=args.crop_top,
        crop_bottom=args.crop_bottom,
        auto_crop=not args.no_auto_crop,
        keep_header=args.keep_header,
        keep_footer=args.keep_footer,
        blend_height=args.blend_height
    )

    out_path = args.output
    cv2.imwrite(out_path, stitched)
    print(f"Successfully saved stitched image to: {out_path} (Dimensions: {stitched.shape[1]}x{stitched.shape[0]} px)")


if __name__ == "__main__":
    main()
