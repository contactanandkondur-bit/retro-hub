import streamlit as st
from services.retro_service import (
    get_summary,
    update_summary,
    save_action_items,
    get_retro_by_id
)

APP_URL = "https://scrum-retrospective-app.streamlit.app"


def show():
    session_id = st.session_state.get('review_session_id')
    readonly = st.session_state.get('review_readonly', False)

    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.title("Summary Review")
    with col_b:
        st.markdown(
            "<div style='height:0.6rem'></div>",
            unsafe_allow_html=True
        )
        if st.button("← Back", use_container_width=True):
            st.session_state['page'] = 'sm_dashboard'
            st.rerun()

    if not session_id:
        st.error("No session selected.")
        return

    with st.spinner("Loading summary..."):
        session = get_retro_by_id(session_id)
        summary = get_summary(session_id)

    if not session or not summary:
        st.error("Summary not found.")
        return

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Sprint", session['sprint_name'])
    i2.metric("Start", session['start_date'])
    i3.metric("End", session['end_date'])
    i4.metric(
        "Status",
        "Approved" if session['status'] == 'approved' else "Pending"
    )

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    with st.container(border=True):
        st.caption(
            "PUBLIC SUMMARY LINK — Share with team for retro call"
        )
        st.code(
            f"{APP_URL}/?token={session.get('summary_token')}",
            language=None
        )

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    if readonly:
        _readonly(summary, session, session_id)
    else:
        _editable(session_id, session, summary)


def _readonly(summary, session, session_id):
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
                st.caption("No content.")

    # Regenerate button in readonly mode too
    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )
    if st.button(
        "🔄 Regenerate AI Summary",
        use_container_width=True
    ):
        _regenerate(session_id, session)


def _editable(session_id, session, summary):
    st.caption(
        "Edit any section below before approving. "
        "All changes are saved to the database."
    )

    with st.form("summary_form"):
        with st.container(border=True):
            st.write("**What Went Well**")
            ww = st.text_area(
                "ww",
                value=summary.get('went_well_summary', ''),
                height=120,
                label_visibility="collapsed"
            )

        with st.container(border=True):
            st.write("**What Can Be Improved**")
            imp = st.text_area(
                "imp",
                value=summary.get('improve_summary', ''),
                height=120,
                label_visibility="collapsed"
            )

        with st.container(border=True):
            st.write("**Recognitions**")
            rec = st.text_area(
                "rec",
                value=summary.get('recognition_summary', ''),
                height=120,
                label_visibility="collapsed"
            )

        with st.container(border=True):
            st.write("**Action Items — AI Generated**")
            ai = st.text_area(
                "ai",
                value=summary.get('action_items_summary', ''),
                height=120,
                label_visibility="collapsed"
            )

        c1, c2 = st.columns(2)
        with c1:
            save = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )
        with c2:
            approve = st.form_submit_button(
                "Approve & Send Email →",
                use_container_width=True,
                type="primary"
            )

    # Regenerate button outside form
    if st.button(
        "🔄 Regenerate AI Summary",
        use_container_width=True
    ):
        _regenerate(session_id, session)

    if save:
        with st.spinner("Saving changes..."):
            update_summary(session_id, ww, imp, rec, ai)
            save_action_items(
                session_id, session['sprint_name'], ai
            )
        st.toast("Changes saved.", icon="✅")
        st.rerun()

    if approve:
        with st.spinner("Preparing email preview..."):
            update_summary(session_id, ww, imp, rec, ai)
            save_action_items(
                session_id, session['sprint_name'], ai
            )
            st.session_state['approve_session_id'] = session_id
            st.session_state['approve_summary'] = {
                'went_well': ww,
                'improve': imp,
                'recognition': rec,
                'action_items': ai
            }
            st.session_state['approve_session'] = session
        st.session_state['page'] = 'send_email'
        st.rerun()


def _regenerate(session_id, session):
    from services.ollama_service import generate_summary
    confirm = st.warning(
        "This will overwrite the current AI summary. "
        "Any manual edits will be lost."
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Yes, Regenerate",
            type="primary",
            use_container_width=True,
            key="confirm_regen"
        ):
            with st.spinner(
                "Regenerating AI summary... "
                "this may take 30-60 seconds."
            ):
                try:
                    generate_summary(session_id)
                    st.toast(
                        "Summary regenerated!",
                        icon="✅"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col2:
        if st.button(
            "Cancel",
            use_container_width=True,
            key="cancel_regen"
        ):
            st.rerun()