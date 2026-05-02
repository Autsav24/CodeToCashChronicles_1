import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import io

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Finlytics – Fundamental Analysis",
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
        --warning:  #d29922;
        --muted:    #8b949e;
        --text:     #e6edf3;
    }

    html, body, [class*="css"] {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

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
    .metric-card.good  { border-left: 3px solid var(--accent2); }
    .metric-card.warn  { border-left: 3px solid var(--warning); }
    .metric-card.bad   { border-left: 3px solid var(--danger); }
    .metric-label {
        font-size: 11px; font-weight: 600; letter-spacing: 1.2px;
        text-transform: uppercase; color: var(--muted); margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'DM Serif Display', serif;
        font-size: 26px; color: var(--text); line-height: 1.1;
    }
    .metric-hint { font-size: 12px; color: var(--muted); margin-top: 6px; line-height: 1.5; }
    .badge-positive { color: var(--accent2); font-weight: 600; }
    .badge-negative { color: var(--danger); font-weight: 600; }
    .badge-warning  { color: var(--warning); font-weight: 600; }

    /* Section headers */
    .section-title {
        font-family: 'DM Serif Display', serif;
        font-size: 22px; color: var(--text);
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px; margin-bottom: 20px;
    }

    /* Hero header */
    .hero {
        background: linear-gradient(135deg, #161b22 0%, #1c2536 100%);
        border: 1px solid var(--border);
        border-radius: 16px; padding: 28px 32px; margin-bottom: 28px;
    }
    .hero-company { font-family: 'DM Serif Display', serif; font-size: 32px; color: var(--text); margin-bottom: 4px; }
    .hero-meta    { font-size: 13px; color: var(--muted); }
    .hero-summary {
        font-size: 14px; color: #c9d1d9; margin-top: 14px; line-height: 1.7;
        border-top: 1px solid var(--border); padding-top: 14px;
    }

    /* Pill badges */
    .pill {
        display: inline-block;
        background: rgba(88,166,255,0.12); color: var(--accent);
        border: 1px solid rgba(88,166,255,0.3); border-radius: 20px;
        padding: 3px 12px; font-size: 12px; font-weight: 500; margin-right: 6px;
    }

    /* Verdict card */
    .verdict-card {
        border-radius: 14px; padding: 22px 28px; margin-bottom: 24px;
        border: 1px solid var(--border);
    }
    .verdict-card.buy  { background: rgba(63,185,80,0.08);  border-color: rgba(63,185,80,0.4); }
    .verdict-card.hold { background: rgba(210,153,34,0.08); border-color: rgba(210,153,34,0.4); }
    .verdict-card.sell { background: rgba(248,81,73,0.08);  border-color: rgba(248,81,73,0.4); }
    .verdict-label { font-size: 11px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
    .verdict-signal { font-family: 'DM Serif Display', serif; font-size: 36px; margin-bottom: 8px; }
    .verdict-signal.buy  { color: var(--accent2); }
    .verdict-signal.hold { color: var(--warning); }
    .verdict-signal.sell { color: var(--danger); }
    .verdict-reason { font-size: 13px; color: #c9d1d9; line-height: 1.7; }
    .verdict-score  { font-size: 13px; color: var(--muted); margin-top: 8px; }

    /* Price range bar */
    .range-bar-wrap { margin: 10px 0 4px 0; }
    .range-bar-bg {
        width: 100%; height: 6px; background: var(--border);
        border-radius: 4px; position: relative; overflow: visible;
    }
    .range-bar-fill { height: 6px; border-radius: 4px; background: var(--accent); }
    .range-bar-dot {
        width: 14px; height: 14px; border-radius: 50%;
        background: var(--text); border: 2px solid var(--accent);
        position: absolute; top: -4px; transform: translateX(-50%);
    }
    .range-labels {
        display: flex; justify-content: space-between;
        font-size: 11px; color: var(--muted); margin-top: 10px;
    }

    /* Score badge */
    .score-badge {
        display: inline-block; border-radius: 6px; padding: 4px 10px;
        font-size: 12px; font-weight: 600; margin-left: 8px;
    }
    .score-good { background: rgba(63,185,80,0.15);  color: var(--accent2); }
    .score-warn { background: rgba(210,153,34,0.15); color: var(--warning); }
    .score-bad  { background: rgba(248,81,73,0.15);  color: var(--danger); }

    /* Trend arrow */
    .trend-up   { color: var(--accent2); font-weight: 600; }
    .trend-down { color: var(--danger);  font-weight: 600; }
    .trend-flat { color: var(--muted);   font-weight: 600; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; background: var(--surface); border-radius: 8px;
        padding: 4px; border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] { color: var(--muted) !important; border-radius: 6px; padding: 6px 18px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background-color: var(--accent) !important; color: #0d1117 !important; }

    .stDataFrame { border-radius: 10px; overflow: hidden; }

    .stTextInput input {
        background: var(--bg) !important; border: 1px solid var(--border) !important;
        color: var(--text) !important; border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(88,166,255,0.2) !important;
    }

    .stButton > button {
        background: var(--accent) !important; color: #0d1117 !important;
        font-weight: 600 !important; border: none !important;
        border-radius: 8px !important; padding: 8px 20px !important;
        width: 100% !important; transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    .streamlit-expanderHeader {
        background: var(--surface) !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; color: var(--text) !important; font-weight: 500 !important;
    }

    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ─── Data Fetching ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_company_data(ticker: str) -> dict | None:
    try:
        company = yf.Ticker(ticker)
        info = {}
        try:
            info = company.info or {}
        except Exception:
            pass

        fast = {}
        try:
            fi = company.fast_info
            fast = {
                "market_cap":    getattr(fi, "market_cap", None),
                "52w_high":      getattr(fi, "year_high", None),
                "52w_low":       getattr(fi, "year_low", None),
                "current_price": getattr(fi, "last_price", None),
                "currency":      getattr(fi, "currency", "INR"),
                "exchange":      getattr(fi, "exchange", ""),
            }
        except Exception:
            pass

        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or fast.get("current_price")
        market_cap    = info.get("marketCap") or fast.get("market_cap")
        if not current_price and not market_cap:
            st.error(f"No data found for **{ticker}**. Please verify the ticker symbol (e.g. RELIANCE.NS, TCS.NS, AAPL).")
            return None

        balance_sheet, cash_flow, income_stmt, calendar, history = None, None, None, None, None
        try: balance_sheet = company.quarterly_balance_sheet
        except Exception: pass
        try: cash_flow = company.quarterly_cashflow
        except Exception: pass
        try: income_stmt = company.quarterly_income_stmt
        except Exception: pass
        try: calendar = company.calendar
        except Exception: pass
        try: history = company.history(period="1y")
        except Exception: pass

        def safe_loc(df, key):
            try:
                if df is not None and key in df.index and not df.loc[key].empty:
                    val = df.loc[key].iloc[0]
                    return float(val) if pd.notna(val) else None
            except Exception:
                pass
            return None

        # Next earnings date
        next_earnings = None
        try:
            cal = company.calendar
            if cal is not None:
                if isinstance(cal, dict):
                    ne = cal.get("Earnings Date")
                    if ne:
                        next_earnings = ne[0] if isinstance(ne, list) else ne
                elif hasattr(cal, "loc"):
                    row = cal.loc["Earnings Date"] if "Earnings Date" in cal.index else None
                    if row is not None:
                        next_earnings = row.iloc[0]
        except Exception:
            pass

        return {
            "company_name":        info.get("longName", ticker),
            "business_summary":    info.get("longBusinessSummary", "No business summary available."),
            "sector":              info.get("sector", "N/A"),
            "industry":            info.get("industry", "N/A"),
            "market_cap":          market_cap,
            "eps":                 info.get("trailingEps"),
            "pe_ratio":            info.get("trailingPE"),
            "forward_pe":          info.get("forwardPE"),
            "pb_ratio":            info.get("priceToBook"),
            "roe":                 info.get("returnOnEquity"),
            "roa":                 info.get("returnOnAssets"),
            "net_profit_margin":   info.get("profitMargins"),
            "gross_margin":        info.get("grossMargins"),
            "dividend_yield":      info.get("dividendYield"),
            "beta":                info.get("beta"),
            "52w_high":            info.get("fiftyTwoWeekHigh") or fast.get("52w_high"),
            "52w_low":             info.get("fiftyTwoWeekLow")  or fast.get("52w_low"),
            "current_price":       current_price,
            "total_assets":        safe_loc(balance_sheet, "Total Assets"),
            "total_liabilities":   safe_loc(balance_sheet, "Total Liabilities Net Minority Interest"),
            "long_term_debt":      safe_loc(balance_sheet, "Long Term Debt"),
            "stockholders_equity": safe_loc(balance_sheet, "Stockholders Equity"),
            "balance_sheet":       balance_sheet,
            "cash_flow":           cash_flow,
            "income_stmt":         income_stmt,
            "calendar":            calendar,
            "history":             history,
            "currency":            info.get("currency") or fast.get("currency", "INR"),
            "exchange":            info.get("exchange") or fast.get("exchange", ""),
            "next_earnings":       next_earnings,
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None


# ─── Formatting Helpers ──────────────────────────────────────────────────────────
def fmt_large(number, currency="USD"):
    if number is None: return "—"
    symbol = "₹" if currency == "INR" else "$"
    if currency == "INR":
        if number >= 1e12: return f"{symbol}{number / 1e12:.2f}T Cr"
        elif number >= 1e7: return f"{symbol}{number / 1e7:.2f} Cr"
        elif number >= 1e5: return f"{symbol}{number / 1e5:.2f} L"
        return f"{symbol}{number:,.0f}"
    else:
        if abs(number) >= 1e12: return f"{symbol}{number / 1e12:.2f}T"
        elif abs(number) >= 1e9: return f"{symbol}{number / 1e9:.2f}B"
        elif abs(number) >= 1e6: return f"{symbol}{number / 1e6:.2f}M"
        return f"{symbol}{number:,.0f}"

def fmt_pct(val, multiply=True):
    if val is None: return "—"
    v = val * 100 if multiply else val
    return f"{v:.2f}%"

def fmt_ratio(val, decimals=2):
    if val is None: return "—"
    return f"{val:.{decimals}f}x"


# ─── Metric Explanations ─────────────────────────────────────────────────────────
EXPLANATIONS = {
    "EPS":               "Earnings Per Share – profit generated per share. Higher is generally better.",
    "P/E Ratio":         "Price-to-Earnings – how much investors pay per ₹/$ of earnings. Compare against sector peers.",
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


# ─── Health Scoring ──────────────────────────────────────────────────────────────
def score_metric(key, val):
    """Returns (score 0–2, css_class). 2=good, 1=warn, 0=bad"""
    if val is None:
        return None, ""
    rules = {
        "roe":               [(0.15, 2), (0.08, 1), (None, 0)],
        "roa":               [(0.08, 2), (0.04, 1), (None, 0)],
        "net_profit_margin": [(0.15, 2), (0.05, 1), (None, 0)],
        "gross_margin":      [(0.40, 2), (0.20, 1), (None, 0)],
        "pe_ratio":          [(None, None)],   # handled specially
        "pb_ratio":          [(None, None)],
        "beta":              [(None, None)],
        "dividend_yield":    [(0.03, 2), (0.005, 1), (None, 0)],
    }
    if key == "pe_ratio":
        if val <= 0:    return 0, "bad"
        elif val <= 25: return 2, "good"
        elif val <= 40: return 1, "warn"
        else:           return 0, "bad"
    if key == "pb_ratio":
        if val <= 1:    return 2, "good"
        elif val <= 3:  return 1, "warn"
        else:           return 0, "bad"
    if key == "beta":
        if 0.5 <= val <= 1.2: return 2, "good"
        elif val <= 1.8:      return 1, "warn"
        else:                 return 0, "bad"
    for threshold, score in rules.get(key, []):
        if threshold is None or val >= threshold:
            css = {2: "good", 1: "warn", 0: "bad"}[score]
            return score, css
    return None, ""

def compute_verdict(d):
    """Returns (signal, score_pct, reasons, strengths, risks)"""
    checks = {
        "roe":               d.get("roe"),
        "roa":               d.get("roa"),
        "net_profit_margin": d.get("net_profit_margin"),
        "pe_ratio":          d.get("pe_ratio"),
        "pb_ratio":          d.get("pb_ratio"),
        "gross_margin":      d.get("gross_margin"),
    }
    total, scored = 0, 0
    strengths, risks = [], []

    for key, val in checks.items():
        sc, _ = score_metric(key, val)
        if sc is None: continue
        scored += 2
        total  += sc
        label = key.replace("_", " ").upper()
        if sc == 2:   strengths.append(label)
        elif sc == 0: risks.append(label)

    # Debt check
    lt_debt = d.get("long_term_debt")
    eq = d.get("stockholders_equity")
    if lt_debt and eq and eq != 0:
        dte = lt_debt / eq
        scored += 2
        if dte < 0.5:
            total += 2; strengths.append("LOW DEBT-TO-EQUITY")
        elif dte < 1.5:
            total += 1
        else:
            risks.append("HIGH DEBT-TO-EQUITY")

    pct = (total / scored * 100) if scored else 0

    if pct >= 65:   signal = "BUY"
    elif pct >= 40: signal = "HOLD"
    else:           signal = "SELL / AVOID"

    reasons = []
    if strengths:
        reasons.append(f"Strong on: {', '.join(strengths[:3])}.")
    if risks:
        reasons.append(f"Weak on: {', '.join(risks[:3])}.")
    if not reasons:
        reasons.append("Insufficient data to draw a strong conclusion.")

    return signal, round(pct), " ".join(reasons), strengths, risks


# ─── Trend Arrow ────────────────────────────────────────────────────────────────
def trend_arrow(df, row_key):
    """Compare latest vs previous quarter for a given row in a DataFrame."""
    try:
        if df is None or row_key not in df.index or df.shape[1] < 2:
            return ""
        latest = df.loc[row_key].iloc[0]
        prev   = df.loc[row_key].iloc[1]
        if pd.isna(latest) or pd.isna(prev) or prev == 0:
            return ""
        chg = (latest - prev) / abs(prev) * 100
        if chg > 2:
            return f'<span class="trend-up">▲ {chg:.1f}%</span>'
        elif chg < -2:
            return f'<span class="trend-down">▼ {abs(chg):.1f}%</span>'
        else:
            return f'<span class="trend-flat">→ {chg:.1f}%</span>'
    except Exception:
        return ""


# ─── Chart Helpers ───────────────────────────────────────────────────────────────
def price_chart(history_df):
    if history_df is None or history_df.empty: return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df.index, y=history_df["Close"],
        mode="lines",
        line=dict(color="#58a6ff", width=2),
        fill="tozeroy", fillcolor="rgba(88,166,255,0.07)",
        name="Close Price",
        hovertemplate="%{x|%b %d, %Y}<br>Price: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#8b949e"),
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, color="#8b949e", showline=False),
        yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e", showline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=280, hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def balance_bar_chart(d):
    labels = ["Total Assets", "Total Liabilities", "Stockholders' Equity"]
    values = [d.get("total_assets"), d.get("total_liabilities"), d.get("stockholders_equity")]
    colors = ["#58a6ff", "#f85149", "#3fb950"]
    valid  = [(l, v, c) for l, v, c in zip(labels, values, colors) if v is not None]
    if not valid: return
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
def metric_card(label, value, hint="", css_class=""):
    cls = f"metric-card {css_class}".strip()
    st.markdown(f"""
    <div class="{cls}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {"<div class='metric-hint'>" + hint + "</div>" if hint else ""}
    </div>
    """, unsafe_allow_html=True)


def scored_metric_card(label, value, hint, score_key, raw_val):
    _, css = score_metric(score_key, raw_val)
    metric_card(label, value, hint, css)


# ─── Price Range Bar ─────────────────────────────────────────────────────────────
def price_range_bar(current, low, high, currency):
    if None in (current, low, high) or high == low: return
    pct = max(0, min(100, (current - low) / (high - low) * 100))
    sym = "₹" if currency == "INR" else "$"
    st.markdown(f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 24px;margin-bottom:20px;">
        <div class="metric-label">52-Week Price Position</div>
        <div style="font-family:'DM Serif Display',serif;font-size:22px;margin-bottom:14px;">
            {sym}{current:,.2f}
            <span style="font-size:13px;color:var(--muted);font-family:'DM Sans',sans-serif;margin-left:8px;">
                {pct:.0f}% of 52W range
            </span>
        </div>
        <div class="range-bar-bg">
            <div class="range-bar-fill" style="width:{pct}%"></div>
            <div class="range-bar-dot" style="left:{pct}%"></div>
        </div>
        <div class="range-labels">
            <span>52W Low: {sym}{low:,.2f}</span>
            <span>52W High: {sym}{high:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Export Helper ───────────────────────────────────────────────────────────────
def build_export_csv(d, ticker):
    rows = [
        ("Ticker", ticker),
        ("Company", d.get("company_name")),
        ("Sector", d.get("sector")),
        ("Industry", d.get("industry")),
        ("Currency", d.get("currency")),
        ("Current Price", d.get("current_price")),
        ("Market Cap", d.get("market_cap")),
        ("52W High", d.get("52w_high")),
        ("52W Low", d.get("52w_low")),
        ("EPS", d.get("eps")),
        ("P/E Ratio", d.get("pe_ratio")),
        ("Forward P/E", d.get("forward_pe")),
        ("P/B Ratio", d.get("pb_ratio")),
        ("ROE", d.get("roe")),
        ("ROA", d.get("roa")),
        ("Net Profit Margin", d.get("net_profit_margin")),
        ("Gross Margin", d.get("gross_margin")),
        ("Dividend Yield", d.get("dividend_yield")),
        ("Beta", d.get("beta")),
        ("Total Assets", d.get("total_assets")),
        ("Total Liabilities", d.get("total_liabilities")),
        ("Long Term Debt", d.get("long_term_debt")),
        ("Stockholders Equity", d.get("stockholders_equity")),
    ]
    df = pd.DataFrame(rows, columns=["Metric", "Value"])
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode()


# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Finlytics")
    st.markdown("<span style='color:#8b949e;font-size:13px'>Fundamental Analysis</span>", unsafe_allow_html=True)
    st.divider()

    ticker_input = st.text_input(
        "Stock Ticker",
        value="RELIANCE.NS",
        placeholder="e.g. AAPL, RELIANCE.NS",
        help="Use .NS suffix for NSE-listed Indian stocks (e.g. TCS.NS)",
    ).upper().strip()

    # Peer comparison
    peer_input = st.text_input(
        "Compare with peers (optional)",
        placeholder="e.g. TCS.NS, INFY.NS",
        help="Comma-separated tickers to compare fundamentals side by side",
    ).upper().strip()

    analyse_btn = st.button("Analyse", use_container_width=True)
    st.divider()
    st.markdown(
        "<span style='color:#8b949e;font-size:11px'>"
        "Data via Yahoo Finance · Cached 5 min<br>"
        "Scoring based on standard fundamental benchmarks.<br>"
        "<b>Not financial advice.</b></span>",
        unsafe_allow_html=True,
    )


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
next_earn_html = ""
if d.get("next_earnings"):
    try:
        ne = pd.Timestamp(d["next_earnings"]).strftime("%d %b %Y")
        next_earn_html = f'<span class="pill" style="background:rgba(63,185,80,0.12);color:#3fb950;border-color:rgba(63,185,80,0.3);">📅 Next Earnings: {ne}</span>'
    except Exception:
        pass

st.markdown(f"""
<div class="hero">
    <div class="hero-company">{d['company_name']}</div>
    <div class="hero-meta">
        <span class="pill">{ticker_input}</span>
        <span class="pill">{d['sector']}</span>
        <span class="pill">{d['industry']}</span>
        <span class="pill">{d['exchange']}</span>
        {next_earn_html}
    </div>
    <div class="hero-summary">{d['business_summary']}</div>
</div>
""", unsafe_allow_html=True)

# ── Verdict Card ─────────────────────────────────────────────────────────────────
signal, score_pct, reason_text, strengths, risks = compute_verdict(d)
sig_lower = signal.split("/")[0].strip().lower()

signal_emoji = {"buy": "✅", "hold": "⚠️", "sell": "🚫"}.get(sig_lower, "")
st.markdown(f"""
<div class="verdict-card {sig_lower}">
    <div class="verdict-label">Fundamental Verdict</div>
    <div class="verdict-signal {sig_lower}">{signal_emoji} {signal}</div>
    <div class="verdict-reason">{reason_text}</div>
    <div class="verdict-score">Health score: <b>{score_pct}/100</b> — based on ROE, ROA, Margins, P/E, P/B, and Debt levels.</div>
</div>
""", unsafe_allow_html=True)

# ── Price Range Bar ───────────────────────────────────────────────────────────────
price_range_bar(d["current_price"], d["52w_low"], d["52w_high"], currency)

# ── KPI Strip ─────────────────────────────────────────────────────────────────────
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

# ── Export Button ─────────────────────────────────────────────────────────────────
csv_bytes = build_export_csv(d, ticker_input)
st.download_button(
    label="⬇ Export Metrics as CSV",
    data=csv_bytes,
    file_name=f"{ticker_input}_fundamentals.csv",
    mime="text/csv",
)

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────────
tab_price, tab_fundamentals, tab_financials, tab_statements, tab_peers = st.tabs([
    "📈  Price History",
    "🔍  Fundamentals",
    "💰  Financials",
    "📄  Statements",
    "🆚  Peer Compare",
])

# ── Tab 1: Price History ─────────────────────────────────────────────────────────
with tab_price:
    st.markdown('<div class="section-title">1-Year Price History</div>', unsafe_allow_html=True)
    price_chart(d["history"])

    if d["history"] is not None and not d["history"].empty:
        h   = d["history"]["Close"]
        ch  = ((h.iloc[-1] - h.iloc[0]) / h.iloc[0]) * 100
        vol = d["history"]["Volume"].mean()
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("1Y Return", f"{ch:+.2f}%", "Change in close price over 12 months",
                        "good" if ch > 0 else "bad")
        with c2:
            metric_card("Avg Daily Volume", f"{vol:,.0f}", "Average shares traded per day")
        with c3:
            metric_card("52W Range",
                        f"{fmt_large(d['52w_low'], currency)} – {fmt_large(d['52w_high'], currency)}",
                        "Lowest to highest in past 52 weeks")


# ── Tab 2: Fundamentals ──────────────────────────────────────────────────────────
with tab_fundamentals:
    st.markdown('<div class="section-title">Valuation Ratios</div>', unsafe_allow_html=True)

    # Score summary bar
    score_class = "score-good" if score_pct >= 65 else ("score-warn" if score_pct >= 40 else "score-bad")
    st.markdown(
        f'<p style="color:var(--muted);font-size:13px;margin-bottom:16px;">'
        f'Cards are colour-coded: <span style="color:#3fb950">■ green = healthy</span> · '
        f'<span style="color:#d29922">■ amber = watch</span> · '
        f'<span style="color:#f85149">■ red = concern</span></p>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        scored_metric_card("EPS", f"{d['eps']:.2f}" if d["eps"] else "—", EXPLANATIONS["EPS"], "eps", d["eps"])
        scored_metric_card("P/E Ratio", fmt_ratio(d["pe_ratio"]), EXPLANATIONS["P/E Ratio"], "pe_ratio", d["pe_ratio"])
    with c2:
        scored_metric_card("Forward P/E", fmt_ratio(d["forward_pe"]), EXPLANATIONS["Forward P/E"], "pe_ratio", d["forward_pe"])
        scored_metric_card("P/B Ratio", fmt_ratio(d["pb_ratio"]), EXPLANATIONS["P/B Ratio"], "pb_ratio", d["pb_ratio"])
    with c3:
        scored_metric_card("Dividend Yield", fmt_pct(d["dividend_yield"]),
                           EXPLANATIONS["Dividend Yield"] if d["dividend_yield"] else "No dividend data — company may not pay dividends.",
                           "dividend_yield", d["dividend_yield"])
        scored_metric_card("Beta", f"{d['beta']:.2f}" if d["beta"] else "—", EXPLANATIONS["Beta"], "beta", d["beta"])

    st.markdown('<div class="section-title" style="margin-top:24px">Profitability</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        scored_metric_card("ROE", fmt_pct(d["roe"]), EXPLANATIONS["ROE"], "roe", d["roe"])
    with c2:
        scored_metric_card("ROA", fmt_pct(d["roa"]), EXPLANATIONS["ROA"], "roa", d["roa"])
    with c3:
        scored_metric_card("Net Profit Margin", fmt_pct(d["net_profit_margin"]),
                           EXPLANATIONS["Net Profit Margin"], "net_profit_margin", d["net_profit_margin"])
    with c4:
        scored_metric_card("Gross Margin", fmt_pct(d["gross_margin"]),
                           EXPLANATIONS["Gross Margin"], "gross_margin", d["gross_margin"])


# ── Tab 3: Financials ────────────────────────────────────────────────────────────
with tab_financials:
    st.markdown('<div class="section-title">Balance Sheet Overview</div>', unsafe_allow_html=True)
    balance_bar_chart(d)

    # Trend arrows for latest vs previous quarter
    bs = d["balance_sheet"]
    cf = d["cash_flow"]

    c1, c2, c3, c4 = st.columns(4)
    items = [
        ("Total Assets",        fmt_large(d["total_assets"], currency),       EXPLANATIONS["Total Assets"],       "total_assets",        "Total Assets"),
        ("Total Liabilities",   fmt_large(d["total_liabilities"], currency),  EXPLANATIONS["Total Liabilities"],  "total_liabilities",   "Total Liabilities Net Minority Interest"),
        ("Long Term Debt",      fmt_large(d["long_term_debt"], currency),     EXPLANATIONS["Long Term Debt"],     "long_term_debt",      "Long Term Debt"),
        ("Stockholders Equity", fmt_large(d["stockholders_equity"], currency),EXPLANATIONS["Stockholders Equity"],"stockholders_equity", "Stockholders Equity"),
    ]
    for col, (label, val, hint, _, bs_key) in zip([c1, c2, c3, c4], items):
        with col:
            arrow = trend_arrow(bs, bs_key)
            metric_card(label, val, f"{hint}<br>{arrow}" if arrow else hint)

    # Quarterly cash flow trend
    if cf is not None and not cf.empty:
        st.markdown('<div class="section-title" style="margin-top:24px">Cash Flow Snapshot</div>', unsafe_allow_html=True)
        row_keys = ["Operating Cash Flow", "Free Cash Flow", "Capital Expenditure"]
        cf_rows = {k: cf.loc[k] if k in cf.index else None for k in row_keys}
        cc1, cc2, cc3 = st.columns(3)
        for col, (key, row) in zip([cc1, cc2, cc3], cf_rows.items()):
            with col:
                val = None
                if row is not None and not row.empty:
                    v = row.iloc[0]
                    val = float(v) if pd.notna(v) else None
                arrow = trend_arrow(cf, key)
                metric_card(key, fmt_large(val, currency), arrow if arrow else "Latest quarter")

    if d["long_term_debt"] and d["stockholders_equity"] and d["stockholders_equity"] != 0:
        dte = d["long_term_debt"] / d["stockholders_equity"]
        st.markdown('<div class="section-title" style="margin-top:24px">Leverage</div>', unsafe_allow_html=True)
        _, dte_css = score_metric("pb_ratio", 1 / max(dte, 0.01))  # invert: lower D/E is better
        dte_css = "good" if dte < 0.5 else ("warn" if dte < 1.5 else "bad")
        metric_card("Debt-to-Equity Ratio", f"{dte:.2f}x",
                    "Long-term debt / stockholders' equity. Below 0.5x = conservative · 0.5–1.5x = moderate · Above 1.5x = high risk.",
                    dte_css)


# ── Tab 4: Statements ────────────────────────────────────────────────────────────
with tab_statements:
    st.markdown('<div class="section-title">Quarterly Financial Statements</div>', unsafe_allow_html=True)

    with st.expander("📋  Balance Sheet", expanded=True):
        if d["balance_sheet"] is not None and not d["balance_sheet"].empty:
            st.dataframe(d["balance_sheet"].style.format("{:,.0f}", na_rep="—"), use_container_width=True)
        else:
            st.info("Balance sheet not available for this ticker.")

    with st.expander("💵  Cash Flow Statement"):
        if d["cash_flow"] is not None and not d["cash_flow"].empty:
            st.dataframe(d["cash_flow"].style.format("{:,.0f}", na_rep="—"), use_container_width=True)
        else:
            st.info("Cash flow data not available for this ticker.")

    with st.expander("📊  Income Statement"):
        if d["income_stmt"] is not None and not d["income_stmt"].empty:
            st.dataframe(d["income_stmt"].style.format("{:,.0f}", na_rep="—"), use_container_width=True)
        else:
            st.info("Income statement not available for this ticker.")

    with st.expander("📅  Earnings Calendar"):
        cal = d["calendar"]
        if cal is not None:
            cal_df = pd.DataFrame([cal]) if isinstance(cal, dict) else pd.DataFrame(cal)
            st.dataframe(cal_df, use_container_width=True)
        else:
            st.info("Earnings calendar not available for this ticker.")


# ── Tab 5: Peer Comparison ───────────────────────────────────────────────────────
with tab_peers:
    st.markdown('<div class="section-title">Peer Comparison</div>', unsafe_allow_html=True)

    peers_raw = peer_input if peer_input else ""
    peer_tickers = [t.strip() for t in peers_raw.split(",") if t.strip() and t.strip() != ticker_input]

    if not peer_tickers:
        st.info("Enter peer tickers in the sidebar (e.g. TCS.NS, INFY.NS) to compare side by side.")
    else:
        all_tickers = [ticker_input] + peer_tickers[:3]
        peer_data = {ticker_input: d}
        for pt in peer_tickers[:3]:
            with st.spinner(f"Fetching {pt}…"):
                pd_ = fetch_company_data(pt)
            if pd_:
                peer_data[pt] = pd_

        metrics = [
            ("P/E Ratio",         lambda x: fmt_ratio(x.get("pe_ratio"))),
            ("Forward P/E",       lambda x: fmt_ratio(x.get("forward_pe"))),
            ("P/B Ratio",         lambda x: fmt_ratio(x.get("pb_ratio"))),
            ("ROE",               lambda x: fmt_pct(x.get("roe"))),
            ("ROA",               lambda x: fmt_pct(x.get("roa"))),
            ("Net Profit Margin", lambda x: fmt_pct(x.get("net_profit_margin"))),
            ("Gross Margin",      lambda x: fmt_pct(x.get("gross_margin"))),
            ("Dividend Yield",    lambda x: fmt_pct(x.get("dividend_yield"))),
            ("Beta",              lambda x: f"{x['beta']:.2f}" if x.get("beta") else "—"),
            ("Market Cap",        lambda x: fmt_large(x.get("market_cap"), x.get("currency", "USD"))),
        ]

        rows = []
        for label, fn in metrics:
            row = {"Metric": label}
            for tk in peer_data:
                row[tk] = fn(peer_data[tk])
            rows.append(row)

        compare_df = pd.DataFrame(rows).set_index("Metric")
        st.dataframe(compare_df, use_container_width=True)
