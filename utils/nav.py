import streamlit as st
from services.auth import logout


def render_nav():
    from services.retro_service import get_active_retro

    current_page = st.session_state.get('page', 'sm_dashboard')

    active = get_active_retro()

    # Brand + nav items
    st.markdown(
        f"""
        <div class="retro-nav">
            <div class="retro-nav-brand">
                Retro<span>Hub</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Nav buttons in columns
    col_dash, col_retro, col_actions, col_spacer, col_status, col_logout = st.columns(
        [1, 1.2, 1.2, 3, 1.8, 0.8]
    )

    with col_dash:
        if st.button(
            "Dashboard",
            use_container_width=True,
            type="primary" if current_page == 'sm_dashboard' else "secondary",
            key="nav_dashboard"
        ):
            st.session_state['page'] = 'sm_dashboard'
            st.rerun()

    with col_retro:
        if st.button(
            "Retrospective",
            use_container_width=True,
            type="primary" if current_page in ['retrospective', 'create_retro'] else "secondary",
            key="nav_retro"
        ):
            st.session_state['page'] = 'retrospective'
            st.rerun()

    with col_actions:
        if st.button(
            "Action Items",
            use_container_width=True,
            type="primary" if current_page == 'action_items' else "secondary",
            key="nav_actions"
        ):
            st.session_state['page'] = 'action_items'
            st.session_state['filter_session_id'] = None
            st.rerun()

    with col_spacer:
        pass

    with col_status:
        if active:
            st.markdown(
                f"<div style='padding:6px 0; text-align:right;'>"
                f"<span class='pill pill-green'>🟢 {active['sprint_name']} — Active</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='padding:6px 0; text-align:right;'>"
                "<span class='pill pill-orange'>⚪ No Active Retro</span>"
                "</div>",
                unsafe_allow_html=True
            )

    with col_logout:
        if st.button(
            "Logout",
            use_container_width=True,
            type="secondary",
            key="nav_logout"
        ):
            logout()
            st.rerun()

    st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)