# Stock Sentiment Analysis Dashboard 🚀📈

A real-time stock analysis tool that combines market data with news sentiment to provide trading insights for major public companies.

## Features

- **Real-time Stock Data**: Fetches current market data using the Yahoo Finance API
- **News Sentiment Analysis**: Analyzes recent news headlines using TextBlob for sentiment scoring
- **Interactive Dashboard**: Built with Streamlit for a responsive user experience
- **Trading Signals**: Provides buy/sell/hold recommendations based on composite analysis
- **Sector-based Filtering**: Filter companies by their market sectors
- **Visual Analytics**: 
  - Candlestick charts for stock price movements
  - Sentiment trend visualization
  - Performance metrics
  - Recent headlines display

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stock-sentiment-analysis.git
cd stock-sentiment-analysis
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your News API key:
```
NEWS_API_KEY=your_api_key_here
```

## Dependencies

- streamlit
- pandas
- yfinance
- textblob
- plotly
- requests
- python-dotenv

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Select a sector and company from the sidebar
3. Click "Analyze" to generate insights
4. View the trading recommendation, sentiment metrics, and price charts
5. Browse through recent headlines and their sentiment scores

## How It Works

1. **Data Collection**:
   - Fetches stock price data using yfinance
   - Retrieves recent news headlines via News API
   - Processes and aggregates data for analysis

2. **Sentiment Analysis**:
   - Analyzes news headlines using TextBlob
   - Calculates sentiment scores (-1 to 1)
   - Aggregates daily sentiment metrics

3. **Trading Signals**:
   - Combines price movements and sentiment trends
   - Generates trading recommendations based on composite analysis
   - Provides visual indicators for decision support

## Configuration

The application monitors 20 major companies across various sectors including:
- Technology (AAPL, MSFT, GOOGL, etc.)
- Financial Services (JPM, BAC)
- Healthcare (JNJ, UNH)
- Energy (XOM, CVX)
- Entertainment (DIS, NFLX)
- And more...

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions or feedback, please contact:
- Email: kirouanemed@protonmail.com

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Trading decisions should not be based solely on this analysis. Always conduct thorough research and consult with financial advisors before making investment decisions.
