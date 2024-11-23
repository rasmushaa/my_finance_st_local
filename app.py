import streamlit as st
from frontend import sidebar
from backend.categories.api import CategoriesAPI
from backend.credentials.api import CredentialsAPI
from backend.ml.api import MLAPI
from backend.files.api import FilesAPI


# Main entry-point and the event-loop, that runs only once.
# Everyihg on this file is executed before all other Pages.

# Define all existing st.Page 'Pages' that are navigateable (required to do so),
# by the st.switch_page and st.page_link functions,
# but hide the default navigation,
# because that is dynamically changed in the code.


def init_apis():
    if 'api' not in st.session_state:
        st.session_state['api'] = {}
        st.session_state['api']['credentials']  = CredentialsAPI()
        st.session_state['api']['categories']   = CategoriesAPI()
        st.session_state['api']['ml']           = MLAPI()
        st.session_state['api']['files']        = FilesAPI()


# Application Constants
st.set_page_config(page_title='My Finance')
st.logo('frontend/app_assets/logo.png', size='large')

all_pages = [
    st.Page('frontend/account/login.py', default=True),
    st.Page('frontend/account/logout.py'),
    st.Page('frontend/banking/file_input.py'),
    st.Page('frontend/banking/file_parsing.py'),
    st.Page('frontend/banking/export.py'),
    st.Page('frontend/assets/uppload_file.py'),
    st.Page('frontend/admin/ai.py'),
    st.Page('frontend/admin/categories.py')
]

pg = st.navigation(
    all_pages,
    position='hidden'
)

init_apis() # Initialize All Backend APIs right away

sidebar.init_to_user_access_level() # Update the navigation accordingly to the user access level after each reload/page switch

pg.run() # Main Event Run


