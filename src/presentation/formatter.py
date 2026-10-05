class SearchResultFormatter:
    """
    Formats raw SearchPipeline results into
    clean presentation-ready structures.

    Supports the provider-neutral LLM fields while
    maintaining backward compatibility with previous
    Gemini-specific field names.
    """

    @staticmethod
    def format_candidate(
        candidate,
        llm_evaluation=None
    ):
        """
        Format a single candidate result.
        """

        result = {
            "rank": candidate["final_rank"],
            "candidate_id": candidate["candidate_id"],

            "semantic_score": round(
                candidate["similarity_score"],
                4
            ),

            "requirement_coverage": round(
                candidate["requirement_coverage"],
                4
            ),

            "hybrid_score": round(
                candidate["hybrid_score"],
                4
            ),

            "matched_requirements": (
                candidate.get(
                    "matched_requirements",
                    []
                )
            ),

            "missing_requirements": (
                candidate.get(
                    "missing_requirements",
                    []
                )
            ),
        }

        # ---------------------------------------------------------
        # LLM evaluation is optional.
        # Retrieval and ranking remain valid even when
        # LLM evaluation is unavailable.
        # ---------------------------------------------------------

        if llm_evaluation:

            result.update({
                "fit_summary": (
                    llm_evaluation.get(
                        "fit_summary",
                        ""
                    )
                ),

                "matching_evidence": (
                    llm_evaluation.get(
                        "matching_evidence",
                        []
                    )
                ),

                "gaps": (
                    llm_evaluation.get(
                        "gaps",
                        []
                    )
                ),

                "bias_check": (
                    llm_evaluation.get(
                        "bias_check",
                        ""
                    )
                ),
            })

        else:

            result.update({
                "fit_summary": None,
                "matching_evidence": [],
                "gaps": [],
                "bias_check": None,
            })

        return result

    @staticmethod
    def format_search_result(
        pipeline_result
    ):
        """
        Format the complete pipeline result.

        New fields:
            llm_evaluation
            llm_source
            llm_error
            cached_source

        Backward-compatible fields:
            gemini_evaluation
            gemini_source
            gemini_error
        """

        # =========================================================
        # Resolve LLM evaluation
        # =========================================================

        llm_evaluation = pipeline_result.get(
            "llm_evaluation"
        )

        # ---------------------------------------------------------
        # Backward compatibility with the old Gemini field.
        # ---------------------------------------------------------

        if llm_evaluation is None:

            llm_evaluation = (
                pipeline_result.get(
                    "gemini_evaluation"
                )
            )

        # =========================================================
        # Build candidate evaluation lookup
        # =========================================================

        llm_candidates = {}

        if (
            isinstance(
                llm_evaluation,
                dict
            )
        ):

            for candidate in (
                llm_evaluation.get(
                    "candidates",
                    []
                )
            ):

                if not isinstance(
                    candidate,
                    dict
                ):
                    continue

                candidate_id = candidate.get(
                    "candidate_id"
                )

                if candidate_id is not None:

                    llm_candidates[
                        candidate_id
                    ] = candidate

        # =========================================================
        # Format final candidates
        # =========================================================

        formatted_candidates = []

        for candidate in pipeline_result.get(
            "candidates",
            []
        ):

            candidate_id = candidate.get(
                "candidate_id"
            )

            candidate_llm_evaluation = (
                llm_candidates.get(
                    candidate_id
                )
            )

            formatted_candidates.append(
                SearchResultFormatter.format_candidate(
                    candidate,
                    candidate_llm_evaluation
                )
            )

        # =========================================================
        # Resolve provider metadata
        # =========================================================

        llm_source = pipeline_result.get(
            "llm_source"
        )

        if llm_source is None:

            llm_source = pipeline_result.get(
                "gemini_source",
                "unavailable"
            )

        llm_error = pipeline_result.get(
            "llm_error"
        )

        if llm_error is None:

            llm_error = pipeline_result.get(
                "gemini_error"
            )

        cached_source = pipeline_result.get(
            "cached_source"
        )

        # =========================================================
        # Return presentation-ready result
        # =========================================================

        return {
            "query": pipeline_result.get(
                "query",
                ""
            ),

            "retrieved_count": pipeline_result.get(
                "retrieved_count",
                0
            ),

            "ranked_count": pipeline_result.get(
                "ranked_count",
                0
            ),

            "unique_count": pipeline_result.get(
                "unique_count",
                0
            ),

            "final_count": pipeline_result.get(
                "final_count",
                0
            ),

            # -----------------------------------------------------
            # New provider-neutral fields
            # -----------------------------------------------------

            "llm_source": llm_source,

            "llm_error": llm_error,

            "cached_source": cached_source,

            "cache_key": pipeline_result.get(
                "cache_key"
            ),

            # -----------------------------------------------------
            # Backward-compatible Gemini fields
            # -----------------------------------------------------

            "gemini_source": llm_source,

            "gemini_error": llm_error,

            # -----------------------------------------------------
            # Final candidates
            # -----------------------------------------------------

            "candidates": formatted_candidates,
        }