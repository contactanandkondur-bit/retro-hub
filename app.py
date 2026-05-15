import streamlit as st
from database.db import init_db
from services.auth import is_logged_in, is_sm, is_member, check_session_timeout, logout
from utils.styles import get_global_styles

st.set_page_config(
    page_title="RetroHub — Reflect. Improve. Deliver.",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(get_global_styles(), unsafe_allow_html=True)

init_db()


def main():
    params = st.query_params
    token = params.get("token")

    if token:
        from pages.public_summary import show
        show(token)
        return

    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'

    if not is_logged_in():
        from pages.login import show
        show()
        return

    if check_session_timeout():
        logout()
        st.warning("Session expired. Please log in again.")
        from pages.login import show
        show()
        return

    if is_sm():
        from utils.nav import render_nav
        render_nav()
        _route_sm()

    elif is_member():
        from pages.submission_form import show
        show()


def _route_sm():
    page = st.session_state.get('page', 'sm_dashboard')
    if page == 'sm_dashboard':
        from pages.sm_dashboard import show
        show()
    elif page == 'retrospective':
        from pages.retrospective import show
        show()
    elif page == 'create_retro':
        from pages.create_retro import show
        show()
    elif page == 'summary_review':
        from pages.summary_review import show
        show()
    elif page == 'send_email':
        from pages.send_email import show
        show()
    elif page == 'action_items':
        from pages.action_items import show
        show()
    else:
        from pages.sm_dashboard import show
        show()


if __name__ == "__main__":
    main()