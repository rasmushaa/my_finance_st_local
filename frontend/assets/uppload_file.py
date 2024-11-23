import streamlit as st
import plotly.graph_objects as go
from frontend.utils import valid_user_state

valid_user_state()


st.subheader(":orange[9. This page is used to tack your Balance sheet, and investments performance. You can uppload some numbers here and Uppload those]")

# Utils
def add_trace(name, value, fig, color):
    x = [f'{quarter}Q-{date.year}']
    fig.add_trace(
        go.Bar(
            x=x, 
            y=[value], 
            customdata=[value/1000],
            name=name, 
            meta=[name], 
            text=f'<b>{value/1000:.0f}k€</b> ', 
            textfont_color='black',
            textposition='auto',
            hovertemplate='<b>%{meta[0]}:</b> %{customdata:.1f}k€ <extra></extra>',
            hoverinfo='skip',
            showlegend=False,
            marker_color=color, 
            marker_line_color=color,
            #marker_line_width=2, 
            opacity=1
        )
    )

@st.cache_data
def st_wrapper_get_collector():
    return st.session_state['api']['files'].get_asset_data_collector()

def push_data():
    if st.session_state['api']['files'].add_assets_to_database(date, st.session_state['user'].name, collector):
        st.success('File added successfully')
    else:
        st.error('File was not uploaded!')


# The page
st.title('Quarterly Asset information')

# Date selection
date = st.date_input(
    'Input date',
    format='YYYY-MM-DD',
)
quarter = (date.month - 1) // 3 + 1

# Init collector
collector = st_wrapper_get_collector()

# Balance sheet input column
col1, col2, col3 = st.columns([10, 2, 13])

with col1:
    st.subheader('Total Equity')
    collector.capital_assets_purchase_price = st.number_input('Capital Assets Purchase price', value=0, min_value=0)
    collector.unrealized_capital_gains = st.number_input('Capital Assets Unrealized Gains', value=0)
    collector.capital_assets_value = collector.unrealized_capital_gains + collector.capital_assets_purchase_price # No need to ask user to sum this
    collector.apartment = st.number_input('Apartment', value=0, min_value=0)
    collector.cash = st.number_input('Cash', value=0, min_value=0)
    collector.other_assets = st.number_input('Other-Assets', value=0, min_value=0)

    st.subheader('Total Liabilities')
    collector.mortgage = st.number_input('Mortgage', value=0, max_value=0)
    collector.student_loan = st.number_input('Student loan', value=0, max_value=0)
    collector.other_loans = st.number_input('Other-Loans', value=0, max_value=0)


# Balance sheet visualization
with col3:
    fig = go.Figure()

    add_trace('Mortgage', collector.mortgage , fig, color='rgb(179, 0, 0)')
    add_trace('Student loan', collector.student_loan , fig, color='rgb(230, 0, 0)')
    add_trace('other_loans', collector.other_loans , fig, color='rgb(255, 26, 26)')

    add_trace('Cash', collector.cash, fig, color='rgb(0, 77, 0)')
    add_trace('Apartment', collector.apartment, fig, color='rgb(0, 102, 0)')
    add_trace('Capital Assets', collector.capital_assets_purchase_price, fig, color='rgb(0, 128, 0)')
    add_trace('Unrealized Gains', collector.unrealized_capital_gains, fig, color='rgb(0, 153, 0)')
    add_trace('Other-Assets', collector.other_assets, fig, color='rgb(0, 200, 0)')

    fig.update_layout(barmode='relative',height=800)
    st.plotly_chart(fig, use_container_width=True)


# Investment performance inputs
st.header('Investment Performance Metrics')
collector.realized_capital_gains = st.number_input('Realized Capital Gains', value=0, min_value=0)
collector.realized_capital_losses = st.number_input('Realized Capital Losses', value=0, max_value=0)
collector.dividends = st.number_input('Received Dividens', value=0, min_value=0)


# Push new data
st.header('Uppload all Metrics')
if st.button('Push'):

    if st.session_state['api']['files'].date_not_in_assets_table(date, user_name=st.session_state['user'].name): # Check for duplicated Dates
        push_data()
        st.subheader(":orange[Now you can go to the Export page to get your freshly created dataset!]")

    else:
        st.error(f"There already exists DATE after '{date}' for user '{st.session_state['user'].name}'")

        st.button('Force Push Data?', on_click=push_data, use_container_width=True)