import yfinance as yf
import streamlit as st

# Function to match labels dynamically and get values from the balance sheet
def get_balance_sheet_value(balance_sheet, possible_labels):
    for label in possible_labels:
        if label in balance_sheet.index:
            return balance_sheet.loc[label].iloc[0]  # Use iloc[0] for positional access
    return None  # Return None if no label matches

# Convert values to Crores
def convert_to_crores(value):
    if value is not None:
        return value / 1e7  # 1 crore = 10 million
    return None

# Function to fetch financial data
@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        balance_sheet = company.balance_sheet
        info = company.info

        # Labels for important balance sheet items
        total_assets_labels = ['Total Assets']
        total_liabilities_labels = ['Total Liabilities', 'Total Liabilities Net Minority Interest']
        current_assets_labels = ['Total Current Assets']
        current_liabilities_labels = ['Total Current Liabilities']
        long_term_debt_labels = ['Long Term Debt', 'Long-Term Debt']
        shareholder_equity_labels = ['Total Stockholder Equity', 'Shareholder Equity']

        # Fetching balance sheet values
        total_assets = get_balance_sheet_value(balance_sheet, total_assets_labels)
        total_liabilities = get_balance_sheet_value(balance_sheet, total_liabilities_labels)
        current_assets = get_balance_sheet_value(balance_sheet, current_assets_labels)
        current_liabilities = get_balance_sheet_value(balance_sheet, current_liabilities_labels)
        long_term_debt = get_balance_sheet_value(balance_sheet, long_term_debt_labels)
        shareholder_equity = get_balance_sheet_value(balance_sheet, shareholder_equity_labels)

        # Fetching other important metrics from company info
        sector = info.get('sector')
        industry = info.get('industry')
        market_cap = info.get('marketCap')
        description = info.get('longBusinessSummary')

        # Fetching fundamental ratios
        pe_ratio = info.get('trailingPE')
        eps = info.get('trailingEps')
        pb_ratio = info.get('priceToBook')
        dividend_yield = info.get('dividendYield')
        return_on_equity = info.get('returnOnEquity')

        # Convert values to crores
        return {
            'Company': info['longName'] if 'longName' in info else ticker,
            'Sector': sector,
            'Industry': industry,
            'Market Cap': convert_to_crores(market_cap),
            'Description': description,
            'Total Assets': convert_to_crores(total_assets),
            'Total Liabilities': convert_to_crores(total_liabilities),
            'Current Assets': convert_to_crores(current_assets),
            'Current Liabilities': convert_to_crores(current_liabilities),
            'Long Term Debt': convert_to_crores(long_term_debt),
            'Shareholder Equity': convert_to_crores(shareholder_equity),
            'P/E Ratio': pe_ratio,
            'EPS': eps,
            'P/B Ratio': pb_ratio,
            'Dividend Yield': dividend_yield,
            'Return on Equity': return_on_equity
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Streamlit UI setup
st.title('**Company Financial Data**')

# Sidebar for user input
st.sidebar.title("Options")
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.NS").upper()

# Function to display explanations of financial metrics
def display_metric_explanation(metric_name):
    explanations = {
        "Earnings Per Share (EPS)": (
            "<b>What it is:</b> How much profit a company makes for each share of stock.<br>"
            "<b>Why it matters:</b> Higher EPS means the company is more profitable per share, which is generally good for investors."
        ),
        "Price-to-Earnings (P/E) Ratio": (
            "<b>What it is:</b> Shows how much you’re paying for ₹1 of the company’s earnings (profits).<br>"
            "<b>Why it matters:</b> A high P/E means the stock is expensive relative to its earnings, and a low P/E could mean it’s cheap."
        ),
        "Price-to-Book (P/B) Ratio": (
            "<b>What it is:</b> Compares the stock price to the company’s net worth (assets minus liabilities).<br>"
            "<b>Why it matters:</b> A lower P/B ratio might mean the stock is undervalued compared to its actual worth."
        ),
        "Return on Equity (ROE)": (
            "<b>What it is:</b> Shows how well the company is using the money from shareholders to make a profit.<br>"
            "<b>Why it matters:</b> A higher ROE means the company is more efficient at making money for its investors."
        ),
        "Debt-to-Equity (D/E) Ratio": (
            "<b>What it is:</b> Tells you how much debt the company has compared to its own money (equity).<br>"
            "<b>Why it matters:</b> A high D/E ratio means the company is more reliant on borrowing, which could be risky."
        ),
        "Current Ratio": (
            "<b>What it is:</b> Measures if the company has enough short-term assets (like cash) to pay off its short-term debts.<br>"
            "<b>Why it matters:</b> A ratio over 1 means the company can pay off its bills easily, while below 1 means it could struggle."
        ),
        "Free Cash Flow (FCF)": (
            "<b>What it is:</b> The cash left over after the company spends on things like equipment and expansion.<br>"
            "<b>Why it matters:</b> Positive FCF means the company is generating extra cash, which can be used to pay dividends or reinvest in growth."
        ),
        "Dividend Yield": (
            "<b>What it is:</b> How much money the company pays you in dividends (if it does) for every rupee you invest in its stock.<br>"
            "<b>Why it matters:</b> A higher dividend yield is attractive for investors looking for regular income from their investment."
        ),
        "Gross Margin": (
            "<b>What it is:</b> The percentage of money the company keeps after covering the basic costs of making its products.<br>"
            "<b>Why it matters:</b> A higher gross margin means the company keeps more of each rupee it earns, which is good for profitability."
        ),
        "Operating Margin": (
            "<b>What it is:</b> The percentage of money the company keeps from its main business activities after paying for things like labor and materials.<br>"
            "<b>Why it matters:</b> A high operating margin means the company is good at running its day-to-day business and making a profit."
        )
    }
    return explanations.get(metric_name, "No explanation available.")

# Custom CSS to enhance visuals
st.markdown("""
    <style>
        body {
            background-color: #f8f9fa;
            color: #343a40;
            font-family: 'Arial', sans-serif;
        }

        .section-header {
            font-size: 24px;
            color: #2c3e50;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 20px;
        }

        .subheader {
            color: #2980b9;
            font-size: 18px;
            margin-bottom: 15px;
        }

        .metric-value {
            color: #e74c3c;
            font-size: 22px;
            font-weight: bold;
        }

        .metric-explanation {
            color: #7f8c8d;
            font-size: 14px;
        }

        .metric-container {
            margin-bottom: 30px;
        }

        .blue-text {
            color: #3498db;
        }

        .green-text {
            color: #2ecc71;
        }

        .hover-effect:hover {
            transform: scale(1.05);
            transition: transform 0.3s ease-in-out;
        }

        .animated-section {
            animation: fadeIn 1s ease-in-out;
        }

        @keyframes fadeIn {
            0% {
                opacity: 0;
            }
            100% {
                opacity: 1;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Fetch and display data if ticker is valid
company_data = fetch_company_data(ticker_input)
if company_data:
    # Company Overview Section
    st.subheader("**Company Overview**")
    st.write(f"<h4>Sector: <span class='blue-text'>{company_data['Sector']}</span></h4>", unsafe_allow_html=True)
    st.write(f"<h4>Industry: <span class='blue-text'>{company_data['Industry']}</span></h4>", unsafe_allow_html=True)
    st.write(f"<h4>Market Cap: <span class='green-text'>₹{company_data['Market Cap']:.2f} Crores</span></h4>", unsafe_allow_html=True)
    st.write(f"<p>{company_data['Description']}</p>", unsafe_allow_html=True)

    # Fundamentals Section
    st.subheader("**Fundamentals**")
    st.write(f"<h4>P/E Ratio: <span class='blue-text'>{company_data['P/E Ratio']}</span></h4>", unsafe_allow_html=True)
    st.write(display_metric_explanation("Price-to-Earnings (P/E) Ratio"), unsafe_allow_html=True)
    st.write(f"<h4>EPS: <span class='blue-text'>{company_data['EPS']}</span></h4>", unsafe_allow_html=True)
    st.write(display_metric_explanation("Earnings Per Share (EPS)"), unsafe_allow_html=True)

    # Financials Section
    st.subheader("**Financials**")
    st.write(f"<h4>Total Assets: ₹{company_data['Total Assets']:.2f} Crores</h4>", unsafe_allow_html=True)
    st.write(display_metric_explanation("Total Assets"), unsafe_allow_html=True)
    st.write(f"<h4>Total Liabilities: ₹{company_data['Total Liabilities']:.2f} Crores</h4>", unsafe_allow_html=True)
    st.write(display_metric_explanation("Total Liabilities"), unsafe_allow_html=True)
    st.write(f"<h4>Current Assets: ₹{company_data['Current Assets']:.2f} Crores</h4>", unsafe_allow_html=True)
    st.write(display_metric_explanation("Current Assets"), unsafe_allow_html=True)

    st.write(f"<h4>Current Liabilities: ₹{company_data['Current Liabilities']:.2f} Crores</h4>", unsafe_allow_html=True)
    st.write(display_metric_explanation("Current Liabilities"), unsafe_allow_html=True)

    st.write(f"<h4>Long Term Debt: ₹{company_data['Long Term Debt']:.2f} Crores</h4>", unsafe_allow_html=True)
    st.write(display_metric_explanation("Long Term Debt"), unsafe_allow_html=True)

    st.write(f"<h4>Shareholder Equity: ₹{company_data['Shareholder Equity']:.2f} Crores</h4>", unsafe_allow_html=True)
    st.write(display_metric_explanation("Shareholder Equity"), unsafe_allow_html=True)
