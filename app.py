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

# Fetch and display data if ticker is provided
if ticker_input:
    company_data = fetch_company_data(ticker_input)

    if company_data:
        # **Company Overview** Section
        st.subheader("Company Overview")
        st.markdown(f"<h3>{company_data['Company']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<b>{company_data['Description']}</b>", unsafe_allow_html=True)
        st.write(f"**Sector**: <span style='color:#3498db;'>{company_data['Sector']}</span>")
        st.write(f"**Industry**: <span style='color:#3498db;'>{company_data['Industry']}</span>")
        st.write(f"**Market Cap**: <span style='color:#2ecc71;'>₹{company_data['Market Cap']} Crores</span>")

        # **Fundamentals** Section
        st.subheader("Fundamentals")
        st.markdown(f"<h4>Price-to-Earnings (P/E) Ratio</h4><b>{company_data['P/E Ratio']}</b>", unsafe_allow_html=True)
        st.markdown(display_metric_explanation("Price-to-Earnings (P/E) Ratio"), unsafe_allow_html=True)
        
        st.markdown(f"<h4>Earnings Per Share (EPS)</h4><b>₹{company_data['EPS']}</b>", unsafe_allow_html=True)
        st.markdown(display_metric_explanation("Earnings Per Share (EPS)"), unsafe_allow_html=True)
        
        st.markdown(f"<h4>Price-to-Book (P/B) Ratio</h4><b>{company_data['P/B Ratio']}</b>", unsafe_allow_html=True)
        st.markdown(display_metric_explanation("Price-to-Book (P/B) Ratio"), unsafe_allow_html=True)
        
        st.markdown(f"<h4>Dividend Yield</h4><b>{company_data['Dividend Yield']}%</b>", unsafe_allow_html=True)
        st.markdown(display_metric_explanation("Dividend Yield"), unsafe_allow_html=True)
        
        st.markdown(f"<h4>Return on Equity (ROE)</h4><b>{company_data['Return on Equity']}%</b>", unsafe_allow_html=True)
        st.markdown(display_metric_explanation("Return on Equity (ROE)"), unsafe_allow_html=True)

        # **Financials** Section
        st.subheader("Financials")
        st.write(f"**Total Assets**: ₹{company_data['Total Assets']} Crores")
        st.write(display_metric_explanation("Total Assets"))
        
        st.write(f"**Total Liabilities**: ₹{company_data['Total Liabilities']} Crores")
        st.write(display_metric_explanation("Total Liabilities"))
        
        st.write(f"**Current Assets**: ₹{company_data['Current Assets']} Crores")
        st.write(display_metric_explanation("Current Assets"))
        
        st.write(f"**Current Liabilities**: ₹{company_data['Current Liabilities']} Crores")
        st.write(display_metric_explanation("Current Liabilities"))
        
        st.write(f"**Long Term Debt**: ₹{company_data['Long Term Debt']} Crores")
        st.write(display_metric_explanation("Long Term Debt"))
        
        st.write(f"**Shareholder Equity**: ₹{company_data['Shareholder Equity']} Crores")
        st.write(display_metric_explanation("Shareholder Equity"))
