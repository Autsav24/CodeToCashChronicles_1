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

def should_invest(
    current_ratio=None, 
    debt_to_equity=None, 
    roe=None, 
    pe_ratio=None, 
    eps_growth=None, 
    free_cash_flow=None, 
    net_profit_margin=None, 
    dividend_yield=None, 
    beta=None, 
    industry=None, 
    investor_preference="balanced"
):
    # Default values for missing data (fallbacks)
    default_values = {
        "current_ratio": 1.5,
        "debt_to_equity": 1.0,
        "roe": 12,
        "pe_ratio": 20,
        "eps_growth": 5,
        "free_cash_flow": 0,
        "net_profit_margin": 8,
        "dividend_yield": 2,
        "beta": 1.0,
    }

    score = 0
    total_weight = 0

    # Industry-based weightings (example)
    industry_sensitivity = {
        "tech": {"pe_ratio": 1.5, "eps_growth": 2.0, "roe": 1.2},
        "finance": {"debt_to_equity": 1.8, "roe": 1.5, "dividend_yield": 1.5},
        "energy": {"free_cash_flow": 1.5, "debt_to_equity": 1.5, "dividend_yield": 1.5},
    }

    # Default weights for a "balanced" investor
    weights = {
        "current_ratio": 1.0,
        "debt_to_equity": 1.5,
        "roe": 1.5,
        "pe_ratio": 1.2,
        "eps_growth": 1.5,
        "free_cash_flow": 1.3,
        "net_profit_margin": 1.2,
        "dividend_yield": 1.2,
        "beta": 1.0,
    }

    if industry is not None and industry in industry_sensitivity:
        for key, multiplier in industry_sensitivity[industry].items():
            if key in weights:
                weights[key] *= multiplier

    # Adjust weights based on investor preference
    if investor_preference == "growth":
        weights.update({"eps_growth": 2.0, "pe_ratio": 1.7})
    elif investor_preference == "value":
        weights.update({"dividend_yield": 2.0, "pe_ratio": 0.8})
    elif investor_preference == "dividend":
        weights.update({"dividend_yield": 2.5, "free_cash_flow": 1.7})

    def get_metric_value(metric, default_value):
        return metric if metric is not None else default_value

    # Calculation for each metric
    current_ratio_value = get_metric_value(current_ratio, default_values["current_ratio"])
    if current_ratio_value >= 1.5:
        score += weights["current_ratio"] * 1
    elif current_ratio_value >= 1:
        score += weights["current_ratio"] * 0.5
    total_weight += weights["current_ratio"]

    debt_to_equity_value = get_metric_value(debt_to_equity, default_values["debt_to_equity"])
    if debt_to_equity_value < 1:
        score += weights["debt_to_equity"] * 1
    elif debt_to_equity_value < 2:
        score += weights["debt_to_equity"] * 0.5
    total_weight += weights["debt_to_equity"]

    roe_value = get_metric_value(roe, default_values["roe"])
    if roe_value > 15:
        score += weights["roe"] * 1
    elif roe_value > 10:
        score += weights["roe"] * 0.5
    total_weight += weights["roe"]

    pe_ratio_value = get_metric_value(pe_ratio, default_values["pe_ratio"])
    if pe_ratio_value < 15:
        score += weights["pe_ratio"] * 1
    elif pe_ratio_value < 25:
        score += weights["pe_ratio"] * 0.5
    total_weight += weights["pe_ratio"]

    eps_growth_value = get_metric_value(eps_growth, default_values["eps_growth"])
    if eps_growth_value > 0:
        score += weights["eps_growth"] * 1
    elif eps_growth_value > -10:
        score += weights["eps_growth"] * 0.5
    total_weight += weights["eps_growth"]

    free_cash_flow_value = get_metric_value(free_cash_flow, default_values["free_cash_flow"])
    if free_cash_flow_value > 0:
        score += weights["free_cash_flow"] * 1
    total_weight += weights["free_cash_flow"]

    net_profit_margin_value = get_metric_value(net_profit_margin, default_values["net_profit_margin"])
    if net_profit_margin_value > 10:
        score += weights["net_profit_margin"] * 1
    elif net_profit_margin_value > 5:
        score += weights["net_profit_margin"] * 0.5
    total_weight += weights["net_profit_margin"]

    dividend_yield_value = get_metric_value(dividend_yield, default_values["dividend_yield"])
    if dividend_yield_value > 2:
        score += weights["dividend_yield"] * 1
    total_weight += weights["dividend_yield"]

    beta_value = get_metric_value(beta, default_values["beta"])
    if beta_value < 1:
        score += weights["beta"] * 1
    elif beta_value < 1.5:
        score += weights["beta"] * 0.5
    total_weight += weights["beta"]

    if total_weight == 0:
        return "Insufficient Data"

    normalized_score = score / total_weight

    # Investment recommendation logic with reasoning
    if normalized_score >= 0.75:
        return "Strong Buy: High confidence in investment potential."
    elif normalized_score >= 0.55:
        return "Buy: Good opportunity with solid metrics."
    elif normalized_score >= 0.35:
        return "Hold: Monitor the situation closely."
    else:
        return "Sell: Consider reallocating investments."

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
            'Company': info['longName'] if 'longName' in info else ticker,
            'Current Ratio': current_ratio,
            'Debt to Equity': debt_to_equity,
            'Investment Status': investment_status,
            'EPS': eps,
            'P/E Ratio': pe_ratio,
            'ROE': roe,
            'Net Profit Margin': net_profit_margin,
            'Dividend Yield': dividend_yield,
            'Sector': info.get('sector'),
            'Industry': info.get('industry'),
            'Market Cap': info.get('marketCap'),
            'Description': info.get('longBusinessSummary'),
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
        st.write(company_data['Description'])
        st.write(f"**Sector**: {company_data['Sector']}")
        st.write(f"**Industry**: {company_data['Industry']}")
        st.write(f"**Market Cap**: {company_data['Market Cap']}")
        
        st.write(f"**Current Ratio**: {company_data['Current Ratio']}")
        st.write(f"**Debt to Equity Ratio**: {company_data['Debt to Equity']}")
        st.write(f"**EPS**: {company_data['EPS']}")
        st.write(f"**P/E Ratio**: {company_data['P/E Ratio']}")
        st.write(f"**ROE**: {company_data['ROE']}")
        st.write(f"**Net Profit Margin**: {company_data['Net Profit Margin']}")
        st.write(f"**Dividend Yield**: {company_data['Dividend Yield']}")
        
        st.subheader("Investment Recommendation")
        st.write(f"**Recommendation**: {company_data['Investment Status']}")
