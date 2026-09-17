from src.pipeline.search_pipeline import SearchPipeline
from src.presentation.formatter import SearchResultFormatter


query = "Python deep learning TensorFlow computer vision"

print("=" * 70)
print("RAG TALENT SEARCH - FORMATTER TEST")
print("=" * 70)

pipeline = SearchPipeline()

pipeline_result = pipeline.search(
    query,
    top_k_chunks=30,
    top_k_candidates=10,
    final_top_k=5
)

formatted_result = (
    SearchResultFormatter.format_search_result(
        pipeline_result
    )
)

print()
print("QUERY:", formatted_result["query"])
print("RETRIEVED:", formatted_result["retrieved_count"])
print("RANKED:", formatted_result["ranked_count"])
print("UNIQUE:", formatted_result["unique_count"])
print("FINAL:", formatted_result["final_count"])
print("GEMINI SOURCE:", formatted_result["gemini_source"])

print()
print("=" * 70)
print("FORMATTED CANDIDATES")
print("=" * 70)

for candidate in formatted_result["candidates"]:

    print()
    print(
        "Rank:",
        candidate["rank"],
        "| Candidate ID:",
        candidate["candidate_id"]
    )

    print(
        "Hybrid Score:",
        candidate["hybrid_score"]
    )

    print(
        "Requirement Coverage:",
        candidate["requirement_coverage"]
    )

    print(
        "Matched:",
        candidate["matched_requirements"]
    )

    print(
        "Missing:",
        candidate["missing_requirements"]
    )

    print(
        "Summary:",
        candidate.get(
            "fit_summary",
            "Not available"
        )
    )

    print(
        "Evidence:",
        candidate.get(
            "matching_evidence",
            []
        )
    )

    print(
        "Gaps:",
        candidate.get(
            "gaps",
            []
        )
    )

    print("-" * 70)
