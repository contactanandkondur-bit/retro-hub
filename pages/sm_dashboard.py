import streamlit as st
from services.retro_service import (
    get_active_retro,
    get_submission_count,
    close_retro_session,
)
from services.ollama_service import generate_summary
from database.db import get_client


def _get_closed_with_summary():
    supabase = get_client()
    result = supabase.table("retro_sessions").select(
        "*, ai_summaries(id)"
    ).eq("status", "closed").order(
        "created_at", desc=True
    ).limit(1).execute()
    if result.data:
        for s in result.data:
            if s.get('ai_summaries'):
                return s
    return None


def _get_closed_without_summary():
    supabase = get_client()
    result = supabase.table("retro_sessions").select(
        "*"
    ).eq("status", "closed").order(
        "created_at", desc=True
    ).limit(1).execute()
    return result.data[0] if result.data else None


def show():
    st.title("Dashboard")

    active = get_active_retro()

    if active:
        _show_active(active)
        return

    closed_with = _get_closed_with_summary()
    closed_without = _get_closed_without_summary()

    if closed_with:
        st.warning(
            f"**{closed_with['sprint_name']}** — "
            f"AI Summary ready. Review and approve to finalise."
        )
        if st.button("Review Summary →", type="primary"):
            st.session_state['page'] = 'summary_review'
            st.session_state['review_session_id'] = closed_with['id']
            st.session_state['review_readonly'] = False
            st.rerun()
        return

    if closed_without:
        st.warning(
            f"**{closed_without['sprint_name']}** — "
            f"Submissions closed. Generate AI summary to proceed."
        )
        if st.button("Generate AI Summary →", type="primary"):
            with st.spinner(
                "Analysing responses... this may take 30-60 seconds."
            ):
                try:
                    generate_summary(closed_without['id'])
                    st.toast("Summary generated!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        return

    st.info(
        "No active retrospective. "
        "Go to Retrospective to start a new sprint retro."
    )
    if st.button("Go to Retrospective →", type="primary"):
        st.session_state['page'] = 'retrospective'
        st.rerun()


def _show_active(active):
    submitted = get_submission_count(active['id'])
    total = active['team_size']
    pct = min(submitted / total, 1.0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sprint", active['sprint_name'])
    c2.metric("Submissions", f"{submitted} / {total}")
    c3.metric("Start", active['start_date'])
    c4.metric("End", active['end_date'])

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    with st.container(border=True):
        st.caption("SUBMISSION PROGRESS")
        st.progress(pct)
        st.caption(
            f"{submitted} of {total} team members have responded"
        )

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    col_l, col_r = st.columns(2)

    with col_l:
        with st.container(border=True):
            st.caption("SPRINT GOAL")
            st.write(active['sprint_goal'])
            st.divider()
            st.caption("TEAM PASSCODE")
            st.code(active['passcode'])
            st.caption("SUBMISSION LINK")
            st.code("http://localhost:8501")
            st.caption(
                "Share the link and passcode privately with your team."
            )

    with col_r:
        with st.container(border=True):
            st.caption("CLOSE SUBMISSIONS")
            st.write(
                "Once your team has finished responding, "
                "close submissions to generate the AI summary."
            )
            st.markdown(
                "<div style='height:0.5rem'></div>",
                unsafe_allow_html=True
            )
            if submitted == 0:
                st.button(
                    "Close Submissions",
                    disabled=True,
                    use_container_width=True,
                    help="At least 1 submission required"
                )
                st.caption("Waiting for at least one submission.")
            else:
                if st.button(
                    "Close & Generate AI Summary →",
                    type="primary",
                    use_container_width=True,
                    key="close_btn"
                ):
                    with st.spinner(
                        "Closing submissions and analysing team "
                        "responses... this may take 30-60 seconds."
                    ):
                        try:
                            close_retro_session(active['id'])
                            generate_summary(active['id'])
                            st.toast(
                                "AI Summary generated!",
                                icon="✅"
                            )
                            st.session_state['page'] = 'summary_review'
                            st.session_state['review_session_id'] = (
                                active['id']
                            )
                            st.session_state['review_readonly'] = False
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))