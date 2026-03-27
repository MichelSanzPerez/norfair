"""
Batch wrapper for the my_norfair: Traverses a root hierarchy with subfolders Annotation/
and Data/ and generates results in Results/Norfair/ for all detected scenes and cameras.
It does not modify my_norfair.py.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional

from my_norfair import Config, run as run_tracker


# ==============================
# CONFIG
# ==============================
# Expected cameras in each scene
CAM_DIRS = ["fisheye_images_12", "fisheye_images_13", "fisheye_images_14", "output_images"]


# ==============================
# CLI UTILITIES
# ==============================
def _optional_int(value: str) -> Optional[int]:
    value = str(value).strip()
    if value.lower() == "none":
        return None
    return int(value)


# ==============================
# FILE DISCOVERY
# ==============================
def iter_annotation_scenes(root: Path) -> Iterable[Path]:
    ann_root = root / "Annotation"
    if not ann_root.is_dir():
        return []
    return [p for p in ann_root.iterdir() if p.is_dir()]


def find_annotation_json(cam_dir: Path) -> Optional[Path]:
    candidates = sorted(cam_dir.glob("cam*_ann.json"))
    return candidates[0] if candidates else None


# ==============================
# BATCH PROCESSING
# ==============================
def process_scene(root: Path, scene_ann_dir: Path, args) -> None:
    scene_ann_name = scene_ann_dir.name
    scene_label_name = scene_ann_name.replace("_json_files", "_label")

    data_scene_dir = root / "Data" / scene_label_name
    if not data_scene_dir.is_dir():
        print(f"[WARN] Data folder does not exist for scenario {scene_ann_name}: {data_scene_dir}")
        return

    out_scene_dir = root / "Results/Norfair" / scene_label_name

    for cam in CAM_DIRS:
        ann_cam_dir = scene_ann_dir / cam
        data_cam_dir = data_scene_dir / cam
        if not ann_cam_dir.is_dir():
            print(f"[WARN] Annotations folder is missing {ann_cam_dir}")
            continue
        if not data_cam_dir.is_dir():
            print(f"[WARN] Frames folder is missing {data_cam_dir}")
            continue

        json_path = find_annotation_json(ann_cam_dir)
        if json_path is None:
            print(f"[WARN] JSON file not found in {ann_cam_dir}")
            continue

        out_cam_dir = out_scene_dir / cam
        out_cam_dir.mkdir(parents=True, exist_ok=True)

        cfg = Config(
            detections_json=json_path,
            frames_dir=data_cam_dir,
            output_video=out_cam_dir / "tracking.mp4",
            distance_function=args.distance_function,
            distance_threshold=args.distance_threshold,
            hit_counter_max=args.hit_counter_max,
            initialization_delay=args.initialization_delay,
            mot_output=out_cam_dir / "results.txt",
            box_thickness=args.box_thickness,
            id_offset=args.id_offset,
            save_frames_dir=out_cam_dir / "results_frames",
        )

        print(f"[INFO] Scenario {scene_ann_name} | Camera {cam}")
        print(f"       JSON: {json_path}")
        print(f"       Frames: {data_cam_dir}")
        print(f"       Output: {out_cam_dir}")
        run_tracker(cfg)


# ==============================
# MAIN
# ==============================
def main():
    p = argparse.ArgumentParser(
        description="Processes all scenarios/cameras from a root directory containing Annotation/ and Data/ folders, and generates tracking results in Results/Norfair/"
    )
    p.add_argument("--root", required=True, type=Path, help="Root directory containing Annotation/ and Data/ folders")
    p.add_argument("--distance_function", type=str, default="iou", help="Norfair distance function")
    p.add_argument("--distance_threshold", type=float, default=0.75, help="Norfair distance threshold for matching")
    p.add_argument("--hit_counter_max", type=int, default=15, help="Maximum missed frames before track deletion")
    p.add_argument("--initialization_delay", type=_optional_int, default=None, help="Frames required to confirm a track (default: hit_counter_max/2)")
    p.add_argument("--box_thickness", type=int, default=2, help="Bounding box line thickness (px)")
    p.add_argument("--id_offset", type=int, default=10, help="Vertical offset for the ID text (px)")

    args = p.parse_args()
    root = args.root.resolve()

    scenes = list(iter_annotation_scenes(root))
    if not scenes:
        print(f"[ERROR] No scenarios found in {root/'Annotation'}")
        return

    for scene_ann_dir in scenes:
        process_scene(root, scene_ann_dir, args)


if __name__ == "__main__":
    main()
