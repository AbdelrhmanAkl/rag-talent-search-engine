from src.retrieval.engine import RetrievalEngine
from src.ranking.deduplicator import deduplicate_candidates
from src.ranking.ranker import rerank_candidates
from src.evaluation.gemini_evaluator import GeminiEvaluator


# Load the persisted retrieval artifacts.
engine = RetrievalEngine("artifacts")


# Define a real recruiter query.
query = "Junior Data Analyst with SQL and Tableau experience"


# Retrieve candidates from FAISS.
retrieved_candidates = engine.retrieve_candidates(
    query=query,
    top_k_chunks=30,
    top_k_candidates=5
)


# Attach candidate profiles.
for candidate in retrieved_candidates:
    profile = engine.get_candidate_profile(
        candidate["candidate_id"]
    )

    candidate["resume_text"] = profile["resume_text"]
    candidate["entities"] = profile["entities"]


# Remove near-duplicate candidates.
unique_candidates = deduplicate_candidates(
    retrieved_candidates
)


# Apply hybrid ranking.
reranked_candidates = rerank_candidates(
    unique_candidates,
    query
)


# Keep the final three candidates.
final_candidates = reranked_candidates[:3]


# Add final ranks required by the evaluator.
for rank, candidate in enumerate(
    final_candidates,
    start=1
):
    candidate["final_rank"] = rank


search_results = {
    "query": query,
    "candidates": final_candidates
}


# Build the evidence context without calling Gemini.
evaluator = GeminiEvaluator()

context = evaluator.build_context(
    search_results,
    max_chunks_per_candidate=2
)


print("GEMINI EVIDENCE CONTEXT TEST")
print("=" * 60)
print(f"Query: {query}")
print(f"Candidates in context: {len(context)}")
print()


for candidate in context:
    print(
        f"Candidate {candidate['candidate_id']} "
        f"| Rank: {candidate['rank']} "
        f"| Hybrid: {candidate['hybrid_score']:.4f} "
        f"| Coverage: "
        f"{candidate['requirement_coverage']:.0%}"
    )

    print(
        f"Matched: "
        f"{candidate['matched_requirements']}"
    )

    print(
        f"Missing: "
        f"{candidate['missing_requirements']}"
    )

    print(
        f"Evidence chunks: "
        f"{len(candidate['evidence_chunks'])}"
    )

    print()
