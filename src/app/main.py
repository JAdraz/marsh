import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Financial Dashboard", layout="wide")

@st.cache_data
def load_data():
    # Local Run
    # df = pd.read_csv("/Users/jesusadraz/Documents/marsh/src/data/Transactions/2024_2.csv")
    # Cloud Run
    df = pd.read_csv("src/data/Transactions/2024_2.csv")
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

df = load_data()

def apply_filters(df, clients, countries, currencies, start_date, end_date):
    filtered_df = df.copy()
    if clients:
        filtered_df = filtered_df[filtered_df['Client'].isin(clients)]
    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
    if currencies:
        filtered_df = filtered_df[filtered_df['Currency'].isin(currencies)]
    filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]
    return filtered_df

st.title("Financial Dashboard")

st.sidebar.header("Filters")
selected_clients = st.sidebar.multiselect("Select Clients", options=df['Client'].unique())
selected_countries = st.sidebar.multiselect("Select Countries", options=df['Country'].unique())
selected_currencies = st.sidebar.multiselect("Select Currencies", options=df['Currency'].unique())

min_date = df['Date'].min()
max_date = df['Date'].max()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = apply_filters(df, selected_clients, selected_countries, selected_currencies, start_date, end_date)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Transactions (USD B)", f"{filtered_df['USD_M'].sum() / 1000:.2f}")
with col2:
    st.metric("Total Clients", filtered_df['Client'].nunique())
with col3:
    st.metric("Total Countries", filtered_df['Country'].nunique())
with col4:
    st.metric("Total Currencies", filtered_df['Currency'].nunique())

@st.cache_data
def create_chart(data, chart_type, x, y, title):
    if chart_type == 'line':
        fig = px.line(data, x=x, y=y, title=title)
    elif chart_type == 'bar':
        fig = px.bar(data, x=x, y=y, title=title)
    elif chart_type == 'pie':
        fig = px.pie(data, values=y, names=x, title=title)
    return fig

daily_transactions = filtered_df.groupby('Date')['USD_M'].sum().reset_index()
fig_time = create_chart(daily_transactions, 'line', 'Date', 'USD_M', "Transactions Over Time (USD M)")
st.plotly_chart(fig_time, use_container_width=True)

top_clients = filtered_df.groupby('Client')['USD_M'].sum().sort_values(ascending=False).head(10).reset_index()
fig_clients = create_chart(top_clients, 'bar', 'Client', 'USD_M', "Top 10 Clients by Transaction Volume (USD M)")
st.plotly_chart(fig_clients, use_container_width=True)

country_trans = filtered_df.groupby('Country')['USD_M'].sum().sort_values(ascending=False).head(15).reset_index()
fig_countries = create_chart(country_trans, 'pie', 'Country', 'USD_M', "Transaction Distribution by Country (USD M)")
st.plotly_chart(fig_countries, use_container_width=True)

currency_counts = filtered_df['Currency'].value_counts().head(10).reset_index()
currency_counts.columns = ['Currency', 'Count']
fig_currency = create_chart(currency_counts, 'bar', 'Currency', 'Count', "Currency Distribution (by Transaction Count)")
st.plotly_chart(fig_currency, use_container_width=True)

st.subheader("Filtered Data (First 1000 rows)")
st.dataframe(filtered_df.head(1000))

if st.button("Prepare CSV for Download"):
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_financial_data.csv",
        mime="text/csv",
    )