import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from textblob import TextBlob
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import logging
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Company:
    name: str
    ticker: str
    sector: str

class StockSentimentAnalyzer:
    def __init__(self):
        self.api_key = st.secrets.get("NEWS_API_KEY", os.getenv('NEWS_API_KEY'))
        self.companies = {
            'AAPL': Company('Apple Inc', 'AAPL', 'Technology'),
            'MSFT': Company('Microsoft Corp', 'MSFT', 'Technology'),
            'GOOGL': Company('Alphabet Inc', 'GOOGL', 'Technology'),
            'TSLA': Company('Tesla Inc', 'TSLA', 'Automotive'),
            'AMZN': Company('Amazon.com Inc', 'AMZN', 'E-commerce'),
            'META': Company('Meta Platforms Inc', 'META', 'Technology'),
            'NVDA': Company('NVIDIA Corporation', 'NVDA', 'Technology'),
            'JPM': Company('JPMorgan Chase & Co', 'JPM', 'Financial Services'),
            'BAC': Company('Bank of America Corp', 'BAC', 'Financial Services'),
            'WMT': Company('Walmart Inc', 'WMT', 'Retail'),
            'PG': Company('Procter & Gamble Co', 'PG', 'Consumer Goods'),
            'JNJ': Company('Johnson & Johnson', 'JNJ', 'Healthcare'),
            'UNH': Company('UnitedHealth Group Inc', 'UNH', 'Healthcare'),
            'XOM': Company('Exxon Mobil Corp', 'XOM', 'Energy'),
            'CVX': Company('Chevron Corporation', 'CVX', 'Energy'),
            'KO': Company('Coca-Cola Co', 'KO', 'Beverages'),
            'PEP': Company('PepsiCo Inc', 'PEP', 'Beverages'),
            'DIS': Company('Walt Disney Co', 'DIS', 'Entertainment'),
            'NFLX': Company('Netflix Inc', 'NFLX', 'Entertainment'),
            'ADBE': Company('Adobe Inc', 'ADBE', 'Technology')
        }

    def get_trading_advice(self, sentiment_df: pd.DataFrame, stock_df: pd.DataFrame) -> Tuple[str, str]:
        if sentiment_df.empty or stock_df.empty or len(stock_df) < 2:
            return "NO ADVICE", "gray"

        avg_sentiment = sentiment_df['sentiment'].mean()
        price_change = ((stock_df['Close'].iloc[-1] / stock_df['Close'].iloc[0]) - 1) * 100
        
        if avg_sentiment > 0.05:
            return "BUYING ADVISED", "green"
        elif avg_sentiment < 0.04:
            return "SELLING ADVISED", "red"
        return "HOLD POSITION", "orange"

    def fetch_news_headlines(self, company: Company, days: int = 2) -> List[Tuple[datetime, str, float]]:
        if not self.api_key:
            st.error("Please set your News API key in the sidebar")
            return []

        headlines = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f"{company.name} OR {company.ticker}",
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "language": "en",
                "sortBy": "publishedAt",
                "apiKey": self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'ok':
                st.warning(f"Error fetching news: {data.get('message', 'Unknown error')}")
                return []

            for article in data.get('articles', []):
                try:
                    date = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                    blob = TextBlob(article['title'])
                    sentiment = blob.sentiment.polarity
                    headlines.append((date, article['title'], sentiment))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing article: {e}")
                    continue

            return headlines
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

    def get_stock_data(self, ticker: str, days: int = 2) -> pd.DataFrame:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, interval='1d')
            
            if not df.empty:
                df['Date'] = df.index
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching stock data: {e}")
            return pd.DataFrame()

    def analyze_sentiment(self, headlines: List[Tuple[datetime, str, float]]) -> pd.DataFrame:
        if not headlines:
            return pd.DataFrame(columns=['date', 'headline', 'sentiment'])

        results = []
        for date, headline, sentiment in headlines:
            results.append({
                'date': date,
                'headline': headline,
                'sentiment': sentiment
            })
        return pd.DataFrame(results)

def create_visualization(stock_data: pd.DataFrame, sentiment_data: pd.DataFrame, company_name: str) -> Optional[go.Figure]:
    if stock_data.empty:
        return None

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f"{company_name} Stock Price", "Sentiment Analysis"),
        vertical_spacing=0.2,
        row_heights=[0.7, 0.3]
    )

    fig.add_trace(
        go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close'],
            name="Stock Price"
        ),
        row=1, col=1
    )

    if not sentiment_data.empty:
        daily_sentiment = sentiment_data.groupby(sentiment_data['date'].dt.date)['sentiment'].mean().reset_index()
        fig.add_trace(
            go.Scatter(
                x=daily_sentiment['date'],
                y=daily_sentiment['sentiment'],
                mode='lines+markers',
                name="Daily Sentiment",
                marker=dict(size=8)
            ),
            row=2, col=1
        )

    fig.update_layout(
        height=800,
        title_text=f"{company_name} Market Analysis Dashboard",
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    return fig

def main():
    st.set_page_config(page_title="Stock Sentiment Analysis", layout="wide")
    st.title("Stock Sentiment Analysis Dashboard")

    analyzer = StockSentimentAnalyzer()
    st.sidebar.title("Controls")
    
    if not analyzer.api_key:
        api_key = st.sidebar.text_input("Enter News API key:", type="password")
        if api_key:
            analyzer.api_key = api_key

    sectors = sorted(set(company.sector for company in analyzer.companies.values()))
    selected_sector = st.sidebar.selectbox("Select Sector:", ["All"] + sectors)
    
    filtered_companies = {
        ticker: company for ticker, company in analyzer.companies.items()
        if selected_sector == "All" or company.sector == selected_sector
    }
    
    selected_ticker = st.sidebar.selectbox(
        "Select Company:",
        options=list(filtered_companies.keys()),
        format_func=lambda x: f"{x} - {filtered_companies[x].name}"
    )

    if st.sidebar.button("Analyze") and analyzer.api_key:
        try:
            with st.spinner("Analyzing market data..."):
                company = analyzer.companies[selected_ticker]
                headlines = analyzer.fetch_news_headlines(company, days=2)
                sentiment_df = analyzer.analyze_sentiment(headlines)
                stock_df = analyzer.get_stock_data(company.ticker, days=2)
                advice, color = analyzer.get_trading_advice(sentiment_df, stock_df)
                
                st.markdown(f"<h2 style='text-align: center; color: {color};'>{advice}</h2>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Sentiment", 
                             f"{sentiment_df['sentiment'].mean():.2f}" if not sentiment_df.empty else "N/A")
                with col2:
                    st.metric("Headlines Analyzed", len(headlines))
                with col3:
                    if not stock_df.empty and len(stock_df) > 1:
                        perf = ((stock_df['Close'].iloc[-1] / stock_df['Close'].iloc[0]) - 1) * 100
                        st.metric("Stock Performance", f"{perf:.1f}%")

                fig = create_visualization(stock_df, sentiment_df, company.name)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Insufficient data for visualization.")

                if not sentiment_df.empty:
                    st.subheader("Recent Headlines")
                    display_df = sentiment_df.sort_values('date', ascending=False)
                    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d %H:%M')
                    st.dataframe(
                        display_df[['date', 'headline', 'sentiment']],
                        use_container_width=True
                    )
                else:
                    st.info("No headlines available for the selected period.")

        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            logger.error(f"Analysis error: {str(e)}")

if __name__ == "__main__":
    main()
