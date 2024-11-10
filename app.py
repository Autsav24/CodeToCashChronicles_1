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

# Function to fetch and display analyst data (price targets, estimates, etc.)
def fetch_analyst_data(ticker):
    try:
        company = yf.Ticker(ticker)

        # Fetching various analyst data
        analyst_price_targets = company.analyst_price_targets
        earnings_estimate = company.earnings_estimate
        revenue_estimate = company.revenue_estimate
        earnings_history = company.earnings_history
        eps_trend = company.eps_trend
        eps_revisions = company.eps_revisions
        growth_estimates = company.growth_estimates

        # Return fetched data
        return {
            'Analyst Price Targets': analyst_price_targets,
            'Earnings Estimate': earnings_estimate,
            'Revenue Estimate': revenue_estimate,
            'Earnings History': earnings_history,
            'EPS Trend': eps_trend,
            'EPS Revisions': eps_revisions,
            'Growth Estimates': growth_estimates
        }
    except Exception as e:
        st.error(f"Error fetching analyst data for {ticker}: {e}")
        return None

# Streamlit UI setup
st.title('**Fundamental Analysis Tool**')

st.sidebar.title("Options")
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.NS").upper()

if ticker_input:
    company_data = fetch_company_data(ticker_input)

    if company_data:
        # Company Overview Section
        st.subheader(f"Company Overview: {company_data['Company']}")
        st.write(f"**Sector**: {company_data['Sector']}")
        st.write(f"**Industry**: {company_data['Industry']}")
        st.write(f"**Market Cap**: ₹{company_data['Market Cap']/1e7:.2f} Crores")

        # Fundamentals Section
        st.subheader("**Fundamentals**")
        if company_data['EPS'] is not None:
            st.write(f"**EPS**: ₹{company_data['EPS']:.2f}")
        else:
            st.write(f"**EPS**: Data not available")
        
        if company_data['P/E Ratio'] is not None:
            st.write(f"**P/E Ratio**: {company_data['P/E Ratio']:.2f}")
        else:
            st.write(f"**P/E Ratio**: Data not available")
        
        if company_data['ROE'] is not None:
            st.write(f"**ROE**: {company_data['ROE']*100:.2f}%")
        else:
            st.write(f"**ROE**: Data not available")
        
        if company_data['Net Profit Margin'] is not None:
            st.write(f"**Net Profit Margin**: {company_data['Net Profit Margin']*100:.2f}%")
        else:
            st.write(f"**Net Profit Margin**: Data not available")
        
        if company_data['Dividend Yield'] is not None:
            st.write(f"**Dividend Yield**: {company_data['Dividend Yield']*100:.2f}%")
        else:
            st.write(f"**Dividend Yield**: Data not available")

        # Financials Section
        st.subheader("**Financials**")
        st.markdown(display_metric_value("Total Assets", company_data.get('Total Assets')), unsafe_allow_html=True)
        st.markdown(display_metric_value("Total Liabilities", company_data.get('Total Liabilities')), unsafe_allow_html=True)
        st.markdown(display_metric_value("Current Assets", company_data.get('Current Assets')), unsafe_allow_html=True)
        st.markdown(display_metric_value("Current Liabilities", company_data.get('Current Liabilities')), unsafe_allow_html=True)
        st.markdown(display_metric_value("Long Term Debt", company_data.get('Long Term Debt')), unsafe_allow_html=True)
        st.markdown(display_metric_value("Shareholder Equity", company_data.get('Shareholder Equity')), unsafe_allow_html=True)

        # Fetch and Display Analyst Data
        analyst_data = fetch_analyst_data(ticker_input)

        if analyst_data:
            st.subheader("**Analyst Data**")
            
            # Display Analyst Price Targets
            if analyst_data['Analyst Price Targets'] is not None:
                st.write("**Analyst Price Targets**:")
                st.write(analyst_data['Analyst Price Targets'])
            else:
                st.write("**Analyst Price Targets**: Data not available")

            # Display Earnings Estimate
            if analyst_data['Earnings Estimate'] is not None:
                st.write("**Earnings Estimate**:")
                st.write(analyst_data['Earnings Estimate'])
            else:
                st.write("**Earnings Estimate**: Data not available")

            # Display Revenue Estimate
            if analyst_data['Revenue Estimate'] is not None:
                st.write("**Revenue Estimate**:")
                st.write(analyst_data['Revenue Estimate'])
            else:
                st.write("**Revenue Estimate**: Data not available")

            # Display Earnings History
            if analyst_data['Earnings History'] is not None:
                st.write("**Earnings History**:")
                st.write(analyst_data['Earnings History'])
            else:
                st.write("**Earnings History**: Data not available")

            # Display EPS Trend
            if analyst_data['EPS Trend'] is not None:
                st.write("**EPS Trend**:")
                st.write(analyst_data['EPS Trend'])
            else:
                st.write("**EPS Trend**: Data not available")

            # Display EPS Revisions
            if analyst_data['EPS Revisions'] is not None:
                st.write("**EPS Revisions**:")
                st.write(analyst_data['EPS Revisions'])
            else:
                st.write("**EPS Revisions**: Data not available")

            # Display Growth Estimates
            if analyst_data['Growth Estimates'] is not None:
                st.write("**Growth Estimates**:")
                st.write(analyst_data['Growth Estimates'])
            else:
                st.write("**Growth Estimates**: Data not available")
