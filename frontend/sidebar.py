import streamlit as st
from streamlit_javascript import st_javascript


def __reset_st_pagestate_on_entry():
    """ The 'pagestate' in the st.session_state
    is used to store the State Machine State
    on pages that require more advanced logic.
    The state is always reseted when user inters to another page.
    active_page is used to detect the change on page.
    """
    if 'pagestate' not in st.session_state:
        st.session_state.active_page = ''
        st.session_state.pagestate = 0

    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    page= '' if isinstance(url, int) or '/' not in url else url.rsplit('/', 1)[1]
    if page != st.session_state.active_page:
        st.session_state.active_page = page
        st.session_state.pagestate = 0


def __authenticated_menu():
    """ Show only the login menu 
    for unauthenticated users, and different admin levels
    """
    st.sidebar.subheader('Account:')
    st.sidebar.page_link(st.Page('frontend/account/logout.py'), label='Logout', icon=':material/logout:')

    st.sidebar.subheader('Uppload Files:')
    st.sidebar.page_link(st.Page('frontend/banking/file_input.py'), label='Transactions', icon=':material/payments:')
    st.sidebar.page_link(st.Page('frontend/assets/uppload_file.py'), label='Assets', icon=':material/account_balance:')
    st.sidebar.page_link(st.Page('frontend/banking/export.py'), label='Export', icon=':material/download:')

    disabled = st.session_state['user'].role != 'admin'
    st.sidebar.subheader('Manage Application:')
    st.sidebar.page_link(st.Page('frontend/admin/ai.py'), label='AI', icon=':material/robot_2:', disabled=disabled)
    st.sidebar.page_link(st.Page('frontend/admin/categories.py'), label='Categories', icon=':material/settings:', disabled=disabled)



def __unauthenticated_menu():
    """ Show only the login menu 
    for unauthenticated users
    """
    st.sidebar.page_link('frontend/account/login.py', label='Login', icon=':material/login:')


def init_to_user_access_level():
    """ Determine if a user is logged in or not, 
    then show the correct navigation menu
    """
    if 'user' in st.session_state and st.session_state['user'].is_logged_in(): # Only if 'user' exists and is logged in!
        __authenticated_menu()
    else:
        __unauthenticated_menu()
    #__reset_st_pagestate_on_entry()