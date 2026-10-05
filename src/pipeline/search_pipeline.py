from src.retrieval.engine import RetrievalEngine
from src.ranking.ranker import rerank_candidates
from src.ranking.deduplicator import deduplicate_candidates
from src.evaluation.llm_evaluator import LLMEvaluator


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
        LLM Evidence Evaluation
            ↓
        Final Search Result

    LLM Provider Strategy:
        Cache → Groq → Gemini Fallback
    """

    def __init__(
        self,
        artifact_dir="artifacts",
        groq_model="openai/gpt-oss-120b",
        gemini_model="gemini-3.6-flash"
    ):
        self.engine = RetrievalEngine(
            artifact_dir
        )

        self.evaluator = LLMEvaluator(
            groq_model=groq_model,
            gemini_model=gemini_model
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

        LLM evaluation is an optional enrichment layer.
        Retrieval and ranking remain available even if
        both LLM providers fail.
        """

        # =====================================================
        # 1. Validate input
        # =====================================================

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

        if top_k_chunks < 1:
            raise ValueError(
                "top_k_chunks must be at least 1."
            )

        if top_k_candidates < 1:
            raise ValueError(
                "top_k_candidates must be at least 1."
            )

        if final_top_k < 1:
            raise ValueError(
                "final_top_k must be at least 1."
            )

        # =====================================================
        # 2. Retrieve candidate chunks
        # =====================================================

        retrieved_candidates = (
            self.engine.retrieve_candidates(
                query,
                top_k_chunks=top_k_chunks,
                top_k_candidates=top_k_candidates
            )
        )

        # =====================================================
        # 3. Load full resume text
        # =====================================================

        for candidate in retrieved_candidates:

            profile = (
                self.engine.get_candidate_profile(
                    candidate["candidate_id"]
                )
            )

            candidate["resume_text"] = (
                profile["resume_text"]
            )

        # =====================================================
        # 4. Hybrid ranking
        # =====================================================

        ranked_candidates = rerank_candidates(
            retrieved_candidates,
            query
        )

        # =====================================================
        # 5. Deduplicate candidates
        # =====================================================

        unique_candidates = (
            deduplicate_candidates(
                ranked_candidates
            )
        )

        # =====================================================
        # 6. Assign final ranking
        # =====================================================

        for rank, candidate in enumerate(
            unique_candidates,
            start=1
        ):
            candidate["final_rank"] = rank

        # =====================================================
        # 7. Select final candidates
        # =====================================================

        final_candidates = (
            unique_candidates[:final_top_k]
        )

        # =====================================================
        # 8. Prepare evaluator input
        # =====================================================

        search_results = {
            "query": query,
            "candidates": final_candidates
        }

        # =====================================================
        # 9. LLM Evidence Evaluation
        # =====================================================

        llm_evaluation = None
        llm_source = "unavailable"
        llm_error = None
        cache_key = None
        cached_source = None

        try:

            llm_result = (
                self.evaluator.evaluate(
                    recruiter_query=query,
                    search_results=search_results
                )
            )

            llm_evaluation = (
                llm_result.get(
                    "evaluation"
                )
            )

            llm_source = (
                llm_result.get(
                    "source",
                    "unavailable"
                )
            )

            cache_key = (
                llm_result.get(
                    "cache_key"
                )
            )

            cached_source = (
                llm_result.get(
                    "cached_source"
                )
            )

            # -------------------------------------------------
            # Groq failed but Gemini fallback succeeded.
            # Keep the Groq error for observability.
            # -------------------------------------------------

            if llm_result.get(
                "groq_error"
            ):

                llm_error = (
                    "Groq failed; "
                    "Gemini fallback succeeded. "
                    f"Groq error: "
                    f"{llm_result['groq_error']}"
                )

        except Exception as exc:

            # -------------------------------------------------
            # LLM is an enrichment layer.
            # Retrieval and ranking remain valid.
            # -------------------------------------------------

            llm_error = str(
                exc
            )

            llm_source = "unavailable"

        # =====================================================
        # 10. Build final structured result
        # =====================================================

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

            # -------------------------------------------------
            # New provider-neutral fields
            # -------------------------------------------------

            "llm_evaluation":
                llm_evaluation,

            "llm_source":
                llm_source,

            "llm_error":
                llm_error,

            "cached_source":
                cached_source,

            "cache_key":
                cache_key,

            # -------------------------------------------------
            # Backward compatibility
            # -------------------------------------------------

            "gemini_evaluation":
                llm_evaluation,

            "gemini_source":
                llm_source,

            "gemini_error":
                llm_error
        }