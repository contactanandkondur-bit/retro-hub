import streamlit as st
from datetime import date
from services.retro_service import create_retro_session
from utils.helpers import validate_emails, format_date


def show():
    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.title("New Retrospective")
    with col_b:
        st.markdown(
            "<div style='height:0.6rem'></div>",
            unsafe_allow_html=True
        )
        if st.button("← Back", use_container_width=True):
            st.session_state['page'] = 'retrospective'
            st.rerun()

    if st.session_state.get('retro_created'):
        _show_success()
        return

    _show_form()


def _show_form():
    with st.form("create_retro"):
        col_l, col_r = st.columns(2)

        with col_l:
            with st.container(border=True):
                st.caption("SPRINT INFORMATION")
                sprint_name = st.text_input(
                    "Sprint Name",
                    placeholder="e.g. Sprint 42"
                )
                sprint_goal = st.text_area(
                    "Sprint Goal",
                    placeholder="What was this sprint trying to achieve?",
                    height=100
                )
                team_size = st.number_input(
                    "Team Size",
                    min_value=1,
                    max_value=200,
                    value=40
                )

        with col_r:
            with st.container(border=True):
                st.caption("SPRINT DATES")
                start_date = st.date_input(
                    "Start Date",
                    value=date.today()
                )
                end_date = st.date_input(
                    "End Date",
                    value=date.today()
                )
            with st.container(border=True):
                st.caption("EMAIL RECIPIENTS")
                email_recipients = st.text_area(
                    "Recipients (comma separated)",
                    placeholder="email1@deloitte.com, email2@deloitte.com",
                    height=80
                )

        st.markdown(
            "<div style='height:0.5rem'></div>",
            unsafe_allow_html=True
        )
        submit = st.form_submit_button(
            "Create Retrospective →",
            use_container_width=True,
            type="primary"
        )

    if submit:
        _handle(
            sprint_name, sprint_goal,
            team_size, start_date,
            end_date, email_recipients
        )


def _handle(
    sprint_name, sprint_goal,
    team_size, start_date,
    end_date, email_recipients
):
    errors = []
    if not sprint_name.strip():
        errors.append("Sprint Name is required.")
    if not sprint_goal.strip():
        errors.append("Sprint Goal is required.")
    if start_date >= end_date:
        errors.append("End Date must be after Start Date.")
    valid, _ = validate_emails(email_recipients)
    if not valid:
        errors.append("At least one valid email recipient is required.")

    if errors:
        for e in errors:
            st.error(e)
        return

    with st.spinner("Creating retro session..."):
        try:
            session = create_retro_session(
                sprint_name=sprint_name.strip(),
                sprint_goal=sprint_goal.strip(),
                team_size=int(team_size),
                start_date=str(start_date),
                end_date=str(end_date),
                email_recipients=email_recipients.strip()
            )
        except Exception as e:
            st.error(str(e))
            return

    st.toast(
        f"{sprint_name} created successfully!",
        icon="✅"
    )
    st.session_state['retro_created'] = True
    st.session_state['created_session'] = session
    st.rerun()


def _show_success():
    s = st.session_state.get('created_session', {})

    st.success(f"**{s.get('sprint_name')}** created successfully.")
    st.markdown(
        "<div style='height:0.5rem'></div>",
        unsafe_allow_html=True
    )

    col_l, col_r = st.columns(2)

    with col_l:
        with st.container(border=True):
            st.caption("SPRINT DETAILS")
            st.write(f"**Name:** {s.get('sprint_name')}")
            st.write(f"**Goal:** {s.get('sprint_goal')}")
            st.write(
                f"**Dates:** {format_date(s.get('start_date'))}"
                f" → {format_date(s.get('end_date'))}"
            )
            st.write(f"**Team Size:** {s.get('team_size')} members")

    with col_r:
        with st.container(border=True):
            st.caption("SHARE WITH YOUR TEAM")
            st.write("**Passcode**")
            st.code(s.get('passcode'))
            st.write("**Submission Link**")
            st.code("http://localhost:8501")
            st.caption(
                "Share the passcode privately. Keep it secure."
            )

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "Go to Dashboard →",
            type="primary",
            use_container_width=True
        ):
            del st.session_state['retro_created']
            del st.session_state['created_session']
            st.session_state['page'] = 'sm_dashboard'
            st.rerun()
    with c2:
        if st.button("Create Another", use_container_width=True):
            del st.session_state['retro_created']
            del st.session_state['created_session']
            st.rerun()