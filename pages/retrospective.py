import streamlit as st
from services.retro_service import get_all_past_retros
from utils.helpers import format_date


def show():
    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.title("Retrospective")
    with col_b:
        st.markdown(
            "<div style='height:0.6rem'></div>",
            unsafe_allow_html=True
        )
        if st.button(
            "+ New Retro",
            type="primary",
            use_container_width=True
        ):
            st.session_state['page'] = 'create_retro'
            st.rerun()

    retros = get_all_past_retros()

    if not retros:
        st.info(
            "No retrospectives yet. "
            "Create your first sprint retro to get started."
        )
        return

    # Summary metrics
    total = len(retros)
    approved = sum(1 for r in retros if r['status'] == 'approved')
    pending = sum(1 for r in retros if r['status'] == 'closed')

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Retros", total)
    m2.metric("Approved", approved)
    m3.metric("Pending Approval", pending)

    st.markdown(
        "<div style='height:1rem'></div>",
        unsafe_allow_html=True
    )

    # Table
    with st.container(border=True):
        # Header
        h1, h2, h3, h4, h5 = st.columns([2.2, 1.8, 1, 0.8, 1.6])
        h1.caption("SPRINT")
        h2.caption("DATES")
        h3.caption("STATUS")
        h4.caption("RESPONSES")
        h5.caption("ACTIONS")

        st.divider()

        for i, r in enumerate(retros):
            c1, c2, c3, c4, c5 = st.columns([2.2, 1.8, 1, 0.8, 1.6])

            with c1:
                st.markdown(
                    f"**{r['sprint_name']}**"
                )
                goal = r['sprint_goal']
                st.caption(
                    f"{goal[:42]}{'...' if len(goal) > 42 else ''}"
                )

            with c2:
                st.write(
                    f"{format_date(r['start_date'])} →"
                    f" {format_date(r['end_date'])}"
                )

            with c3:
                if r['status'] == 'approved':
                    st.success("Approved")
                else:
                    st.warning("Pending")

            with c4:
                st.write(
                    f"**{r['submission_count']}** / {r['team_size']}"
                )

            with c5:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button(
                        "Summary",
                        key=f"s_{r['id']}",
                        use_container_width=True
                    ):
                        st.session_state['page'] = 'summary_review'
                        st.session_state['review_session_id'] = r['id']
                        st.session_state['review_readonly'] = True
                        st.rerun()
                with b2:
                    if st.button(
                        "Actions",
                        key=f"a_{r['id']}",
                        use_container_width=True
                    ):
                        st.session_state['page'] = 'action_items'
                        st.session_state['filter_session_id'] = r['id']
                        st.rerun()

            if i < len(retros) - 1:
                st.divider()