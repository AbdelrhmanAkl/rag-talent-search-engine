from src.retrieval.engine import RetrievalEngine


# Load the persisted retrieval artifacts.
engine = RetrievalEngine("artifacts")


# Run a real semantic retrieval query.
query = "Junior Data Analyst with SQL and Tableau experience"

results = engine.retrieve_candidates(
    query=query,
    top_k_chunks=30,
    top_k_candidates=5
)


print("RETRIEVAL ENGINE TEST")
print("=" * 60)
print(f"Query: {query}")
print(f"Candidates returned: {len(results)}")
print()


# Display the retrieved candidates and their best chunk scores.
for rank, result in enumerate(results, start=1):
    print(
        f"{rank}. Candidate {result['candidate_id']} "
        f"| Similarity: {result['similarity_score']:.4f} "
        f"| Chunks: {len(result['matched_chunks'])}"
    )
