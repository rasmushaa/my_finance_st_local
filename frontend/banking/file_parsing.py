import streamlit as st
from frontend.utils import valid_user_state

valid_user_state()


# Utilities
def predict():
    if not st.session_state['api']['ml'].has_model():
        st.session_state['api']['ml'].load_model_from_gcs()

    preds, probs = st.session_state['api']['ml'].predict(st.session_state['banking_file'])
    st.session_state['banking_file']['Category'] = preds
    st.session_state['banking_file']['Confidence'] = probs

def highlight_rows(row):
    return ['background-color: grey' if i % 2 != 0 else '' for i in range(len(row))]

@st.cache_data
def get_categories():
    all_categories = st.session_state['api']['categories'].get_expenditure_categories()
    old_categories = list(st.session_state['api']['ml'].get_priors().keys()) # Get existing categories in desc prior order
    added_cateogries = [item for item in all_categories if item not in old_categories]
    old_categories.extend(added_cateogries)
    return old_categories

def push_data():
    if not st.session_state['api']['ml'].has_model():
        st.subheader(":orange[Nice work. Now, lets go to train a new model for you at the AI-page, and switch to Admin role from the Login page, if not already in use)]")
    else:
        st.subheader(":orange[Looking good, lets go to see the Assets-page!]")

    if st.session_state['api']['files'].add_transactions_to_database(edited_df, user_name=st.session_state['user'].name):
            st.success('File added successfully')
    else:
        st.error('File was not uploaded!')



if st.session_state['banking_file']['Category'].isna().all():
    predict()

if not st.session_state['api']['ml'].has_model():
    st.subheader(":orange[5. It seems you don't have an active AI model yet, you have to manually insert all categories by using arrows and enter, or use mouse.]")
else:
    st.subheader(":orange[8. The model is now actice, and it has updated the most likley category to all rows, and the condifence of that prediction is also visible. You should still be cautios and at least validate all rows by yourself.]")

edited_df = st.data_editor(
    st.session_state['banking_file'],
    column_config={
        'KeyDate': st.column_config.Column(
            'Date',
            disabled=True,
            width='small'
        ),
        'Amount': st.column_config.NumberColumn(
            'Amount [€]',
            format="%.2f",
            disabled=True,
            width='small'
        ),
        'Receiver': st.column_config.Column(
            'Receiver',
            disabled=True
        ),
        'Category': st.column_config.SelectboxColumn(
            'Category',
            options=get_categories()
        ),
        'Confidence': st.column_config.ProgressColumn(
            'Confidence',
            format='%.1f',
            min_value=0.0,
            max_value=1.0,
        ),
    },
    use_container_width=True,
    hide_index=True,
    height=35*len(st.session_state['banking_file'])+38
)


if not st.session_state['api']['ml'].has_model():
    st.subheader(":orange[6. After processing all rows, you can push the latest data, and don't wory it has sanity checks to prevent accidental uploads.]")

if st.button('Upload the file', use_container_width=True):

    if st.session_state['api']['files'].date_not_in_transactions_table(edited_df['KeyDate'].min(), user_name=st.session_state['user'].name): # Check for duplicated Dates
        push_data()

    else:
        st.error(f"There already exists DATE after '{edited_df['KeyDate'].min()}' for user '{st.session_state['user'].name}'")

        st.button('Force Push Data?', on_click=push_data, use_container_width=True)


