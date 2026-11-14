#!/usr/bin/env python3
"""Extract layered 2D skeletal parts from v1.1.0 mage_caster.png and boss_kardon.png.

Uses scipy distance_transform_edt + OpenCV TELEA so transparent white RGB halos never leak
into inpainted under-layers, erases all open-air weapon/hand gaps cleanly, and saves parts
plus inspection sheets.
"""
import json
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(REPO, "godot_project/assets/sprites")
PARTS_DIR = os.path.join(REPO, "godot_project/assets/parts")


def poly_mask(w: int, h: int, pts: list[tuple[int, int]], feather: float = 1.2) -> np.ndarray:
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    arr = np.array(mask, dtype=np.float32)
    if feather > 0.0:
        k = int(max(3, round(feather * 4) | 1))
        arr = cv2.GaussianBlur(arr, (k, k), feather)
    return arr / 255.0


def cut_part(src_rgba: np.ndarray, region_mask: np.ndarray) -> np.ndarray:
    out = src_rgba.copy()
    alpha = out[:, :, 3].astype(np.float32) * np.clip(region_mask, 0.0, 1.0)
    out[:, :, 3] = np.clip(np.round(alpha), 0, 255).astype(np.uint8)
    return out


def inpaint_underlayer(
    src_rgba: np.ndarray,
    erase_mask_u8: np.ndarray,
    radius: int = 7,
    alpha_thresh: int = 235,
) -> np.ndarray:
    """Inpaint opaque areas under an occluder strictly seeded from clean interior pixels."""
    out = src_rgba.copy()
    a = out[:, :, 3]
    work_mask = ((erase_mask_u8 > 127) & (a >= 120)).astype(np.uint8) * 255
    # Strictly seeded from deep interior pixels (eroded 2px from transparent borders so white edge AA never leaks)
    interior = cv2.erode((a >= alpha_thresh).astype(np.uint8), np.ones((5, 5), np.uint8), iterations=1) > 0
    lum = out[:, :, :3].mean(axis=2)
    seed_valid = interior & (work_mask == 0) & (lum < 210)
    if not np.any(seed_valid):
        seed_valid = (a >= alpha_thresh) & (work_mask == 0)
    if not np.any(seed_valid) or not np.any(work_mask > 0):
        return out

    # Replace ALL non-seed pixels (transparent white air & occluder spot) with nearest clean opaque RGB
    iy, ix = distance_transform_edt(~seed_valid, return_distances=False, return_indices=True)
    clean_rgb = out[iy, ix, :3]

    # Blend edge via OpenCV TELEA over the clean nearest-color prefill
    bgr = cv2.cvtColor(clean_rgb, cv2.COLOR_RGB2BGR)
    painted_bgr = cv2.inpaint(bgr, work_mask, radius, cv2.INPAINT_TELEA)
    painted_rgb = cv2.cvtColor(painted_bgr, cv2.COLOR_BGR2RGB)
    out[:, :, :3] = np.where(work_mask[:, :, None] > 0, painted_rgb, out[:, :, :3])
    return out


def save_part(arr: np.ndarray, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    Image.fromarray(arr, mode="RGBA").save(out_path)


def extract_mage() -> dict:
    src_path = os.path.join(SPRITES_DIR, "mage_caster.png")
    src = np.array(Image.open(src_path).convert("RGBA"))
    h, w = src.shape[:2]

    # 1. Head + subtle collar-tuck neck bottom
    head_poly = [
        (235, 55), (420, 55), (420, 178),
        (382, 180), (355, 206), (322, 198), (298, 168), (235, 152),
    ]
    head_arr = cut_part(src, poly_mask(w, h, head_poly, feather=1.2))

    # 2. Left arm + bell sleeve + fingers (trimmed above stray lower stole ribbon tip)
    left_arm_poly = [
        (0, 205), (242, 196), (266, 232), (288, 252), (255, 274),
        (232, 296), (262, 304), (270, 336), (242, 346), (210, 344),
        (182, 360), (145, 398), (92, 412), (0, 416),
    ]
    left_arm_arr = cut_part(src, poly_mask(w, h, left_arm_poly, feather=1.2))

    # 3. Right arm + wide sleeve + full ruby staff
    right_arm_upper = [
        (434, 196), (560, 172), (655, 0), (764, 0),
        (764, 385), (565, 385), (534, 302), (465, 286),
        (434, 276), (398, 260), (406, 224),
    ]
    staff_lower = [
        (405, 412), (532, 260), (546, 274), (416, 422),
    ]
    right_arm_mask = np.maximum(
        poly_mask(w, h, right_arm_upper, feather=1.2),
        poly_mask(w, h, staff_lower, feather=0.8),
    )
    right_arm_arr = cut_part(src, right_arm_mask)

    # 4. Main continuous Body (Collar/Torso + Lower Robes + Boots + Coat Tail)
    body_erase = np.zeros((h, w), dtype=np.float32)
    # Remove head above collar line so tilting head shows zero ghost duplicate
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (235, 50), (420, 50), (420, 172), (376, 174),
        (352, 188), (324, 184), (304, 160), (235, 148),
    ], feather=1.2))
    # Erase outer right arm/sleeve + upper staff in open air (keep red dangling stole at x=450..495, y>335!)
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (444, 195), (560, 170), (655, 0), (764, 0),
        (764, 355), (565, 355), (534, 302), (460, 288),
        (415, 262), (422, 220),
    ], feather=1.2))
    # Erase ONLY open-air staff gap LEFT & RIGHT of red dangling stole (preserving ribbon at (454..476, 338..366))
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (396, 408), (446, 356), (462, 372), (416, 428),
    ], feather=0.8))
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (472, 326), (550, 232), (580, 255), (484, 336),
    ], feather=0.8))
    # Erase left outer sleeve/hand away from torso AND air gap under wrist before waist
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (0, 200), (222, 196), (228, 246), (195, 290),
        (232, 304), (236, 338), (226, 355), (165, 366), (105, 405), (0, 412),
    ], feather=1.0))

    body_arr = cut_part(src, 1.0 - body_erase)

    # Inpaint inside opaque torso/stole behind overlapping hand fingers & staff crossing over red ribbon
    paint_mask = np.zeros((h, w), dtype=np.uint8)
    hand_on_stole = poly_mask(w, h, [
        (228, 298), (270, 298), (270, 346), (228, 346),
    ], feather=0.0)
    paint_mask |= (hand_on_stole > 0.5).astype(np.uint8) * 255
    staff_tip_cross = poly_mask(w, h, [
        (456, 340), (484, 332), (488, 372), (456, 376),
    ], feather=0.0)
    paint_mask |= (staff_tip_cross > 0.5).astype(np.uint8) * 255

    body_inpainted = inpaint_underlayer(body_arr, paint_mask, radius=6, alpha_thresh=230)

    out_dir = os.path.join(PARTS_DIR, "mage")
    save_part(head_arr, os.path.join(out_dir, "head.png"))
    save_part(left_arm_arr, os.path.join(out_dir, "left_arm.png"))
    save_part(right_arm_arr, os.path.join(out_dir, "right_arm_staff.png"))
    save_part(body_inpainted, os.path.join(out_dir, "body.png"))

    return {
        "size": [w, h],
        "parts": ["body.png", "head.png", "left_arm.png", "right_arm_staff.png"],
        "pivots": {
            "root_feet": [315, 795],
            "pelvis": [350, 410],
            "spine": [350, 320],
            "chest": [348, 240],
            "neck": [336, 184],
            "shoulder_l": [254, 232],
            "elbow_l": [155, 310],
            "hand_l": [228, 326],
            "shoulder_r": [416, 224],
            "elbow_r": [498, 212],
            "hand_r": [578, 198],
            "staff_tip": [686, 102],
            "knee_l": [172, 710],
            "foot_l": [150, 792],
            "knee_r": [455, 675],
            "foot_r": [458, 765],
            "tail_1": [220, 505],
            "tail_2": [105, 590],
            "tail_3": [32, 685],
        },
    }


def extract_boss() -> dict:
    src_path = os.path.join(SPRITES_DIR, "boss_kardon.png")
    src = np.array(Image.open(src_path).convert("RGBA"))
    h, w = src.shape[:2]

    # 1. Torn Cape behind right/rear shoulder (tucks 60px deep behind Body z=1 so fast upward whip never leaves a vertical gap)
    cape_poly = [
        (575, 200), (725, 190), (930, 260), (1024, 380),
        (1024, 595), (785, 585), (705, 480), (630, 380), (580, 290),
    ]
    cape_arr = cut_part(src, poly_mask(w, h, cape_poly, feather=1.5))

    # 2. Horned Head / Helm
    head_poly = [
        (312, 5), (518, 5), (508, 168), (464, 212),
        (392, 220), (344, 186), (312, 130),
    ]
    head_arr = cut_part(src, poly_mask(w, h, head_poly, feather=1.2))

    # 3. Left Pauldron + Left Arm
    left_arm_poly = [
        (508, 70), (668, 78), (748, 268), (702, 412),
        (610, 476), (528, 468), (528, 396), (584, 326),
        (566, 228), (502, 180),
    ]
    left_arm_arr = cut_part(src, poly_mask(w, h, left_arm_poly, feather=1.2))

    # 4. Right Pauldron + Right Arm
    right_arm_poly = [
        (268, 195), (382, 152), (438, 226), (436, 342),
        (518, 424), (484, 494), (350, 416), (264, 330),
    ]
    right_arm_arr = cut_part(src, poly_mask(w, h, right_arm_poly, feather=1.2))

    # 5. Abyss Greatsword
    sword_poly = [
        (0, 888), (0, 740), (260, 505), (425, 425),
        (555, 382), (618, 424), (585, 488), (470, 578),
        (265, 810), (140, 888),
    ]
    sword_arr = cut_part(src, poly_mask(w, h, sword_poly, feather=1.0))

    # 6. Main Body (Chest + Belt/Tassets + Legs + Boots)
    body_erase = np.zeros((h, w), dtype=np.float32)
    # Remove cape protruding on right
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (665, 195), (1024, 240), (1024, 595), (810, 580),
        (765, 495), (725, 405), (695, 290),
    ], feather=1.2))
    # Erase blade + magenta lightning left of Boss's true right leg silhouette!
    # True leg contour: (355, 485) -> (345, 560) -> (336, 635) -> (325, 700) -> (302, 760) -> (218, 812) -> (195, 860)
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (0, 891), (0, 460), (358, 460), (356, 515),
        (344, 565), (336, 635), (326, 700), (304, 758),
        (218, 812), (205, 856), (135, 891),
    ], feather=1.0))
    # Remove outer right pauldron + upper/lower right arm protruding left of chest plate
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (260, 165), (378, 165), (382, 235), (380, 355),
        (420, 415), (375, 455), (260, 415),
    ], feather=1.2))
    # Remove giant left spiked pauldron & outer left arm overhanging chest/hip
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (518, 70), (675, 70), (755, 250), (725, 425),
        (588, 460), (548, 410), (585, 315), (568, 215), (512, 168),
    ], feather=1.2))
    # Remove helm top/horns cleanly including right horn tip
    body_erase = np.maximum(body_erase, poly_mask(w, h, [
        (308, 0), (540, 0), (526, 178), (420, 185), (320, 165),
    ], feather=1.2))

    body_arr = cut_part(src, 1.0 - body_erase)

    # Strictly inside the opaque armor torso/tasset zone behind hilt & right shin crease:
    paint_mask = np.zeros((h, w), dtype=np.uint8)
    hilt_cut = poly_mask(w, h, [
        (366, 418), (576, 392), (582, 468), (478, 558), (358, 520),
    ], feather=0.0)
    paint_mask |= (hilt_cut > 0.5).astype(np.uint8) * 255
    shin_overlap = poly_mask(w, h, [
        (328, 515), (376, 515), (356, 645), (325, 700),
    ], feather=0.0)
    paint_mask |= (shin_overlap > 0.5).astype(np.uint8) * 255

    body_inpainted = inpaint_underlayer(body_arr, paint_mask, radius=8, alpha_thresh=235)

    out_dir = os.path.join(PARTS_DIR, "boss")
    save_part(cape_arr, os.path.join(out_dir, "cape.png"))
    save_part(body_inpainted, os.path.join(out_dir, "body.png"))
    save_part(head_arr, os.path.join(out_dir, "head.png"))
    save_part(right_arm_arr, os.path.join(out_dir, "right_arm.png"))
    save_part(left_arm_arr, os.path.join(out_dir, "left_arm.png"))
    save_part(sword_arr, os.path.join(out_dir, "greatsword.png"))

    return {
        "size": [w, h],
        "parts": ["cape.png", "body.png", "right_arm.png", "left_arm.png", "greatsword.png", "head.png"],
        "pivots": {
            "root_feet": [540, 845],
            "pelvis": [505, 445],
            "spine": [482, 340],
            "chest": [468, 250],
            "neck": [416, 185],
            "shoulder_r": [368, 226],
            "elbow_r": [388, 336],
            "hand_r": [480, 448],
            "shoulder_l": [578, 190],
            "elbow_l": [650, 315],
            "hand_l": [568, 412],
            "sword_tip": [65, 835],
            "knee_r": [356, 650],
            "foot_r": [315, 818],
            "knee_l": [702, 650],
            "foot_l": [832, 855],
            "cape_1": [655, 225],
            "cape_2": [805, 315],
            "cape_3": [950, 425],
        },
    }


def make_contact_preview(char_name: str, meta: dict, out_path: str) -> None:
    part_dir = os.path.join(PARTS_DIR, char_name)
    parts = meta["parts"]
    cols = 3
    rows = (len(parts) + cols - 1) // cols
    cell_w, cell_h = 340, 340
    canvas = Image.new("RGBA", (cols * cell_w, rows * cell_h), (28, 32, 42, 255))
    draw = ImageDraw.Draw(canvas)
    for idx, fn in enumerate(parts):
        im = Image.open(os.path.join(part_dir, fn)).convert("RGBA")
        im_scaled = im.copy()
        im_scaled.thumbnail((cell_w - 20, cell_h - 36), Image.Resampling.LANCZOS)
        cx = (idx % cols) * cell_w + (cell_w - im_scaled.width) // 2
        cy = (idx // cols) * cell_h + 26 + (cell_h - 36 - im_scaled.height) // 2
        canvas.alpha_composite(im_scaled, (cx, cy))
        draw.rectangle(
            [(idx % cols) * cell_w, (idx // cols) * cell_h, ((idx % cols) + 1) * cell_w - 1, ((idx // cols) + 1) * cell_h - 1],
            outline=(70, 88, 120, 255),
            width=1,
        )
        draw.text(((idx % cols) * cell_w + 10, (idx // cols) * cell_h + 6), fn, fill=(255, 210, 90, 255))
    canvas.convert("RGB").save(out_path)


def main() -> None:
    mage_meta = extract_mage()
    boss_meta = extract_boss()
    os.makedirs(PARTS_DIR, exist_ok=True)
    with open(os.path.join(PARTS_DIR, "rig_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"mage": mage_meta, "boss": boss_meta}, f, indent=2)
    make_contact_preview("mage", mage_meta, "/tmp/preview_mage_parts.png")
    make_contact_preview("boss", boss_meta, "/tmp/preview_boss_parts.png")
    print("Extracted mage & boss rigged parts + previews cleanly.")


if __name__ == "__main__":
    main()
