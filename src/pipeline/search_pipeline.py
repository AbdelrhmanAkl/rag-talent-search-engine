from src.retrieval.engine import RetrievalEngine
from src.ranking.ranker import rerank_candidates
from src.ranking.deduplicator import deduplicate_candidates
from src.evaluation.gemini_evaluator import GeminiEvaluator


class SearchPipeline:
    """
    End-to-end RAG Talent Search pipeline.

    Flow:
        Recruiter Query
            ↓
        FAISS Retrieval
            ↓
        Candidate Profile Loading
            ↓
        Hybrid Ranking
            ↓
        Deduplication
            ↓
        Final Ranking
            ↓
        Gemini Evidence Evaluation
            ↓
        Final Search Result
    """

    def __init__(
        self,
        artifact_dir="artifacts",
        gemini_model="gemini-3.6-flash"
    ):
        self.engine = RetrievalEngine(
            artifact_dir
        )

        self.evaluator = GeminiEvaluator(
            model_name=gemini_model
        )

    def search(
        self,
        query,
        top_k_chunks=30,
        top_k_candidates=10,
        final_top_k=5
    ):
        """
        Run the complete talent search pipeline.

        Gemini evaluation is treated as an optional enrichment step.
        If Gemini is unavailable because of quota/rate limits or
        another evaluation error, retrieval and ranking results are
        still returned.
        """

        if not isinstance(
            query,
            str
        ):
            raise TypeError(
                "Query must be a string."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        # ---------------------------------------------------------
        # 1. Retrieve candidate chunks
        # ---------------------------------------------------------

        retrieved_candidates = (
            self.engine.retrieve_candidates(
                query,
                top_k_chunks=top_k_chunks,
                top_k_candidates=top_k_candidates
            )
        )

        # ---------------------------------------------------------
        # 2. Load full resume text
        # ---------------------------------------------------------

        for candidate in retrieved_candidates:

            profile = (
                self.engine.get_candidate_profile(
                    candidate["candidate_id"]
                )
            )

            candidate["resume_text"] = (
                profile["resume_text"]
            )

        # ---------------------------------------------------------
        # 3. Hybrid ranking
        # ---------------------------------------------------------

        ranked_candidates = rerank_candidates(
            retrieved_candidates,
            query
        )

        # ---------------------------------------------------------
        # 4. Deduplicate candidates
        # ---------------------------------------------------------

        unique_candidates = (
            deduplicate_candidates(
                ranked_candidates
            )
        )

        # ---------------------------------------------------------
        # 5. Assign final ranking
        # ---------------------------------------------------------

        for rank, candidate in enumerate(
            unique_candidates,
            start=1
        ):
            candidate["final_rank"] = rank

        # ---------------------------------------------------------
        # 6. Select final candidates
        # ---------------------------------------------------------

        final_candidates = (
            unique_candidates[:final_top_k]
        )

        # ---------------------------------------------------------
        # 7. Build base search result
        # ---------------------------------------------------------

        search_results = {
            "query": query,
            "candidates": final_candidates
        }

        # ---------------------------------------------------------
        # 8. Gemini evidence evaluation
        # ---------------------------------------------------------

        gemini_evaluation = None
        gemini_source = "unavailable"
        cache_key = None
        gemini_error = None

        try:

            gemini_result = (
                self.evaluator.evaluate(
                    query,
                    search_results
                )
            )

            gemini_evaluation = (
                gemini_result.get(
                    "evaluation"
                )
            )

            gemini_source = (
                gemini_result.get(
                    "source",
                    "live"
                )
            )

            cache_key = (
                gemini_result.get(
                    "cache_key"
                )
            )

        except Exception as exc:

            # Gemini is an enrichment layer.
            # Retrieval and ranking must remain available
            # even when Gemini is temporarily unavailable.

            gemini_error = str(exc)

            gemini_source = "unavailable"

        # ---------------------------------------------------------
        # 9. Return structured result
        # ---------------------------------------------------------

        return {
            "query": query,
            "retrieved_count": len(
                retrieved_candidates
            ),
            "ranked_count": len(
                ranked_candidates
            ),
            "unique_count": len(
                unique_candidates
            ),
            "final_count": len(
                final_candidates
            ),
            "candidates": final_candidates,
            "gemini_evaluation": gemini_evaluation,
            "gemini_source": gemini_source,
            "gemini_error": gemini_error,
            "cache_key": cache_key
        }