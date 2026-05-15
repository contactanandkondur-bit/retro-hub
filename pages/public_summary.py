import streamlit as st
from services.retro_service import get_retro_by_token, get_summary
from utils.helpers import format_date


def show(token: str):
    with st.spinner("Loading summary..."):
        session = get_retro_by_token(token)

    if not session:
        st.error("Invalid or expired summary link.")
        return

    with st.spinner("Fetching content..."):
        summary = get_summary(session['id'])

    if not summary:
        st.info("Summary not available yet. Check back later.")
        return

    st.markdown(
        f"<h2 style='text-align:center; margin-bottom:0.25rem;'>"
        f"Retro<span style='color:#86BC25;'>Hub</span></h2>"
        f"<h3 style='text-align:center; margin-bottom:0.25rem;'>"
        f"{session['sprint_name']}</h3>"
        f"<p style='text-align:center; color:#888; font-size:0.875rem;'>"
        f"Retrospective Summary</p>",
        unsafe_allow_html=True
    )

    st.divider()

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Sprint Dates",
        f"{format_date(session['start_date'])} → "
        f"{format_date(session['end_date'])}"
    )
    m2.metric("Team Size", session['team_size'])
    m3.metric("Sprint Goal", session['sprint_goal'][:30])

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    sections = [
        ("What Went Well", "went_well_summary"),
        ("What Can Be Improved", "improve_summary"),
        ("Recognitions", "recognition_summary"),
        ("Action Items", "action_items_summary"),
    ]

    for title, key in sections:
        with st.container(border=True):
            st.write(f"**{title}**")
            if summary.get(key):
                for line in summary[key].split('\n'):
                    if line.strip():
                        st.write(line.strip())
            else:
                st.caption("No content in this section.")
        st.markdown(
            "<div style='height:0.5rem'></div>",
            unsafe_allow_html=True
        )

    st.divider()
    st.caption(
        "RetroHub — Reflect. Improve. Deliver. | Read-only view"
    )