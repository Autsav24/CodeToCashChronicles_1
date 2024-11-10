import streamlit as st
import yfinance as yf

# Function to fetch financial data and calculate key metrics
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info
        balance_sheet = company.balance_sheet

        # Financial Metrics
        total_assets = balance_sheet.loc['Total Assets'][0] if 'Total Assets' in balance_sheet.index else None
        total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'][0] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else None
        current_assets = balance_sheet.loc['Total Current Assets'][0] if 'Total Current Assets' in balance_sheet.index else None
        current_liabilities = balance_sheet.loc['Total Current Liabilities'][0] if 'Total Current Liabilities' in balance_sheet.index else None
        long_term_debt = balance_sheet.loc['Long Term Debt'][0] if 'Long Term Debt' in balance_sheet.index else None
        shareholder_equity = balance_sheet.loc['Total Stockholder Equity'][0] if 'Total Stockholder Equity' in balance_sheet.index else None

        # Key Data
        eps = info.get('trailingEps', None)
        pe_ratio = info.get('forwardPE', None)
        roe = info.get('returnOnEquity', None)
        net_profit_margin = info.get('profitMargins', None)
        dividend_yield = info.get('dividendYield', None)
        market_cap = info.get('marketCap', None)
        sector = info.get('sector', None)
        industry = info.get('industry', None)
        company_name = info.get('longName', ticker)

        return {
            'Company': company_name,
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
            'Current Assets': current_assets,
            'Current Liabilities': current_liabilities,
            'Long Term Debt': long_term_debt,
            'Shareholder Equity': shareholder_equity
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Function to display a metric with fallback if the data is None
def display_metric_value(metric_name, value):
    if value is not None:
        return f"<h4>{metric_name}: ₹{value/1e7:.2f} Crores</h4>"  # Convert to Crores
    return f"<h4>{metric_name}: Data not available</h4>"

# Metric Explanations
def display_metric_explanation(metric_name):
    explanations = {
        "Total Assets": "What it is: The total value of everything the company owns. Why it matters: Higher assets can mean more growth potential.",
        "Total Liabilities": "What it is: The total debt the company owes. Why it matters: Less debt is often better for stability.",
        "Current Assets": "What it is: Cash or assets that can quickly be converted into cash. Why it matters: Shows the company's short-term financial health.",
        "Current Liabilities": "What it is: Debts that are due in the short-term. Why it matters: A high ratio to current assets may indicate liquidity problems.",
        "Long Term Debt": "What it is: Debt that is due in more than one year. Why it matters: It indicates the company’s long-term financial health.",
        "Shareholder Equity": "What it is: The company's net worth, calculated as assets minus liabilities. Why it matters: Positive equity is a sign of financial stability.",
        "EPS": "What it is: Earnings Per Share – how much profit the company generates per share. Why it matters: A higher EPS indicates better profitability.",
        "P/E Ratio": "What it is: Price-to-Earnings ratio – compares the price of the stock to its earnings. Why it matters: A high P/E ratio could indicate an overvalued stock.",
        "ROE": "What it is: Return on Equity – measures profitability based on shareholder equity. Why it matters: A higher ROE is generally good for investors.",
        "Net Profit Margin": "What it is: The percentage of revenue that becomes profit. Why it matters: A higher margin means the company is better at converting sales into actual profit.",
        "Dividend Yield": "What it is: The annual dividend payment divided by the stock price. Why it matters: A higher yield is attractive to income-focused investors."
    }
    return explanations.get(metric_name, "No explanation available.")

# Fetching major holders data
def fetch_major_holders(ticker):
    try:
        company = yf.Ticker(ticker)
        major_holders = company.major_holders
        institutional_holders = company.institutional_holders
        mutualfund_holders = company.mutualfund_holders

        return {
            'Major Holders': major_holders,
            'Institutional Holders': institutional_holders,
            'Mutual Fund Holders': mutualfund_holders
        }
    except Exception as e:
        st.error(f"Error fetching holders data for {ticker}: {e}")
        return None

# Display Major Holders Information
def display_major_holders(holders_data):
    st.subheader("**Major Holders Information**")
    
    if holders_data:
        if holders_data['Major Holders'] is not None:
            st.write("**Major Holders:**")
            st.write(holders_data['Major Holders'])
        else:
            st.write("**Major Holders:** Data not available")
        
        if holders_data['Institutional Holders'] is not None:
            st.write("**Institutional Holders:**")
            st.write(holders_data['Institutional Holders'])
        else:
            st.write("**Institutional Holders:** Data not available")
        
        if holders_data['Mutual Fund Holders'] is not None:
            st.write("**Mutual Fund Holders:**")
            st.write(holders_data['Mutual Fund Holders'])
        else:
            st.write("**Mutual Fund Holders:** Data not available")
    else:
        st.write("No data available for holders.")

# Streamlit UI setup
st.title('**Fundamental Analysis Tool**')

st.sidebar.title("Options")
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.NS").upper()

if ticker_input:
    company_data = fetch_company_data(ticker_input)
    holders_data = fetch_major_holders(ticker_input)

    if company_data:
        # Company Overview Section
        st.subheader(f"Company Overview: {company_data['Company']}")
        st.write(f"**Sector**: {company_data['Sector']}")
        st.write(f"**Industry**: {company_data['Industry']}")
        st.write(f"**Market Cap**: ₹{company_data['Market Cap']/1e7:.2f} Crores")

        # Fundamentals Section
        st.subheader("**Fundamentals**")
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

        # Financials Section
        st.subheader("**Financials**")
        asset_display = display_metric_value("Total Assets", company_data.get('Total Assets'))
        st.markdown(asset_display, unsafe_allow_html=True)
        st.write(display_metric_explanation("Total Assets"))

        liabilities_display = display_metric_value("Total Liabilities", company_data.get('Total Liabilities'))
        st.markdown(liabilities_display, unsafe_allow_html=True)
        st.write(display_metric_explanation("Total Liabilities"))

        current_assets_display = display_metric_value("Current Assets", company_data.get('Current Assets'))
        st.markdown(current_assets_display, unsafe_allow_html=True)
        st.write(display_metric_explanation("Current Assets"))

        current_liabilities_display = display_metric_value("Current Liabilities", company_data.get('Current Liabilities'))
        st.markdown(current_liabilities_display, unsafe_allow_html=True)
        st.write(display_metric_explanation("Current Liabilities"))

        long_term_debt_display = display_metric_value("Long Term Debt", company_data.get('Long Term Debt'))
        st.markdown(long_term_debt_display, unsafe_allow_html=True)
        st.write(display_metric_explanation("Long Term Debt"))

        shareholder_equity_display = display_metric_value("Shareholder Equity", company_data.get('Shareholder Equity'))
        st.markdown(shareholder_equity_display, unsafe_allow_html=True)
        st.write(display_metric_explanation("Shareholder Equity"))

        # Major Holders Information Section
        display_major_holders(holders_data)
