import streamlit as st
from services.auth import (
    verify_scrum_master,
    verify_passcode,
    login_as_sm,
    login_as_member
)


def show():
    _, col, _ = st.columns([1, 1.6, 1])

    with col:
        st.markdown(
            "<div style='height:2.5rem'></div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<h2 style='text-align:center; margin-bottom:0.25rem;'>"
            "Retro<span style='color:#86BC25;'>Hub</span></h2>"
            "<p style='text-align:center; color:#888; font-size:0.85rem;"
            "margin-bottom:2rem; margin-top:0;'>"
            "Reflect. Improve. Deliver.</p>",
            unsafe_allow_html=True
        )

        tab_sm, tab_member = st.tabs(["Scrum Master", "Team Member"])

        with tab_sm:
            st.markdown(
                "<div style='height:0.75rem'></div>",
                unsafe_allow_html=True
            )
            with st.form("sm_login"):
                email = st.text_input(
                    "Email",
                    placeholder="your@deloitte.com"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••"
                )
                submitted = st.form_submit_button(
                    "Sign In",
                    use_container_width=True,
                    type="primary"
                )

            if submitted:
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
                    with st.spinner("Signing in..."):
                        success, message = verify_scrum_master(
                            email, password
                        )
                    if success:
                        login_as_sm()
                        st.toast("Welcome back!", icon="✅")
                        st.rerun()
                    else:
                        st.error(message)

        with tab_member:
            st.markdown(
                "<div style='height:0.75rem'></div>",
                unsafe_allow_html=True
            )
            st.caption(
                "Enter the passcode shared by your Scrum Master "
                "to access the retrospective."
            )
            with st.form("member_login"):
                passcode = st.text_input(
                    "Sprint Passcode",
                    type="password",
                    placeholder="Enter passcode"
                )
                submitted_p = st.form_submit_button(
                    "Enter Retrospective",
                    use_container_width=True,
                    type="primary"
                )

            if submitted_p:
                if not passcode:
                    st.error("Please enter the passcode.")
                else:
                    with st.spinner("Verifying passcode..."):
                        session = verify_passcode(passcode)
                    if session:
                        login_as_member(session)
                        st.toast("Passcode verified!", icon="✅")
                        st.rerun()
                    else:
                        st.error(
                            "Invalid or expired passcode. "
                            "The retro may be closed."
                        )

        st.markdown(
            "<div style='height:1.5rem'></div>",
            unsafe_allow_html=True
        )
        st.caption("RetroHub © 2026 — Built for Deloitte teams")