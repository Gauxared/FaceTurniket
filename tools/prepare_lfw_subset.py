#!/usr/bin/env python3
"""
Prepare LFW subset for face recognition evaluation.

Downloads the LFW dataset (if not cached) via sklearn.datasets.fetch_lfw_people,
copies selected images into datasets/lfw_subset/enrollment/ and /probes/,
and produces datasets/lfw_subset/metadata.json.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# Add repo root to path so we can import project modules if needed
repo_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(repo_root))


def _ensure_lfw_downloaded(data_home: str) -> str:
    """Ensure LFW funneled images exist on disk. Returns path to funneled directory."""
    lfw_funneled = os.path.join(data_home, "lfw_home", "lfw_funneled")
    if os.path.isdir(lfw_funneled):
        return lfw_funneled

    # Trigger download via sklearn (uses default params = fast, grayscale + small resize)
    from sklearn.datasets import fetch_lfw_people
    print("Downloading LFW dataset (~200 MB)...")
    fetch_lfw_people(
        data_home=data_home,
        min_faces_per_person=1,
        download_if_missing=True,
    )
    if not os.path.isdir(lfw_funneled):
        print(f"ERROR: LFW funneled directory not found at {lfw_funneled}")
        sys.exit(1)
    return lfw_funneled


def prepare_lfw_subset(
    data_home: str,
    output_dir: str,
    min_faces: int,
    max_people: int,
    enroll_per_person: int,
    probe_per_person: int,
    seed: int,
):
    import random

    rng = random.Random(seed)

    # Ensure LFW images are on disk (download if needed)
    lfw_funneled = _ensure_lfw_downloaded(data_home)

    # Gather person directories sorted by number of images (descending)
    persons = []
    for name in sorted(os.listdir(lfw_funneled)):
        person_dir = os.path.join(lfw_funneled, name)
        if not os.path.isdir(person_dir):
            continue
        images = sorted(
            os.path.join(person_dir, f)
            for f in os.listdir(person_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        )
        if len(images) >= min_faces:
            persons.append((name, images))

    persons.sort(key=lambda x: len(x[1]), reverse=True)
    if max_people:
        persons = persons[:max_people]

    print(f"Using {len(persons)} person(s) with >= {min_faces} images each")

    # Prepare output directories — flat per-person dirs compatible with evaluate_dataset.py
    metadata_users = []
    metadata_positive_pairs = []
    metadata_negative_samples = []

    for person_name, images in persons:
        user_id = person_name.replace(" ", "_")
        rng.shuffle(images)

        # Split into enrollment and probes
        enroll_images = images[:enroll_per_person]
        probe_images = images[enroll_per_person : enroll_per_person + probe_per_person]

        # If not enough images, reuse some
        if len(probe_images) < probe_per_person:
            extra = probe_per_person - len(probe_images)
            probe_images.extend(enroll_images[:extra])

        # Create person directory flat under output root
        person_dir = os.path.join(output_dir, person_name)
        os.makedirs(person_dir, exist_ok=True)

        # Copy all images into the flat person directory
        all_copied = []
        for src in enroll_images + probe_images:
            dst = os.path.join(person_dir, os.path.basename(src))
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
            rel = os.path.relpath(dst, output_dir)
            all_copied.append(rel)

        # Record paths relative to output_dir for metadata
        enroll_paths = all_copied[:enroll_per_person]
        probe_paths = all_copied[enroll_per_person:enroll_per_person + probe_per_person]

        metadata_users.append({
            "user_id": user_id,
            "name": person_name,
            "enrollment_paths": enroll_paths,
            "probe_paths": probe_paths,
        })

        # Positive pairs: each probe matched against same person's enrollment
        for p in probe_paths:
            metadata_positive_pairs.append({
                "user_id": user_id,
                "probe_path": p,
            })

    # Negative samples: cross-person pairs
    all_users = list(metadata_users)
    for i, user in enumerate(all_users):
        for p in user["probe_paths"]:
            # Pick a random different person
            others = [u for u in all_users if u["user_id"] != user["user_id"]]
            if not others:
                continue
            wrong_user = rng.choice(others)
            metadata_negative_samples.append({
                "user_id": wrong_user["user_id"],
                "probe_path": p,
            })

    # Write metadata
    metadata = {
        "source": "LFW (Labeled Faces in the Wild)",
        "description": "LFW subset prepared for face recognition evaluation",
        "data_home": data_home,
        "min_faces_per_person": min_faces,
        "enroll_per_person": enroll_per_person,
        "probe_per_person": probe_per_person,
        "total_people": len(metadata_users),
        "total_enrollment_images": sum(len(u["enrollment_paths"]) for u in metadata_users),
        "total_probe_images": sum(len(u["probe_paths"]) for u in metadata_users),
        "positive_pairs_count": len(metadata_positive_pairs),
        "negative_samples_count": len(metadata_negative_samples),
        "users": metadata_users,
        "positive_pairs": metadata_positive_pairs,
        "negative_samples": metadata_negative_samples,
    }

    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nOutput directory: {output_dir}")
    print(f"People copied: {len(metadata_users)}")
    print(f"Enrollment images: {metadata['total_enrollment_images']}")
    print(f"Probe images: {metadata['total_probe_images']}")
    print(f"Positive pairs: {metadata['positive_pairs_count']}")
    print(f"Negative samples: {metadata['negative_samples_count']}")
    print(f"Metadata saved to: {meta_path}")

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Prepare LFW subset for face recognition evaluation"
    )
    parser.add_argument(
        "--data-home",
        default=os.path.join(os.path.expanduser("~"), "scikit_learn_data"),
        help="Directory where LFW dataset is cached (default: ~/scikit_learn_data)",
    )
    parser.add_argument(
        "--output",
        default="datasets/lfw_subset",
        help="Output directory for the prepared subset (default: datasets/lfw_subset)",
    )
    parser.add_argument(
        "--min-faces",
        type=int,
        default=10,
        help="Minimum faces per person to include (default: 10)",
    )
    parser.add_argument(
        "--max-people",
        type=int,
        default=None,
        help="Maximum number of people to process (default: all)",
    )
    parser.add_argument(
        "--enroll-per-person",
        type=int,
        default=3,
        help="Number of enrollment images per person (default: 3)",
    )
    parser.add_argument(
        "--probe-per-person",
        type=int,
        default=5,
        help="Number of probe images per person (default: 5)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()
    prepare_lfw_subset(
        data_home=args.data_home,
        output_dir=args.output,
        min_faces=args.min_faces,
        max_people=args.max_people,
        enroll_per_person=args.enroll_per_person,
        probe_per_person=args.probe_per_person,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
