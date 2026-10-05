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
    layout="wide",
    initial_sidebar_state="expanded",
)

# Candidates with coverage below this are flagged as "Weak match".
WEAK_COVERAGE_THRESHOLD = 0.25

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
    --warning-soft: #FFFAEB;
    --danger: #D92D20;
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
            circle at 88% 0%,
            rgba(91, 91, 247, .08),
            transparent 25%
        ),
        linear-gradient(
            180deg,
            #FBFCFF 0%,
            var(--page) 100%
        );
    color: var(--ink);
}

.main .block-container {
    max-width: 1440px;
    padding: 20px 38px 52px;
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
    letter-spacing: -0.045em;
}


/* =====================================================
   SIDEBAR
   ===================================================== */

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1F2937;
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255, 255, 255, .06) !important;
    border: 1px solid rgba(255, 255, 255, .12) !important;
    color: #E5E7EB !important;
    min-height: 0 !important;
    padding: 10px 12px !important;
    border-radius: 11px !important;
    font-size: .74rem !important;
    font-weight: 600 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button div {
    color: #E5E7EB !important;
    text-align: left !important;
    font-size: .74rem !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(91, 91, 247, .28) !important;
    border-color: rgba(129, 129, 255, .55) !important;
    transform: none !important;
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
    background: linear-gradient(
        135deg,
        #7777FF,
        #4F46E5
    );
    color: #fff;
    font-size: 21px;
    font-weight: 800;
    box-shadow: 0 12px 30px rgba(91, 91, 247, .28);
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
    background: rgba(91, 91, 247, .18);
    color: #C7C7FF !important;
}

.sidebar-note {
    background: rgba(255, 255, 255, .055);
    border: 1px solid rgba(255, 255, 255, .09);
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
    box-shadow: 0 0 0 4px rgba(18, 183, 106, .10);
}


/* =====================================================
   TOPBAR
   ===================================================== */

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
    box-shadow: 0 10px 24px rgba(91, 91, 247, .22);
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


/* =====================================================
   HERO
   ===================================================== */

.hero-shell {
    display: grid;
    grid-template-columns:
        minmax(0, 1.55fr)
        minmax(300px, .75fr);
    gap: 18px;
    margin-bottom: 20px;
}

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 24px;
    background: linear-gradient(
        135deg,
        #FFFFFF 0%,
        #F8F8FF 100%
    );
    padding: 30px 34px;
    min-height: 225px;
    box-shadow: 0 16px 45px rgba(16, 24, 40, .045);
}

.hero::after {
    content: "";
    position: absolute;
    width: 270px;
    height: 270px;
    border-radius: 50%;
    right: -120px;
    top: -150px;
    background: rgba(91, 91, 247, .08);
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

.hero-title span {
    color: var(--primary);
}

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
    box-shadow: 0 16px 45px rgba(16, 24, 40, .035);
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

.hero-stat:last-child {
    border-bottom: 0;
}

.hero-stat-label {
    color: var(--muted);
    font-size: .73rem;
}

.hero-stat-value {
    font-family: "Space Grotesk", sans-serif;
    color: var(--ink);
    font-weight: 700;
    font-size: .85rem;
}


/* =====================================================
   SEARCH
   ===================================================== */

.st-key-search_panel {
    background: white;
    border: 1px solid var(--line);
    border-radius: 19px;
    padding: 20px 20px 16px;
    box-shadow: 0 8px 28px rgba(16, 24, 40, .03);
    margin-bottom: 14px;
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
    margin-bottom: 6px;
}

/* Streamlit wraps the <input> in a "base-input" div that keeps the
   dark-theme background; force it to be light/transparent. */
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background: #FCFCFD !important;
}

div[data-baseweb="input"] {
    border: 1px solid #D0D5DD !important;
    border-radius: 12px !important;
    min-height: 54px;
    box-shadow: none !important;
}

div[data-baseweb="input"]:focus-within {
    border-color: var(--primary) !important;
    box-shadow:
        0 0 0 4px rgba(91, 91, 247, .09) !important;
}

div[data-baseweb="input"] input {
    background: transparent !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    font-size: .86rem !important;
}

div[data-baseweb="input"] input::placeholder {
    color: var(--soft) !important;
    -webkit-text-fill-color: var(--soft) !important;
}

/* Default (secondary) buttons in the main area, e.g. "Clear" */
.stButton > button {
    min-height: 54px;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: .79rem !important;
    border: 1px solid #D0D5DD !important;
    background: #FFFFFF !important;
    color: var(--ink) !important;
    transition: all .18s ease;
}

.stButton > button p,
.stButton > button div {
    color: inherit !important;
}

.stButton > button:hover {
    background: #F9FAFB !important;
    border-color: #B8BFCC !important;
}

.stButton > button[kind="primary"] {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    color: white !important;
    box-shadow:
        0 9px 22px rgba(91, 91, 247, .18);
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
    margin-top: 4px;
}

.suggestion-chip {
    border: 1px solid #E4E7EC;
    background: #FAFBFC;
    color: #667085;
    border-radius: 999px;
    padding: 6px 9px;
    font-size: .64rem;
}

.pipeline-line {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin: 6px 0 22px;
    color: #667085;
    font-size: .66rem;
    font-weight: 700;
}

.pipeline-line .on {
    color: #4F46E5;
}

.pipeline-line .done {
    color: #12B76A;
}


/* =====================================================
   METRICS
   ===================================================== */

.metric-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px 17px;
    min-height: 98px;
    box-shadow: 0 5px 18px rgba(16, 24, 40, .025);
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


/* =====================================================
   RESULTS
   ===================================================== */

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
    box-shadow: 0 7px 24px rgba(16, 24, 40, .028);
}

.candidate-top {
    display: grid;
    grid-template-columns:
        1.25fr .7fr 1.15fr;
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

.score-value.weak {
    color: #B54708;
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
    background:
        linear-gradient(
            90deg,
            #6366F1,
            #4F46E5
        );
}

.score-progress-fill.weak {
    background:
        linear-gradient(
            90deg,
            #FDB022,
            #F79009
        );
}

.score-percent {
    color: var(--muted);
    font-size: .61rem;
    margin-top: 4px;
}

.badge-weak {
    display: inline-block;
    margin-top: 7px;
    padding: 3px 9px;
    border-radius: 999px;
    background: #FFFAEB;
    border: 1px solid #FEDF89;
    color: #B54708;
    font-size: .6rem;
    font-weight: 800;
    letter-spacing: .04em;
    text-transform: uppercase;
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

.no-match-box {
    border: 1px dashed #D0D5DD;
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    color: var(--muted);
    font-size: .72rem;
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

.coverage-label {
    color: var(--muted);
    font-size: .65rem;
    font-weight: 700;
}

.coverage-value {
    color: var(--ink);
    font-size: .7rem;
    font-weight: 800;
}

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
    background:
        linear-gradient(
            135deg,
            #F8F7FF,
            #FCFCFF
        );
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


/* =====================================================
   PROVIDER STATUS
   ===================================================== */

.evaluation-banner {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 11px 13px;
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

.evaluation-dot.warning {
    background: var(--warning);
}

.evaluation-provider {
    color: var(--ink);
    font-weight: 800;
}


/* =====================================================
   EMPTY / FOOTER
   ===================================================== */

.empty-state {
    border: 1px dashed #D0D5DD;
    border-radius: 17px;
    background: rgba(255, 255, 255, .7);
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

.footer strong {
    color: var(--muted);
}


/* =====================================================
   RESPONSIVE
   ===================================================== */

@media (max-width: 950px) {

    .main .block-container {
        padding: 20px 18px 45px;
    }

    .hero-shell {
        grid-template-columns: 1fr;
    }

    .candidate-top {
        grid-template-columns: 1fr;
    }

    .score-center {
        border-left: 0;
        border-right: 0;
        border-top: 1px solid #F0F2F5;
        border-bottom: 1px solid #F0F2F5;
        padding: 12px 0;
    }

    .topbar {
        align-items: flex-start;
        gap: 15px;
        flex-direction: column;
    }

    .topbar-right {
        flex-wrap: wrap;
    }
}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================


_INITIAL_NAME_RE = re.compile(
    r"\b[A-Z][a-z]{2,}\s[A-Z].(?=\s|,|$)"
)


def clean_html(markup: str) -> str:
    """
    Make an HTML snippet safe for st.markdown.

    Markdown ends an HTML block at the first blank line, and any line
    indented by 4+ spaces after that is rendered as a code block. That
    is exactly what happened when an optional fragment (like the weak
    badge) was an empty string and left a whitespace-only line behind.

    Stripping every line and dropping empty ones removes both problems.
    """
    return "\n".join(
        line.strip()
        for line in markup.splitlines()
        if line.strip()
    )


def render_html(markup: str) -> None:
    """Render an HTML snippet through st.markdown, safely."""
    st.markdown(
        clean_html(markup),
        unsafe_allow_html=True,
    )


def safe_text(value: Any) -> str:
    """
    Safely escape arbitrary values before rendering as HTML.
    """
    if value is None:
        return ""

    return html.escape(
        str(value),
        quote=True,
    )


def normalize_items(value: Any) -> List[str]:
    """
    Normalize backend values into a clean list of strings.
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


def anonymize_text(
    text: Any,
    candidate: Dict[str, Any],
) -> str:
    """
    Defensive anonymization for AI-generated text.

    The actual privacy protection belongs in the evaluator
    prompt and context builder. This function acts as a UI-side
    safety net.
    """
    if text is None:
        return ""

    cleaned = str(text)

    for key in (
        "name",
        "full_name",
        "candidate_name",
    ):
        name = candidate.get(key)

        if isinstance(name, str) and name.strip():
            cleaned = re.sub(
                re.escape(name.strip()),
                "The candidate",
                cleaned,
                flags=re.IGNORECASE,
            )

    return _INITIAL_NAME_RE.sub(
        "The candidate",
        cleaned,
    )


def parse_coverage(
    value: Any,
) -> Optional[float]:
    """
    Return coverage as a fraction in [0, 1].
    """
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if number > 1:
        number = number / 100.0

    return max(
        0.0,
        min(number, 1.0),
    )


def render_tags(
    items: Any,
    css_class: str,
) -> str:
    valid_items = normalize_items(items)

    return " ".join(
        f'<span class="tag {css_class}">'
        f"{safe_text(item)}"
        "</span>"
        for item in valid_items
    )


@st.cache_resource(show_spinner=False)
def load_pipeline() -> SearchPipeline:
    """
    Keep one SearchPipeline instance per Streamlit process.
    """
    return SearchPipeline()


def execute_search(
    query: str,
) -> Dict[str, Any]:
    pipeline = load_pipeline()

    pipeline_result = pipeline.search(
        query,
        top_k_chunks=30,
        top_k_candidates=10,
        final_top_k=5,
    )

    return SearchResultFormatter.format_search_result(
        pipeline_result,
    )


def clear_results() -> None:
    for key in (
        "search_result",
        "last_query",
        "search_error",
    ):
        st.session_state.pop(
            key,
            None,
        )


# =========================================================
# LLM SOURCE HELPERS
# =========================================================


def get_llm_source(
    result: Dict[str, Any],
) -> str:
    """
    Return the current evaluation source.

    Possible values:
        groq
        gemini
        cache
        unavailable
    """
    source = result.get("llm_source")

    if source is None:
        source = result.get("gemini_source")

    if source is None:
        source = result.get("evaluation_source")

    if not source:
        return "unavailable"

    return str(source).strip().lower()


def get_cached_provider(
    result: Dict[str, Any],
) -> str:
    """
    Return the original provider when the current result
    was served from the local cache.
    """
    cached_source = result.get("cached_source")

    if not cached_source:
        return ""

    return str(cached_source).strip().lower()


def provider_display_name(
    source: str,
    cached_provider: str = "",
) -> str:
    """
    Convert internal provider identifiers into
    human-readable UI labels.
    """
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


def provider_status_text(
    source: str,
    cached_provider: str = "",
) -> str:
    """
    Return the provider status message shown below results.
    """
    if source == "groq":
        return (
            "AI evidence evaluation generated by "
            "Groq (primary provider)"
        )

    if source == "gemini":
        return (
            "AI evidence evaluation generated by "
            "Gemini after Groq fallback"
        )

    if source == "cache":
        if cached_provider == "groq":
            return (
                "AI evidence evaluation served from local cache "
                "· originally generated by Groq"
            )

        if cached_provider == "gemini":
            return (
                "AI evidence evaluation served from local cache "
                "· originally generated by Gemini"
            )

        return "AI evidence evaluation served from local cache"

    if source in {"live", "api"}:
        return "AI evidence evaluation generated live"

    return (
        "AI evidence evaluation unavailable; "
        "retrieval and ranking results remain available"
    )


# =========================================================
# CANDIDATE RENDERING
# =========================================================

def render_candidate(
    candidate: Dict[str, Any]
) -> None:
    """
    Render one candidate using the portfolio-oriented UI.
    """

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

    try:
        score = float(
            candidate.get(
                "hybrid_score",
                0.0
            ) or 0.0
        )
    except (
        TypeError,
        ValueError
    ):
        score = 0.0

    score_percent = (
        max(
            0.0,
            min(score, 1.0)
        )
        * 100.0
    )

    coverage_value = parse_coverage(
        candidate.get(
            "requirement_coverage"
        )
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

    fit_summary = anonymize_text(
        candidate.get(
            "fit_summary"
        ),
        candidate
    )

    evidence_items = [
        anonymize_text(
            item,
            candidate
        )
        for item in normalize_items(
            candidate.get(
                "matching_evidence"
            )
        )
    ]

    gap_items = [
        anonymize_text(
            item,
            candidate
        )
        for item in normalize_items(
            candidate.get(
                "gaps"
            )
        )
    ]

    bias_check = anonymize_text(
        candidate.get(
            "bias_check"
        ),
        candidate
    )

    # ---------------------------------------------------------
    # Weak-match detection
    # ---------------------------------------------------------

    is_weak = (
        (
            coverage_value is not None
            and coverage_value < WEAK_COVERAGE_THRESHOLD
        )
        or (
            coverage_value is None
            and not matched
        )
    )

    weak_class = (
        " weak"
        if is_weak
        else ""
    )

    if is_weak:
        score_caption = (
            "semantic similarity only · "
            "limited requirement fit"
        )

        weak_badge = (
            '<div class="badge-weak">'
            'Weak match'
            '</div>'
        )

    else:
        score_caption = (
            "semantic relevance + "
            "requirement fit"
        )

        weak_badge = ""

    # ---------------------------------------------------------
    # Requirement fit preview
    # ---------------------------------------------------------

    if matched:
        requirement_html = render_tags(
            matched[:6],
            "tag-match"
        )
    else:
        requirement_html = (
            '<div class="no-match-box">'
            'No explicit matches identified.'
            '</div>'
        )

    # ---------------------------------------------------------
    # Candidate header card
    # (render_html strips blank/indented lines so an empty
    #  {weak_badge} can't turn the rest into a code block)
    # ---------------------------------------------------------

    render_html(
        f"""
        <div class="candidate-card">
            <div class="candidate-top">
                <div class="candidate-identity">
                    <div class="candidate-rank">
                        {rank:02d}
                    </div>
                    <div>
                        <div class="candidate-label">
                            Ranked candidate
                        </div>
                        <div class="candidate-name">
                            Candidate {candidate_id}
                        </div>
                        <div class="candidate-id">
                            Candidate ID · {candidate_id}
                        </div>
                    </div>
                </div>
                <div class="score-center">
                    <div class="score-label">
                        Hybrid match
                    </div>
                    <div class="score-value{weak_class}">
                        {score_percent:.1f}%
                    </div>
                    <div class="score-progress">
                        <div
                            class="score-progress-fill{weak_class}"
                            style="width:{score_percent:.1f}%"
                        ></div>
                    </div>
                    <div class="score-percent">
                        {score_caption}
                    </div>
                    {weak_badge}
                </div>
                <div>
                    <div class="mini-heading">
                        Requirement fit
                    </div>
                    {requirement_html}
                </div>
            </div>
        </div>
        """
    )

    # ---------------------------------------------------------
    # Matching requirements + gaps
    # ---------------------------------------------------------

    left, right = st.columns(
        2,
        gap="large"
    )

    with left:

        render_html(
            '<div class="mini-heading">'
            'Matching requirements'
            '</div>'
        )

        if matched:
            render_html(
                render_tags(
                    matched,
                    "tag-match"
                )
            )
        else:
            st.caption(
                "No specific matching requirements identified."
            )

    with right:

        render_html(
            '<div class="mini-heading">'
            'Potential gaps'
            '</div>'
        )

        if missing:
            render_html(
                render_tags(
                    missing,
                    "tag-missing"
                )
            )
        elif gap_items:
            st.caption(
                "See gap details below."
            )
        else:
            st.caption(
                "No explicit requirement gaps identified."
            )

        if gap_items:
            with st.expander(
                "Gap details"
            ):
                for gap in gap_items:
                    st.markdown(
                        f"- {safe_text(gap)}",
                        unsafe_allow_html=True
                    )

    # ---------------------------------------------------------
    # Requirement coverage
    # ---------------------------------------------------------

    if coverage_value is not None:

        render_html(
            f"""
            <div class="coverage-box">
                <div class="coverage-row">
                    <div class="coverage-label">
                        Explicit requirement coverage
                    </div>
                    <div class="coverage-value">
                        {coverage_value:.0%}
                    </div>
                </div>
                <div class="coverage-track">
                    <div
                        class="coverage-fill"
                        style="width:{coverage_value * 100:.1f}%"
                    ></div>
                </div>
            </div>
            """
        )

    # ---------------------------------------------------------
    # AI evidence summary
    # ---------------------------------------------------------

    if fit_summary:

        render_html(
            f"""
            <div class="fit-box">
                <div class="fit-heading">
                    AI evidence summary
                </div>
                <div class="fit-text">
                    {safe_text(fit_summary)}
                </div>
            </div>
            """
        )

    # ---------------------------------------------------------
    # Supporting evidence
    # ---------------------------------------------------------

    if evidence_items:

        with st.expander(
            "Supporting evidence"
        ):
            for evidence in evidence_items:
                st.markdown(
                    f"- {safe_text(evidence)}",
                    unsafe_allow_html=True
                )

    # ---------------------------------------------------------
    # Evaluation notes
    # ---------------------------------------------------------

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

if "pending_search" not in st.session_state:
    st.session_state["pending_search"] = False


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    render_html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">◈</div>
            <div class="sidebar-title">RAG Talent Search</div>
            <div class="sidebar-subtitle">
                AI-powered candidate discovery using semantic
                retrieval, hybrid ranking, and evidence-grounded
                evaluation.
            </div>
        </div>
        """
    )

    render_html(
        '<div class="sidebar-section">Workspace</div>'
    )

    render_html(
        '<div class="sidebar-nav active">⌂ &nbsp; Talent Search</div>'
    )

    render_html(
        '<div class="sidebar-nav">⌕ &nbsp; Candidate Discovery</div>'
    )

    render_html(
        '<div class="sidebar-section">Suggested searches</div>'
    )

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
            st.session_state["pending_search"] = True
            st.rerun()

    render_html(
        '<div class="sidebar-section">AI architecture</div>'
    )

    architecture_status = [
        ("RAG Pipeline", "Ready"),
        ("Hybrid Ranking", "Ready"),
        ("Groq · Primary", "Ready"),
        ("Gemini · Fallback", "Ready"),
        ("Local Evaluation Cache", "Ready"),
    ]

    for label, status in architecture_status:
        render_html(
            f"""
            <div class="sidebar-status">
                <span></span>
                {safe_text(label)}
                <small style="margin-left:auto;color:#98A2B3!important;">
                    {safe_text(status)}
                </small>
            </div>
            """
        )

    render_html(
        """
        <div style="height:10px;"></div>
        <div class="sidebar-note">
            <b>Decision support only</b>
            <br>
            Results provide retrieval and evidence to support
            human review. They are not an automated hiring
            decision.
        </div>
        """
    )


# =========================================================
# TOPBAR
# =========================================================

render_html(
    """
    <div class="topbar">
        <div class="brand-row">
            <div class="topbar-mark">◈</div>
            <div>
                <div class="topbar-title">RAG Talent Search</div>
                <div class="topbar-subtitle">
                    Intelligent candidate discovery workspace
                </div>
            </div>
        </div>
        <div class="topbar-right">
            <div class="tech-pill">
                RAG + Hybrid Ranking + Groq / Gemini
            </div>
            <div class="status-pill">
                <span class="status-dot"></span>
                System ready
            </div>
        </div>
    </div>
    """
)


# =========================================================
# HERO
# =========================================================

render_html(
    """
    <div class="hero-shell">
        <section class="hero">
            <div class="eyebrow">AI-powered recruitment</div>
            <div class="hero-title">
                Find the right talent, <span>faster.</span>
            </div>
            <div class="hero-copy">
                Describe the candidate you need in natural language.
                The engine retrieves relevant profiles, ranks them
                with a hybrid score, and evaluates the evidence using
                Groq with Gemini as an automatic fallback.
            </div>
            <div class="hero-meta">
                <span class="hero-chip">Semantic retrieval</span>
                <span class="hero-chip">Hybrid ranking</span>
                <span class="hero-chip">Groq primary</span>
                <span class="hero-chip">Gemini fallback</span>
                <span class="hero-chip">Local cache</span>
            </div>
        </section>
        <aside class="hero-side">
            <div class="hero-side-title">How the engine works</div>
            <div class="hero-stat">
                <span class="hero-stat-label">01 · Retrieve</span>
                <span class="hero-stat-value">Semantic</span>
            </div>
            <div class="hero-stat">
                <span class="hero-stat-label">02 · Aggregate</span>
                <span class="hero-stat-value">Candidate-level</span>
            </div>
            <div class="hero-stat">
                <span class="hero-stat-label">03 · Rank</span>
                <span class="hero-stat-value">Hybrid</span>
            </div>
            <div class="hero-stat">
                <span class="hero-stat-label">04 · Evaluate</span>
                <span class="hero-stat-value">Groq → Gemini</span>
            </div>
            <div class="hero-stat">
                <span class="hero-stat-label">05 · Review</span>
                <span class="hero-stat-value">Human-led</span>
            </div>
        </aside>
    </div>
    """
)


# =========================================================
# SEARCH PANEL
# =========================================================

with st.container(key="search_panel"):
    render_html(
        """
        <div class="panel-heading">Who are you looking for?</div>
        <div class="panel-description">
            Add skills, technologies, experience, or project
            requirements in plain language.
        </div>
        """
    )

    search_col, button_col, clear_col = st.columns(
        [6.4, 1.15, 0.9],
        gap="small",
    )

    with search_col:
        query = st.text_input(
            "Candidate search",
            value=st.session_state.get("selected_query", ""),
            placeholder=(
                "e.g. Python developer with NLP, RAG, "
                "SQL, and deep learning experience"
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

    render_html(
        """
        <div class="suggestion-row">
            <span class="suggestion-chip">Python + ML</span>
            <span class="suggestion-chip">NLP + SQL</span>
            <span class="suggestion-chip">Computer Vision</span>
            <span class="suggestion-chip">RAG + LLM</span>
            <span class="suggestion-chip">Vector Search</span>
            <span class="suggestion-chip">Natural Language</span>
        </div>
        """
    )

if clear_clicked:
    clear_results()
    st.session_state["selected_query"] = ""
    st.session_state["pending_search"] = False
    st.rerun()


# =========================================================
# PIPELINE LINE
# =========================================================

render_html(
    """
    <div class="pipeline-line">
        <span class="on">01 Retrieve</span>
        <span>→</span>
        <span class="on">02 Aggregate</span>
        <span>→</span>
        <span class="on">03 Rank</span>
        <span>→</span>
        <span class="on">04 Evaluate</span>
        <span>→</span>
        <span class="done">05 Review</span>
    </div>
    """
)


# =========================================================
# SEARCH EXECUTION
# =========================================================

run_search = (
    search_clicked
    or st.session_state.get("pending_search", False)
)

st.session_state["pending_search"] = False

if run_search:
    if not query.strip():
        st.warning(
            "Enter a few skills, technologies, or requirements "
            "to start searching."
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
    last_query = st.session_state.get(
        "last_query",
        query,
    )

    render_html(
        f"""
        <div class="results-head">
            <div>
                <div class="section-kicker">Search results</div>
                <div class="section-title">
                    Best-matching candidate profiles
                </div>
                <div class="section-copy">
                    Ranked for <b>{safe_text(last_query)}</b>
                    using semantic relevance,
                    requirement coverage, and
                    evidence-grounded evaluation.
                </div>
            </div>
        </div>
        """
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
            render_html(
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
                """
            )

    # =====================================================
    # CANDIDATES
    # =====================================================

    candidates = result.get("candidates", []) or []

    if not candidates:
        render_html(
            """
            <div class="empty-state">
                <b>No matching candidates found.</b>
                <br>
                Try a broader description or fewer constraints.
            </div>
            """
        )
    else:
        for candidate in candidates:
            render_candidate(candidate)

    # =====================================================
    # TECHNICAL DETAILS
    # =====================================================

    llm_source = get_llm_source(result)
    cached_provider = get_cached_provider(result)

    provider_name = provider_display_name(
        llm_source,
        cached_provider,
    )

    with st.expander("Technical details"):
        technical_rows = {
            "Retrieved chunks": result.get(
                "retrieved_count",
                0,
            ),
            "Ranked candidates": result.get(
                "ranked_count",
                0,
            ),
            "Unique profiles": result.get(
                "unique_count",
                0,
            ),
            "Final candidates": result.get(
                "final_count",
                0,
            ),
            "LLM evaluation source": provider_name,
        }

        if llm_source == "cache" and cached_provider:
            technical_rows["Original LLM provider"] = (
                provider_display_name(cached_provider)
            )

        for key, value in technical_rows.items():
            st.write(f"**{key}:** {value}")

        groq_error = result.get("groq_error")

        if groq_error:
            st.write("**Groq fallback reason:**")
            st.code(
                str(groq_error),
                language="text",
            )

        evaluation_error = result.get("llm_error")

        if evaluation_error:
            st.write("**Evaluation error:**")
            st.code(
                str(evaluation_error),
                language="text",
            )

        cache_key = result.get("cache_key")

        if cache_key:
            st.write("**Evaluation cache:** Enabled")
            st.caption(f"Cache key: {cache_key}")

    # =====================================================
    # PROVIDER STATUS
    # =====================================================

    evaluation_status = provider_status_text(
        llm_source,
        cached_provider,
    )

    status_class = ""

    if llm_source in {
        "unavailable",
        "",
        "unknown",
    }:
        status_class = "warning"

    render_html(
        f"""
        <div class="evaluation-banner">
            <span class="evaluation-dot {status_class}"></span>
            <span>
                {safe_text(evaluation_status)}
            </span>
        </div>
        """
    )


# =========================================================
# FOOTER
# =========================================================

render_html(
    """
    <div class="footer">
        <strong>RAG Talent Search</strong>
        <br>
        Semantic Retrieval · Hybrid Ranking · Evidence-Grounded AI
        <br>
        Groq Primary · Gemini Automatic Fallback · Local Evaluation Cache
        <br>
        AI talent discovery with semantic retrieval,
        hybrid ranking, and evidence-grounded evaluation.
    </div>
    """
)