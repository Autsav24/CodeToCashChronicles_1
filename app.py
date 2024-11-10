import streamlit as st
import yfinance as yf

# Function to convert large numbers to more understandable units
def format_money(value):
    if value is None:
        return "N/A"
    if isinstance(value, str):
        return value  # In case the value is already a string, return as is
    
    if value >= 1_00_00_000:
        # Convert to crores (for India)
        return f"₹ {value / 1_00_00_000:.2f} Cr"
    elif value >= 10_00_000:
        # Convert to lakhs
        return f"₹ {value / 1_00_000:.2f} L"
    elif value >= 1_000_000:
        # Convert to millions
        return f"$ {value / 1_000_000:.2f} M"
    elif value >= 1_000_000_000:
        # Convert to billions (e.g., Market Cap)
        return f"$ {value / 1_000_000_000:.2f} B"
    else:
        return f"₹ {value:.2f}"

st.set_page_config(page_title="Stock Fundamental and Financial Data", layout="wide")

@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def fetch_company_data(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info

        # Fetching data
        actions = company.actions
        dividends = company.dividends
        splits = company.splits
        capital_gains = company.capital_gains
        shares_outstanding = company.get_shares_full(start="2022-01-01")

        # Financials
        income_stmt = company.income_stmt
        quarterly_income_stmt = company.quarterly_income_stmt
        balance_sheet = company.balance_sheet
        quarterly_balance_sheet = company.quarterly_balance_sheet
        cashflow = company.cashflow
        quarterly_cashflow = company.quarterly_cashflow
        
        # Holders and Transactions
        major_holders = company.major_holders if 'major_holders' in dir(company) else None
        institutional_holders = company.institutional_holders if 'institutional_holders' in dir(company) else None
        mutualfund_holders = company.mutualfund_holders if 'mutualfund_holders' in dir(company) else None
        insider_transactions = company.insider_transactions if 'insider_transactions' in dir(company) else None
        insider_purchases = company.insider_purchases if 'insider_purchases' in dir(company) else None
        insider_roster = company.insider_roster if 'insider_roster' in dir(company) else None

        # Sustainability data
        sustainability = company.sustainability

        # Recommendations
        recommendations = company.recommendations
        recommendations_summary = company.recommendations_summary
        upgrades_downgrades = company.upgrades_downgrades
        
        # Analyst data
        analyst_price_targets = company.analyst_price_targets
        earnings_estimate = company.earnings_estimate
        revenue_estimate = company.revenue_estimate
        earnings_history = company.earnings_history
        eps_trend = company.eps_trend
        eps_revisions = company.eps_revisions
        growth_estimates = company.growth_estimates

        # Earnings dates
        earnings_dates = company.earnings_dates

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
st.title("Stock Fundamental and Financial Data")
st.markdown("Enter a stock ticker symbol to fetch its comprehensive financial and fundamental data.")

ticker = st.text_input("Ticker Symbol (e.g., AAPL, MSFT)")

if st.button("Fetch Data"):
    if ticker:
        data = fetch_company_data(ticker.upper())
        
        if data:
            # Overview Tab
            tabs = st.tabs(["Company Overview", "Actions", "Financials", "Holders", "Sustainability", "Recommendations", "Analyst Data"])

            # Company Overview
            with tabs[0]:
                st.subheader("Company Overview")
                st.write(f"**Company Name:** {data['Company Info'].get('longName', 'N/A')}")
                st.write(f"**Description:** {data['Company Info'].get('longBusinessSummary', 'N/A')}")
                st.write(f"**Market Cap:** {format_money(data['Company Info'].get('marketCap', 'N/A'))}")
                st.write(f"**Sector:** {data['Company Info'].get('sector', 'N/A')}")
                st.write(f"**Industry:** {data['Company Info'].get('industry', 'N/A')}")

            # Actions (Dividends, Splits, Capital Gains)
            with tabs[1]:
                st.subheader("Actions (Dividends, Splits, Capital Gains)")
                st.write("**Dividends:**")
                st.write(data['Dividends'])
                st.write("**Stock Splits:**")
                st.write(data['Splits'])
                st.write("**Capital Gains:**")
                st.write(data['Capital Gains'])

            # Financials
            with tabs[2]:
                st.subheader("Financials")
                st.write("**Income Statement:**")
                st.write(data['Financials']['Income Statement'])
                st.write("**Quarterly Income Statement:**")
                st.write(data['Financials']['Quarterly Income Statement'])
                st.write("**Balance Sheet:**")
                st.write(data['Financials']['Balance Sheet'])
                st.write("**Quarterly Balance Sheet:**")
                st.write(data['Financials']['Quarterly Balance Sheet'])
                st.write("**Cash Flow Statement:**")
                st.write(data['Financials']['Cash Flow Statement'])
                st.write("**Quarterly Cash Flow Statement:**")
                st.write(data['Financials']['Quarterly Cash Flow Statement'])

            # Holders
            with tabs[3]:
                st.subheader("Holders and Transactions")
                st.write("**Major Holders:**")
                st.write(data['Holders']['Major Holders'])
                st.write("**Institutional Holders:**")
                st.write(data['Holders']['Institutional Holders'])
                st.write("**Mutual Fund Holders:**")
                st.write(data['Holders']['Mutual Fund Holders'])
                st.write("**Insider Transactions:**")
                st.write(data['Holders']['Insider Transactions'])
                st.write("**Insider Purchases:**")
                st.write(data['Holders']['Insider Purchases'])
                st.write("**Insider Roster:**")
                st.write(data['Holders']['Insider Roster'])

            # Sustainability
            with tabs[4]:
                st.subheader("Sustainability")
                st.write(data['Sustainability'])

            # Recommendations
            with tabs[5]:
                st.subheader("Recommendations")
                st.write("**Recommendations:**")
                st.write(data['Recommendations'])
                st.write("**Recommendations Summary:**")
                st.write(data['Recommendations Summary'])
                st.write("**Upgrades and Downgrades:**")
                st.write(data['Upgrades/Downgrades'])

            # Analyst Data
            with tabs[6]:
                st.subheader("Analyst Data")
                st.write("**Analyst Price Targets:**")
                st.write(data['Analyst Data']['Price Targets'])
                st.write("**Earnings Estimate:**")
                st.write(data['Analyst Data']['Earnings Estimate'])
                st.write("**Revenue Estimate:**")
                st.write(data['Analyst Data']['Revenue Estimate'])
                st.write("**Earnings History:**")
                st.write(data['Analyst Data']['Earnings History'])
                st.write("**EPS Trend:**")
                st.write(data['Analyst Data']['EPS Trend'])
                st.write("**EPS Revisions:**")
                st.write(data['Analyst Data']['EPS Revisions'])
                st.write("**Growth Estimates:**")
                st.write(data['Analyst Data']['Growth Estimates'])
        else:
            st.error("Failed to fetch data. Please try again.")
    else:
        st.warning("Please enter a ticker symbol.")
