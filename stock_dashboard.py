import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv('API_KEY')  # Load API key from .env file
BASE_URL = 'https://www.alphavantage.co/query'

# Function to fetch intraday stock data
def fetch_stock_data(symbol):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '5min',
        'apikey': API_KEY,
        'outputsize': 'compact'
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Check if the API returned valid data
    if 'Time Series (5min)' not in data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(data['Time Series (5min)'], orient='index')
    df = df.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. volume': 'Volume'
    })
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()  # Sort by timestamp (most recent last)
    return df

# Function to calculate key metrics
def calculate_metrics(df):
    latest = df.iloc[-1]
    previous_close = df.iloc[-2]['Close'] if len(df) > 1 else latest['Close']
    current_price = latest['Close']
    change = current_price - previous_close
    change_percent = (change / previous_close) * 100
    volume = latest['Volume']
    return current_price, change, change_percent, volume

# Function to create candlestick chart
def create_candlestick_chart(df):
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )
    ])
    fig.update_layout(
        title='Stock Price Candlestick Chart',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False,
        template='plotly_dark'
    )
    return fig

# Streamlit app
def main():
    st.title('Real-Time Stock Market Dashboard')
    
    # Stock selection
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    symbol = st.selectbox('Select Stock Symbol', stocks)
    
    # Placeholder for chart and metrics
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()
    
    # Auto-refresh loop
    while True:
        df = fetch_stock_data(symbol)
        if df is None:
            st.error('Error fetching data. Please check your API key or symbol.')
            break
        
        # Display metrics
        current_price, change, change_percent, volume = calculate_metrics(df)
        metrics_placeholder.markdown(f"""
            **Current Price**: ${current_price:.2f}  
            **Change**: ${change:.2f} ({change_percent:.2f}%)  
            **Volume**: {volume:,.0f}
        """)
        
        # Display candlestick chart
        fig = create_candlestick_chart(df)
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Refresh every 60 seconds
        time.sleep(60)
        st.experimental_rerun()

if __name__ == '__main__':
    main()