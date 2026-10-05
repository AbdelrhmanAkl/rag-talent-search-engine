import html
import re
from typing import Any, Dict, List, Optional

import streamlit as st

from src.pipeline.search_pipeline import SearchPipeline
from src.presentation.formatter import SearchResultFormatter

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RAG Talent Search",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Candidates with coverage below this are flagged as "Weak match".
WEAK_COVERAGE_THRESHOLD = 0.25

SUGGESTED_SEARCHES = [
    "Python developer with NLP and SQL",
    "Machine learning engineer with deep learning",
    "Computer vision and OpenCV experience",
    "RAG, LLM, and vector database skills",
]

# =========================================================
# DESIGN SYSTEM  (light, calm, minimal)
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root {
    --bg: #FAFAF8;
    --surface: #FFFFFF;
    --ink: #1D1D2B;
    --text: #4A4F5C;
    --muted: #7B8191;
    --faint: #A9AEBB;
    --line: #ECECE8;
    --line-strong: #DEDED8;
    --accent: #5B5BD6;
    --accent-dark: #4A4AC0;
    --accent-soft: #F0F0FF;
    --good: #2F9E6E;
    --good-soft: #EEF8F2;
    --warn: #B7791F;
    --warn-soft: #FEF6E7;
    --radius: 18px;
}

html, body, .stApp, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(900px 380px at 85% -5%, rgba(91, 91, 214, .07), transparent 60%),
        radial-gradient(700px 320px at 0% 0%, rgba(47, 158, 110, .05), transparent 60%),
        var(--bg);
    color: var(--ink);
}

.main .block-container {
    max-width: 920px;
    padding: 36px 24px 64px;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }

h1, h2, h3 {
    font-family: "Plus Jakarta Sans", sans-serif !important;
    color: var(--ink) !important;
}

/* ---------- Sidebar (light) ---------- */

section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--line);
}

section[data-testid="stSidebar"] .block-container,
section[data-testid="stSidebar"] > div {
    padding-top: 1.2rem;
}

.sb-brand { display: flex; align-items: center; gap: 11px; margin-bottom: 6px; }

.logo {
    width: 36px; height: 36px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #7C7CEB, #5B5BD6);
    color: #fff; font-size: 17px; font-weight: 700;
    box-shadow: 0 6px 16px rgba(91, 91, 214, .25);
}

.sb-title {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 700; font-size: .98rem; color: var(--ink);
}

.sb-sub { color: var(--muted); font-size: .76rem; line-height: 1.6; margin: 8px 0 22px; }

.sb-label {
    color: var(--faint); font-size: .66rem; font-weight: 700;
    letter-spacing: .12em; text-transform: uppercase; margin: 6px 0 10px;
}

section[data-testid="stSidebar"] .stButton > button {
    justify-content: flex-start;
    text-align: left;
    min-height: 0;
    padding: 10px 12px;
    border-radius: 12px;
    background: #FAFAF8;
    border: 1px solid var(--line);
    color: var(--text);
    font-size: .8rem;
    font-weight: 500;
    box-shadow: none;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--accent-soft);
    border-color: #DCDCFA;
    color: var(--accent-dark);
}

.sb-note {
    margin-top: 22px; padding: 13px 14px; border-radius: 14px;
    background: var(--accent-soft); color: var(--text);
    font-size: .74rem; line-height: 1.65;
}

/* ---------- Hero ---------- */

.hero { text-align: center; padding: 18px 0 26px; }

.hero-badge {
    display: inline-block; padding: 5px 12px; border-radius: 999px;
    background: var(--accent-soft); color: var(--accent);
    font-size: .72rem; font-weight: 600; margin-bottom: 16px;
}

.hero-title {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: clamp(2rem, 4.4vw, 3rem);
    font-weight: 800; letter-spacing: -.04em; line-height: 1.08;
    color: var(--ink);
}

.hero-title span { color: var(--accent); }

.hero-copy {
    max-width: 560px; margin: 14px auto 0;
    color: var(--muted); font-size: .96rem; line-height: 1.7;
}

/* ---------- Search ---------- */

div[data-baseweb="input"], div[data-baseweb="base-input"] {
    background: #FFFFFF !important;
}

div[data-baseweb="input"] {
    border: 1px solid var(--line-strong) !important;
    border-radius: 16px !important;
    min-height: 54px;
    box-shadow: 0 6px 22px rgba(29, 29, 43, .04) !important;
    transition: all .18s ease;
}

div[data-baseweb="input"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 4px rgba(91, 91, 214, .10), 0 6px 22px rgba(29, 29, 43, .05) !important;
}

div[data-baseweb="input"] input {
    background: transparent !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    font-size: .95rem !important;
    padding-left: 16px !important;
}

div[data-baseweb="input"] input::placeholder {
    color: var(--faint) !important;
    -webkit-text-fill-color: var(--faint) !important;
}

.stButton > button {
    min-height: 54px;
    border-radius: 16px;
    font-weight: 600;
    font-size: .88rem;
    border: 1px solid var(--line-strong);
    background: #FFFFFF;
    color: var(--text);
    transition: all .18s ease;
}

.stButton > button p, .stButton > button div { color: inherit !important; }

.stButton > button:hover { border-color: #C9C9C2; background: #FAFAF8; }

.stButton > button[kind="primary"] {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
    box-shadow: 0 8px 20px rgba(91, 91, 214, .22);
}

.stButton > button[kind="primary"]:hover {
    background: var(--accent-dark);
    border-color: var(--accent-dark);
    transform: translateY(-1px);
}

/* Quick-search chips under the search box */
.st-key-chips .stButton > button {
    min-height: 0;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(255, 255, 255, .8);
    border: 1px solid var(--line);
    color: var(--muted);
    font-size: .74rem;
    font-weight: 500;
    white-space: nowrap;
}

.st-key-chips .stButton > button:hover {
    background: var(--accent-soft);
    border-color: #DCDCFA;
    color: var(--accent-dark);
}

/* ---------- Results ---------- */

.results-head { margin: 34px 0 14px; }

.results-title {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: 1.3rem; font-weight: 700; letter-spacing: -.02em; color: var(--ink);
}

.results-sub { color: var(--muted); font-size: .82rem; margin-top: 4px; line-height: 1.6; }

.notice {
    margin: 4px 0 14px; padding: 11px 14px; border-radius: 12px;
    background: var(--warn-soft); color: #8A5A12;
    font-size: .8rem; line-height: 1.55;
}

/* Candidate card = a bordered Streamlit container */
[class*="st-key-cand_"] {
    background: var(--surface);
    border: 1px solid var(--line) !important;
    border-radius: var(--radius) !important;
    padding: 6px 8px 4px;
    margin-bottom: 14px;
    box-shadow: 0 4px 18px rgba(29, 29, 43, .035);
    transition: box-shadow .2s ease, border-color .2s ease;
}

[class*="st-key-cand_"]:hover {
    border-color: var(--line-strong) !important;
    box-shadow: 0 10px 30px rgba(29, 29, 43, .06);
}

.cand-head { display: flex; align-items: center; justify-content: space-between; gap: 18px; }

.cand-id { display: flex; align-items: center; gap: 13px; min-width: 0; }

.rank {
    width: 40px; height: 40px; flex-shrink: 0; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    background: var(--accent-soft); color: var(--accent);
    font-family: "Plus Jakarta Sans", sans-serif; font-weight: 700; font-size: .85rem;
}

.cand-name {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 700; font-size: 1.02rem; color: var(--ink);
}

.cand-meta { color: var(--muted); font-size: .74rem; margin-top: 2px; }

.score { text-align: right; min-width: 150px; }

.score-num {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 800; font-size: 1.5rem; letter-spacing: -.03em; color: var(--accent);
    line-height: 1;
}

.score-num.weak { color: var(--warn); }

.score-bar {
    height: 5px; border-radius: 999px; background: #F0F0EC;
    overflow: hidden; margin-top: 8px;
}

.score-fill { height: 100%; border-radius: 999px; background: var(--accent); }
.score-fill.weak { background: #E5A93C; }

.score-cap { color: var(--faint); font-size: .66rem; margin-top: 5px; }

.badge-weak {
    display: inline-block; margin-left: 8px; padding: 2px 9px; border-radius: 999px;
    background: var(--warn-soft); color: var(--warn);
    font-size: .64rem; font-weight: 700; vertical-align: middle;
}

.summary {
    margin-top: 14px; padding: 13px 15px; border-radius: 13px;
    background: #FAFAF8; color: var(--text);
    font-size: .85rem; line-height: 1.75;
}

.tag-group { margin-top: 14px; }

.tag-label {
    color: var(--faint); font-size: .66rem; font-weight: 700;
    letter-spacing: .1em; text-transform: uppercase; margin-bottom: 7px;
}

.tag {
    display: inline-block; border-radius: 999px; padding: 4px 11px;
    margin: 0 5px 5px 0; font-size: .74rem; font-weight: 500; line-height: 1.4;
}

.tag-match { background: var(--good-soft); color: #23754F; }
.tag-missing { background: #F4F4F0; color: var(--muted); }

.empty-inline { color: var(--faint); font-size: .78rem; }

.detail-list { margin: 0; padding-left: 18px; color: var(--text); font-size: .82rem; line-height: 1.75; }

div[data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
    border-top: 1px solid var(--line) !important;
    border-radius: 0 !important;
    margin-top: 10px;
}

div[data-testid="stExpander"] summary {
    color: var(--muted) !important; font-size: .8rem; font-weight: 600;
}

div[data-testid="stExpander"] summary:hover { color: var(--accent) !important; }

.status-line {
    display: flex; align-items: center; gap: 8px; justify-content: center;
    margin-top: 22px; color: var(--muted); font-size: .76rem;
}

.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--good); }
.dot.warn { background: #E5A93C; }

.empty-state {
    border: 1px dashed var(--line-strong); border-radius: var(--radius);
    padding: 44px 20px; text-align: center; color: var(--muted);
    font-size: .9rem; background: rgba(255, 255, 255, .6);
}

.footer {
    margin-top: 48px; padding-top: 18px; border-top: 1px solid var(--line);
    text-align: center; color: var(--faint); font-size: .72rem; line-height: 1.8;
}

@media (max-width: 700px) {
    .main .block-container { padding: 22px 14px 48px; }
    .cand-head { flex-direction: column; align-items: flex-start; }
    .score { text-align: left; width: 100%; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================

_INITIAL_NAME_RE = re.compile(r"\b[A-Z][a-z]{2,}\s[A-Z].(?=\s|,|$)")


def clean_html(markup: str) -> str:
    """Strip every line and drop empty ones so Markdown never turns
    part of an HTML snippet into a code block."""
    return "\n".join(
        line.strip() for line in markup.splitlines() if line.strip()
    )


def render_html(markup: str) -> None:
    st.markdown(clean_html(markup), unsafe_allow_html=True)


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def normalize_items(value: Any) -> List[str]:
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


def anonymize_text(text: Any, candidate: Dict[str, Any]) -> str:
    """UI-side safety net; real anonymization belongs in the evaluator."""
    if text is None:
        return ""

    cleaned = str(text)

    for key in ("name", "full_name", "candidate_name"):
        name = candidate.get(key)
        if isinstance(name, str) and name.strip():
            cleaned = re.sub(
                re.escape(name.strip()),
                "The candidate",
                cleaned,
                flags=re.IGNORECASE,
            )

    return _INITIAL_NAME_RE.sub("The candidate", cleaned)


def parse_coverage(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number > 1:
        number = number / 100.0
    return max(0.0, min(number, 1.0))


def render_tags(items: Any, css_class: str) -> str:
    return " ".join(
        f'<span class="tag {css_class}">{safe_text(item)}</span>'
        for item in normalize_items(items)
    )


@st.cache_resource(show_spinner=False)
def load_pipeline() -> SearchPipeline:
    return SearchPipeline()


def execute_search(query: str) -> Dict[str, Any]:
    pipeline = load_pipeline()
    pipeline_result = pipeline.search(
        query,
        top_k_chunks=30,
        top_k_candidates=10,
        final_top_k=5,
    )
    return SearchResultFormatter.format_search_result(pipeline_result)


# ---------------------------------------------------------
# Callbacks (they run before the script reruns, so they can
# safely modify the text input's session-state value)
# ---------------------------------------------------------


def use_suggestion(text: str) -> None:
    st.session_state["query_input"] = text
    st.session_state["pending_search"] = True


def request_search() -> None:
    st.session_state["pending_search"] = True


def clear_all() -> None:
    st.session_state["query_input"] = ""
    st.session_state["pending_search"] = False
    for key in ("search_result", "last_query", "search_error"):
        st.session_state.pop(key, None)


# =========================================================
# LLM SOURCE HELPERS
# =========================================================


def get_llm_source(result: Dict[str, Any]) -> str:
    source = (
        result.get("llm_source")
        or result.get("gemini_source")
        or result.get("evaluation_source")
    )
    if not source:
        return "unavailable"
    return str(source).strip().lower()


def get_cached_provider(result: Dict[str, Any]) -> str:
    cached_source = result.get("cached_source")
    return str(cached_source).strip().lower() if cached_source else ""


def provider_display_name(source: str, cached_provider: str = "") -> str:
    if source == "groq":
        return "Groq"
    if source == "gemini":
        return "Gemini fallback"
    if source == "cache":
        if cached_provider == "groq":
            return "Local cache · originally Groq"
        if cached_provider == "gemini":
            return "Local cache · originally Gemini"
        return "Local cache"
    if source in {"live", "api"}:
        return "Live LLM"
    if source == "unavailable":
        return "Unavailable"
    return source.replace("_", " ").title()


def provider_status_text(source: str, cached_provider: str = "") -> str:
    if source == "groq":
        return "Evidence evaluation by Groq"
    if source == "gemini":
        return "Evidence evaluation by Gemini (Groq fallback)"
    if source == "cache":
        if cached_provider:
            return (
                "Evidence evaluation from local cache · originally "
                f"{provider_display_name(cached_provider)}"
            )
        return "Evidence evaluation from local cache"
    if source in {"live", "api"}:
        return "Evidence evaluation generated live"
    return (
        "AI evaluation unavailable; retrieval and ranking "
        "results are still shown"
    )


# =========================================================
# CANDIDATE RENDERING
# =========================================================


def candidate_is_weak(candidate: Dict[str, Any]) -> bool:
    coverage = parse_coverage(candidate.get("requirement_coverage"))
    matched = normalize_items(candidate.get("matched_requirements"))
    if coverage is not None:
        return coverage < WEAK_COVERAGE_THRESHOLD
    return not matched


def render_candidate(candidate: Dict[str, Any], position: int) -> None:
    rank = int(candidate.get("rank", position) or position)
    candidate_id = safe_text(candidate.get("candidate_id", "N/A"))

    try:
        score = float(candidate.get("hybrid_score", 0.0) or 0.0)
    except (TypeError, ValueError):
        score = 0.0
    score_percent = max(0.0, min(score, 1.0)) * 100.0

    coverage = parse_coverage(candidate.get("requirement_coverage"))
    matched = normalize_items(candidate.get("matched_requirements"))
    missing = normalize_items(candidate.get("missing_requirements"))

    fit_summary = anonymize_text(candidate.get("fit_summary"), candidate)

    evidence_items = [
        anonymize_text(i, candidate)
        for i in normalize_items(candidate.get("matching_evidence"))
    ]
    gap_items = [
        anonymize_text(i, candidate)
        for i in normalize_items(candidate.get("gaps"))
    ]
    bias_check = anonymize_text(candidate.get("bias_check"), candidate)

    is_weak = candidate_is_weak(candidate)
    weak_class = " weak" if is_weak else ""
    badge = '<span class="badge-weak">Weak match</span>' if is_weak else ""

    meta = f"ID {candidate_id}"
    if coverage is not None:
        meta += f" · {coverage:.0%} of requirements covered"

    caption = (
        "similarity only · limited requirement fit"
        if is_weak
        else "relevance + requirement fit"
    )

    with st.container(key=f"cand_{position}"):
        render_html(
            f"""
            <div class="cand-head">
                <div class="cand-id">
                    <div class="rank">{rank:02d}</div>
                    <div>
                        <div class="cand-name">Candidate {candidate_id}{badge}</div>
                        <div class="cand-meta">{safe_text(meta)}</div>
                    </div>
                </div>
                <div class="score">
                    <div class="score-num{weak_class}">{score_percent:.0f}%</div>
                    <div class="score-bar">
                        <div class="score-fill{weak_class}" style="width:{score_percent:.1f}%"></div>
                    </div>
                    <div class="score-cap">{caption}</div>
                </div>
            </div>
            """
        )

        if fit_summary:
            render_html(f'<div class="summary">{safe_text(fit_summary)}</div>')

        if matched:
            render_html(
                f"""
                <div class="tag-group">
                    <div class="tag-label">Matches</div>
                    {render_tags(matched, "tag-match")}
                </div>
                """
            )

        if missing:
            render_html(
                f"""
                <div class="tag-group">
                    <div class="tag-label">Not found</div>
                    {render_tags(missing, "tag-missing")}
                </div>
                """
            )

        if evidence_items or gap_items or bias_check:
            with st.expander("View evidence & notes"):
                if evidence_items:
                    items = "".join(f"<li>{safe_text(i)}</li>" for i in evidence_items)
                    render_html(
                        f'<div class="tag-label">Supporting evidence</div>'
                        f'<ul class="detail-list">{items}</ul>'
                    )
                if gap_items:
                    items = "".join(f"<li>{safe_text(i)}</li>" for i in gap_items)
                    render_html(
                        f'<div class="tag-label" style="margin-top:14px">Gaps</div>'
                        f'<ul class="detail-list">{items}</ul>'
                    )
                if bias_check:
                    render_html(
                        f'<div class="tag-label" style="margin-top:14px">Evaluation notes</div>'
                        f'<div class="detail-list" style="padding-left:0">{safe_text(bias_check)}</div>'
                    )


# =========================================================
# SESSION STATE
# =========================================================

st.session_state.setdefault("query_input", "")
st.session_state.setdefault("search_result", None)
st.session_state.setdefault("last_query", None)
st.session_state.setdefault("pending_search", False)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    render_html(
        """
        <div class="sb-brand">
            <div class="logo">◈</div>
            <div class="sb-title">RAG Talent Search</div>
        </div>
        <div class="sb-sub">
            Find candidates by describing what you need in plain language.
        </div>
        <div class="sb-label">Try a search</div>
        """
    )

    for index, example in enumerate(SUGGESTED_SEARCHES):
        st.button(
            example,
            key=f"side_query_{index}",
            use_container_width=True,
            on_click=use_suggestion,
            args=(example,),
        )

    render_html(
        """
        <div class="sb-note">
            <b>Decision support only.</b><br>
            Results are evidence to support human review, not an
            automated hiring decision.
        </div>
        """
    )


# =========================================================
# HERO
# =========================================================

render_html(
    """
    <div class="hero">
        <div class="hero-badge">AI-powered recruitment</div>
        <div class="hero-title">Find the right talent, <span>faster.</span></div>
        <div class="hero-copy">
            Describe the person you need. We search the profiles,
            rank the best matches, and show the evidence behind each one.
        </div>
    </div>
    """
)


# =========================================================
# SEARCH
# =========================================================

search_col, button_col, clear_col = st.columns([6, 1.3, 1], gap="small")

with search_col:
    st.text_input(
        "Candidate search",
        key="query_input",
        placeholder="e.g. Python developer with NLP, SQL and deep learning",
        label_visibility="collapsed",
        on_change=request_search,
    )

with button_col:
    search_clicked = st.button("Search", type="primary", use_container_width=True)

with clear_col:
    st.button("Clear", use_container_width=True, on_click=clear_all)

with st.container(key="chips"):
    chip_cols = st.columns([1, 1, 1, 1, 1.4], gap="small")
    chips = ["Python + ML", "NLP + SQL", "Computer Vision", "RAG + LLM"]
    chip_queries = [
        "Python developer with machine learning",
        "NLP engineer with SQL",
        "Computer vision engineer",
        "RAG and LLM engineer",
    ]
    for col, label, chip_query in zip(chip_cols, chips, chip_queries):
        with col:
            st.button(
                label,
                key=f"chip_{label}",
                on_click=use_suggestion,
                args=(chip_query,),
            )


# =========================================================
# SEARCH EXECUTION
# =========================================================

run_search = search_clicked or st.session_state.get("pending_search", False)
st.session_state["pending_search"] = False

if run_search:
    query_text = (st.session_state.get("query_input") or "").strip()

    if not query_text:
        st.warning(
            "Type a few skills, technologies or requirements to start."
        )
    else:
        with st.spinner("Searching profiles…"):
            try:
                st.session_state["search_result"] = execute_search(query_text)
                st.session_state["last_query"] = query_text
                st.session_state.pop("search_error", None)
            except Exception as exc:
                st.session_state["search_error"] = str(exc)
                st.error("The search could not be completed.")
                with st.expander("Technical details"):
                    st.write(str(exc))


# =========================================================
# RESULTS
# =========================================================

result = st.session_state.get("search_result")

if result:
    last_query = st.session_state.get("last_query") or ""
    candidates = result.get("candidates", []) or []

    count = len(candidates)
    noun = "candidate" if count == 1 else "candidates"

    render_html(
        f"""
        <div class="results-head">
            <div class="results-title">Top {count} {noun}</div>
            <div class="results-sub">
                For <b>{safe_text(last_query)}</b> ·
                searched {safe_text(result.get("retrieved_count", 0))} passages
                across {safe_text(result.get("unique_count", 0))} profiles
            </div>
        </div>
        """
    )

    if not candidates:
        render_html(
            """
            <div class="empty-state">
                <b>No matching candidates found.</b><br>
                Try a broader description or fewer constraints.
            </div>
            """
        )
    else:
        if all(candidate_is_weak(c) for c in candidates):
            render_html(
                """
                <div class="notice">
                    No strong matches for this search. These are the closest
                    profiles by similarity — try rephrasing or using
                    different skills.
                </div>
                """
            )

        for position, candidate in enumerate(candidates, start=1):
            render_candidate(candidate, position)

    # ----- Provider status + technical details -----

    llm_source = get_llm_source(result)
    cached_provider = get_cached_provider(result)
    status_class = (
        " warn" if llm_source in {"unavailable", "", "unknown"} else ""
    )

    render_html(
        f"""
        <div class="status-line">
            <span class="dot{status_class}"></span>
            <span>{safe_text(provider_status_text(llm_source, cached_provider))}</span>
        </div>
        """
    )

    with st.expander("Technical details"):
        rows = {
            "Retrieved chunks": result.get("retrieved_count", 0),
            "Ranked candidates": result.get("ranked_count", 0),
            "Unique profiles": result.get("unique_count", 0),
            "Final candidates": result.get("final_count", 0),
            "LLM evaluation source": provider_display_name(
                llm_source, cached_provider
            ),
        }

        if llm_source == "cache" and cached_provider:
            rows["Original LLM provider"] = provider_display_name(cached_provider)

        for key, value in rows.items():
            st.write(f"**{key}:** {value}")

        if result.get("groq_error"):
            st.write("**Groq fallback reason:**")
            st.code(str(result["groq_error"]), language="text")

        if result.get("llm_error"):
            st.write("**Evaluation error:**")
            st.code(str(result["llm_error"]), language="text")

        if result.get("cache_key"):
            st.write("**Evaluation cache:** Enabled")
            st.caption(f"Cache key: {result['cache_key']}")


# =========================================================
# FOOTER
# =========================================================

render_html(
    """
    <div class="footer">
        <strong>RAG Talent Search</strong><br>
        Semantic retrieval · Hybrid ranking · Evidence-grounded AI
    </div>
    """
)
