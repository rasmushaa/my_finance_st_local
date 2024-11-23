import streamlit as st

st.session_state['user'].logout()
st.switch_page('frontend/account/login.py')