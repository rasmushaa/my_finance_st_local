import streamlit as st
import plotly.graph_objects as go
from frontend.utils import valid_user_state

valid_user_state()


# Utility
@st.cache_data
def st_wrapper_pull_training_data():
    return st.session_state['api']['ml'] .pull_training_data()


#Training Section
st.title('Train a new Naive-Bayes Model')

st.subheader(":orange[7. Now you can use your own data to teach the AI to parse it for you.]")

# Pull the training Data
df = st.session_state['api']['ml'] .pull_training_data() # Override cache for demo

if df.shape[0] == 0:
    st.error('There is not Data to train a mode. Uppload new parsed Banking files before.')
    st.stop()

# Select the date-range
d0 = st.date_input(
    'Training Data Range Start',
    df['date'].min(),
    df['date'].min(),
    df['date'].max(),
    format='YYYY-MM-DD',
)
d1 = st.date_input(
    'Training Data Range End',
    df['date'].max(),
    df['date'].min(),
    df['date'].max(),
    format='YYYY-MM-DD',
)
df = df.loc[(df['date'] > d0) & (df['date'] < d1)]
df = df.drop('date', axis=1) # Remove the date, that is only used to select the date range

# Display the selected training data
st.subheader(f'Selected Training Data: {df.shape[0]} Rows')
st.dataframe(df, use_container_width=True)

# Train Valid Split
st.subheader('Training-Validation Split')
ratio = st.slider('Percentage', 0.05, 0.95, 0.90, 0.01)
df_train = df.iloc[:int(df.shape[0] * ratio)]
df_valid = df.iloc[int(df.shape[0] * ratio):]

if df_train.shape[0] <  2:
    st.subheader(":orange[You didn't Categorize enough rows to train the model, go back to add more data with the Labels :(]")
    st.stop()


# Fit the model automatically constantly (if json is shown, this may be slow)
st.session_state['api']['ml'].train_new_model(df_train, target_col='category')


st.subheader(":orange[You can simply hit Save, or see what all of the numbers are telling to you.]")
# Save the model
if st.button('Save the Model', use_container_width=True):
    st.session_state['api']['ml'].save_model_to_gcs()
    st.subheader(":orange[A new model was trained! You can now go back to the Transaction page and uppload yout 2nd testfile!]")


# Results section
st.divider()
st.title('Model Results')

# Prior Prob. Distribution
priors = st.session_state['api']['ml'].get_priors()
fig = go.Figure(data=[go.Bar(
    x=list(priors.keys()),
    y=list(priors.values()),
    marker_color='red',
    hovertemplate = '%{y:.2f}<extra></extra>'
)])
fig.update_layout(hovermode='x unified')
fig.update_layout(yaxis_title='Prior Prob. [%]', title='Class Prior Propabilities')
st.plotly_chart(fig, use_container_width=True)

# Accuracy Plot
st.subheader('Validation data Results')
max_error = st.number_input('Maximum Allowed Error on Placement', 0, 5, 1)
if df_valid.shape[0] <  2:
    st.subheader(":orange[You didn't Categorize enough rows to run this analysis, moving the Train/Valid split may help, or you just have to add more data...]")
    st.stop()
wa, stats = st.session_state['api']['ml'].validate_model(df_valid, target_col='category', accepted_error=max_error)
st.subheader(f'Total Weighted Accuracy: {wa*100:.2f}%')
st.dataframe(
    stats,
    column_config={
        'y_valid': st.column_config.Column(
            'Class',
        ),
        'Events': st.column_config.Column(
            'Class',
        ),
        'place_q50': st.column_config.NumberColumn(
            'Median Place',
            format="%.2f",
        ),
        'accuracy': st.column_config.ProgressColumn(
            'Accuracy',
            format='%.2f',
            min_value=0.0,
            max_value=1.0,
        ),
    },
    use_container_width=True
)


# Print all Likelihoods as JSON
if st.toggle('Show Likelihoods'):
    likes = st.session_state['api']['ml'].get_likelihoods()
    st.write(likes)