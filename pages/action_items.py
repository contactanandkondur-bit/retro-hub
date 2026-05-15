import streamlit as st
from services.retro_service import (
    get_all_action_items,
    get_action_items_by_session,
    update_action_item_status,
    get_all_past_retros
)

STATUS_OPTIONS = ['open', 'in-progress', 'done']
STATUS_LABELS = ['Open', 'In Progress', 'Done']


def show():
    filter_id = st.session_state.get('filter_session_id')

    with st.spinner("Loading action items..."):
        all_items = get_all_action_items()

    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.title("Action Items")
    with col_b:
        st.markdown(
            "<div style='height:0.6rem'></div>",
            unsafe_allow_html=True
        )
        if filter_id:
            if st.button(
                "All Sprints",
                use_container_width=True
            ):
                st.session_state['filter_session_id'] = None
                st.rerun()

    # Dashboard counts
    total = len(all_items)
    open_c = sum(1 for i in all_items if i['status'] == 'open')
    inprog = sum(1 for i in all_items if i['status'] == 'in-progress')
    done_c = sum(1 for i in all_items if i['status'] == 'done')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("Open", open_c)
    c3.metric("In Progress", inprog)
    c4.metric("Done", done_c)

    st.markdown(
        "<div style='height:0.75rem'></div>",
        unsafe_allow_html=True
    )

    if not all_items:
        st.info(
            "No action items yet. "
            "They appear here after a retro is approved."
        )
        return

    # Filters
    col_f1, col_f2, _ = st.columns([1.5, 1.5, 3])

    with st.spinner("Loading filters..."):
        past = get_all_past_retros()

    sprint_map = {'all': 'All Sprints'}
    sprint_map.update({r['id']: r['sprint_name'] for r in past})

    with col_f1:
        sel_sprint = st.selectbox(
            "Sprint",
            options=list(sprint_map.keys()),
            format_func=lambda x: sprint_map[x]
        )
    with col_f2:
        sel_status = st.selectbox(
            "Status",
            options=['all', 'open', 'in-progress', 'done'],
            format_func=lambda x: (
                'All Statuses' if x == 'all' else
                'Open' if x == 'open' else
                'In Progress' if x == 'in-progress' else 'Done'
            )
        )

    st.markdown(
        "<div style='height:0.5rem'></div>",
        unsafe_allow_html=True
    )

    # Apply filters
    items = (
        get_action_items_by_session(sel_sprint)
        if sel_sprint != 'all'
        else all_items
    )
    if sel_status != 'all':
        items = [
            i for i in items if i['status'] == sel_status
        ]

    if not items:
        st.info("No items match the selected filters.")
        return

    # Group by sprint
    groups = {}
    for item in items:
        groups.setdefault(item['sprint_name'], []).append(item)

    for sprint_name, sprint_items in groups.items():
        st.write(f"**{sprint_name}**")

        with st.container(border=True):
            h1, h2, h3 = st.columns([4.5, 1.2, 1.5])
            h1.caption("ACTION ITEM")
            h2.caption("CREATED")
            h3.caption("STATUS")

            st.divider()

            for idx, item in enumerate(sprint_items):
                r1, r2, r3 = st.columns([4.5, 1.2, 1.5])

                with r1:
                    st.write(item['item_text'])
                with r2:
                    st.caption(item['created_at'][:10])
                with r3:
                    cur = STATUS_OPTIONS.index(item['status'])
                    new_label = st.selectbox(
                        f"s_{item['id']}",
                        options=STATUS_LABELS,
                        index=cur,
                        label_visibility="collapsed",
                        key=f"st_{item['id']}"
                    )
                    new_status = STATUS_OPTIONS[
                        STATUS_LABELS.index(new_label)
                    ]
                    if new_status != item['status']:
                        with st.spinner("Updating status..."):
                            update_action_item_status(
                                item['id'], new_status
                            )
                        st.toast(
                            "Status updated.",
                            icon="✅"
                        )
                        st.rerun()

                if idx < len(sprint_items) - 1:
                    st.divider()

        st.markdown(
            "<div style='height:0.5rem'></div>",
            unsafe_allow_html=True
        )