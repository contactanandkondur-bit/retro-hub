import streamlit as st
from services.retro_service import (
    get_summary,
    update_summary,
    save_action_items,
    get_retro_by_id
)
from services.pdf_service import generate_retro_pdf

APP_URL = "https://scrum-retrospective-app.streamlit.app"


def show():
    session_id = st.session_state.get('review_session_id')
    readonly = st.session_state.get('review_readonly', False)
    edit_mode = st.session_state.get('summary_edit_mode', False)

    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.title("Summary Review")
    with col_b:
        st.markdown(
            "<div style='height:0.6rem'></div>",
            unsafe_allow_html=True
        )
        if st.button("← Back", use_container_width=True):
            st.session_state['summary_edit_mode'] = False
            st.session_state['show_regen_confirm'] = False
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

    # Public link + PDF download
    col_link, col_pdf = st.columns([3, 1])

    with col_link:
        with st.container(border=True):
            st.caption(
                "PUBLIC SUMMARY LINK — Share with team for retro call"
            )
            st.code(
                f"{APP_URL}/?token={session.get('summary_token')}",
                language=None
            )

    with col_pdf:
        st.markdown(
            "<div style='height:0.5rem'></div>",
            unsafe_allow_html=True
        )
        try:
            pdf_bytes = generate_retro_pdf(session, summary)
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=(
                    f"{session['sprint_name'].replace(' ', '_')}"
                    f"_Retro_Summary.pdf"
                ),
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF error: {str(e)}")

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    # Route to correct view
    if readonly and not edit_mode:
        _readonly(summary, session, session_id)
    else:
        _editable(session_id, session, summary, readonly)


def _readonly(summary, session, session_id):
    col_edit, col_regen = st.columns(2)

    with col_edit:
        if st.button(
            "Edit Summary",
            use_container_width=True,
            type="primary"
        ):
            st.session_state['summary_edit_mode'] = True
            st.session_state['show_regen_confirm'] = False
            st.rerun()

    with col_regen:
        if st.button(
            "Regenerate AI Summary",
            use_container_width=True
        ):
            st.session_state['show_regen_confirm'] = True
            st.rerun()

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    # Regenerate confirmation
    if st.session_state.get('show_regen_confirm'):
        _regen_confirm(session_id, session, summary)
        return

    # Read only sections
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


def _editable(session_id, session, summary, came_from_readonly=False):
    st.caption(
        "Edit any section below. "
        "Click Save to update the summary."
    )

    with st.form("summary_edit_form"):
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

        st.markdown(
            "<div style='height:0.5rem'></div>",
            unsafe_allow_html=True
        )

        if came_from_readonly:
            col1, col2 = st.columns(2)
            with col1:
                save = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                cancel = st.form_submit_button(
                    "Cancel",
                    use_container_width=True
                )
            approve = False
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                save = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True
                )
            with col2:
                cancel = st.form_submit_button(
                    "Cancel",
                    use_container_width=True
                )
            with col3:
                approve = st.form_submit_button(
                    "Approve & Send Email →",
                    use_container_width=True,
                    type="primary"
                )

    # Regenerate button outside form
    if st.button(
        "Regenerate AI Summary",
        use_container_width=True
    ):
        st.session_state['show_regen_confirm'] = True
        st.rerun()

    # Regenerate confirmation
    if st.session_state.get('show_regen_confirm'):
        _regen_confirm(session_id, session, summary)
        return

    if cancel:
        st.session_state['summary_edit_mode'] = False
        st.session_state['show_regen_confirm'] = False
        st.rerun()

    if save:
        with st.spinner("Saving changes..."):
            update_summary(session_id, ww, imp, rec, ai)
            save_action_items(
                session_id, session['sprint_name'], ai
            )
        st.toast("Changes saved.", icon="✅")
        st.session_state['summary_edit_mode'] = False
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
        st.session_state['summary_edit_mode'] = False
        st.session_state['page'] = 'send_email'
        st.rerun()


def _regen_confirm(session_id, session, summary):
    """
    Shows regenerate confirmation with strong warning
    if summary has been manually edited.
    """
    is_edited = summary.get('is_edited', 0)

    if is_edited:
        st.error(
            "⚠️ You have manually edited this summary. "
            "Regenerating will replace everything with fresh AI output "
            "from the original team responses. "
            "All your manual edits will be permanently lost."
        )
    else:
        st.warning(
            "Regenerating will replace the current AI summary "
            "with a fresh one generated from team responses. "
            "This cannot be undone."
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
                    from services.ollama_service import generate_summary
                    generate_summary(session_id)
                    st.session_state['show_regen_confirm'] = False
                    st.session_state['summary_edit_mode'] = False
                    st.toast("Summary regenerated!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col2:
        if st.button(
            "Cancel",
            use_container_width=True,
            key="cancel_regen"
        ):
            st.session_state['show_regen_confirm'] = False
            st.rerun()