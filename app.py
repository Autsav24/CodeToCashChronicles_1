import os
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image

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

        current_ratio = (current_assets / current_liabilities) if current_liabilities else None
        debt_to_equity = (total_liabilities / shareholder_equity) if shareholder_equity else None

        eps = info.get('trailingEps')
        pe_ratio = info.get('forwardPE')
        roe = info.get('returnOnEquity')
        net_profit_margin = info.get('profitMargins')
        dividend_yield = info.get('dividendYield')

        investment_status = should_invest(current_ratio, debt_to_equity, roe, pe_ratio, None, None, net_profit_margin, dividend_yield)

        return {
            'Company': info.get('longName', ticker),
            'Founded': info.get('yearFounded', 'N/A'),
            'Products': info.get('products', 'N/A'),
            'Description': info.get('longBusinessSummary', 'N/A'),
            'Current Projects': info.get('currentProjects', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'Current Ratio': current_ratio,
            'Debt to Equity': debt_to_equity,
            'EPS': eps,
            'P/E Ratio': pe_ratio,
            'ROE': roe,
            'Net Profit Margin': net_profit_margin,
            'Dividend Yield': dividend_yield,
            'Investment Status': investment_status
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Streamlit UI setup
st.title('**Investment Analysis Tool**')

st.sidebar.title("Options")
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.NS").upper()
investor_preference = st.sidebar.selectbox("Select Investor Preference", ["balanced", "growth", "value", "dividend"])

if ticker_input:
    company_data = fetch_company_data(ticker_input)

    if company_data:
        st.subheader(f"Company Overview: {company_data['Company']}")
        st.write(f"**Founded**: {company_data['Founded']}")
        st.write(f"**Products/Services**: {company_data['Products']}")
        st.write(f"**Description**: {company_data['Description']}")
        st.write(f"**Current Projects**: {company_data['Current Projects']}")
        st.write(f"**Sector**: {company_data['Sector']}")
        st.write(f"**Industry**: {company_data['Industry']}")
        st.write(f"**Market Cap**: {company_data['Market Cap']}")

        st.subheader("Financial Metrics")
        st.write(f"**Current Ratio**: {company_data['Current Ratio']}")
        st.write(f"**Debt to Equity Ratio**: {company_data['Debt to Equity']}")
        st.write(f"**EPS**: {company_data['EPS']}")
        st.write(f"**P/E Ratio**: {company_data['P/E Ratio']}")
        st.write(f"**ROE**: {company_data['ROE']}")
        st.write(f"**Net Profit Margin**: {company_data['Net Profit Margin']}")
        st.write(f"**Dividend Yield**: {company_data['Dividend Yield']}")

        st.subheader("Investment Recommendation")
        st.write(f"**Recommendation**: {company_data['Investment Status']}")
