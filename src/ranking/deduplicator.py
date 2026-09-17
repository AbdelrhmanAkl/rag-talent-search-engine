import re
from difflib import SequenceMatcher


DUPLICATE_THRESHOLD = 0.95


def normalize_for_comparison(text):
    """
    Normalize resume text before similarity comparison.
    """

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip().lower()

    return text


def compare_candidate_profiles(
    candidate_a,
    candidate_b
):
    """
    Calculate text similarity between two candidate resumes.
    """

    text_a = normalize_for_comparison(
        candidate_a["resume_text"]
    )

    text_b = normalize_for_comparison(
        candidate_b["resume_text"]
    )

    similarity = SequenceMatcher(
        None,
        text_a,
        text_b
    ).ratio()

    return similarity


def deduplicate_candidates(
    candidate_results,
    similarity_threshold=DUPLICATE_THRESHOLD
):
    """
    Remove near-duplicate candidate resumes.

    Candidates are compared in their current retrieval order,
    so the first occurrence is retained when a duplicate is found.
    """

    unique_candidates = []

    for candidate in candidate_results:
        is_duplicate = False

        for existing_candidate in unique_candidates:
            similarity = compare_candidate_profiles(
                candidate,
                existing_candidate
            )

            if similarity >= similarity_threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_candidates.append(candidate)

    return unique_candidates
