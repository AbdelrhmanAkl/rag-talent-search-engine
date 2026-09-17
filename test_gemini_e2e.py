from src.retrieval.engine import RetrievalEngine
from src.ranking.ranker import rerank_candidates
from src.ranking.deduplicator import deduplicate_candidates
from src.evaluation.gemini_evaluator import GeminiEvaluator


query = "Python deep learning TensorFlow computer vision"

print("=" * 70)
print("RAG TALENT SEARCH - GEMINI END-TO-END TEST")
print("=" * 70)

engine = RetrievalEngine("artifacts")

retrieved = engine.retrieve_candidates(
    query,
    top_k_chunks=30,
    top_k_candidates=10
)

print("RETRIEVED:", len(retrieved))

for candidate in retrieved:
    profile = engine.get_candidate_profile(
        candidate["candidate_id"]
    )

    candidate["resume_text"] = profile["resume_text"]


ranked = rerank_candidates(
    retrieved,
    query
)

print("RANKED:", len(ranked))

unique = deduplicate_candidates(
    ranked
)

print("UNIQUE:", len(unique))

for i, candidate in enumerate(
    unique,
    start=1
):
    candidate["final_rank"] = i


search_results = {
    "query": query,
    "candidates": unique[:5]
}


evaluator = GeminiEvaluator()

result = evaluator.evaluate(
    query,
    search_results
)

print()
print("GEMINI SOURCE:", result["source"])
print("CACHE KEY:", result["cache_key"])

print()
print("=" * 70)
print("TOP GEMINI EVALUATIONS")
print("=" * 70)

for candidate in result["evaluation"]["candidates"]:

    print()
    print(
        "Rank:",
        candidate["rank"],
        "| Candidate ID:",
        candidate["candidate_id"]
    )

    print(
        "Summary:",
        candidate["fit_summary"]
    )

    print(
        "Evidence:",
        candidate["matching_evidence"]
    )

    print(
        "Gaps:",
        candidate["gaps"]
    )

    print("-" * 70)
