from src.pipeline.search_pipeline import SearchPipeline


query = "Python deep learning TensorFlow computer vision"

print("=" * 70)
print("RAG TALENT SEARCH - PRODUCTION PIPELINE TEST")
print("=" * 70)

pipeline = SearchPipeline()

result = pipeline.search(
    query,
    top_k_chunks=30,
    top_k_candidates=10,
    final_top_k=5
)

print()
print("QUERY:", result["query"])
print("RETRIEVED:", result["retrieved_count"])
print("RANKED:", result["ranked_count"])
print("UNIQUE:", result["unique_count"])
print("FINAL:", result["final_count"])
print("GEMINI SOURCE:", result["gemini_source"])
print("CACHE KEY:", result["cache_key"])

print()
print("=" * 70)
print("FINAL CANDIDATES")
print("=" * 70)

for candidate in result["candidates"]:

    print()
    print(
        "Rank:",
        candidate["final_rank"],
        "| Candidate ID:",
        candidate["candidate_id"]
    )

    print(
        "Semantic Score:",
        round(candidate["similarity_score"], 4)
    )

    print(
        "Requirement Coverage:",
        round(
            candidate["requirement_coverage"],
            4
        )
    )

    print(
        "Hybrid Score:",
        round(
            candidate["hybrid_score"],
            4
        )
    )

    print(
        "Matched:",
        candidate["matched_requirements"]
    )

    print(
        "Missing:",
        candidate["missing_requirements"]
    )

    print("-" * 70)

print()
print("=" * 70)
print("GEMINI EVALUATION")
print("=" * 70)

for evaluation in result[
    "gemini_evaluation"
]["candidates"]:

    print()
    print(
        "Rank:",
        evaluation["rank"],
        "| Candidate ID:",
        evaluation["candidate_id"]
    )

    print(
        "Summary:",
        evaluation["fit_summary"]
    )

    print(
        "Evidence:",
        evaluation["matching_evidence"]
    )

    print(
        "Gaps:",
        evaluation["gaps"]
    )

    print("-" * 70)

