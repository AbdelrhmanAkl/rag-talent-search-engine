            "Candidates found",
            result.get("final_count", 0),
            "Final returned profiles",
        ),
        (
            "Retrieved chunks",
            result.get("retrieved_count", 0),
            "Relevant knowledge chunks",
        ),
        (
            "Ranked candidates",
            result.get("ranked_count", 0),
            "Profiles considered",
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
        Built as a portfolio-ready intelligent talent discovery and decision-support experience.
    </div>
    """,
    unsafe_allow_html=True,
)
