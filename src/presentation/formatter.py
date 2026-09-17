class SearchResultFormatter:

    """
    Formats raw SearchPipeline results into
    clean presentation-ready structures.
    """

    @staticmethod
    def format_candidate(
        candidate,
        gemini_evaluation=None
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
                candidate["matched_requirements"]
            ),
            "missing_requirements": (
                candidate["missing_requirements"]
            ),
        }

        # Gemini evaluation is optional.
        # Retrieval and ranking results remain valid
        # when Gemini is unavailable.
        if gemini_evaluation:

            result.update({
                "fit_summary": (
                    gemini_evaluation.get(
                        "fit_summary",
                        ""
                    )
                ),
                "matching_evidence": (
                    gemini_evaluation.get(
                        "matching_evidence",
                        []
                    )
                ),
                "gaps": (
                    gemini_evaluation.get(
                        "gaps",
                        []
                    )
                ),
                "bias_check": (
                    gemini_evaluation.get(
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
        """

        # ---------------------------------------------------------
        # Gemini evaluation is optional.
        # ---------------------------------------------------------

        gemini_evaluation = (
            pipeline_result.get(
                "gemini_evaluation"
            )
        )

        gemini_candidates = {}

        if (
            gemini_evaluation
            and isinstance(
                gemini_evaluation,
                dict
            )
        ):

            for candidate in (
                gemini_evaluation.get(
                    "candidates",
                    []
                )
            ):

                candidate_id = candidate.get(
                    "candidate_id"
                )

                if candidate_id is not None:
                    gemini_candidates[
                        candidate_id
                    ] = candidate

        # ---------------------------------------------------------
        # Format final candidates.
        # ---------------------------------------------------------

        formatted_candidates = []

        for candidate in pipeline_result.get(
            "candidates",
            []
        ):

            candidate_id = candidate[
                "candidate_id"
            ]

            candidate_gemini_evaluation = (
                gemini_candidates.get(
                    candidate_id
                )
            )

            formatted_candidates.append(
                SearchResultFormatter.format_candidate(
                    candidate,
                    candidate_gemini_evaluation
                )
            )

        # ---------------------------------------------------------
        # Return presentation-ready result.
        # ---------------------------------------------------------

        return {
            "query": pipeline_result[
                "query"
            ],

            "retrieved_count": pipeline_result[
                "retrieved_count"
            ],

            "ranked_count": pipeline_result[
                "ranked_count"
            ],

            "unique_count": pipeline_result[
                "unique_count"
            ],

            "final_count": pipeline_result[
                "final_count"
            ],

            "gemini_source": pipeline_result.get(
                "gemini_source",
                "unavailable"
            ),

            "gemini_error": pipeline_result.get(
                "gemini_error"
            ),

            "candidates": formatted_candidates,
        }