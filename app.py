import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Finlytics AI – Fundamental Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    :root {
        --bg:       #0d1117;
        --surface:  #161b22;
        --border:   #30363d;
        --accent:   #58a6ff;
        --accent2:  #3fb950;
        --danger:   #f85149;
        --muted:    #8b949e;
        --text:     #e6edf3;
    }

    html, body, [class*="css"] {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border);
    }

    /* Metric cards */
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: var(--accent); }
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'DM Serif Display', serif;
        font-size: 26px;
        color: var(--text);
        line-height: 1.1;
    }
    .metric-hint {
        font-size: 12px;
        color: var(--muted);
        margin-top: 6px;
        line-height: 1.5;
    }
    .badge-positive { color: var(--accent2); font-weight: 600; }
    .badge-negative { color: var(--danger); font-weight: 600; }

    /* Section headers */
    .section-title {
        font-family: 'DM Serif Display', serif;
        font-size: 22px;
        color: var(--text);
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Hero header */
    .hero {
        background: linear-gradient(135deg, #161b22 0%, #1c2536 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
    }
    .hero-company {
        font-family: 'DM Serif Display', serif;
        font-size: 32px;
        color: var(--text);
        margin-bottom: 4px;
    }
    .hero-meta {
        font-size: 13px;
        color: var(--muted);
    }
    .hero-summary {
        font-size: 14px;
        color: #c9d1d9;
        margin-top: 14px;
        line-height: 1.7;
        border-top: 1px solid var(--border);
        padding-top: 14px;
    }

    /* Pill badges */
    .pill {
        display: inline-block;
        background: rgba(88,166,255,0.12);
        color: var(--accent);
        border: 1px solid rgba(88,166,255,0.3);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 6px;
    }

    /* Tab styling override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--surface);
        border-radius: 8px;
        padding: 4px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--muted) !important;
        border-radius: 6px;
        padding: 6px 18px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--accent) !important;
        color: #0d1117 !important;
    }

    /* Dataframe */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* Input */
    .stTextInput input {
        background: var(--bg) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(88,166,255,0.2) !important;
    }

    /* Button */
    .stButton > button {
        background: var(--accent) !important;
        color: #0d1117 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        width: 100% !important;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        font-weight: 500 !important;
    }

    /* Hide default Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)



# ─── Data Fetching ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_company_data(ticker: str) -> dict | None:
    try:
        company = yf.Ticker(ticker)
        info = company.info
        if not info or info.get("trailingPE") is None and info.get("marketCap") is None:
            st.error(f"No data found for **{ticker}**. Check the ticker symbol and try again.")
            return None

        balance_sheet = company.quarterly_balance_sheet
        cash_flow     = company.quarterly_cashflow
        income_stmt   = company.quarterly_income_stmt
        calendar      = company.calendar
        history       = company.history(period="1y")

        def safe_loc(df, key):
            return df.loc[key][0] if key in df.index and not df.loc[key].empty else None

        return {
            "company_name":      info.get("longName", ticker),
            "business_summary":  info.get("longBusinessSummary", "No business summary available."),
            "sector":            info.get("sector", "N/A"),
            "industry":          info.get("industry", "N/A"),
            "market_cap":        info.get("marketCap"),
            "eps":               info.get("trailingEps"),
            "pe_ratio":          info.get("trailingPE"),
            "forward_pe":        info.get("forwardPE"),
            "pb_ratio":          info.get("priceToBook"),
            "roe":               info.get("returnOnEquity"),
            "roa":               info.get("returnOnAssets"),
            "net_profit_margin": info.get("profitMargins"),
            "gross_margin":      info.get("grossMargins"),
            "dividend_yield":    info.get("dividendYield"),
            "beta":              info.get("beta"),
            "52w_high":          info.get("fiftyTwoWeekHigh"),
            "52w_low":           info.get("fiftyTwoWeekLow"),
            "current_price":     info.get("currentPrice") or info.get("regularMarketPrice"),
            "total_assets":      safe_loc(balance_sheet, "Total Assets"),
            "total_liabilities": safe_loc(balance_sheet, "Total Liabilities Net Minority Interest"),
            "long_term_debt":    safe_loc(balance_sheet, "Long Term Debt"),
            "stockholders_equity": safe_loc(balance_sheet, "Stockholders Equity"),
            "balance_sheet":     balance_sheet,
            "cash_flow":         cash_flow,
            "income_stmt":       income_stmt,
            "calendar":          calendar,
            "history":           history,
            "currency":          info.get("currency", "USD"),
            "exchange":          info.get("exchange", ""),
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None


# ─── Formatting Helpers ──────────────────────────────────────────────────────────
def fmt_large(number, currency="USD"):
    if number is None:
        return "—"
    symbol = "₹" if currency == "INR" else "$"
    if currency == "INR":
        if number >= 1e12:
            return f"{symbol}{number / 1e12:.2f}T Cr"
        elif number >= 1e7:
            return f"{symbol}{number / 1e7:.2f} Cr"
        elif number >= 1e5:
            return f"{symbol}{number / 1e5:.2f} L"
        return f"{symbol}{number:,.0f}"
    else:
        if abs(number) >= 1e12:
            return f"{symbol}{number / 1e12:.2f}T"
        elif abs(number) >= 1e9:
            return f"{symbol}{number / 1e9:.2f}B"
        elif abs(number) >= 1e6:
            return f"{symbol}{number / 1e6:.2f}M"
        return f"{symbol}{number:,.0f}"

def fmt_pct(val, multiply=True):
    if val is None:
        return "—"
    v = val * 100 if multiply else val
    return f"{v:.2f}%"

def fmt_ratio(val, decimals=2):
    if val is None:
        return "—"
    return f"{val:.{decimals}f}x"

def color_val(val, good_positive=True):
    if val is None:
        return "—"
    positive = val > 0
    cls = "badge-positive" if (positive == good_positive) else "badge-negative"
    return f'<span class="{cls}">{val:.2f}</span>'


# ─── Metric Explanations ─────────────────────────────────────────────────────────
EXPLANATIONS = {
    "EPS":               "Earnings Per Share – profit generated per share. Higher is generally better.",
    "P/E Ratio":         "Price-to-Earnings – how much investors pay per dollar of earnings. Compare against sector peers.",
    "Forward P/E":       "P/E based on projected future earnings. Lower may indicate undervaluation.",
    "P/B Ratio":         "Price-to-Book – compares market price to book value. <1 may signal undervaluation.",
    "ROE":               "Return on Equity – profitability relative to shareholder equity. >15% is typically strong.",
    "ROA":               "Return on Assets – how efficiently assets generate profit. Higher = better asset utilisation.",
    "Net Profit Margin": "% of revenue that becomes net profit. Higher margins = stronger pricing power.",
    "Gross Margin":      "Revenue minus COGS as a % of revenue. Reflects operational efficiency.",
    "Dividend Yield":    "Annual dividend / stock price. Attractive for income-focused investors.",
    "Beta":              "Volatility vs. market. >1 = more volatile than market; <1 = more stable.",
    "Total Assets":      "Everything the company owns – a proxy for size and growth potential.",
    "Total Liabilities": "All obligations owed. Lower relative to assets means a healthier balance sheet.",
    "Long Term Debt":    "Debt due beyond one year. Excessive debt can strain future cash flows.",
    "Stockholders Equity": "Assets minus Liabilities – the book value belonging to shareholders.",
}


# ─── Chart Helper ────────────────────────────────────────────────────────────────
def price_chart(history_df, company_name, current_price, w52_high, w52_low):
    if history_df is None or history_df.empty:
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df.index, y=history_df["Close"],
        mode="lines",
        line=dict(color="#58a6ff", width=2),
        fill="tozeroy",
        fillcolor="rgba(88,166,255,0.07)",
        name="Close Price",
        hovertemplate="%{x|%b %d, %Y}<br>Price: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#8b949e"),
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, color="#8b949e", showline=False),
        yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e", showline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=280,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def balance_bar_chart(d):
    labels = ["Total Assets", "Total Liabilities", "Stockholders' Equity"]
    values = [d.get("total_assets"), d.get("total_liabilities"), d.get("stockholders_equity")]
    colors = ["#58a6ff", "#f85149", "#3fb950"]
    valid = [(l, v, c) for l, v, c in zip(labels, values, colors) if v is not None]
    if not valid:
        return
    labels, values, colors = zip(*valid)
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors,
        hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#8b949e"),
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#21262d"),
        height=260,
    )
    st.plotly_chart(fig, use_container_width=True)


# ─── Metric Card Helper ──────────────────────────────────────────────────────────
def metric_card(label, value, hint=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {"<div class='metric-hint'>" + hint + "</div>" if hint else ""}
    </div>
    """, unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Finlytics AI")
    st.markdown("<span style='color:#8b949e;font-size:13px'>Fundamental Analysis</span>", unsafe_allow_html=True)
    st.divider()
    ticker_input = st.text_input(
        "Stock Ticker",
        value="RELIANCE.NS",
        placeholder="e.g. AAPL, RELIANCE.NS",
        help="Use .NS suffix for NSE-listed Indian stocks (e.g. TCS.NS)",
    ).upper().strip()

    analyse_btn = st.button("Analyse", use_container_width=True)
    st.divider()
    st.markdown("<span style='color:#8b949e;font-size:11px'>Data sourced from Yahoo Finance via yfinance · Cached 5 min · Rate-limited 2 req/5s</span>", unsafe_allow_html=True)


# ─── Main Content ────────────────────────────────────────────────────────────────
if not ticker_input:
    st.info("Enter a ticker symbol in the sidebar to begin.")
    st.stop()

with st.spinner(f"Fetching data for **{ticker_input}**…"):
    d = fetch_company_data(ticker_input)

if not d:
    st.stop()

currency = d["currency"]

# ── Hero Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-company">{d['company_name']}</div>
    <div class="hero-meta">
        <span class="pill">{ticker_input}</span>
        <span class="pill">{d['sector']}</span>
        <span class="pill">{d['industry']}</span>
        <span class="pill">{d['exchange']}</span>
    </div>
    <div class="hero-summary">{d['business_summary']}</div>
</div>
""", unsafe_allow_html=True)

# ── KPI Strip ────────────────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpis = [
    ("Current Price", fmt_large(d["current_price"], currency)),
    ("Market Cap",    fmt_large(d["market_cap"], currency)),
    ("52W High",      fmt_large(d["52w_high"], currency)),
    ("52W Low",       fmt_large(d["52w_low"], currency)),
    ("Beta",          f"{d['beta']:.2f}" if d["beta"] else "—"),
]
for col, (label, val) in zip([kpi1, kpi2, kpi3, kpi4, kpi5], kpis):
    with col:
        st.metric(label, val)

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────────
tab_price, tab_fundamentals, tab_financials, tab_statements = st.tabs([
    "📈  Price History",
    "🔍  Fundamentals",
    "💰  Financials",
    "📄  Statements",
])

# ── Tab 1: Price History ─────────────────────────────────────────────────────────
with tab_price:
    st.markdown('<div class="section-title">1-Year Price History</div>', unsafe_allow_html=True)
    price_chart(d["history"], d["company_name"], d["current_price"], d["52w_high"], d["52w_low"])

    if d["history"] is not None and not d["history"].empty:
        h = d["history"]["Close"]
        ch = ((h.iloc[-1] - h.iloc[0]) / h.iloc[0]) * 100
        vol = d["history"]["Volume"].mean()
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("1Y Return", f"{ch:+.2f}%", "Change in close price over 12 months")
        with c2:
            metric_card("Avg Daily Volume", f"{vol:,.0f}", "Average shares traded per day")
        with c3:
            metric_card("52W Range", f"{fmt_large(d['52w_low'], currency)} – {fmt_large(d['52w_high'], currency)}", "Lowest to highest in past 52 weeks")


# ── Tab 2: Fundamentals ──────────────────────────────────────────────────────────
with tab_fundamentals:
    st.markdown('<div class="section-title">Valuation Ratios</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("EPS", f"{d['eps']:.2f}" if d["eps"] else "—", EXPLANATIONS["EPS"])
        metric_card("P/E Ratio", fmt_ratio(d["pe_ratio"]), EXPLANATIONS["P/E Ratio"])
    with c2:
        metric_card("Forward P/E", fmt_ratio(d["forward_pe"]), EXPLANATIONS["Forward P/E"])
        metric_card("P/B Ratio", fmt_ratio(d["pb_ratio"]), EXPLANATIONS["P/B Ratio"])
    with c3:
        metric_card("Dividend Yield", fmt_pct(d["dividend_yield"]), EXPLANATIONS["Dividend Yield"])
        metric_card("Beta", f"{d['beta']:.2f}" if d["beta"] else "—", EXPLANATIONS["Beta"])

    st.markdown('<div class="section-title" style="margin-top:24px">Profitability</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("ROE", fmt_pct(d["roe"]), EXPLANATIONS["ROE"])
    with c2:
        metric_card("ROA", fmt_pct(d["roa"]), EXPLANATIONS["ROA"])
    with c3:
        metric_card("Net Profit Margin", fmt_pct(d["net_profit_margin"]), EXPLANATIONS["Net Profit Margin"])
    with c4:
        metric_card("Gross Margin", fmt_pct(d["gross_margin"]), EXPLANATIONS["Gross Margin"])


# ── Tab 3: Financials ────────────────────────────────────────────────────────────
with tab_financials:
    st.markdown('<div class="section-title">Balance Sheet Overview</div>', unsafe_allow_html=True)
    balance_bar_chart(d)

    c1, c2, c3, c4 = st.columns(4)
    items = [
        ("Total Assets",       fmt_large(d["total_assets"], currency),        EXPLANATIONS["Total Assets"]),
        ("Total Liabilities",  fmt_large(d["total_liabilities"], currency),    EXPLANATIONS["Total Liabilities"]),
        ("Long Term Debt",     fmt_large(d["long_term_debt"], currency),       EXPLANATIONS["Long Term Debt"]),
        ("Stockholders Equity",fmt_large(d["stockholders_equity"], currency),  EXPLANATIONS["Stockholders Equity"]),
    ]
    for col, (label, val, hint) in zip([c1, c2, c3, c4], items):
        with col:
            metric_card(label, val, hint)

    # Debt-to-equity
    if d["long_term_debt"] and d["stockholders_equity"] and d["stockholders_equity"] != 0:
        dte = d["long_term_debt"] / d["stockholders_equity"]
        st.markdown('<div class="section-title" style="margin-top:24px">Leverage</div>', unsafe_allow_html=True)
        metric_card("Debt-to-Equity Ratio", f"{dte:.2f}x", "Long-term debt divided by stockholders' equity. Below 1x is generally conservative.")


# ── Tab 4: Statements ────────────────────────────────────────────────────────────
with tab_statements:
    st.markdown('<div class="section-title">Quarterly Financial Statements</div>', unsafe_allow_html=True)

    with st.expander("📋  Balance Sheet", expanded=True):
        if d["balance_sheet"] is not None and not d["balance_sheet"].empty:
            st.dataframe(
                d["balance_sheet"].style.format("{:,.0f}", na_rep="—"),
                use_container_width=True,
            )
        else:
            st.info("Balance sheet data not available.")

    with st.expander("💵  Cash Flow Statement"):
        if d["cash_flow"] is not None and not d["cash_flow"].empty:
            st.dataframe(
                d["cash_flow"].style.format("{:,.0f}", na_rep="—"),
                use_container_width=True,
            )
        else:
            st.info("Cash flow data not available.")

    with st.expander("📊  Income Statement"):
        if d["income_stmt"] is not None and not d["income_stmt"].empty:
            st.dataframe(
                d["income_stmt"].style.format("{:,.0f}", na_rep="—"),
                use_container_width=True,
            )
        else:
            st.info("Income statement data not available.")

    with st.expander("📅  Earnings Calendar"):
        cal = d["calendar"]
        if cal is not None:
            if isinstance(cal, dict):
                cal_df = pd.DataFrame([cal])
            else:
                cal_df = pd.DataFrame(cal)
            st.dataframe(cal_df, use_container_width=True)
        else:
            st.info("Earnings calendar not available.")
