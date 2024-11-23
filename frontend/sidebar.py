import streamlit as st


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