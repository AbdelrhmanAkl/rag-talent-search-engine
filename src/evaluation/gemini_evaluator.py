import hashlib
import json
import os
from pathlib import Path

from google import genai


CACHE_DIR = Path("artifacts") / "gemini_cache"


class GeminiEvaluator:
    """
    Evidence-based Gemini evaluator for the final talent search candidates.

    The evaluator:
    - Uses retrieved chunks as retrieval evidence.
    - Uses the full resume text as verification evidence.
    - Generates a structured evaluation prompt.
    - Calls Gemini when no cached result exists.
    - Validates the returned JSON.
    - Stores validated evaluations in a local cache.
    """

    def __init__(
        self,
        model_name="gemini-3.6-flash",
        cache_dir=CACHE_DIR
    ):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def build_context(
        self,
        search_results,
        max_chunks_per_candidate=2
    ):
        """
        Build evidence context for Gemini.

        Each candidate contains:
        - Ranking metadata
        - Retrieved evidence chunks
        - Full resume text for verification
        """

        gemini_context = []

        for candidate in search_results["candidates"]:

            sorted_chunks = sorted(
                candidate["matched_chunks"],
                key=lambda item: item["similarity_score"],
                reverse=True
            )

            selected_chunks = sorted_chunks[
                :max_chunks_per_candidate
            ]

            evidence_chunks = []

            for chunk in selected_chunks:
                evidence_chunks.append({
                    "chunk_id": chunk["chunk_id"],
                    "similarity_score": round(
                        chunk["similarity_score"],
                        4
                    ),
                    "text": chunk["retrieval_text"]
                })

            gemini_context.append({
                "rank": candidate["final_rank"],
                "candidate_id": candidate["candidate_id"],
                "semantic_score": round(
                    candidate["similarity_score"],
                    4
                ),
                "hybrid_score": round(
                    candidate["hybrid_score"],
                    4
                ),
                "requirement_coverage": round(
                    candidate["requirement_coverage"],
                    4
                ),
                "matched_requirements":
                    candidate["matched_requirements"],
                "missing_requirements":
                    candidate["missing_requirements"],
                "retrieved_evidence": evidence_chunks,
                "full_resume_text": candidate["resume_text"]
            })

        return gemini_context

    def build_prompt(
        self,
        recruiter_query,
        gemini_context
    ):
        """
        Build the evidence-constrained Gemini evaluation prompt.
        """

        context_json = json.dumps(
            gemini_context,
            ensure_ascii=False,
            indent=2
        )

        return f"""
You are an AI recruitment assistant working inside a
Retrieval-Augmented Generation (RAG) talent search system.

Recruiter query:
{recruiter_query}

The retrieval and ranking system selected the following candidates.

Candidate evidence:
{context_json}

IMPORTANT EVIDENCE POLICY:

Each candidate has two evidence sources:

1. retrieved_evidence:
   These are the resume chunks that contributed to semantic retrieval.

2. full_resume_text:
   This is the complete resume text for the candidate and is provided
   as verification evidence.

Use BOTH sources when evaluating the candidate.

The full resume text may contain relevant information that is not
present in the retrieved chunks. Therefore, if a requirement is
explicitly stated anywhere in the full resume text, it may be used
as matching evidence.

However:

- Do NOT infer a skill from related skills.
- Do NOT infer experience from semantic similarity.
- Do NOT infer a qualification that is not explicitly stated.
- Do NOT assume that one technology implies another technology.
- Only treat a requirement as matched when it is explicitly supported
  by the provided candidate evidence.
- If a requested requirement is not explicitly supported anywhere in
  the provided evidence, state "Not specified".
- The ranking scores are metadata and are not proof of a skill.

Evaluation rules:

1. Use ONLY the candidate evidence provided above.
2. Do not invent skills, experience, qualifications, job titles,
   education, or achievements.
3. Do not infer information that is not explicitly stated.
4. If a requested requirement is not supported by the evidence,
   state "Not specified".
5. Clearly identify direct matching evidence.
6. Clearly identify important gaps or missing requirements.
7. Consider seniority only when it is explicitly supported.
8. Do not use contact information.
9. Do not infer or use demographic or protected characteristics.
10. Do not make a hiring decision.
11. Do not recommend hiring or rejecting any candidate.
12. Do not treat semantic similarity alone as proof of a skill.
13. Return ONLY valid JSON.
14. Do not return Markdown or code fences.
15. Keep the evaluation concise and evidence-based.

Return exactly this structure:

{{
  "query": "{recruiter_query}",
  "candidates": [
    {{
      "rank": 1,
      "candidate_id": 0,
      "fit_summary": "Concise evidence-based summary.",
      "matching_evidence": [
        "Direct evidence supporting the query."
      ],
      "gaps": [
        "Missing or unsupported requirement."
      ],
      "bias_check": "Evaluation uses only job-relevant evidence."
    }}
  ]
}}
"""

    def validate_evaluation(
        self,
        evaluation
    ):
        """
        Validate the required structure of Gemini's JSON response.
        """

        if not isinstance(
            evaluation,
            dict
        ):
            raise ValueError(
                "Gemini evaluation must be a JSON object."
            )

        required_top_level_fields = {
            "query",
            "candidates"
        }

        missing_fields = (
            required_top_level_fields
            - evaluation.keys()
        )

        if missing_fields:
            raise ValueError(
                "Missing top-level fields: "
                f"{sorted(missing_fields)}"
            )

        if not isinstance(
            evaluation["candidates"],
            list
        ):
            raise ValueError(
                "The 'candidates' field must be a list."
            )

        required_candidate_fields = {
            "rank",
            "candidate_id",
            "fit_summary",
            "matching_evidence",
            "gaps",
            "bias_check"
        }

        for candidate in evaluation["candidates"]:

            if not isinstance(
                candidate,
                dict
            ):
                raise ValueError(
                    "Each candidate evaluation must be an object."
                )

            missing_fields = (
                required_candidate_fields
                - candidate.keys()
            )

            if missing_fields:
                raise ValueError(
                    "Missing candidate fields: "
                    f"{sorted(missing_fields)}"
                )

        return True

    def parse_and_validate(
        self,
        raw_output
    ):
        """
        Parse Gemini JSON output and validate its structure.
        """

        try:
            evaluation = json.loads(
                raw_output
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Gemini returned invalid JSON: {error}"
            ) from error

        self.validate_evaluation(
            evaluation
        )

        return evaluation

    def create_cache_key(
        self,
        recruiter_query,
        search_results
    ):
        """
        Create a deterministic cache key from the complete
        candidate evidence used by Gemini.
        """

        cache_candidates = []

        for candidate in search_results["candidates"]:

            resume_text = candidate.get(
                "resume_text",
                ""
            )

            resume_hash = hashlib.sha256(
                resume_text.encode("utf-8")
            ).hexdigest()

            retrieved_chunks = [
                {
                    "chunk_id": chunk["chunk_id"],
                    "similarity_score": round(
                        chunk["similarity_score"],
                        6
                    ),
                    "text": chunk["retrieval_text"]
                }
                for chunk in candidate["matched_chunks"]
            ]

            cache_candidates.append({
                "candidate_id":
                    candidate["candidate_id"],
                "final_rank":
                    candidate["final_rank"],
                "semantic_score":
                    round(
                        candidate["similarity_score"],
                        6
                    ),
                "hybrid_score":
                    round(
                        candidate["hybrid_score"],
                        6
                    ),
                "requirement_coverage":
                    round(
                        candidate["requirement_coverage"],
                        6
                    ),
                "matched_requirements":
                    candidate["matched_requirements"],
                "missing_requirements":
                    candidate["missing_requirements"],
                "resume_hash":
                    resume_hash,
                "retrieved_chunks":
                    retrieved_chunks
            })

        cache_payload = {
            "query": recruiter_query,
            "model": self.model_name,
            "candidates": cache_candidates
        }

        serialized_payload = json.dumps(
            cache_payload,
            sort_keys=True,
            ensure_ascii=False
        )

        return hashlib.sha256(
            serialized_payload.encode("utf-8")
        ).hexdigest()

    def get_cache_path(
        self,
        cache_key
    ):
        """
        Return the cache path for a specific evaluation.
        """

        return (
            self.cache_dir
            / f"{cache_key}.json"
        )

    def save_cache(
        self,
        cache_key,
        evaluation
    ):
        """
        Save a validated Gemini evaluation to disk.
        """

        self.validate_evaluation(
            evaluation
        )

        cache_path = self.get_cache_path(
            cache_key
        )

        with open(
            cache_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                evaluation,
                file,
                ensure_ascii=False,
                indent=2
            )

        return cache_path

    def load_cache(
        self,
        cache_key
    ):
        """
        Load a cached Gemini evaluation if available.
        """

        cache_path = self.get_cache_path(
            cache_key
        )

        if not cache_path.exists():
            return None

        with open(
            cache_path,
            "r",
            encoding="utf-8"
        ) as file:
            evaluation = json.load(file)

        self.validate_evaluation(
            evaluation
        )

        return evaluation

    def evaluate(
        self,
        recruiter_query,
        search_results,
        max_chunks_per_candidate=2
    ):
        """
        Evaluate the final candidates using Gemini.

        Cached evaluations are returned without making an API call.
        """

        cache_key = self.create_cache_key(
            recruiter_query,
            search_results
        )

        cached_evaluation = self.load_cache(
            cache_key
        )

        if cached_evaluation is not None:
            return {
                "evaluation": cached_evaluation,
                "source": "cache",
                "cache_key": cache_key
            }

        gemini_context = self.build_context(
            search_results,
            max_chunks_per_candidate
        )

        prompt = self.build_prompt(
            recruiter_query,
            gemini_context
        )

        interaction = self.client.interactions.create(
            model=self.model_name,
            input=prompt
        )

        evaluation = self.parse_and_validate(
            interaction.output_text
        )

        self.save_cache(
            cache_key,
            evaluation
        )

        return {
            "evaluation": evaluation,
            "source": "gemini",
            "cache_key": cache_key
        }