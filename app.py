import streamlit as st
import yfinance as yf
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)


# Function to fetch financial data and calculate key metrics
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info

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


def format_in_indian_style(number):
    """Formats numbers into Indian numbering style (Lakhs, Crores, Thousands of Crores)."""
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


def display_metric_explanation(metric_name):
    explanations = {
        "Total Assets": "The total value of everything the company owns. Higher assets can mean more growth potential.",
        "Total Liabilities": "The total debt the company owes. Less debt is often better for stability.",
        "Long Term Debt": "Debt that is due in more than one year. It indicates the company’s long-term financial health.",
        "EPS": "Earnings Per Share – how much profit the company generates per share. A higher EPS indicates better profitability.",
        "P/E Ratio": "Price-to-Earnings ratio – compares the price of the stock to its earnings. A high P/E ratio could indicate an overvalued stock.",
        "ROE": "Return on Equity – measures profitability based on shareholder equity. A higher ROE is generally good for investors.",
        "Net Profit Margin": "The percentage of revenue that becomes profit. A higher margin means the company is better at converting sales into actual profit.",
        "Dividend Yield": "The annual dividend payment divided by the stock price. A higher yield is attractive to income-focused investors."
    }
    return explanations.get(metric_name, "No explanation available.")


# Custom CSS for Background
st.markdown(
    """
    <style>
    /* Full-screen background */
    .stApp {
        background-image: url('blob:https://web.telegram.org/6e053a8d-fdf0-4e1b-acba-1367d049431b');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Semi-transparent container for content */
    .main {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 10px;
    }

    /* Card styling */
    .stTabs {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True
)

# Streamlit UI setup
st.title('**Fundamental Analysis Tool**')
st.sidebar.title("Options")
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.NS").upper()

if ticker_input:
    company_data = fetch_company_data(ticker_input)

    if company_data:
        with st.container():
            st.subheader(f"Company Overview: {company_data['Company']}")
            st.write(f"**Business Summary**: {company_data['Business Summary']}")
            st.write(f"**Sector**: {company_data['Sector']}")
            st.write(f"**Industry**: {company_data['Industry']}")
            st.write(f"**Market Cap**: {format_in_indian_style(company_data['Market Cap'])}")

        # Tabs for different sections
        tab1, tab2, tab3 = st.tabs(["Fundamentals", "Financials", "Financial Statements"])

        with tab1:
            st.subheader("Fundamentals")
            st.write(f"**EPS**: ₹{company_data['EPS']:.2f}" if company_data['EPS'] else "Data not available")
            st.write(display_metric_explanation("EPS"))

            st.write(f"**P/E Ratio**: {company_data['P/E Ratio']:.2f}" if company_data['P/E Ratio'] else "Data not available")
            st.write(display_metric_explanation("P/E Ratio"))

            st.write(f"**ROE**: {company_data['ROE']*100:.2f}%" if company_data['ROE'] else "Data not available")
            st.write(display_metric_explanation("ROE"))

            st.write(f"**Net Profit Margin**: {company_data['Net Profit Margin']*100:.2f}%" if company_data['Net Profit Margin'] else "Data not available")
            st.write(display_metric_explanation("Net Profit Margin"))

            st.write(f"**Dividend Yield**: {company_data['Dividend Yield']*100:.2f}%" if company_data['Dividend Yield'] else "Data not available")
            st.write(display_metric_explanation("Dividend Yield"))

        with tab2:
            st.subheader("Financials")
            st.write(f"**Total Assets**: {format_in_indian_style(company_data['Total Assets'])}")
            st.write(display_metric_explanation("Total Assets"))

            st.write(f"**Total Liabilities**: {format_in_indian_style(company_data['Total Liabilities'])}")
            st.write(display_metric_explanation("Total Liabilities"))

            st.write(f"**Long Term Debt**: {format_in_indian_style(company_data['Long Term Debt'])}")
            st.write(display_metric_explanation("Long Term Debt"))

        with tab3:
            st.subheader("Financial Statements")
            st.write("**Quarterly Balance Sheet**:")
            st.write(company_data['Quarterly Balance Sheet'])

            st.write("**Quarterly Cash Flow Statement**:")
            st.write(company_data['Quarterly Cash Flow'])

            st.write("**Calendar Data**:")
            st.write(company_data['Calendar'])
