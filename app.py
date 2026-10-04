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
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --ink: #14213D;
        --text: #475467;
        --muted: #667085;
        --soft: #98A2B3;
        --line: #E7EAF0;
        --surface: #FFFFFF;
        --page: #F7F9FC;
        --primary: #4F46E5;
        --primary-dark: #4338CA;
        --primary-soft: #EEF2FF;
        --success: #12B76A;
        --success-soft: #ECFDF3;
        --warning: #F79009;
        --danger: #D92D20;
    }

    * {
        font-family: "DM Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 88% 0%, rgba(91,91,247,.08), transparent 25%),
            linear-gradient(180deg, #FBFCFF 0%, var(--page) 100%);
        color: var(--ink);
    }

    .main .block-container {
        max-width: 1440px;
        padding: 20px 38px 52px;
    }

    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }

    h1, h2, h3 {
        font-family: "Space Grotesk", sans-serif !important;
        color: var(--ink) !important;
        letter-spacing: -0.045em;
    }

    /* ---------------- Sidebar ---------------- */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1F2937;
    }

    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    .sidebar-brand {
        padding: 4px 0 30px;
    }

    .sidebar-logo {
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        background: linear-gradient(135deg, #7777FF, #4F46E5);
        color: #fff;
        font-size: 21px;
        font-weight: 800;
        box-shadow: 0 12px 30px rgba(91,91,247,.28);
        margin-bottom: 14px;
    }

    .sidebar-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.08rem;
        font-weight: 700;
    }

    .sidebar-subtitle {
        color: #98A2B3 !important;
        font-size: .74rem;
        line-height: 1.55;
        margin-top: 5px;
    }

    .sidebar-section {
        color: #98A2B3 !important;
        font-size: .65rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin: 24px 0 9px;
    }

    .sidebar-nav {
        padding: 10px 12px;
        border-radius: 11px;
        color: #E5E7EB !important;
        font-size: .78rem;
        margin-bottom: 6px;
    }

    .sidebar-nav.active {
        background: rgba(91,91,247,.18);
        color: #C7C7FF !important;
    }

    .sidebar-note {
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 14px;
        padding: 13px 14px;
        color: #D0D5DD !important;
        font-size: .72rem;
        line-height: 1.65;
    }

    .sidebar-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        color: #D0D5DD !important;
        font-size: .73rem;
    }

    .sidebar-status span {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #12B76A;
        box-shadow: 0 0 0 4px rgba(18,183,106,.10);
    }

    /* ---------------- Topbar ---------------- */

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 26px;
    }

    .brand-row {
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
        background: #5B5BF7;
        color: white;
        font-size: 20px;
        font-weight: 800;
        box-shadow: 0 10px 24px rgba(91,91,247,.22);
    }

    .topbar-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: var(--ink);
    }

    .topbar-subtitle {
        color: var(--soft);
        font-size: .69rem;
        margin-top: 2px;
    }

    .topbar-right {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border: 1px solid #DCEFE5;
        background: #F5FFFA;
        border-radius: 999px;
        color: #067647;
        font-size: .69rem;
        font-weight: 700;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--success);
    }

    .tech-pill {
        color: #667085;
        font-size: .68rem;
        padding-left: 3px;
    }

    /* ---------------- Hero ---------------- */

    .hero-shell {
        display: grid;
        grid-template-columns: minmax(0, 1.55fr) minmax(300px, .75fr);
        gap: 18px;
        margin-bottom: 20px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 24px;
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F8FF 100%);
        padding: 30px 34px;
        min-height: 225px;
        box-shadow: 0 16px 45px rgba(16,24,40,.045);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 270px;
        height: 270px;
        border-radius: 50%;
        right: -120px;
        top: -150px;
        background: rgba(91,91,247,.08);
        pointer-events: none;
    }

    .eyebrow {
        display: inline-flex;
        padding: 6px 10px;
        border-radius: 999px;
        background: #F0F0FF;
        color: #5148E5;
        font-size: .63rem;
        font-weight: 800;
        letter-spacing: .11em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }

    .hero-title {
        max-width: 700px;
        font-family: "Space Grotesk", sans-serif;
        font-size: clamp(2rem, 3.4vw, 3.05rem);
        line-height: 1.02;
        font-weight: 700;
        letter-spacing: -.065em;
        color: var(--ink);
    }

    .hero-title span { color: var(--primary); }

    .hero-copy {
        max-width: 700px;
        color: var(--muted);
        font-size: .88rem;
        line-height: 1.75;
        margin-top: 15px;
    }

    .hero-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 19px;
    }

    .hero-chip {
        border: 1px solid #E1E2FF;
        background: #FAFAFF;
        color: #5148E5;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: .65rem;
        font-weight: 700;
    }

    .hero-side {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: white;
        padding: 22px;
        box-shadow: 0 16px 45px rgba(16,24,40,.035);
    }

    .hero-side-title {
        color: var(--soft);
        font-size: .65rem;
        font-weight: 800;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }

    .hero-stat {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #F0F2F5;
    }

    .hero-stat:last-child { border-bottom: 0; }

    .hero-stat-label { color: var(--muted); font-size: .73rem; }
    .hero-stat-value {
        font-family: "Space Grotesk", sans-serif;
        color: var(--ink);
        font-weight: 700;
        font-size: .85rem;
    }

    /* ---------------- Search ---------------- */

    .search-panel {
        background: white;
        border: 1px solid var(--line);
        border-radius: 19px;
        padding: 20px;
        box-shadow: 0 8px 28px rgba(16,24,40,.03);
        margin-bottom: 24px;
    }

    .panel-heading {
        font-family: "Space Grotesk", sans-serif;
        font-size: .98rem;
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 3px;
    }

    .panel-description {
        color: var(--muted);
        font-size: .75rem;
        margin-bottom: 14px;
    }

    div[data-baseweb="input"] {
        background: #FCFCFD !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 12px !important;
        min-height: 54px;
        box-shadow: none !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(91,91,247,.09) !important;
    }

    div[data-baseweb="input"] input {
        color: var(--ink) !important;
        font-size: .86rem !important;
    }

    .stButton > button {
        min-height: 54px;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: .79rem !important;
        border: 1px solid #D0D5DD !important;
        transition: all .18s ease;
    }

    .stButton > button[kind="primary"] {
        background: var(--primary) !important;
        border-color: var(--primary) !important;
        color: white !important;
        box-shadow: 0 9px 22px rgba(91,91,247,.18);
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--primary-dark) !important;
        border-color: var(--primary-dark) !important;
        transform: translateY(-1px);
    }

    .suggestion-row {
        display: flex;
        gap: 7px;
        flex-wrap: wrap;
        margin-top: 12px;
    }

    .suggestion-chip {
        border: 1px solid #E4E7EC;
        background: #FAFBFC;
        color: #667085;
        border-radius: 999px;
        padding: 6px 9px;
        font-size: .64rem;
    }

    /* ---------------- Metrics ---------------- */

    .metric-card {
        background: white;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 16px 17px;
        min-height: 98px;
        box-shadow: 0 5px 18px rgba(16,24,40,.025);
    }

    .metric-label {
        color: var(--soft);
        font-size: .66rem;
        font-weight: 700;
    }

    .metric-value {
        font-family: "Space Grotesk", sans-serif;
        color: var(--ink);
        font-size: 1.55rem;
        font-weight: 700;
        margin-top: 6px;
        letter-spacing: -.04em;
    }

    .metric-caption {
        color: var(--muted);
        font-size: .63rem;
        margin-top: 3px;
    }

    /* ---------------- Results ---------------- */

    .results-head {
        display: flex;
        justify-content: space-between;
        align-items: end;
        margin: 28px 0 12px;
    }

    .section-kicker {
        color: var(--primary);
        font-size: .64rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .section-title {
        font-family: "Space Grotesk", sans-serif;
        color: var(--ink);
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: -.04em;
    }

    .section-copy {
        color: var(--muted);
        font-size: .74rem;
        line-height: 1.6;
        margin-top: 4px;
    }

    .candidate-card {
        background: white;
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 20px;
        margin: 13px 0;
        box-shadow: 0 7px 24px rgba(16,24,40,.028);
    }

    .candidate-top {
        display: grid;
        grid-template-columns: 1.25fr .7fr 1.15fr;
        gap: 20px;
        align-items: center;
    }

    .candidate-identity {
        display: flex;
        align-items: center;
        gap: 13px;
    }

    .candidate-rank {
        width: 43px;
        height: 43px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--primary-soft);
        border: 1px solid #E4E1FF;
        color: var(--primary);
        font-family: "Space Grotesk", sans-serif;
        font-size: .82rem;
        font-weight: 700;
    }

    .candidate-label {
        color: var(--soft);
        font-size: .59rem;
        font-weight: 800;
        letter-spacing: .1em;
        text-transform: uppercase;
    }

    .candidate-name {
        color: var(--ink);
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.03rem;
        font-weight: 700;
        margin-top: 3px;
    }

    .candidate-id {
        color: var(--muted);
        font-size: .67rem;
        margin-top: 2px;
    }

    .score-center {
        text-align: center;
        border-left: 1px solid #F0F2F5;
        border-right: 1px solid #F0F2F5;
        padding: 4px 15px;
    }

    .score-label {
        color: var(--soft);
        font-size: .59rem;
        font-weight: 800;
        letter-spacing: .09em;
        text-transform: uppercase;
    }

    .score-value {
        color: var(--primary);
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.55rem;
        font-weight: 700;
        letter-spacing: -.04em;
        margin-top: 1px;
    }

    .score-sub {
        color: var(--muted);
        font-size: .62rem;
    }

    .score-progress {
        height: 6px;
        width: 100%;
        margin-top: 8px;
        border-radius: 999px;
        background: #EAECF0;
        overflow: hidden;
    }

    .score-progress-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #6366F1, #4F46E5);
    }

    .score-percent {
        color: var(--muted);
        font-size: .61rem;
        margin-top: 4px;
    }

    .mini-heading {
        color: var(--text);
        font-size: .63rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .tag {
        display: inline-block;
        border-radius: 8px;
        padding: 5px 8px;
        margin: 0 4px 4px 0;
        font-size: .64rem;
        font-weight: 700;
        line-height: 1.3;
        white-space: nowrap;
    }

    .tag-match {
        background: #F0FDF4;
        color: #027A48;
        border: 1px solid #ABEFC6;
    }

    .tag-missing {
        background: #F8FAFC;
        color: #667085;
        border: 1px solid #EAECF0;
    }

    .card-divider {
        height: 1px;
        background: #F0F2F5;
        margin: 17px 0;
    }

    .coverage-box {
        margin-top: 13px;
        padding: 10px 12px;
        border-radius: 11px;
        background: #F8F9FC;
        border: 1px solid #EAECF0;
    }

    .coverage-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .coverage-label { color: var(--muted); font-size: .65rem; font-weight: 700; }
    .coverage-value { color: var(--ink); font-size: .7rem; font-weight: 800; }

    .coverage-track {
        height: 6px;
        margin-top: 8px;
        border-radius: 999px;
        background: #EAECF0;
        overflow: hidden;
    }

    .coverage-fill {
        height: 100%;
        border-radius: 999px;
        background: #12B76A;
    }

    .fit-box {
        background: linear-gradient(135deg, #F8F7FF, #FCFCFF);
        border: 1px solid #E9E7FF;
        border-radius: 13px;
        padding: 13px 15px;
        margin-top: 14px;
    }

    .fit-heading {
        color: var(--primary);
        font-size: .63rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .fit-text {
        color: var(--text);
        font-size: .75rem;
        line-height: 1.7;
    }

    div[data-testid="stExpander"] {
        background: #FCFCFD !important;
        border: 1px solid #EAECF0 !important;
        border-radius: 11px !important;
        margin-top: 8px;
    }

    div[data-testid="stExpander"] summary {
        color: var(--text) !important;
        font-size: .73rem;
        font-weight: 700;
    }

    .evaluation-banner {
        display: flex;
        align-items: center;
        gap: 9px;
        padding: 10px 13px;
        border-radius: 11px;
        margin-top: 16px;
        background: #F8F9FC;
        border: 1px solid #EAECF0;
        color: var(--muted);
        font-size: .69rem;
        font-weight: 600;
    }

    .evaluation-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--success);
        flex-shrink: 0;
    }

    .evaluation-dot.warning { background: var(--warning); }

    .empty-state {
        border: 1px dashed #D0D5DD;
        border-radius: 17px;
        background: rgba(255,255,255,.7);
        padding: 42px 20px;
        text-align: center;
        color: var(--muted);
        font-size: .78rem;
    }

    .footer {
        border-top: 1px solid var(--line);
        margin-top: 42px;
        padding-top: 18px;
        text-align: center;
        color: var(--soft);
        font-size: .67rem;
        line-height: 1.8;
    }

    .footer strong { color: var(--muted); }

    @media (max-width: 950px) {
        .main .block-container { padding: 20px 18px 45px; }
        .hero-shell { grid-template-columns: 1fr; }
        .candidate-top { grid-template-columns: 1fr; }
        .score-center {
            border-left: 0;
            border-right: 0;
            border-top: 1px solid #F0F2F5;
            border-bottom: 1px solid #F0F2F5;
            padding: 12px 0;
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
    """Render one candidate using the portfolio-oriented card UI."""

    rank = int(candidate.get("rank", 0) or 0)

    candidate_id = safe_text(
        candidate.get("candidate_id", "N/A")
    )

    score = float(
        candidate.get("hybrid_score", 0.0) or 0.0
    )

    # Scores are stored as normalized values in [0, 1].
    score_percent = max(0.0, min(score, 1.0)) * 100.0

    requirement_coverage = candidate.get(
        "requirement_coverage"
    )

    matched = normalize_items(
        candidate.get("matched_requirements")
    )

    missing = normalize_items(
        candidate.get("missing_requirements")
    )

    fit_summary = candidate.get("fit_summary")

    evidence_items = normalize_items(
        candidate.get("matching_evidence")
    )

    gap_items = normalize_items(
        candidate.get("gaps")
    )

    bias_check = candidate.get("bias_check")

    # Candidate overview
    st.markdown(
        f"""
        <div class="candidate-card">
            <div class="candidate-top">
                <div class="candidate-identity">
                    <div class="candidate-rank">{rank:02d}</div>
                    <div>
                        <div class="candidate-label">Ranked candidate</div>
                        <div class="candidate-name">
                            Candidate {candidate_id}
                        </div>
                        <div class="candidate-id">
                            Candidate ID · {candidate_id}
                        </div>
                    </div>
                </div>
                <div class="score-center">
                    <div class="score-label">Hybrid match</div>
                    <div class="score-value">{score_percent:.1f}%</div>
                    <div class="score-progress">
                        <div class="score-progress-fill" style="width:{score_percent:.1f}%"></div>
                    </div>
                    <div class="score-percent">semantic relevance + requirement fit</div>
                </div>
                <div>
                    <div class="mini-heading">Requirement fit</div>
                    {
                        render_tags(
                            matched[:6],
                            "tag-match",
                        )
                        if matched
                        else '<span class="empty-state" style="display:block;padding:8px;">No explicit matches identified.</span>'
                    }
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Requirement coverage + missing requirements
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown(
            '<div class="mini-heading">Matching requirements</div>',
            unsafe_allow_html=True,
        )

        if matched:
            st.markdown(
                render_tags(matched, "tag-match"),
                unsafe_allow_html=True,
            )
        else:
            st.caption("No specific matching requirements identified.")

    with right:
        st.markdown(
            '<div class="mini-heading">Potential gaps</div>',
            unsafe_allow_html=True,
        )

        if missing:
            st.markdown(
                render_tags(missing, "tag-missing"),
                unsafe_allow_html=True,
            )
        else:
            st.caption("No explicit requirement gaps identified.")

    if requirement_coverage is not None:
        try:
            coverage_value = float(requirement_coverage)

            if 0 <= coverage_value <= 1:
                coverage_display = f"{coverage_value:.0%}"
            else:
                coverage_display = str(requirement_coverage)

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
                    <div class="coverage-track">
                        <div class="coverage-fill" style="width:{coverage_value * 100:.1f}%"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except (TypeError, ValueError):
            pass

    # Gemini fit summary
    if fit_summary:
        st.markdown(
            f"""
            <div class="fit-box">
                <div class="fit-heading">AI evidence summary</div>
                <div class="fit-text">
                    {safe_text(fit_summary)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Supporting evidence
    if evidence_items:
        with st.expander("Supporting evidence"):
            for evidence in evidence_items:
                st.markdown(
                    f"- {safe_text(evidence)}",
                    unsafe_allow_html=True,
                )

    # AI-identified gaps
    if gap_items:
        with st.expander("AI-identified gaps"):
            for gap in gap_items:
                st.markdown(
                    f"- {safe_text(gap)}",
                    unsafe_allow_html=True,
                )

    # Evaluation notes
    if bias_check:
        with st.expander("Evaluation notes"):
            st.markdown(
                safe_text(bias_check)
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
            <div class="sidebar-logo">◈</div>
            <div class="sidebar-title">RAG Talent Search</div>
            <div class="sidebar-subtitle">
                AI-powered candidate discovery using semantic retrieval,
                hybrid ranking, and evidence-grounded evaluation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">Workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-nav active">⌂ &nbsp; Talent Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-nav">⌕ &nbsp; Candidate Discovery</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Suggested searches</div>', unsafe_allow_html=True)

    sidebar_examples = [
        "Python developer with NLP and SQL",
        "Machine learning engineer with deep learning",
        "Computer vision and OpenCV experience",
        "RAG, LLM, and vector database skills",
    ]

    for index, example in enumerate(sidebar_examples):
        if st.button(
            example,
            key=f"side_query_{index}",
            use_container_width=True,
        ):
            st.session_state["selected_query"] = example
            st.rerun()

    st.markdown('<div class="sidebar-section">System status</div>', unsafe_allow_html=True)

    for label in ["RAG Pipeline", "Hybrid Ranking", "Gemini Evaluation"]:
        st.markdown(
            f'<div class="sidebar-status"><span></span>{label}<small style="margin-left:auto;color:#98A2B3!important;">Ready</small></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="height:10px;"></div>
        <div class="sidebar-note">
            <b>Decision support only</b><br>
            Results provide retrieval and evidence to support human review.
            They are not an automated hiring decision.
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
        <div class="brand-row">
            <div class="topbar-mark">◈</div>
            <div>
                <div class="topbar-title">RAG Talent Search</div>
                <div class="topbar-subtitle">Intelligent candidate discovery workspace</div>
            </div>
        </div>
        <div class="topbar-right">
            <div class="tech-pill">RAG + Hybrid Ranking + Gemini</div>
            <div class="status-pill">
                <span class="status-dot"></span>
                System ready
            </div>
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
    <div class="hero-shell">
        <section class="hero">
            <div class="eyebrow">AI-powered recruitment</div>
            <div class="hero-title">
                Find the right talent, <span>faster.</span>
            </div>
            <div class="hero-copy">
                Describe the candidate you need in natural language. The engine retrieves
                relevant profiles, ranks them with a hybrid score, and explains the result
                with evidence so recruiters stay in control.
            </div>
            <div class="hero-meta">
                <span class="hero-chip">Semantic retrieval</span>
                <span class="hero-chip">Hybrid ranking</span>
                <span class="hero-chip">Evidence-grounded AI</span>
            </div>
        </section>
        <aside class="hero-side">
            <div class="hero-side-title">How the engine works</div>
            <div class="hero-stat">
                <span class="hero-stat-label">01 · Retrieve</span>
                <span class="hero-stat-value">Semantic</span>
            </div>
            <div class="hero-stat">
                <span class="hero-stat-label">02 · Rank</span>
                <span class="hero-stat-value">Hybrid</span>
            </div>
            <div class="hero-stat">
                <span class="hero-stat-label">03 · Evaluate</span>
                <span class="hero-stat-value">AI + Evidence</span>
            </div>
            <div class="hero-stat">
                <span class="hero-stat-label">04 · Review</span>
                <span class="hero-stat-value">Human-led</span>
            </div>
        </aside>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SEARCH PANEL
# =========================================================

st.markdown(
    """
    <div class="search-panel">
        <div class="panel-heading">Who are you looking for?</div>
        <div class="panel-description">
            Add skills, technologies, experience, or project requirements in plain language.
        </div>
    """,
    unsafe_allow_html=True,
)

search_col, button_col, clear_col = st.columns([6.4, 1.15, .9], gap="small")

with search_col:
    query = st.text_input(
        "Candidate search",
        value=st.session_state.get("selected_query", ""),
        placeholder="e.g. Python developer with NLP, RAG, SQL, and deep learning experience",
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
    st.session_state["selected_query"] = ""
    st.rerun()

st.markdown(
    """
        <div class="suggestion-row">
            <span class="suggestion-chip">Python + ML</span>
            <span class="suggestion-chip">NLP + SQL</span>
            <span class="suggestion-chip">Computer Vision</span>
            <span class="suggestion-chip">RAG + LLM</span>
            <span class="suggestion-chip">Vector Search</span>
            <span class="suggestion-chip">Natural Language</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Compact product-level pipeline explanation.
st.markdown(
    """
    <div style="
        display:flex;
        align-items:center;
        gap:8px;
        flex-wrap:wrap;
        margin:-10px 0 20px;
        color:#667085;
        font-size:.66rem;
        font-weight:700;
    ">
        <span style="color:#4F46E5;">01 Retrieve</span>
        <span>→</span>
        <span style="color:#4F46E5;">02 Aggregate</span>
        <span>→</span>
        <span style="color:#4F46E5;">03 Rank</span>
        <span>→</span>
        <span style="color:#4F46E5;">04 Evaluate</span>
        <span>→</span>
        <span style="color:#12B76A;">05 Review</span>
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
            "Enter a few skills, technologies, or requirements to start searching."
        )
    else:
        clean_query = query.strip()
        st.session_state["selected_query"] = clean_query

        with st.spinner("Searching the talent knowledge base..."):
            try:
                result = execute_search(clean_query)
                st.session_state["search_result"] = result
                st.session_state["last_query"] = clean_query
                st.session_state.pop("search_error", None)
            except Exception as exc:
                error_message = str(exc)
                st.session_state["search_error"] = error_message
                st.error("The search could not be completed.")

                with st.expander("Technical details"):
                    st.write(error_message)


# =========================================================
# RESULTS
# =========================================================

result = st.session_state.get("search_result")

if result:
    last_query = st.session_state.get("last_query", query)

    st.markdown(
        f"""
        <div class="results-head">
            <div>
                <div class="section-kicker">Search results</div>
                <div class="section-title">Best-matching candidate profiles</div>
                <div class="section-copy">
                    Ranked for <b>{safe_text(last_query)}</b> using semantic relevance,
                    requirement coverage, and evidence-grounded evaluation.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Metrics
    c1, c2, c3, c4 = st.columns(4, gap="small")

    metrics = [
        (
            "Displayed candidates",
            result.get("final_count", 0),
            "Profiles shown to the recruiter",
        ),
        (
            "Retrieved chunks",
            result.get("retrieved_count", 0),
            "Relevant knowledge chunks",
        ),
        (
            "Ranked candidates",
            result.get("ranked_count", 0),
            "Profiles considered for ranking",
        ),
        (
            "Unique profiles",
            result.get("unique_count", 0),
            "Distinct candidate IDs",
        ),
    ]

    for col, (label, value, caption) in zip(
        [c1, c2, c3, c4],
        metrics,
    ):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{safe_text(label)}</div>
                    <div class="metric-value">{safe_text(value)}</div>
                    <div class="metric-caption">{safe_text(caption)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    candidates = result.get("candidates", []) or []

    if not candidates:
        st.markdown(
            """
            <div class="empty-state">
                <b>No matching candidates found.</b><br>
                Try a broader description or fewer constraints.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for candidate in candidates:
            render_candidate(candidate)

    with st.expander("Technical details"):
        technical_rows = {
            "Retrieved chunks": result.get("retrieved_count", 0),
            "Ranked candidates": result.get("ranked_count", 0),
            "Unique profiles": result.get("unique_count", 0),
            "Final candidates": result.get("final_count", 0),
            "Evaluation source": result.get("gemini_source", "unknown"),
        }

        for key, value in technical_rows.items():
            st.write(f"**{key}:** {value}")

    source = result.get("gemini_source", "unknown")

    if source == "cache":
        evaluation_status = "AI evidence evaluation served from cache"
        status_class = ""
    elif source in {"live", "gemini", "api"}:
        evaluation_status = "AI evidence evaluation generated live"
        status_class = ""
    else:
        evaluation_status = (
            "AI evidence evaluation unavailable; retrieval and ranking results remain available"
        )
        status_class = "warning"

    st.markdown(
        f"""
        <div class="evaluation-banner">
            <span class="evaluation-dot {status_class}"></span>
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
        <strong>RAG Talent Search</strong><br>
        Semantic Retrieval · Hybrid Ranking · Evidence-Grounded AI<br>
        AI talent discovery with semantic retrieval, hybrid ranking, and evidence-grounded evaluation.
    </div>
    """,
    unsafe_allow_html=True,
)
