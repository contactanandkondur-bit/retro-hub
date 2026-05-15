import streamlit as st
from services.retro_service import (
    approve_retro_session,
    save_action_items
)
from utils.helpers import format_date


def show():
    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.title("Email Preview")
    with col_b:
        st.markdown(
            "<div style='height:0.6rem'></div>",
            unsafe_allow_html=True
        )
        if st.button("← Back", use_container_width=True):
            st.session_state['page'] = 'summary_review'
            st.rerun()

    session = st.session_state.get('approve_session', {})
    summary = st.session_state.get('approve_summary', {})
    session_id = st.session_state.get('approve_session_id')

    if not session or not summary:
        st.error("No session data found.")
        return

    sprint = session.get('sprint_name')
    emails = [
        e.strip()
        for e in session.get('email_recipients', '').split(',')
        if e.strip()
    ]

    with st.container(border=True):
        st.caption("RECIPIENTS")
        cols = st.columns(3)
        for i, email in enumerate(emails):
            cols[i % 3].write(email)

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    with st.container(border=True):
        st.caption("EMAIL PREVIEW")
        st.write(f"**Subject:** Sprint Retro Summary — {sprint}")
        st.divider()

        st.write(f"### {sprint}")
        st.write(
            f"{format_date(session.get('start_date'))} → "
            f"{format_date(session.get('end_date'))}"
        )
        st.write(
            f"**Sprint Goal:** {session.get('sprint_goal')}"
        )
        st.divider()

        for title, key in [
            ("What Went Well", 'went_well'),
            ("What Can Be Improved", 'improve'),
            ("Recognitions", 'recognition'),
            ("Action Items", 'action_items'),
        ]:
            st.write(f"**{title}**")
            if summary.get(key):
                for line in summary[key].split('\n'):
                    if line.strip():
                        st.write(line.strip())
            else:
                st.caption("No content.")
            st.markdown(
                "<div style='height:0.25rem'></div>",
                unsafe_allow_html=True
            )

        st.divider()
        st.caption(
            "Sent via RetroHub — Reflect. Improve. Deliver."
        )

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.button(
            "Send Email — Coming Soon",
            disabled=True,
            use_container_width=True
        )
    with c2:
        if st.button(
            "Approve & Save Action Items →",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Approving retrospective..."):
                try:
                    save_action_items(
                        session_id,
                        sprint,
                        summary.get('action_items', '')
                    )
                    approve_retro_session(session_id)
                except Exception as e:
                    st.error(str(e))
                    return
            st.toast(
                f"{sprint} approved successfully!",
                icon="✅"
            )
            st.session_state['page'] = 'action_items'
            st.rerun()