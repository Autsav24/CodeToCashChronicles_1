import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Fundamental Analysis", layout="wide")

# Function to handle missing data and provide fallback
def safe_get_data(data, label, fallback="Data not available"):
    return data.get(label, fallback)

# Function to fetch data
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info
        
        # Ensure data is valid
        if 'longName' not in info:
            st.error(f"No data found for the ticker symbol: {ticker}. Please check the symbol and try again.")
            return None
        
        # Essential data points (Company Essentials)
        market_cap = safe_get_data(info, 'marketCap')
        pe_ratio = safe_get_data(info, 'forwardPE')
        pb_ratio = safe_get_data(info, 'priceToBook')
        face_value = safe_get_data(info, 'faceValue')
        dividend_yield = safe_get_data(info, 'dividendYield')
        book_value = safe_get_data(info, 'bookValue')
        cash = safe_get_data(info, 'cash')
        debt = safe_get_data(info, 'debt')
        promoter_holding = safe_get_data(info, 'heldPercentInstitutions')
        eps = safe_get_data(info, 'regularMarketEPS')
        sales_growth = safe_get_data(info, 'revenueGrowth')
        roe = safe_get_data(info, 'returnOnEquity')
        roce = safe_get_data(info, 'returnOnCapitalEmployed')
        profit_growth = safe_get_data(info, 'earningsQuarterlyGrowth')

        # Prepare the data
        return {
            'Company': info.get('longName', 'N/A'),
            'Market Cap': market_cap,
            'PE Ratio': pe_ratio,
            'PB Ratio': pb_ratio,
            'Face Value': face_value,
            'Dividend Yield': dividend_yield,
            'Book Value': book_value,
            'Cash': cash,
            'Debt': debt,
            'Promoter Holding (%)': promoter_holding,
            'EPS': eps,
            'Sales Growth': sales_growth,
            'ROE': roe,
            'ROCE': roce,
            'Profit Growth': profit_growth,
        }

    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Layout
st.title("Stock Fundamental Analysis")
st.markdown("Enter a stock ticker symbol to fetch its fundamental data.")

ticker = st.text_input("Ticker Symbol (e.g., TCS.NS, MSFT)")

if st.button("Fetch Data"):
    if ticker:
        data = fetch_company_data(ticker.upper())
        
        if data:
            # Create tabs
            tabs = st.tabs(["Company Essentials", "Key Metrics"])

            # Company Essentials tab
            with tabs[0]:
                st.subheader("Company Overview")
                st.write(f"**Company:** {data['Company']}")
                st.write(f"**Market Cap:** {data['Market Cap']}")
                st.write(f"**EPS (TTM):** {data['EPS']}")
                st.write(f"**Promoter Holding (%):** {data['Promoter Holding (%)']}")

            # Key Metrics tab
            with tabs[1]:
                st.subheader("Key Financial Metrics")
                st.write(f"**PE Ratio:** {data['PE Ratio']}")
                st.write(f"**PB Ratio:** {data['PB Ratio']}")
                st.write(f"**Face Value:** {data['Face Value']}")
                st.write(f"**Dividend Yield:** {data['Dividend Yield']}")
                st.write(f"**Book Value:** {data['Book Value']}")
                st.write(f"**Cash:** {data['Cash']}")
                st.write(f"**Debt:** {data['Debt']}")
                st.write(f"**Sales Growth:** {data['Sales Growth']}")
                st.write(f"**ROE:** {data['ROE']}")
                st.write(f"**ROCE:** {data['ROCE']}")
                st.write(f"**Profit Growth:** {data['Profit Growth']}")
        else:
            st.error("Failed to fetch data. Please try again.")
    else:
        st.warning("Please enter a ticker symbol.")
