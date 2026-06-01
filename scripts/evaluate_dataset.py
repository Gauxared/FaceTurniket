#!/usr/bin/env python3
"""
Dataset evaluation script for face recognition system.

Evaluates 1:1 verification and 1:N identification on a celebrity dataset.
Does NOT copy photos to repository - only stores paths in report.
"""

import argparse
import json
import os
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

# Add repo root to path
repo_root = Path(__file__).parent.parent.resolve()
import sys
sys.path.insert(0, str(repo_root))

from src.contracts.models import RecognitionResult
from src.face.providers.factory import ProviderFactory
from src.face.providers.insightface_provider import _import_insightface
from src.identity.enrollment import EnrollmentService, generate_mock_embedding
from src.identity.matcher import IdentityMatcher, cosine_similarity
from src.identity.template_store import InMemoryTemplateStore


@dataclass
class PersonData:
    person_name: str
    images: List[str]


@dataclass
class EvalMetrics:
    total_people: int = 0
    enrolled_templates: int = 0
    probe_images: int = 0
    detection_failures: int = 0
    quality_failures: int = 0
    verification_1to1_true_accept: int = 0
    verification_1to1_false_reject: int = 0
    verification_1to1_true_reject: int = 0
    verification_1to1_false_accept: int = 0
    identification_1toN_top1_correct: int = 0
    identification_1toN_not_found: int = 0
    identification_1toN_ambiguous: int = 0
    confidence_allow_zone: int = 0
    confidence_review_zone: int = 0
    confidence_deny_zone: int = 0
    manual_check_suggested: int = 0
    avg_similarity_positive_pairs: float = 0.0
    avg_similarity_negative_pairs: float = 0.0


def scan_dataset(dataset_path: str, max_people: Optional[int] = None) -> List[PersonData]:
    """Scan dataset directory and return list of persons with their images."""
    persons = []
    for name in sorted(os.listdir(dataset_path)):
        person_dir = os.path.join(dataset_path, name)
        if not os.path.isdir(person_dir):
            continue
        
        images = [
            os.path.join(person_dir, f)
            for f in sorted(os.listdir(person_dir))
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if images:
            persons.append(PersonData(person_name=name, images=images))
    
    if max_people:
        persons = persons[:max_people]
    
    return persons


def select_images(images: List[str], enroll_count: int, probe_count: int, seed: int = 42) -> Tuple[List[str], List[str]]:
    """Select enrollment and probe images from list."""
    rng = random.Random(seed)
    shuffled = images.copy()
    rng.shuffle(shuffled)
    
    total_needed = enroll_count + probe_count
    if len(shuffled) < total_needed:
        # Reuse images if not enough
        enroll_images = shuffled[:enroll_count]
        probe_images = shuffled[enroll_count:enroll_count + probe_count]
        if len(probe_images) < probe_count:
            probe_images.extend(shuffled[:probe_count - len(probe_images)])
    else:
        enroll_images = shuffled[:enroll_count]
        probe_images = shuffled[enroll_count:enroll_count + probe_count]
    
    return enroll_images, probe_images


def load_image(path: str) -> Optional[np.ndarray]:
    """Load image to numpy array."""
    if not os.path.exists(path):
        return None
    return cv2.imread(path)


def evaluate_1to1_verification(
    probe_image_path: str,
    claimed_user_id: str,
    matcher: IdentityMatcher,
    recognition_result: RecognitionResult,
) -> Tuple[str, float]:
    """
    Evaluate 1:1 verification.
    Returns ('accept'/'reject', similarity_score).
    """
    search_result = matcher.verify_1to1(recognition_result, claimed_user_id)
    similarity = float(search_result.similarity) if search_result.similarity is not None else 0.0
    
    if search_result.status == "matched":
        return ("accept", similarity)
    else:
        return ("reject", similarity)


def evaluate_1toN_identification(
    probe_image_path: str,
    expected_user_id: str,
    matcher: IdentityMatcher,
    recognition_result: RecognitionResult,
) -> Tuple[str, Optional[str], float]:
    """
    Evaluate 1:N identification.
    Returns ('found'/'not_found'/'ambiguous', matched_user_id, similarity).
    """
    search_result = matcher.identify_1toN(recognition_result)
    similarity = float(search_result.similarity) if search_result.similarity is not None else 0.0
    
    if search_result.status == "matched":
        matched_user = search_result.user_id
        if matched_user == expected_user_id:
            return ("found", matched_user, similarity)
        else:
            return ("found_wrong", matched_user, similarity)
    elif search_result.status == "ambiguous":
        return ("ambiguous", search_result.user_id, similarity)
    else:
        return ("not_found", None, similarity)


def run_evaluation(
    dataset_path: str,
    max_people: Optional[int],
    enroll_per_person: int,
    probe_per_person: int,
    threshold: float,
    provider_name: str,
    report_path: str,
) -> Dict[str, Any]:
    """Run full dataset evaluation."""
    
    # Initialize provider
    if provider_name == "insightface":
        try:
            provider = ProviderFactory.create(provider_name="insightface")
        except ImportError as e:
            print(f"ERROR: {e}")
            return {}
    else:
        provider = ProviderFactory.create(provider_name="mock")
    
    # Initialize pipeline and store
    from src.face.recognition_pipeline import RecognitionPipeline
    pipeline = RecognitionPipeline(provider)
    store = InMemoryTemplateStore()
    enrollment = EnrollmentService(pipeline, store)
    matcher = IdentityMatcher(store, threshold=threshold)
    
    # Scan dataset
    print(f"Scanning dataset: {dataset_path}")
    persons = scan_dataset(dataset_path, max_people)
    print(f"Found {len(persons)} person(s)")
    
    # Metrics
    metrics = EvalMetrics()
    review_threshold = max(0.0, threshold - 0.12)
    positive_similarities = []
    negative_similarities = []
    results = []
    
    for person in persons:
        print(f"\nProcessing: {person.person_name}")
        
        # Select images
        enroll_images, probe_images = select_images(
            person.images, enroll_per_person, probe_per_person
        )
        
        # Enrollment
        enrolled_count = 0
        for img_path in enroll_images:
            user_id = person.person_name.replace(" ", "_")
            result = enrollment.enroll(img_path, user_id=user_id)
            
            if result.success:
                enrolled_count += 1
                metrics.enrolled_templates += 1
            else:
                if "face_not_detected" in result.reason:
                    metrics.detection_failures += 1
                elif "quality_not_acceptable" in result.reason:
                    metrics.quality_failures += 1
        
        if enrolled_count == 0:
            print(f"  Skipping {person.person_name}: no templates enrolled")
            continue
        
        # Verification and identification
        person_results = []
        for probe_img in probe_images:
            user_id = person.person_name.replace(" ", "_")
            recognition = pipeline.process(probe_img)
            
            metrics.probe_images += 1
            
            if not recognition.face_detected:
                metrics.detection_failures += 1
                person_results.append({
                    "image": probe_img,
                    "status": "detection_failure",
                })
                continue
            
            if not recognition.quality.is_acceptable:
                metrics.quality_failures += 1
                person_results.append({
                    "image": probe_img,
                    "status": "quality_failure",
                })
                continue
            
            # 1:1 verification (positive pair)
            verif_result, verif_sim = evaluate_1to1_verification(
                probe_img, user_id, matcher, recognition
            )
            
            if verif_result == "accept":
                metrics.verification_1to1_true_accept += 1
            else:
                metrics.verification_1to1_false_reject += 1
            positive_similarities.append(verif_sim)

            if verif_sim >= threshold:
                metrics.confidence_allow_zone += 1
            elif verif_sim >= review_threshold:
                metrics.confidence_review_zone += 1
                metrics.manual_check_suggested += 1
            else:
                metrics.confidence_deny_zone += 1
            
            # 1:1 verification (negative pair) - try wrong user
            wrong_user_id = "wrong_user"
            neg_verif_result, neg_verif_sim = evaluate_1to1_verification(
                probe_img, wrong_user_id, matcher, recognition
            )
            
            if neg_verif_result == "reject":
                metrics.verification_1to1_true_reject += 1
            else:
                metrics.verification_1to1_false_accept += 1
            negative_similarities.append(neg_verif_sim)
            
            # 1:N identification
            id_result, matched_user, id_sim = evaluate_1toN_identification(
                probe_img, user_id, matcher, recognition
            )
            
            if id_result == "found":
                metrics.identification_1toN_top1_correct += 1
            elif id_result == "not_found":
                metrics.identification_1toN_not_found += 1
            elif id_result == "ambiguous":
                metrics.identification_1toN_ambiguous += 1
            
            person_results.append({
                "image": probe_img,
                "verification_1to1": verif_result,
                "verification_1to1_similarity": round(float(verif_sim), 4),
                "verification_1to1_negative": neg_verif_result,
                "identification_1toN": id_result,
                "identification_matched_user": matched_user,
                "identification_similarity": round(float(id_sim), 4) if id_sim is not None else None,
            })
        
        metrics.total_people += 1
        results.append({
            "person": person.person_name,
            "enrolled_templates": enrolled_count,
            "probe_count": len(probe_images),
            "results": person_results,
        })
    
    # Calculate averages
    if positive_similarities:
        metrics.avg_similarity_positive_pairs = float(sum(positive_similarities) / len(positive_similarities))
    if negative_similarities:
        metrics.avg_similarity_negative_pairs = float(sum(negative_similarities) / len(negative_similarities))
    
    # Build report
    report = {
        "dataset_path": dataset_path,
        "max_people": max_people,
        "enroll_per_person": enroll_per_person,
        "probe_per_person": probe_per_person,
        "threshold": threshold,
        "provider": provider_name,
        "threshold_policy": {
            "allow_threshold": threshold,
            "review_threshold": review_threshold,
        },
        "suggested_threshold_observations": {
            "manual_check_count": metrics.manual_check_suggested,
            "ambiguous_count": metrics.identification_1toN_ambiguous,
            "positive_minus_negative_gap": round(
                metrics.avg_similarity_positive_pairs
                - metrics.avg_similarity_negative_pairs,
                4,
            ),
        },
        "metrics": asdict(metrics),
        "results": results,
    }
    
    # Save report
    os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Dataset: {dataset_path}")
    print(f"People processed: {metrics.total_people}")
    print(f"Enrolled templates: {metrics.enrolled_templates}")
    print(f"Probe images: {metrics.probe_images}")
    print(f"Detection failures: {metrics.detection_failures}")
    print(f"Quality failures: {metrics.quality_failures}")
    print(f"\n1:1 Verification:")
    print(f"  True Accept: {metrics.verification_1to1_true_accept}")
    print(f"  False Reject: {metrics.verification_1to1_false_reject}")
    print(f"  True Reject: {metrics.verification_1to1_true_reject}")
    print(f"  False Accept: {metrics.verification_1to1_false_accept}")
    print(f"\n1:N Identification:")
    print(f"  Top-1 Correct: {metrics.identification_1toN_top1_correct}")
    print(f"  Not Found: {metrics.identification_1toN_not_found}")
    print(f"  Ambiguous: {metrics.identification_1toN_ambiguous}")
    print(f"\nAverage similarity (positive pairs): {metrics.avg_similarity_positive_pairs:.4f}")
    print(f"Average similarity (negative pairs): {metrics.avg_similarity_negative_pairs:.4f}")
    print(f"\nReport saved to: {report_path}")
    print("="*60)
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Dataset evaluation for face recognition")
    parser.add_argument("--dataset", required=True, help="Path to dataset directory")
    parser.add_argument("--max-people", type=int, default=None, help="Max people to process")
    parser.add_argument("--enroll-per-person", type=int, default=2, help="Images for enrollment per person")
    parser.add_argument("--probe-per-person", type=int, default=2, help="Images for probing per person")
    parser.add_argument("--threshold", type=float, default=0.7, help="Similarity threshold")
    parser.add_argument("--provider", default="mock", choices=["mock", "insightface"], help="Provider to use")
    parser.add_argument("--report", default="reports/dataset_eval.json", help="Output report path")
    
    args = parser.parse_args()
    
    run_evaluation(
        dataset_path=args.dataset,
        max_people=args.max_people,
        enroll_per_person=args.enroll_per_person,
        probe_per_person=args.probe_per_person,
        threshold=args.threshold,
        provider_name=args.provider,
        report_path=args.report,
    )


if __name__ == "__main__":
    main()
