import re


# Controlled technical vocabulary used to detect
# explicit requirements from recruiter queries.
TECHNICAL_REQUIREMENTS = [
    # AI / ML
    "natural language processing",
    "machine learning",
    "deep learning",
    "computer vision",
    "generative ai",
    "large language model",
    "large language models",
    "llm",
    "rag",
    "retrieval augmented generation",
    "retrieval-augmented generation",
    "embeddings",
    "embedding",
    "vector database",
    "vector databases",
    "vector search",
    "faiss",
    "transformers",
    "bert",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "langchain",
    "langgraph",

    # Data
    "business intelligence",
    "data analytics",
    "data analysis",
    "data science",
    "big data",
    "pandas",
    "numpy",
    "spark",
    "hadoop",
    "hive",
    "etl",
    "ssis",
    "ssas",
    "sql",
    "sql server",
    "mysql",
    "oracle",
    "pl/sql",
    "mongodb",
    "redis",
    "power bi",
    "tableau",
    "excel",

    # Software / Backend
    "python",
    "java",
    "c++",
    "c#",
    "c",
    "django",
    "flask",
    "fastapi",

    # Cloud / DevOps
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "jenkins",
    "git",
]


# Common aliases used when checking whether a requirement
# is explicitly present in a resume.
REQUIREMENT_ALIASES = {
    "nlp": [
        "nlp",
        "natural language processing",
    ],
    "natural language processing": [
        "natural language processing",
        "nlp",
    ],
    "machine learning": [
        "machine learning",
        "machine-learning",
    ],
    "deep learning": [
        "deep learning",
        "deep-learning",
    ],
    "computer vision": [
        "computer vision",
        "computer-vision",
    ],
    "power bi": [
        "power bi",
        "powerbi",
    ],
    "scikit-learn": [
        "scikit-learn",
        "sklearn",
    ],
    "sql server": [
        "sql server",
        "microsoft sql server",
    ],
    "pl/sql": [
        "pl/sql",
        "plsql",
    ],
    "rag": [
        "rag",
    ],
    "retrieval augmented generation": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
    ],
    "retrieval-augmented generation": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
    ],
    "llm": [
        "llm",
        "large language model",
        "large language models",
    ],
    "large language model": [
        "large language model",
        "large language models",
        "llm",
    ],
    "large language models": [
        "large language model",
        "large language models",
        "llm",
    ],
    "embedding": [
        "embedding",
        "embeddings",
    ],
    "embeddings": [
        "embedding",
        "embeddings",
    ],
    "vector database": [
        "vector database",
        "vector databases",
    ],
    "vector databases": [
        "vector database",
        "vector databases",
    ],
    "vector search": [
        "vector search",
    ],
    "faiss": [
        "faiss",
    ],
    "langchain": [
        "langchain",
    ],
    "langgraph": [
        "langgraph",
    ],
}


SEMANTIC_WEIGHT = 0.70
REQUIREMENT_WEIGHT = 0.30


def clean_text_for_matching(text):
    """
    Normalize whitespace and lowercase text
    for requirement matching.
    """

    return re.sub(
        r"\s+",
        " ",
        str(text).lower()
    ).strip()


def extract_requirements(query):
    """
    Extract explicit technical requirements
    from a recruiter query.
    """

    query_normalized = clean_text_for_matching(
        query
    )

    detected_requirements = []

    for requirement in TECHNICAL_REQUIREMENTS:
        escaped_requirement = re.escape(
            requirement
        )

        pattern = (
            rf"(?<![a-z0-9+#])"
            rf"{escaped_requirement}"
            rf"(?![a-z0-9+#])"
        )

        if re.search(
            pattern,
            query_normalized
        ):
            detected_requirements.append(
                requirement
            )

    return detected_requirements


def requirement_in_text(
    requirement,
    text
):
    """
    Check whether a requirement or one of its
    known aliases is explicitly present in
    the resume text.
    """

    text_normalized = clean_text_for_matching(
        text
    )

    aliases = REQUIREMENT_ALIASES.get(
        requirement,
        [requirement]
    )

    for alias in aliases:
        escaped_alias = re.escape(alias)

        pattern = (
            rf"(?<![a-z0-9+#])"
            rf"{escaped_alias}"
            rf"(?![a-z0-9+#])"
        )

        if re.search(
            pattern,
            text_normalized
        ):
            return True

    return False


def match_candidate_requirements(
    candidate,
    requirements
):
    """
    Match explicit recruiter requirements
    against a candidate resume.
    """

    resume_text = candidate["resume_text"]

    matched_requirements = []
    missing_requirements = []

    for requirement in requirements:

        if requirement_in_text(
            requirement,
            resume_text
        ):
            matched_requirements.append(
                requirement
            )
        else:
            missing_requirements.append(
                requirement
            )

    total_requirements = len(
        requirements
    )

    if total_requirements > 0:
        coverage = (
            len(matched_requirements)
            / total_requirements
        )
    else:
        coverage = 0.0

    return {
        "matched_requirements": (
            matched_requirements
        ),
        "missing_requirements": (
            missing_requirements
        ),
        "requirement_coverage": coverage,
    }


def calculate_hybrid_score(
    semantic_score,
    requirement_coverage
):
    """
    Combine semantic similarity and explicit
    requirement coverage.

    70% semantic relevance
    30% explicit requirement coverage.
    """

    return (
        SEMANTIC_WEIGHT * semantic_score
        + REQUIREMENT_WEIGHT * requirement_coverage
    )


def rerank_candidates(
    candidate_results,
    query
):
    """
    Rerank retrieved candidates using
    hybrid scoring.
    """

    requirements = extract_requirements(
        query
    )

    reranked_candidates = []

    for candidate in candidate_results:

        requirement_result = (
            match_candidate_requirements(
                candidate,
                requirements
            )
        )

        semantic_score = candidate[
            "similarity_score"
        ]

        requirement_coverage = (
            requirement_result[
                "requirement_coverage"
            ]
        )

        hybrid_score = calculate_hybrid_score(
            semantic_score,
            requirement_coverage
        )

        reranked_candidate = candidate.copy()

        reranked_candidate.update({
            "matched_requirements": (
                requirement_result[
                    "matched_requirements"
                ]
            ),
            "missing_requirements": (
                requirement_result[
                    "missing_requirements"
                ]
            ),
            "requirement_coverage": (
                requirement_coverage
            ),
            "hybrid_score": hybrid_score,
        })

        reranked_candidates.append(
            reranked_candidate
        )

    reranked_candidates.sort(
        key=lambda item: item[
            "hybrid_score"
        ],
        reverse=True
    )

    return reranked_candidates