from src.retrieval.engine import RetrievalEngine
from src.ranking.ranker import rerank_candidates


# Load the persisted retrieval artifacts.
engine = RetrievalEngine("artifacts")


# Define a real recruiter query.
query = "Junior Data Analyst with SQL and Tableau experience"


# Retrieve candidate-level results from FAISS.
candidates = engine.retrieve_candidates(
    query=query,
    top_k_chunks=30,
    top_k_candidates=5
)


# Attach the full candidate profiles required by the ranking engine.
for candidate in candidates:
    profile = engine.get_candidate_profile(
        candidate["candidate_id"]
    )

    candidate["resume_text"] = profile["resume_text"]
    candidate["entities"] = profile["entities"]


# Apply requirement matching and hybrid reranking.
reranked_candidates = rerank_candidates(
    candidates,
    query
)


print("RETRIEVAL + RANKING TEST")
print("=" * 60)
print(f"Query: {query}")
print()


for rank, candidate in enumerate(
    reranked_candidates,
    start=1
):
    print(
        f"{rank}. Candidate {candidate['candidate_id']} "
        f"| Hybrid: {candidate['hybrid_score']:.4f} "
        f"| Semantic: {candidate['similarity_score']:.4f} "
        f"| Coverage: {candidate['requirement_coverage']:.0%}"
    )

    print(
        f"   Matched: {candidate['matched_requirements']}"
    )

    print(
        f"   Missing: {candidate['missing_requirements']}"
    )
