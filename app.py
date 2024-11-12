import streamlit as st
import yfinance as yf
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter

# Custom session class to manage caching and rate limiting for API calls
class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

# Initialize the session with rate limiting and caching
session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND * 5)),  # Max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)

# Function to fetch financial data and calculate key metrics
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info

        # Ensure info data is valid
        if not info:
            st.warning(f"No data returned for {ticker}.")
            return None

        balance_sheet = company.quarterly_balance_sheet
        cash_flow = company.quarterly_cashflow
        calendar = company.calendar

        # Financial Metrics
        total_assets = balance_sheet.loc['Total Assets'][0] if 'Total Assets' in balance_sheet.index else None
        total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'][0] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else None
        long_term_debt = balance_sheet.loc['Long Term Debt'][0] if 'Long Term Debt' in balance_sheet.index else None

        # Key Data
        eps = info.get('trailingEps', None)
        pe_ratio = info.get('trailingPE', None)
        roe = info.get('returnOnEquity', None)
        net_profit_margin = info.get('profitMargins', None)
        dividend_yield = info.get('dividendYield', None)
        market_cap = info.get('marketCap', None)
        sector = info.get('sector', None)
        business_summary = info.get('longBusinessSummary', 'No business summary available')
        industry = info.get('industry', None)
        company_name = info.get('longName', ticker)

        return {
            'Company': company_name,
            'Business Summary': business_summary,
            'Sector': sector,
            'Industry': industry,
            'Market Cap': market_cap,
            'EPS': eps,
            'P/E Ratio': pe_ratio,
            'ROE': roe,
            'Net Profit Margin': net_profit_margin,
            'Dividend Yield': dividend_yield,
            'Total Assets': total_assets,
            'Total Liabilities': total_liabilities,
            'Long Term Debt': long_term_debt,
            'Calendar': calendar,
            'Quarterly Balance Sheet': balance_sheet,
            'Quarterly Cash Flow': cash_flow
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Function to format numbers in Indian numbering style (Lakhs, Crores, etc.)
def format_in_indian_style(number):
    """Formats numbers into Indian numbering style."""
    if number is None:
        return "Data not available"
    elif number >= 1e12:  # Thousands of crores
        return f"₹{number / 1e12:.2f} Thousand Crores"
    elif number >= 1e7:  # Crores
        return f"₹{number / 1e7:.2f} Crores"
    elif number >= 1e5:  # Lakhs
        return f"₹{number / 1e5:.2f} Lakhs"
    else:
        return f"₹{number:.2f}"

# Metric explanations for each financial term
def display_metric_explanation(metric_name):
    explanations = {
        "Total Assets": "The total value of everything the company owns.",
        "Total Liabilities": "The total debt the company owes.",
        "Long Term Debt": "Debt that is due in more than one year.",
        "EPS": "Earnings Per Share – profit generated per share.",
        "P/E Ratio": "Price-to-Earnings ratio – compares stock price to earnings.",
        "ROE": "Return on Equity – profitability based on shareholder equity.",
        "Net Profit Margin": "Percentage of revenue that becomes profit.",
        "Dividend Yield": "Annual dividend payment divided by stock price."
    }
    return explanations.get(metric_name, "No explanation available.")

# Streamlit UI setup
st.title('**Fundamental Analysis Tool**')

st.sidebar.title("Options")
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.NS").upper()

if ticker_input:
    company_data = fetch_company_data(ticker_input)

    if company_data:
        # Display Company Overview
        st.subheader(f"Company Overview: {company_data['Company']}")
        st.write(f"**Business Summary**: {company_data['Business Summary']}")
        st.write(f"**Sector**: {company_data['Sector']}")
        st.write(f"**Industry**: {company_data['Industry']}")
        st.write(f"**Market Cap**: {format_in_indian_style(company_data['Market Cap'])}")

        # Display Financial Metrics
        st.subheader("**Fundamentals**")
        
        metrics = {
            "EPS": company_data['EPS'],
            "P/E Ratio": company_data['P/E Ratio'],
            "ROE": company_data['ROE'] * 100 if company_data['ROE'] else None,
            "Net Profit Margin": company_data['Net Profit Margin'] * 100 if company_data['Net Profit Margin'] else None,
            "Dividend Yield": company_data['Dividend Yield'] * 100 if company_data['Dividend Yield'] else None
        }
        
        for metric, value in metrics.items():
            if value is not None:
                st.write(f"**{metric}**: {value:.2f}" if metric != "Market Cap" else f"**{metric}**: {format_in_indian_style(value)}")
            else:
                st.write(f"**{metric}**: Data not available")
            st.write(display_metric_explanation(metric))
        
        # Display Financials
        st.subheader("**Financials**")
        financials = {
            "Total Assets": company_data['Total Assets'],
            "Total Liabilities": company_data['Total Liabilities'],
            "Long Term Debt": company_data['Long Term Debt']
        }
        
        for financial, value in financials.items():
            st.markdown(f"**{financial}**: {format_in_indian_style(value)}" if value else f"**{financial}**: Data not available")
            st.write(display_metric_explanation(financial))
        
        # Display Financial Statements
        st.subheader("**Financial Statements**")
        
        st.write("**Quarterly Balance Sheet**:")
        st.write(company_data['Quarterly Balance Sheet'])
        
        st.write("**Quarterly Cash Flow Statement**:")
        st.write(company_data['Quarterly Cash Flow'])
        
        st.write("**Calendar Data**:")
        st.write(company_data['Calendar'])

    else:
        st.error(f"No data available for ticker '{ticker_input}'. Please check the ticker symbol or try a different one.")
