import os
import streamlit as st
import hashlib
import random
from frontend.utils import init_random_captcha_color,  validate_captcha_color
from backend.credentials.user import User



col1, col2 = st.columns([3, 1])
col2.image('frontend/app_assets/logo.png')

col1.title(f'My Finance App Demo')

col1.markdown('''This tuorial requires no finance or coding knowledge\\
              and you can just :orange[**follow to guides**] ''')

col1.markdown('''This online Application helps you to\\
              automatically process your Banking files :moneybag:\\
              with a help of an AI :robot_face:''')

url = 'https://github.com/rasmushaa/my_finance_st_local'
col1.markdown('The code [link](%s)' % url)
col1.markdown('- Is easy to make it yours :handshake:')
col1.markdown('- Builds an actual Local SQL Database :floppy_disk:')
col1.markdown('- Allows you to analyse your data with *PowerBI*, *LookerStudio*, *Ecxel* :bar_chart:')

col1.markdown('''This online demo does not save your data,\\
              but you can export it\\
              to try different visualization methods :wink:''')

st.divider()



st.subheader(':orange[1. Get your testing files]')
with open("frontend/app_assets/your_banking_file1.csv", "rb") as file:
    btn = st.download_button(
        label="Download CSV1",
        data=file,
        file_name='your_banking_file1.csv',
        mime='text/csv',
    )
with open("frontend/app_assets/your_banking_file2.csv", "rb") as file:
    btn = st.download_button(
        label="Download CSV2",
        data=file,
        file_name='your_banking_file2.csv',
        mime='text/csv',
    )


st.subheader(':orange[2. Input your user info (Use admin for extra features)]')
name = st.text_input(
        'Account Username',
        'DemoUser',
    )

admin = st.checkbox('Are you Admin?')
role = 'admin' if admin else 'user'

# Init the loging sequence
if st.button('Login', icon=":material/login:"):

    st.session_state['user'] = User(id=1, name=name, role=role, is_logged_in=True) 
    st.switch_page('frontend/banking/file_input.py')