import html
from typing import Any, Dict, List

import streamlit as st

from src.pipeline.search_pipeline import SearchPipeline
from src.presentation.formatter import SearchResultFormatter


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RAG Talent Search",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap'
    );

    :root {
        --ink: #101828;
        --text: #344054;
        --muted: #667085;
        --soft: #98A2B3;
        --line: #E4E7EC;
        --surface: #FFFFFF;
        --page: #F7F8FC;

        --primary: #635BFF;
        --primary-dark: #5148E5;
        --primary-soft: #F0EFFF;

        --success: #12B76A;
        --success-soft: #ECFDF3;

        --warning: #F79009;
        --warning-soft: #FFFAEB;

        --danger: #F04438;
    }

    * {
        font-family:
            "DM Sans",
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 85% 0%,
                rgba(99, 91, 255, 0.07),
                transparent 28%
            ),
            var(--page);

        color: var(--ink);
    }

    .main .block-container {
        max-width: 1320px;
        padding: 28px 42px 64px;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    h1,
    h2,
    h3 {
        font-family: "Space Grotesk", sans-serif !important;
        color: var(--ink) !important;
        letter-spacing: -0.04em;
    }

    p,
    label,
    span,
    div {
        letter-spacing: -0.01em;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background: #101828;
        border-right: 1px solid #1D2939;
    }

    section[data-testid="stSidebar"] * {
        color: #EAECF0 !important;
    }

    .sidebar-brand {
        padding: 8px 0 28px;
    }

    .sidebar-logo {
        width: 44px;
        height: 44px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 14px;

        background:
            linear-gradient(
                135deg,
                #7C74FF,
                #5148E5
            );

        color: white;

        font-size: 21px;
        font-weight: 800;

        box-shadow:
            0 10px 30px rgba(99, 91, 255, 0.28);

        margin-bottom: 14px;
    }

    .sidebar-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: white;
    }

    .sidebar-subtitle {
        color: #98A2B3;
        font-size: 0.76rem;
        margin-top: 4px;
        line-height: 1.5;
    }

    .sidebar-section {
        color: #98A2B3;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 26px 0 10px;
    }

    .sidebar-note {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 14px;

        padding: 14px;

        color: #D0D5DD;
        font-size: 0.75rem;
        line-height: 1.65;
    }


    /* =====================================================
       TOPBAR
       ===================================================== */

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;

        margin-bottom: 26px;
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .topbar-mark {
        width: 42px;
        height: 42px;

        border-radius: 13px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: var(--primary);
        color: white;

        font-size: 21px;

        box-shadow:
            0 10px 24px rgba(99, 91, 255, 0.22);
    }

    .topbar-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.02rem;
        font-weight: 700;
        color: var(--ink);
    }

    .topbar-subtitle {
        color: var(--soft);
        font-size: 0.72rem;
        margin-top: 3px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;

        padding: 8px 12px;

        border: 1px solid var(--line);
        background: white;

        border-radius: 999px;

        color: var(--text);
        font-size: 0.72rem;
        font-weight: 700;
    }

    .status-dot {
        width: 8px;
        height: 8px;

        border-radius: 50%;

        background: var(--success);

        box-shadow:
            0 0 0 4px rgba(18, 183, 106, 0.10);
    }


    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        position: relative;
        overflow: hidden;

        border: 1px solid var(--line);
        border-radius: 26px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.98),
                rgba(248, 247, 255, 0.98)
            ),
            white;

        padding: 42px 46px;

        box-shadow:
            0 18px 55px rgba(16, 24, 40, 0.06);

        margin-bottom: 28px;
    }

    .hero::after {
        content: "";

        position: absolute;

        width: 280px;
        height: 280px;

        border-radius: 50%;

        right: -110px;
        top: -150px;

        background: rgba(99, 91, 255, 0.08);

        pointer-events: none;
    }

    .eyebrow {
        color: var(--primary);

        font-size: 0.7rem;
        font-weight: 800;

        letter-spacing: 0.13em;
        text-transform: uppercase;

        margin-bottom: 12px;
    }

    .hero-title {
        max-width: 760px;

        font-family: "Space Grotesk", sans-serif;

        font-size: clamp(2.1rem, 4vw, 3.65rem);
        line-height: 1.04;

        font-weight: 700;

        letter-spacing: -0.065em;

        color: var(--ink);
    }

    .hero-title span {
        color: var(--primary);
    }

    .hero-copy {
        max-width: 760px;

        color: var(--muted);

        font-size: 0.94rem;
        line-height: 1.8;

        margin-top: 18px;
    }

    .hero-meta {
        display: flex;
        flex-wrap: wrap;

        gap: 9px;

        margin-top: 24px;
    }

    .hero-chip {
        border: 1px solid #E4E1FF;

        background: #F8F7FF;

        color: #5148E5;

        border-radius: 999px;

        padding: 7px 11px;

        font-size: 0.7rem;
        font-weight: 700;
    }


    /* =====================================================
       SEARCH PANEL
       ===================================================== */

    .search-panel {
        background: white;

        border: 1px solid var(--line);
        border-radius: 20px;

        padding: 22px;

        box-shadow:
            0 8px 28px rgba(16, 24, 40, 0.035);

        margin-bottom: 30px;
    }

    .panel-heading {
        font-family: "Space Grotesk", sans-serif;

        font-size: 1rem;
        font-weight: 700;

        color: var(--ink);

        margin-bottom: 4px;
    }

    .panel-description {
        color: var(--muted);

        font-size: 0.78rem;

        margin-bottom: 16px;
    }

    .search-note {
        display: flex;
        align-items: center;

        gap: 8px;

        margin-top: 13px;

        color: var(--soft);

        font-size: 0.68rem;
        line-height: 1.5;
    }

    .search-note-dot {
        width: 6px;
        height: 6px;

        flex-shrink: 0;

        border-radius: 50%;

        background: var(--primary);
    }

    div[data-baseweb="input"] {
        background: #FCFCFD !important;

        border: 1px solid #D0D5DD !important;

        border-radius: 13px !important;

        min-height: 54px;

        box-shadow: none !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: var(--primary) !important;

        box-shadow:
            0 0 0 4px rgba(99, 91, 255, 0.10) !important;
    }

    div[data-baseweb="input"] input {
        color: var(--ink) !important;
        font-size: 0.88rem !important;
    }

    .stButton > button {
        min-height: 54px;

        border-radius: 13px !important;

        font-weight: 700 !important;
        font-size: 0.82rem !important;

        border: 1px solid #D0D5DD !important;

        transition: all 0.18s ease;
    }

    .stButton > button[kind="primary"] {
        background: var(--primary) !important;

        border-color: var(--primary) !important;

        color: white !important;

        box-shadow:
            0 10px 24px rgba(99, 91, 255, 0.20);
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--primary-dark) !important;

        border-color: var(--primary-dark) !important;

        transform: translateY(-1px);
    }

    .stButton > button:hover {
        border-color: #B7B9C8 !important;
    }

    .suggestions {
        color: var(--soft);

        font-size: 0.72rem;

        margin-top: 12px;
    }

    .suggestions strong {
        color: var(--muted);
    }


    /* =====================================================
       SECTION HEADINGS
       ===================================================== */

    .section-kicker {
        color: var(--primary);

        font-size: 0.68rem;
        font-weight: 800;

        letter-spacing: 0.13em;
        text-transform: uppercase;

        margin-bottom: 5px;
    }

    .section-title {
        font-family: "Space Grotesk", sans-serif;

        color: var(--ink);

        font-size: 1.45rem;
        font-weight: 700;

        letter-spacing: -0.04em;
    }

    .section-copy {
        color: var(--muted);

        font-size: 0.78rem;
        line-height: 1.6;

        margin-top: 5px;
    }


    /* =====================================================
       METRICS
       ===================================================== */

    .metric-card {
        background: white;

        border: 1px solid var(--line);
        border-radius: 16px;

        padding: 17px 18px;

        min-height: 102px;

        box-shadow:
            0 5px 18px rgba(16, 24, 40, 0.025);
    }

    .metric-label {
        color: var(--soft);

        font-size: 0.69rem;
        font-weight: 700;
    }

    .metric-value {
        font-family: "Space Grotesk", sans-serif;

        color: var(--ink);

        font-size: 1.65rem;
        font-weight: 700;

        margin-top: 7px;

        letter-spacing: -0.04em;
    }

    .metric-caption {
        color: var(--muted);

        font-size: 0.66rem;

        margin-top: 4px;
    }


    /* =====================================================
       CANDIDATE CARDS
       ===================================================== */

    .candidate-card {
        background: white;

        border: 1px solid var(--line);
        border-radius: 20px;

        padding: 23px;

        margin: 14px 0;

        box-shadow:
            0 8px 25px rgba(16, 24, 40, 0.035);
    }

    .candidate-header {
        display: flex;

        align-items: center;
        justify-content: space-between;

        gap: 18px;
    }

    .candidate-identity {
        display: flex;

        align-items: center;

        gap: 13px;
    }

    .candidate-rank {
        width: 46px;
        height: 46px;

        border-radius: 14px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: var(--primary-soft);

        border: 1px solid #E4E1FF;

        color: var(--primary);

        font-family: "Space Grotesk", sans-serif;

        font-size: 0.9rem;
        font-weight: 700;
    }

    .candidate-label {
        color: var(--soft);

        font-size: 0.63rem;
        font-weight: 800;

        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .candidate-name {
        color: var(--ink);

        font-family: "Space Grotesk", sans-serif;

        font-size: 1.1rem;
        font-weight: 700;

        margin-top: 3px;
    }

    .candidate-id {
        color: var(--muted);

        font-size: 0.7rem;

        margin-top: 3px;
    }

    .score-box {
        text-align: right;

        min-width: 100px;
    }

    .score-label {
        color: var(--soft);

        font-size: 0.62rem;
        font-weight: 800;

        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .score-value {
        color: var(--primary);

        font-family: "Space Grotesk", sans-serif;

        font-size: 1.55rem;
        font-weight: 700;

        letter-spacing: -0.04em;

        margin-top: 2px;
    }

    .card-divider {
        height: 1px;

        background: #F0F2F5;

        margin: 20px 0;
    }

    .mini-heading {
        color: var(--text);

        font-size: 0.68rem;
        font-weight: 800;

        letter-spacing: 0.08em;
        text-transform: uppercase;

        margin-bottom: 9px;
    }

    .tag {
        display: inline-block;

        border-radius: 8px;

        padding: 6px 9px;

        margin: 0 5px 5px 0;

        font-size: 0.69rem;
        font-weight: 700;

        line-height: 1.3;

        white-space: nowrap;
    }

    .tag-match {
        background: #ECFDF3;

        color: #027A48;

        border: 1px solid #ABEFC6;
    }

    .tag-missing {
        background: #F9FAFB;

        color: #667085;

        border: 1px solid #EAECF0;
    }

    .empty-state {
        color: var(--soft);

        font-size: 0.72rem;

        line-height: 1.5;
    }

    .coverage-box {
        margin-top: 17px;

        padding: 12px 14px;

        border-radius: 12px;

        background: #F8F9FC;

        border: 1px solid #EAECF0;
    }

    .coverage-row {
        display: flex;

        justify-content: space-between;
        align-items: center;

        gap: 12px;
    }

    .coverage-label {
        color: var(--muted);

        font-size: 0.7rem;
        font-weight: 700;
    }

    .coverage-value {
        color: var(--ink);

        font-size: 0.75rem;
        font-weight: 800;
    }

    .fit-box {
        background:
            linear-gradient(
                135deg,
                #F8F7FF,
                #FCFCFF
            );

        border: 1px solid #E9E7FF;

        border-radius: 14px;

        padding: 15px 17px;

        margin-top: 18px;
    }

    .fit-heading {
        color: var(--primary);

        font-size: 0.67rem;
        font-weight: 800;

        letter-spacing: 0.08em;
        text-transform: uppercase;

        margin-bottom: 7px;
    }

    .fit-text {
        color: var(--text);

        font-size: 0.8rem;

        line-height: 1.75;
    }

    div[data-testid="stExpander"] {
        background: #FCFCFD !important;

        border: 1px solid #EAECF0 !important;

        border-radius: 12px !important;

        margin-top: 9px;
    }

    div[data-testid="stExpander"] summary {
        color: var(--text) !important;

        font-size: 0.76rem;
        font-weight: 700;
    }


    /* =====================================================
       STATUS / ERROR
       ===================================================== */

    .evaluation-banner {
        display: flex;

        align-items: center;

        gap: 9px;

        padding: 11px 14px;

        border-radius: 12px;

        margin-top: 16px;

        background: #F8F9FC;

        border: 1px solid #EAECF0;

        color: var(--muted);

        font-size: 0.72rem;

        font-weight: 600;
    }

    .evaluation-dot {
        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: var(--success);

        flex-shrink: 0;
    }

    .evaluation-dot.warning {
        background: var(--warning);
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        border-top: 1px solid var(--line);

        margin-top: 45px;

        padding-top: 20px;

        text-align: center;

        color: var(--soft);

        font-size: 0.7rem;

        line-height: 1.8;
    }

    .footer strong {
        color: var(--muted);
    }


    /* =====================================================
       RESPONSIVE
       ===================================================== */

    @media (max-width: 900px) {

        .main .block-container {
            padding: 22px 18px 45px;
        }

        .hero {
            padding: 30px 25px;
        }

        .hero-title {
            font-size: 2.35rem;
        }

        .candidate-card {
            padding: 18px;
        }

        .topbar {
            align-items: flex-start;

            gap: 15px;

            flex-direction: column;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def safe_text(value: Any) -> str:
    if value is None:
        return ""

    return html.escape(
        str(value),
        quote=True
    )


def normalize_items(value: Any) -> List[str]:
    """
    Normalize backend values into a clean list of strings.

    Handles:
    - None
    - strings
    - lists
    - tuples
    - sets
    - unexpected scalar values
    """

    if value is None:
        return []

    if isinstance(value, str):
        value = value.strip()

        return [value] if value else []

    if isinstance(value, (list, tuple, set)):
        items = value

    else:
        value = str(value).strip()

        return [value] if value else []

    normalized = []

    for item in items:

        if item is None:
            continue

        item = str(item).strip()

        if item:
            normalized.append(item)

    return normalized


def render_tags(
    items: Any,
    css_class: str
) -> str:

    valid_items = normalize_items(items)

    return " ".join(
        f'<span class="tag {css_class}">'
        f'{safe_text(item)}'
        f'</span>'
        for item in valid_items
    )


def render_bullet_list(
    items: Any,
    empty_message: str
) -> None:

    normalized = normalize_items(items)

    if normalized:

        for item in normalized:

            st.markdown(
                f"- {safe_text(item)}",
                unsafe_allow_html=True,
            )

    else:

        st.caption(
            empty_message
        )


@st.cache_resource(show_spinner=False)
def load_pipeline() -> SearchPipeline:
    return SearchPipeline()


def execute_search(
    query: str
) -> Dict[str, Any]:

    pipeline = load_pipeline()

    pipeline_result = pipeline.search(
        query,
        top_k_chunks=30,
        top_k_candidates=10,
        final_top_k=5,
    )

    return SearchResultFormatter.format_search_result(
        pipeline_result
    )


def clear_results() -> None:

    st.session_state.pop(
        "search_result",
        None,
    )

    st.session_state.pop(
        "last_query",
        None,
    )

    st.session_state.pop(
        "search_error",
        None,
    )


def render_candidate(
    candidate: Dict[str, Any]
) -> None:

    rank = int(
        candidate.get(
            "rank",
            0
        ) or 0
    )

    candidate_id = safe_text(
        candidate.get(
            "candidate_id",
            "N/A"
        )
    )

    score = float(
        candidate.get(
            "hybrid_score",
            0.0
        ) or 0.0
    )

    requirement_coverage = candidate.get(
        "requirement_coverage"
    )

    matched = normalize_items(
        candidate.get(
            "matched_requirements"
        )
    )

    missing = normalize_items(
        candidate.get(
            "missing_requirements"
        )
    )

    fit_summary = candidate.get(
        "fit_summary"
    )


    # =====================================================
    # CANDIDATE HEADER
    # =====================================================

    st.markdown(
        f"""
        <div class="candidate-card">
            <div class="candidate-header">
                <div class="candidate-identity">
                    <div class="candidate-rank">
                        {rank:02d}
                    </div>
                    <div>
                        <div class="candidate-label">
                            Candidate profile
                        </div>
                        <div class="candidate-name">
                            Candidate {candidate_id}
                        </div>
                        <div class="candidate-id">
                            Profile ID · {candidate_id}
                        </div>
                    </div>
                </div>
                <div class="score-box">
                    <div class="score-label">
                        Hybrid score
                    </div>
                    <div class="score-value">
                        {score:.3f}
                    </div>
                </div>
            </div>
            <div class="card-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # =====================================================
    # REQUIREMENTS
    # =====================================================

    left, right = st.columns(
        2,
        gap="large"
    )

    with left:

        st.markdown(
            """
            <div class="mini-heading">
                Matching requirements
            </div>
            """,
            unsafe_allow_html=True,
        )

        if matched:

            st.markdown(
                render_tags(
                    matched,
                    "tag-match",
                ),
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="empty-state">
                    No specific matching requirements identified.
                </div>
                """,
                unsafe_allow_html=True,
            )


    with right:

        st.markdown(
            """
            <div class="mini-heading">
                Missing requirements
            </div>
            """,
            unsafe_allow_html=True,
        )

        if missing:

            st.markdown(
                render_tags(
                    missing,
                    "tag-missing",
                ),
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="empty-state">
                    No explicit requirement gaps identified.
                </div>
                """,
                unsafe_allow_html=True,
            )


    # =====================================================
    # REQUIREMENT COVERAGE
    # =====================================================

    if requirement_coverage is not None:

        try:

            coverage_value = float(
                requirement_coverage
            )

            if 0 <= coverage_value <= 1:

                coverage_display = (
                    f"{coverage_value:.0%}"
                )

            else:

                coverage_display = str(
                    requirement_coverage
                )

            st.markdown(
                f"""
                <div class="coverage-box">
                    <div class="coverage-row">
                        <div class="coverage-label">
                            Explicit requirement coverage
                        </div>
                        <div class="coverage-value">
                            {safe_text(coverage_display)}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except (
            TypeError,
            ValueError
        ):
            pass


    # =====================================================
    # GEMINI FIT SUMMARY
    # =====================================================

    if fit_summary:

        st.markdown(
            f"""
            <div class="fit-box">
                <div class="fit-heading">
                    AI evidence summary
                </div>
                <div class="fit-text">
                    {safe_text(fit_summary)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # =====================================================
    # SUPPORTING EVIDENCE
    # =====================================================

    evidence_items = normalize_items(
        candidate.get(
            "matching_evidence"
        )
    )

    if evidence_items:

        with st.expander(
            "Supporting evidence"
        ):

            for evidence in evidence_items:

                st.markdown(
                    f"- {safe_text(evidence)}",
                    unsafe_allow_html=True,
                )


    # =====================================================
    # AI-IDENTIFIED GAPS
    # =====================================================

    gap_items = normalize_items(
        candidate.get(
            "gaps"
        )
    )

    if gap_items:

        with st.expander(
            "AI-identified gaps"
        ):

            for gap in gap_items:

                st.markdown(
                    f"- {safe_text(gap)}",
                    unsafe_allow_html=True,
                )


    # =====================================================
    # EVALUATION NOTES
    # =====================================================

    bias_check = candidate.get(
        "bias_check"
    )

    if bias_check:

        with st.expander(
            "Evaluation notes"
        ):

            st.markdown(
                safe_text(
                    bias_check
                )
            )


# =========================================================
# SESSION STATE
# =========================================================

if "selected_query" not in st.session_state:
    st.session_state["selected_query"] = ""

if "search_result" not in st.session_state:
    st.session_state["search_result"] = None

if "last_query" not in st.session_state:
    st.session_state["last_query"] = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">
                Q
            </div>
            <div class="sidebar-title">
                RAG Talent Search
            </div>
            <div class="sidebar-subtitle">
                Semantic talent discovery powered by
                retrieval, ranking, and evidence-grounded AI.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="sidebar-section">
            Search workflow
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="sidebar-note">
            <b>01</b>
            Describe the profile you need.
            <br>
            <b>02</b>
            Retrieve semantically relevant profile chunks.
            <br>
            <b>03</b>
            Rank candidates by relevance.
            <br>
            <b>04</b>
            Review evidence and potential gaps.
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="sidebar-section">
            Suggested queries
        </div>
        """,
        unsafe_allow_html=True,
    )


    sidebar_examples = [
        "Python developer with NLP and SQL",
        "Machine learning engineer with deep learning",
        "Computer vision and OpenCV experience",
        "RAG, LLM, and vector database skills",
    ]


    for index, example in enumerate(
        sidebar_examples
    ):

        if st.button(
            example,
            key=f"side_query_{index}",
            use_container_width=True,
        ):

            st.session_state[
                "selected_query"
            ] = example

            st.rerun()


    st.markdown(
        """
        <div class="sidebar-section">
            System
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="sidebar-note">
            <b>Retrieval:</b>
            Semantic search
            <br>
            <b>Ranking:</b>
            Hybrid relevance ranking
            <br>
            <b>Evaluation:</b>
            Evidence-grounded AI
            <br>
            <b>Purpose:</b>
            Candidate discovery support
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# TOPBAR
# =========================================================

st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            <div class="topbar-mark">
                Q
            </div>
            <div>
                <div class="topbar-title">
                    RAG Talent Search Engine
                </div>
                <div class="topbar-subtitle">
                    Intelligent candidate discovery workspace
                </div>
            </div>
        </div>
        <div class="status-pill">
            <span class="status-dot"></span>
            Search engine ready
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">
            AI-powered talent discovery
        </div>
        <div class="hero-title">
            Discover relevant talent.
            <br>
            <span>
                Start with a simple sentence.
            </span>
        </div>
        <div class="hero-copy">
            Describe the candidate profile you are looking for
            using natural language. The engine searches the talent
            knowledge base, ranks relevant profiles, and presents
            evidence and requirement coverage to support human review.
        </div>
        <div class="hero-meta">
            <span class="hero-chip">
                Semantic retrieval
            </span>
            <span class="hero-chip">
                Hybrid ranking
            </span>
            <span class="hero-chip">
                Evidence-grounded AI
            </span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SEARCH PANEL
# =========================================================

st.markdown(
    """
    <div class="search-panel">
        <div class="panel-heading">
            What kind of candidate are you looking for?
        </div>
        <div class="panel-description">
            Add skills, technologies, experience, or project
            requirements in plain language.
        </div>
    """,
    unsafe_allow_html=True,
)


search_col, button_col, clear_col = st.columns(
    [6.0, 1.35, 1.05],
    gap="small",
)


with search_col:

    query = st.text_input(
        "Candidate search",

        value=st.session_state.get(
            "selected_query",
            "",
        ),

        placeholder=(
            "e.g. Python developer with NLP, RAG, SQL, "
            "and deep learning experience"
        ),

        label_visibility="collapsed",
    )


with button_col:

    search_clicked = st.button(
        "Search",
        type="primary",
        use_container_width=True,
    )


with clear_col:

    clear_clicked = st.button(
        "Clear",
        use_container_width=True,
    )


if clear_clicked:

    clear_results()

    st.session_state[
        "selected_query"
    ] = ""

    st.rerun()


st.markdown(
    """
        <div class="search-note">
            <span class="search-note-dot"></span>
            Results combine semantic retrieval,
            hybrid ranking, and evidence-grounded AI evaluation.
        </div>
        <div class="suggestions">
            <strong>Try:</strong>
            Python + Machine Learning
            &nbsp;·&nbsp;
            NLP + SQL
            &nbsp;·&nbsp;
            Computer Vision
            &nbsp;·&nbsp;
            RAG + LLM
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SEARCH EXECUTION
# =========================================================

if search_clicked:

    if not query.strip():

        st.warning(
            "Enter a few skills, technologies, or requirements "
            "to start searching."
        )

    else:

        clean_query = query.strip()

        st.session_state[
            "selected_query"
        ] = clean_query

        with st.spinner(
            "Searching the talent knowledge base..."
        ):

            try:

                result = execute_search(
                    clean_query
                )

                st.session_state[
                    "search_result"
                ] = result

                st.session_state[
                    "last_query"
                ] = clean_query

                st.session_state.pop(
                    "search_error",
                    None,
                )

            except Exception as exc:

                error_message = str(exc)

                st.session_state[
                    "search_error"
                ] = error_message

                st.error(
                    "The search could not be completed."
                )

                with st.expander(
                    "Technical details"
                ):

                    st.write(
                        error_message
                    )


# =========================================================
# RESULTS
# =========================================================

result = st.session_state.get(
    "search_result"
)


if result:

    last_query = st.session_state.get(
        "last_query",
        query,
    )


    # =====================================================
    # RESULTS HEADER
    # =====================================================

    st.markdown(
        f"""
        <div style="margin-top: 30px;">
            <div class="section-kicker">
                Search results
            </div>
            <div class="section-title">
                Relevant candidate profiles
            </div>
            <div class="section-copy">
                Results for:
                <b>{safe_text(last_query)}</b>
                <br>
                Ranked using semantic relevance,
                explicit requirement coverage, and
                evidence-grounded evaluation.
                <br>
                Use these results as decision-support evidence
                rather than as an automated hiring decision.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # =====================================================
    # METRICS
    # =====================================================

    c1, c2, c3, c4 = st.columns(
        4,
        gap="small",
    )


    metrics = [

        (
            "Candidates found",

            result.get(
                "final_count",
                0,
            ),

            "Final returned profiles",
        ),

        (
            "Retrieved chunks",

            result.get(
                "retrieved_count",
                0,
            ),

            "Relevant knowledge chunks",
        ),

        (
            "Ranked candidates",

            result.get(
                "ranked_count",
                0,
            ),

            "Profiles considered",
        ),

        (
            "Unique profiles",

            result.get(
                "unique_count",
                0,
            ),

            "Distinct candidate IDs",
        ),

    ]


    for col, (
        label,
        value,
        caption
    ) in zip(
        [c1, c2, c3, c4],
        metrics,
    ):

        with col:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        {safe_text(label)}
                    </div>
                    <div class="metric-value">
                        {safe_text(value)}
                    </div>
                    <div class="metric-caption">
                        {safe_text(caption)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


    # =====================================================
    # CANDIDATES
    # =====================================================

    candidates = result.get(
        "candidates",
        []
    ) or []


    if not candidates:

        st.info(
            "No matching candidate profiles were found "
            "for this request."
        )

    else:

        for candidate in candidates:

            render_candidate(
                candidate
            )


    # =====================================================
    # TECHNICAL DETAILS
    # =====================================================

    with st.expander(
        "Technical details"
    ):

        technical_rows = {

            "Retrieved chunks":
                result.get(
                    "retrieved_count",
                    0,
                ),

            "Ranked candidates":
                result.get(
                    "ranked_count",
                    0,
                ),

            "Unique profiles":
                result.get(
                    "unique_count",
                    0,
                ),

            "Final candidates":
                result.get(
                    "final_count",
                    0,
                ),

            "Evaluation source":
                result.get(
                    "gemini_source",
                    "unknown",
                ),

        }


        for key, value in technical_rows.items():

            st.write(
                f"**{key}:** {value}"
            )


    # =====================================================
    # EVALUATION STATUS
    # =====================================================

    source = result.get(
        "gemini_source",
        "unknown",
    )


    if source == "cache":

        evaluation_status = (
            "AI evidence evaluation served from cache"
        )

        status_class = ""


    elif source in {
        "live",
        "gemini",
        "api",
    }:

        evaluation_status = (
            "AI evidence evaluation generated live"
        )

        status_class = ""


    else:

        evaluation_status = (
            "AI evidence evaluation unavailable; "
            "retrieval and ranking results remain available"
        )

        status_class = "warning"


    st.markdown(
        f"""
        <div class="evaluation-banner">
            <span class="evaluation-dot {status_class}">
            </span>
            {safe_text(evaluation_status)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        <strong>
            RAG Talent Search Engine
        </strong>
        <br>
        Semantic Retrieval · Hybrid Ranking ·
        Evidence-Grounded AI
        <br>
        Built as a portfolio-ready intelligent
        talent discovery and decision-support experience.
    </div>
    """,
    unsafe_allow_html=True,
)