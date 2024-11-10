import yfinance as yf
import streamlit as st

# Function to match labels dynamically and get values from the balance sheet
def get_balance_sheet_value(balance_sheet, possible_labels):
    for label in possible_labels:
        if label in balance_sheet.index:
            return balance_sheet.loc[label].iloc[0]  # Use iloc[0] for positional access
    return None  # Return None if no label matches

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

        return {
            'Company': info['longName'] if 'longName' in info else ticker,
            'Sector': sector,
            'Industry': industry,
            'Market Cap': market_cap,
            'Description': description,
            'Total Assets': total_assets,
            'Total Liabilities': total_liabilities,
            'Current Assets': current_assets,
            'Current Liabilities': current_liabilities,
            'Long Term Debt': long_term_debt,
            'Shareholder Equity': shareholder_equity
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Streamlit UI setup
st.title('**Company Financial Data**')

# Sidebar for user input
st.sidebar.title("Options")
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.NS").upper()

# Fetch and display data if ticker is provided
if ticker_input:
    company_data = fetch_company_data(ticker_input)

    if company_data:
        # Display Company Overview
        st.subheader(f"Company Overview: {company_data['Company']}")
        st.write(company_data['Description'])
        st.write(f"**Sector**: {company_data['Sector']}")
        st.write(f"**Industry**: {company_data['Industry']}")
        st.write(f"**Market Cap**: {company_data['Market Cap']}")

        # Display Key Financial Data
        st.subheader("Key Financial Data:")
        st.write(f"**Total Assets**: {company_data['Total Assets']}")
        st.write(f"**Total Liabilities**: {company_data['Total Liabilities']}")
        st.write(f"**Current Assets**: {company_data['Current Assets']}")
        st.write(f"**Current Liabilities**: {company_data['Current Liabilities']}")
        st.write(f"**Long Term Debt**: {company_data['Long Term Debt']}")
        st.write(f"**Shareholder Equity**: {company_data['Shareholder Equity']}")
