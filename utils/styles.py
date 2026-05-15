def get_global_styles() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif !important;
    }

    /* ── Hide Streamlit Chrome ── */
    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stToolbar"]        { display: none !important; }
    [data-testid="stDecoration"]     { display: none !important; }
    .stDeployButton                  { display: none !important; }
    footer                           { display: none !important; }
    #MainMenu                        { display: none !important; }

    /* ── Page padding ── */
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1100px !important;
    }

    /* ── Progress bar color ── */
    .stProgress > div > div > div > div {
        background-color: #86BC25 !important;
    }

    /* ── Tab active color ── */
    .stTabs [aria-selected="true"] {
        color: #86BC25 !important;
        border-bottom-color: #86BC25 !important;
    }

    /* ── Metric label size ── */
    [data-testid="stMetricLabel"] p {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.4px !important;
    }

    /* ── Code block ── */
    .stCode code {
        font-size: 0.9rem !important;
    }
    </style>
    """