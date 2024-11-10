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
        "Total Assets": (
            "What it is: Total Assets represent everything a company owns. "
            "It includes current and non-current assets like cash, receivables, and property. "
            "Why it matters: Total Assets give an indication of the scale of the company and its ability to generate revenue. "
            "A larger asset base can lead to higher earnings potential."
        ),
        "Total Liabilities": (
            "What it is: Total Liabilities are the total debts a company owes. "
            "It includes both current and long-term liabilities such as loans and payables. "
            "Why it matters: Liabilities indicate the financial obligations a company must meet. "
            "A high level of debt can increase financial risk but can also leverage growth if managed well."
        ),
        "Current Assets": (
            "What it is: Current Assets are assets that are expected to be converted into cash within a year. "
            "This includes cash, inventory, and accounts receivable. "
            "Why it matters: The higher the current assets, the more liquid the company is, making it easier to meet short-term obligations."
        ),
        "Current Liabilities": (
            "What it is: Current Liabilities are the company's debts or obligations that are due within a year. "
            "This includes short-term loans and accounts payable. "
            "Why it matters: High current liabilities relative to current assets can indicate potential liquidity problems."
        ),
        "Long Term Debt": (
            "What it is: Long Term Debt is the portion of the company's debt that is due after more than one year. "
            "This includes bonds and long-term loans. "
            "Why it matters: A high level of long-term debt could signal potential future financial strain but can also fund expansion."
        ),
        "Shareholder Equity": (
            "What it is: Shareholder Equity represents the residual interest in the assets of the company after subtracting its liabilities. "
            "It is also known as net assets or net worth. "
            "Why it matters: A higher shareholder equity is generally a positive sign, showing the company has substantial backing from its shareholders."
        ),
        "P/E Ratio": (
            "What it is: The Price-to-Earnings (P/E) ratio measures the price investors are willing to pay for a company's earnings. "
            "It is calculated as the share price divided by earnings per share (EPS). "
            "Why it matters: A higher P/E ratio could suggest that investors expect future growth, while a lower P/E may indicate undervaluation or poor growth prospects."
        ),
        "EPS": (
            "What it is: Earnings Per Share (EPS) is the portion of a company's profit allocated to each outstanding share of common stock. "
            "It is calculated as Net Income divided by the number of outstanding shares. "
            "Why it matters: EPS is a key indicator of a company’s profitability. Higher EPS generally indicates better financial performance."
        ),
        "P/B Ratio": (
            "What it is: The Price-to-Book (P/B) ratio compares a company’s market value to its book value. "
            "It is calculated as the stock price divided by the book value per share. "
            "Why it matters: A lower P/B ratio might indicate that a stock is undervalued, while a higher ratio could signal overvaluation."
        ),
        "Dividend Yield": (
            "What it is: Dividend Yield is the annual dividend payment expressed as a percentage of the stock's price. "
            "It is calculated by dividing the annual dividend per share by the stock price. "
            "Why it matters: Dividend yield is important for income-focused investors. A high dividend yield can indicate a strong and consistent company."
        ),
        "Return on Equity": (
            "What it is: Return on Equity (ROE) measures a company’s ability to generate profits from its shareholders' equity. "
            "It is calculated as Net Income divided by Shareholder Equity. "
            "Why it matters: A higher ROE indicates efficient use of equity capital and can be a sign of a profitable company."
        )
    }
    return explanations.get(metric_name, "No explanation available.")

# Fetch and display data if ticker is provided
if ticker_input:
    company_data = fetch_company_data(ticker_input)

    if company_data:
        # **Company Overview** Section
        st.subheader("Company Overview")
        st.write(f"**Company Name**: {company_data['Company']}")
        st.write(company_data['Description'])
        st.write(f"**Sector**: {company_data['Sector']}")
        st.write(f"**Industry**: {company_data['Industry']}")
        st.write(f"**Market Cap**: ₹{company_data['Market Cap']} Crores")

        # **Fundamentals** Section
        st.subheader("Fundamentals")
        st.write(f"**P/E Ratio**: {company_data['P/E Ratio']}")
        st.write(display_metric_explanation("P/E Ratio"))
        
        st.write(f"**EPS**: ₹{company_data['EPS']}")
        st.write(display_metric_explanation("EPS"))
        
        st.write(f"**P/B Ratio**: {company_data['P/B Ratio']}")
        st.write(display_metric_explanation("P/B Ratio"))
        
        st.write(f"**Dividend Yield**: {company_data['Dividend Yield']}%")
        st.write(display_metric_explanation("Dividend Yield"))
        
        st.write(f"**Return on Equity**: {company_data['Return on Equity']}%")
        st.write(display_metric_explanation("Return on Equity"))

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
