import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from groq import Groq


load_dotenv()


CACHE_DIR = Path("artifacts") / "llm_cache"

DEFAULT_MAX_CHUNKS_PER_CANDIDATE = 1
MAX_RESUME_CHARS = 3500
CONTEXT_VERSION = "v2"


class LLMEvaluator:
    """
    Evidence-based LLM evaluator for final talent search candidates.

    Provider strategy:
        1. Groq - Primary
        2. Gemini - Automatic fallback

    The evaluator:
    - Uses the strongest retrieved chunk as retrieval evidence.
    - Uses a bounded portion of the resume as verification evidence.
    - Generates a structured evidence-constrained prompt.
    - Attempts Groq first.
    - Falls back to Gemini if Groq fails.
    - Validates the returned JSON.
    - Stores validated evaluations in a local cache.

    Context controls:
        - One retrieved chunk per candidate.
        - Maximum 3500 resume characters per candidate.
    """

    def __init__(
        self,
        groq_model="openai/gpt-oss-120b",
        gemini_model="gemini-3.6-flash",
        cache_dir=CACHE_DIR
    ):
        self.groq_model = groq_model
        self.gemini_model = gemini_model
        self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        groq_api_key = os.getenv("GROQ_API_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.groq_client = None
        self.gemini_client = None

        if groq_api_key:
            self.groq_client = Groq(
                api_key=groq_api_key
            )

        if gemini_api_key:
            self.gemini_client = genai.Client(
                api_key=gemini_api_key
            )

        if not self.groq_client and not self.gemini_client:
            raise EnvironmentError(
                "Neither GROQ_API_KEY nor GEMINI_API_KEY "
                "environment variable is set."
            )

    def build_context(
        self,
        search_results,
        max_chunks_per_candidate=DEFAULT_MAX_CHUNKS_PER_CANDIDATE
    ):
        """
        Build evidence context for the LLM evaluator.
        """

        if max_chunks_per_candidate < 1:
            raise ValueError(
                "max_chunks_per_candidate must be at least 1."
            )

        llm_context = []

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

            resume_text = candidate.get(
                "resume_text",
                ""
            )

            bounded_resume_text = resume_text[
                :MAX_RESUME_CHARS
            ]

            llm_context.append({
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
                "retrieved_evidence":
                    evidence_chunks,
                "full_resume_text":
                    bounded_resume_text
            })

        return llm_context

    def build_prompt(
        self,
        recruiter_query,
        llm_context
    ):
        """
        Build the evidence-constrained evaluation prompt.
        """

        context_json = json.dumps(
            llm_context,
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
   This is the strongest resume chunk selected by the retrieval system.

2. full_resume_text:
   This is a bounded portion of the candidate resume provided
   as verification evidence.

Use BOTH sources when evaluating the candidate.

The resume text may contain relevant information that is not
present in the retrieved evidence. Therefore, if a requirement
is explicitly stated in the provided resume evidence, it may
be used as matching evidence.

However:

- Do NOT infer a skill from related skills.
- Do NOT infer experience from semantic similarity.
- Do NOT infer a qualification that is not explicitly stated.
- Do NOT assume that one technology implies another technology.
- Only treat a requirement as matched when it is explicitly
  supported by the provided candidate evidence.
- If a requested requirement is not explicitly supported
  anywhere in the provided evidence, state "Not specified".
- Ranking scores are metadata and are not proof of a skill.

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
        Validate the required structure of the LLM JSON response.
        """

        if not isinstance(
            evaluation,
            dict
        ):
            raise ValueError(
                "LLM evaluation must be a JSON object."
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
        Parse LLM JSON output and validate its structure.
        """

        try:
            evaluation = json.loads(
                raw_output
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                f"LLM returned invalid JSON: {error}"
            ) from error

        self.validate_evaluation(
            evaluation
        )

        return evaluation

    def create_cache_key(
        self,
        recruiter_query,
        search_results,
        max_chunks_per_candidate=DEFAULT_MAX_CHUNKS_PER_CANDIDATE
    ):
        """
        Create a deterministic cache key from the evidence
        configuration and candidate data used by the evaluator.
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
            "context_version":
                CONTEXT_VERSION,

            "max_chunks_per_candidate":
                max_chunks_per_candidate,

            "max_resume_chars":
                MAX_RESUME_CHARS,

            "query":
                recruiter_query,

            "groq_model":
                self.groq_model,

            "gemini_model":
                self.gemini_model,

            "candidates":
                cache_candidates
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
        evaluation,
        source
    ):
        """
        Save a validated LLM evaluation and its provider source.
        """

        self.validate_evaluation(
            evaluation
        )

        if source not in {
            "groq",
            "gemini"
        }:
            raise ValueError(
                "Cache source must be 'groq' or 'gemini'."
            )

        cache_payload = {
            "evaluation": evaluation,
            "source": source
        }

        cache_path = self.get_cache_path(
            cache_key
        )

        with open(
            cache_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                cache_payload,
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
        Load a cached LLM evaluation if available.

        Supports:
        1. New cache format with provider metadata.
        2. Legacy cache format containing only the evaluation.
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
            cached_data = json.load(
                file
            )

        if (
            isinstance(cached_data, dict)
            and "evaluation" in cached_data
            and "source" in cached_data
        ):
            evaluation = cached_data["evaluation"]
            source = cached_data["source"]

            self.validate_evaluation(
                evaluation
            )

            return {
                "evaluation": evaluation,
                "source": source
            }

        self.validate_evaluation(
            cached_data
        )

        return {
            "evaluation": cached_data,
            "source": None
        }

    def evaluate_with_groq(
        self,
        prompt
    ):
        """
        Run evaluation using Groq as the primary provider.
        """

        if self.groq_client is None:
            raise EnvironmentError(
                "GROQ_API_KEY is not configured."
            )

        response = (
            self.groq_client
            .chat
            .completions
            .create(
                model=self.groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an evidence-based AI "
                            "recruitment evaluation assistant."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                response_format={
                    "type": "json_object"
                }
            )
        )

        raw_output = (
            response
            .choices[0]
            .message
            .content
        )

        return self.parse_and_validate(
            raw_output
        )

    def evaluate_with_gemini(
        self,
        prompt
    ):
        """
        Run evaluation using Gemini as the fallback provider.
        """

        if self.gemini_client is None:
            raise EnvironmentError(
                "GEMINI_API_KEY is not configured."
            )

        interaction = (
            self.gemini_client
            .interactions
            .create(
                model=self.gemini_model,
                input=prompt
            )
        )

        return self.parse_and_validate(
            interaction.output_text
        )

    def evaluate(
        self,
        recruiter_query,
        search_results,
        max_chunks_per_candidate=DEFAULT_MAX_CHUNKS_PER_CANDIDATE
    ):
        """
        Evaluate the final candidates.

        Provider order:
            1. Cache
            2. Groq
            3. Gemini fallback
        """

        if max_chunks_per_candidate < 1:
            raise ValueError(
                "max_chunks_per_candidate must be at least 1."
            )

        cache_key = self.create_cache_key(
            recruiter_query,
            search_results,
            max_chunks_per_candidate
        )

        cached_result = self.load_cache(
            cache_key
        )

        if cached_result is not None:
            return {
                "evaluation":
                    cached_result["evaluation"],

                "source":
                    "cache",

                "cached_source":
                    cached_result["source"],

                "cache_key":
                    cache_key
            }

        llm_context = self.build_context(
            search_results,
            max_chunks_per_candidate
        )

        prompt = self.build_prompt(
            recruiter_query,
            llm_context
        )

        groq_error = None

        try:
            evaluation = self.evaluate_with_groq(
                prompt
            )

            self.save_cache(
                cache_key,
                evaluation,
                source="groq"
            )

            return {
                "evaluation":
                    evaluation,

                "source":
                    "groq",

                "cache_key":
                    cache_key
            }

        except Exception as exc:
            groq_error = str(exc)

        try:
            evaluation = self.evaluate_with_gemini(
                prompt
            )

            self.save_cache(
                cache_key,
                evaluation,
                source="gemini"
            )

            return {
                "evaluation":
                    evaluation,

                "source":
                    "gemini",

                "cache_key":
                    cache_key,

                "groq_error":
                    groq_error
            }

        except Exception as gemini_exc:
            raise RuntimeError(
                "Both LLM providers failed. "
                f"Groq error: {groq_error} | "
                f"Gemini error: {gemini_exc}"
            ) from gemini_exc