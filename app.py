# Function to format numbers in Indian numbering style (Lakhs, Crores, etc.)
def format_in_indian_style(number):
    """Formats numbers into Indian numbering style."""
    if number is None:
        return "Data not available"
    elif number >= 1e12:  # Thousands of crores
        return f"₹{number / 1e12:.2f} Thousand Crores"
    elif number >= 1e7:  # Crores
        return f"₹{number / 1e7:.2f} Crores"
    elif number >= 1e5:  # Lakhs
        return f"₹{number / 1e5:.2f} Lakhs"
    else:
        return f"₹{number:.2f}"

# Metric explanations for each financial term
def display_metric_explanation(metric_name):
    explanations = {
        "Total Assets": "The total value of everything the company owns.",
        "Total Liabilities": "The total debt the company owes.",
        "Long Term Debt": "Debt that is due in more than one year.",
        "EPS": "Earnings Per Share – profit generated per share.",
        "P/E Ratio": "Price-to-Earnings ratio – compares stock price to earnings.",
        "ROE": "Return on Equity – profitability based on shareholder equity.",
        "Net Profit Margin": "Percentage of revenue that becomes profit.",
        "Dividend Yield": "Annual dividend payment divided by stock price."
    }
    return explanations.get(metric_name, "No explanation available.")

# Streamlit UI setup
st.title('**Fundamental Analysis Tool**')

st.sidebar.title("Options")
ticker_input = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.NS").upper()

if ticker_input:
    company_data = fetch_company_data(ticker_input)

    if company_data:
        # Display Company Overview
        st.subheader(f"Company Overview: {company_data['Company']}")
        st.write(f"**Business Summary**: {company_data['Business Summary']}")
        st.write(f"**Sector**: {company_data['Sector']}")
        st.write(f"**Industry**: {company_data['Industry']}")
        st.write(f"**Market Cap**: {format_in_indian_style(company_data['Market Cap'])}")

        # Display Financial Metrics
        st.subheader("**Fundamentals**")
        
        metrics = {
            "EPS": company_data['EPS'],
            "P/E Ratio": company_data['P/E Ratio'],
            "ROE": company_data['ROE'] * 100 if company_data['ROE'] else None,
            "Net Profit Margin": company_data['Net Profit Margin'] * 100 if company_data['Net Profit Margin'] else None,
            "Dividend Yield": company_data['Dividend Yield'] * 100 if company_data['Dividend Yield'] else None
        }
        
        for metric, value in metrics.items():
            if value is not None:
                st.write(f"**{metric}**: {value:.2f}" if metric != "Market Cap" else f"**{metric}**: {format_in_indian_style(value)}")
            else:
                st.write(f"**{metric}**: Data not available")
            st.write(display_metric_explanation(metric))
        
        # Display Financials
        st.subheader("**Financials**")
        financials = {
            "Total Assets": company_data['Total Assets'],
            "Total Liabilities": company_data['Total Liabilities'],
            "Long Term Debt": company_data['Long Term Debt']
        }
        
        for financial, value in financials.items():
            st.markdown(f"**{financial}**: {format_in_indian_style(value)}" if value else f"**{financial}**: Data not available")
            st.write(display_metric_explanation(financial))
        
        # Display Financial Statements
        st.subheader("**Financial Statements**")
        
        st.write("**Quarterly Balance Sheet**:")
        st.write(company_data['Quarterly Balance Sheet'])
        
        st.write("**Quarterly Cash Flow Statement**:")
        st.write(company_data['Quarterly Cash Flow'])
        
        st.write("**Calendar Data**:")
        st.write(company_data['Calendar'])

    else:
        st.error(f"No data available for ticker '{ticker_input}'. Please check the ticker symbol or try a different one.")
