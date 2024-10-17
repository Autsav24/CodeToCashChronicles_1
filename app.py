import os
import yfinance as yf
import pandas as pd
import streamlit as st

# Function to match labels dynamically and get values from the balance sheet
def get_balance_sheet_value(balance_sheet, possible_labels):
    for label in possible_labels:
        if label in balance_sheet.index:
            return balance_sheet.loc[label].iloc[0]  # Use iloc[0] for positional access
    return None  # Return None if no label matches

# Function to fetch financial data and calculate key metrics
@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        balance_sheet = company.balance_sheet
        info = company.info

        total_assets_labels = ['Total Assets']
        total_liabilities_labels = ['Total Liabilities', 'Total Liabilities Net Minority Interest']
        current_assets_labels = ['Total Current Assets']
        current_liabilities_labels = ['Total Current Liabilities']
        long_term_debt_labels = ['Long Term Debt', 'Long-Term Debt']
        shareholder_equity_labels = ['Total Stockholder Equity', 'Shareholder Equity']

        total_assets = get_balance_sheet_value(balance_sheet, total_assets_labels)
        total_liabilities = get_balance_sheet_value(balance_sheet, total_liabilities_labels)
        current_assets = get_balance_sheet_value(balance_sheet, current_assets_labels)
        current_liabilities = get_balance_sheet_value(balance_sheet, current_liabilities_labels)
        long_term_debt = get_balance_sheet_value(balance_sheet, long_term_debt_labels)
        shareholder_equity = get_balance_sheet_value(balance_sheet, shareholder_equity_labels)

        # New metrics
        pe_ratio = info.get('forwardPE')
        pb_ratio = info.get('priceToBook')
        roe = info.get('returnOnEquity')
        roce = info.get('returnOnCapitalEmployed')
        promoter_holding = info.get('heldPercentInstitutions')
        debt = total_liabilities / shareholder_equity if shareholder_equity else None
        sales_growth = info.get('revenueGrowth')
        eps_growth = info.get('earningsQuarterlyGrowth')

        # Sector PE and PB
        sector_pe = info.get('sector')  # You might need an additional call to get sector data
        sector_pb = info.get('sector')  # Placeholder, you will need to fetch this data

        return {
            'Company': info['longName'] if 'longName' in info else ticker,
            'PE Ratio': pe_ratio,
            'PB Ratio': pb_ratio,
            'Sector PE': sector_pe,
            'Sector PB': sector_pb,
            'ROE': roe,
            'ROCE': roce,
            'Promoter Holding (%)': promoter_holding,
            'Debt to Equity': debt,
            'Sales Growth': sales_growth,
            'EPS Growth': eps_growth,
            'Market Cap': info.get('marketCap'),
            'Description': info.get('longBusinessSummary'),
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Streamlit UI setup
st.set_page_config(page_title='Investment Analysis Tool', page_icon='📈', layout='wide')

# Custom CSS for styling
st.markdown("""
<style>
body {
    background-color: #f0f2f5;
}
h1 {
    color: #333;
    text-align: center;
}
h2 {
    color: #0073e6;
}
.table-container {
    overflow-x: auto;
}
.table {
    border-collapse: collapse;
    width: 100%;
}
.table th, .table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}
.table th {
    background-color: #0073e6;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title('📊 Investment Analysis Tool')

# Text input for ticker symbol
ticker = st.text_input('Enter Ticker Symbol', '')

# Button to fetch data
if st.button('Fetch Data'):
    if ticker:
        data = fetch_company_data(ticker)
        if data:
            # Store data in session state
            st.session_state.data = data
            st.success("Analysis completed!")
        else:
            st.error("No data found for the ticker symbol.")

# Tabs for displaying different data
tab1, tab2 = st.tabs(["Current Analysis", "Company Overview"])

# Current Analysis Tab
with tab1:
    if 'data' in st.session_state:
        data = st.session_state.data
        st.subheader(f"Results for {data['Company']}")
        
        # Create a horizontal table for financial metrics
        metrics_df = pd.DataFrame({
            'Metric': [
                'PE Ratio', 
                'PB Ratio', 
                'Sector PE', 
                'Sector PB', 
                'ROE', 
                'ROCE', 
                'Promoter Holding (%)', 
                'Debt to Equity', 
                'Sales Growth', 
                'EPS Growth'
            ],
            'Value': [
                data['PE Ratio'], 
                data['PB Ratio'], 
                data['Sector PE'], 
                data['Sector PB'], 
                data['ROE'], 
                data['ROCE'], 
                data['Promoter Holding (%)'], 
                data['Debt to Equity'], 
                data['Sales Growth'], 
                data['EPS Growth']
            ]
        })

        st.markdown("<div class='table-container'><table class='table'>", unsafe_allow_html=True)
        st.write(metrics_df.style.hide_index())
        st.markdown("</table></div>", unsafe_allow_html=True)

    else:
        st.write("No data found for the ticker symbol.")

# Company Overview Tab
with tab2:
    if 'data' in st.session_state:
        data = st.session_state.data
        st.subheader(f"Company Overview for {data['Company']}")
        
        # Display company overview details
        overview_df = pd.DataFrame({
            'Detail': [
                'Market Cap', 
                'Description'
            ],
            'Value': [
                f"${data['Market Cap']:,}" if data['Market Cap'] else "N/A", 
                data['Description']
            ]
        })

        st.markdown("<div class='table-container'><table class='table'>", unsafe_allow_html=True)
        st.write(overview_df.style.hide_index())
        st.markdown("</table></div>", unsafe_allow_html=True)

    else:
        st.write("No data found for the ticker symbol.")
