import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Fundamental Analysis", layout="wide")

def get_balance_sheet_value(balance_sheet, labels):
    for label in labels:
        if label in balance_sheet.index:
            return balance_sheet.loc[label].values[0]
    return None

@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        balance_sheet = company.balance_sheet
        info = company.info
        
        # Check if data is valid
        if balance_sheet.empty or 'longName' not in info:
            st.error(f"No data found for the ticker symbol: {ticker}. Please check the symbol and try again.")
            return None

        # Fetch necessary values using labels
        total_assets = get_balance_sheet_value(balance_sheet, ['Total Assets'])
        total_liabilities = get_balance_sheet_value(balance_sheet, ['Total Liabilities'])
        current_assets = get_balance_sheet_value(balance_sheet, ['Total Current Assets'])
        current_liabilities = get_balance_sheet_value(balance_sheet, ['Total Current Liabilities'])
        long_term_debt = get_balance_sheet_value(balance_sheet, ['Long Term Debt'])
        shareholder_equity = get_balance_sheet_value(balance_sheet, ['Total Stockholder Equity'])

        # New metrics
        pe_ratio = info.get('forwardPE', 'N/A')
        pb_ratio = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 'N/A')
        roce = info.get('returnOnCapitalEmployed', 'N/A')
        promoter_holding = info.get('heldPercentInstitutions', 'N/A')
        debt = total_liabilities / shareholder_equity if shareholder_equity else 'N/A'
        sales_growth = info.get('revenueGrowth', 'N/A')
        eps_growth = info.get('earningsQuarterlyGrowth', 'N/A')

        return {
            'Company': info['longName'],
            'PE Ratio': pe_ratio,
            'PB Ratio': pb_ratio,
            'Sector PE': 'N/A',  # Placeholder for sector PE
            'Sector PB': 'N/A',  # Placeholder for sector PB
            'ROE': roe,
            'ROCE': roce,
            'Promoter Holding (%)': promoter_holding,
            'Debt to Equity': debt,
            'Sales Growth': sales_growth,
            'EPS Growth': eps_growth,
            'Market Cap': info.get('marketCap', 'N/A'),
            'Description': info.get('longBusinessSummary', 'N/A'),
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Layout
st.title("Stock Fundamental Analysis")
st.markdown("Enter a stock ticker symbol to fetch its fundamental data.")

ticker = st.text_input("Ticker Symbol (e.g., AAPL, MSFT)")

if st.button("Fetch Data"):
    if ticker:
        data = fetch_company_data(ticker.upper())
        
        if data:
            st.subheader("Company Overview")
            st.write(f"**Company:** {data['Company']}")
            st.write(f"**Description:** {data['Description']}")
            st.write(f"**Market Cap:** {data['Market Cap']}")
            
            st.subheader("Fundamental Metrics")
            st.write(f"**PE Ratio:** {data['PE Ratio']}")
            st.write(f"**PB Ratio:** {data['PB Ratio']}")
            st.write(f"**Sector PE:** {data['Sector PE']}")
            st.write(f"**Sector PB:** {data['Sector PB']}")
            st.write(f"**ROE:** {data['ROE']}")
            st.write(f"**ROCE:** {data['ROCE']}")
            st.write(f"**Promoter Holding (%):** {data['Promoter Holding (%)']}")
            st.write(f"**Debt to Equity:** {data['Debt to Equity']}")
            st.write(f"**Sales Growth:** {data['Sales Growth']}")
            st.write(f"**EPS Growth:** {data['EPS Growth']}")
        else:
            st.error("Failed to fetch data. Please try again.")
    else:
        st.warning("Please enter a ticker symbol.")
