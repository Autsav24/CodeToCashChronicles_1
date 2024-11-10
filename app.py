import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Fundamental Analysis", layout="wide")

# Function to handle missing data and provide fallback
def safe_get_data(data, label, fallback="Data not available"):
    return data[label] if label in data else fallback

# Function to format numbers into crores, lakhs, or billions for easier understanding
def format_money(amount):
    if isinstance(amount, (int, float)):
        if amount >= 1e9:
            return f"₹ {amount / 1e7:.2f} Cr"  # Convert to Crores
        elif amount >= 1e7:
            return f"₹ {amount / 1e5:.2f} Lakhs"  # Convert to Lakhs
        elif amount >= 1e6:
            return f"$ {amount / 1e6:.2f} M"  # Convert to Millions (for non-INR)
        else:
            return f"₹ {amount:.2f}"  # Show as it is in INR
    return amount

@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info
        
        # Financial Data (Check for missing values)
        actions = company.actions if hasattr(company, 'actions') else None
        dividends = company.dividends if hasattr(company, 'dividends') else None
        splits = company.splits if hasattr(company, 'splits') else None
        capital_gains = company.capital_gains if hasattr(company, 'capital_gains') else None
        shares_outstanding = company.get_shares_full(start="2022-01-01") if hasattr(company, 'get_shares_full') else None

        # Financials
        income_stmt = company.income_stmt if hasattr(company, 'income_stmt') else None
        quarterly_income_stmt = company.quarterly_income_stmt if hasattr(company, 'quarterly_income_stmt') else None
        balance_sheet = company.balance_sheet if hasattr(company, 'balance_sheet') else None
        quarterly_balance_sheet = company.quarterly_balance_sheet if hasattr(company, 'quarterly_balance_sheet') else None
        cashflow = company.cashflow if hasattr(company, 'cashflow') else None
        quarterly_cashflow = company.quarterly_cashflow if hasattr(company, 'quarterly_cashflow') else None
        
        # Holders and Transactions
        major_holders = company.major_holders if hasattr(company, 'major_holders') else None
        institutional_holders = company.institutional_holders if hasattr(company, 'institutional_holders') else None
        mutualfund_holders = company.mutualfund_holders if hasattr(company, 'mutualfund_holders') else None
        insider_transactions = company.insider_transactions if hasattr(company, 'insider_transactions') else None
        insider_purchases = company.insider_purchases if hasattr(company, 'insider_purchases') else None
        insider_roster = company.insider_roster if hasattr(company, 'insider_roster') else None

        # Sustainability
        sustainability = company.sustainability if hasattr(company, 'sustainability') else None

        # Recommendations
        recommendations = company.recommendations if hasattr(company, 'recommendations') else None
        recommendations_summary = company.recommendations_summary if hasattr(company, 'recommendations_summary') else None
        upgrades_downgrades = safe_get_data(company, 'upgrades_downgrades')

        # Analyst data
        analyst_price_targets = company.analyst_price_targets if hasattr(company, 'analyst_price_targets') else None
        earnings_estimate = company.earnings_estimate if hasattr(company, 'earnings_estimate') else None
        revenue_estimate = company.revenue_estimate if hasattr(company, 'revenue_estimate') else None
        earnings_history = company.earnings_history if hasattr(company, 'earnings_history') else None
        eps_trend = company.eps_trend if hasattr(company, 'eps_trend') else None
        eps_revisions = company.eps_revisions if hasattr(company, 'eps_revisions') else None
        growth_estimates = company.growth_estimates if hasattr(company, 'growth_estimates') else None

        # Earnings dates
        earnings_dates = company.earnings_dates if hasattr(company, 'earnings_dates') else None

        # Return the fetched data
        return {
            'Company Info': info,
            'Actions': actions,
            'Dividends': dividends,
            'Splits': splits,
            'Capital Gains': capital_gains,
            'Shares Outstanding': shares_outstanding,
            'Financials': {
                'Income Statement': income_stmt,
                'Quarterly Income Statement': quarterly_income_stmt,
                'Balance Sheet': balance_sheet,
                'Quarterly Balance Sheet': quarterly_balance_sheet,
                'Cash Flow Statement': cashflow,
                'Quarterly Cash Flow Statement': quarterly_cashflow
            },
            'Holders': {
                'Major Holders': major_holders,
                'Institutional Holders': institutional_holders,
                'Mutual Fund Holders': mutualfund_holders,
                'Insider Transactions': insider_transactions,
                'Insider Purchases': insider_purchases,
                'Insider Roster': insider_roster
            },
            'Sustainability': sustainability,
            'Recommendations': recommendations,
            'Recommendations Summary': recommendations_summary,
            'Upgrades/Downgrades': upgrades_downgrades,
            'Analyst Data': {
                'Price Targets': analyst_price_targets,
                'Earnings Estimate': earnings_estimate,
                'Revenue Estimate': revenue_estimate,
                'Earnings History': earnings_history,
                'EPS Trend': eps_trend,
                'EPS Revisions': eps_revisions,
                'Growth Estimates': growth_estimates
            },
            'Earnings Dates': earnings_dates
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
            # Create tabs
            tabs = st.tabs(["Overview", "Fundamental Metrics", "Analyst Data", "Financial Data"])

            # Overview tab
            with tabs[0]:
                st.subheader("Company Overview")
                st.write(f"**Company:** {data['Company Info'].get('longName', 'N/A')}")
                st.write(f"**Description:** {data['Company Info'].get('longBusinessSummary', 'N/A')}")
                st.write(f"**Market Cap:** {format_money(data['Company Info'].get('marketCap', 'N/A'))}")

            # Fundamental Metrics tab
            with tabs[1]:
                st.subheader("Fundamental Metrics")
                st.write(f"**PE Ratio:** {data['Company Info'].get('forwardPE', 'N/A')} (High stock price valuation)")
                st.write(f"**PB Ratio:** {data['Company Info'].get('priceToBook', 'N/A')} (Expensive relative to assets)")
                st.write(f"**ROE:** {data['Company Info'].get('returnOnEquity', 'N/A')} (Profitability from equity investment)")
                st.write(f"**ROCE:** {data['Company Info'].get('returnOnCapitalEmployed', 'N/A')} (Efficiency in using capital)")
                st.write(f"**Promoter Holding (%):** {data['Company Info'].get('heldPercentInstitutions', 'N/A')} (Significant promoter ownership)")

            # Analyst Data tab
            with tabs[2]:
                st.subheader("Analyst Data")
                st.write(f"**Earnings Estimate:** {data['Analyst Data'].get('Earnings Estimate', 'N/A')}")
                st.write(f"**Revenue Estimate:** {data['Analyst Data'].get('Revenue Estimate', 'N/A')}")
                st.write(f"**EPS Trend:** {data['Analyst Data'].get('EPS Trend', 'N/A')}")
                st.write(f"**Growth Estimates:** {data['Analyst Data'].get('Growth Estimates', 'N/A')}")

            # Financial Data tab
            with tabs[3]:
                st.subheader("Financial Data")
                st.write(f"**Income Statement:** {data['Financials'].get('Income Statement', 'N/A')}")
                st.write(f"**Quarterly Income Statement:** {data['Financials'].get('Quarterly Income Statement', 'N/A')}")
                st.write(f"**Balance Sheet:** {data['Financials'].get('Balance Sheet', 'N/A')}")
                st.write(f"**Quarterly Balance Sheet:** {data['Financials'].get('Quarterly Balance Sheet', 'N/A')}")
                st.write(f"**Cash Flow Statement:** {data['Financials'].get('Cash Flow Statement', 'N/A')}")
        else:
            st.error("Failed to fetch data. Please try again.")
    else:
        st.warning("Please enter a ticker symbol.")
