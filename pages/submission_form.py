import streamlit as st
from services.retro_service import save_submission
from services.auth import logout, has_already_submitted, mark_as_submitted


def show():
    retro = st.session_state.get('retro_session', {})
    session_id = retro.get('id')

    if has_already_submitted(session_id) or \
            st.session_state.get('already_submitted'):
        _thankyou()
        return

    st.markdown(
        f"<h2 style='text-align:center; margin-bottom:0.25rem;'>"
        f"Retro<span style='color:#86BC25;'>Hub</span></h2>"
        f"<h3 style='text-align:center; font-weight:600;"
        f"margin-bottom:0.25rem;'>"
        f"{retro.get('sprint_name', 'Sprint Retrospective')}</h3>"
        f"<p style='text-align:center; color:#888; font-size:0.875rem;'>"
        f"🎯 {retro.get('sprint_goal', '')}</p>",
        unsafe_allow_html=True
    )

    st.divider()

    st.info(
        "Your responses are completely anonymous. "
        "Be honest and constructive."
    )

    with st.form("retro_form"):
        with st.container(border=True):
            st.write("**What Went Well?**")
            st.caption(
                "What are you proud of this sprint? What worked great?"
            )
            went_well = st.text_area(
                "went_well",
                placeholder="Share what went well...",
                height=100,
                label_visibility="collapsed"
            )

        with st.container(border=True):
            st.write("**What Can Be Improved?**")
            st.caption(
                "What slowed us down? What should we do differently?"
            )
            improve = st.text_area(
                "improve",
                placeholder="Share what could be improved...",
                height=100,
                label_visibility="collapsed"
            )

        with st.container(border=True):
            st.write("**Recognitions**")
            st.caption(
                "Give a shoutout to a teammate who did great work."
            )
            recognition = st.text_area(
                "recognition",
                placeholder="Recognise someone from your team...",
                height=100,
                label_visibility="collapsed"
            )

        submitted = st.form_submit_button(
            "Submit Responses →",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        if not any([
            went_well.strip(),
            improve.strip(),
            recognition.strip()
        ]):
            st.error("Please fill in at least one section.")
            return
        with st.spinner("Submitting your responses..."):
            try:
                save_submission(
                    session_id=retro['id'],
                    went_well=went_well.strip(),
                    improve=improve.strip(),
                    recognition=recognition.strip()
                )
                st.session_state['already_submitted'] = True
                mark_as_submitted(retro['id'])
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
                return
        st.rerun()


def _thankyou():
    st.markdown(
        "<div style='height:3rem'></div>",
        unsafe_allow_html=True
    )
    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.container(border=True):
            st.markdown(
                "<div style='text-align:center; padding:2rem 1rem;'>"
                "<h2>✓ Response Submitted</h2>"
                "<p style='color:#888;'>"
                "Your feedback has been recorded anonymously.<br/>"
                "The Scrum Master will share a summary after "
                "the session closes.</p>"
                "</div>",
                unsafe_allow_html=True
            )
            if st.button("Exit", use_container_width=True):
                with st.spinner("Logging out..."):
                    logout()
                st.rerun()