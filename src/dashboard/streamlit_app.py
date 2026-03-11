"""
streamlit_app.py  ── FinSight AI Personal Finance Analyzer
───────────────────────────────────────────────────────────
Premium redesign: Deep-space luxury theme with
glassmorphism cards, animated gradient mesh background,
neon accents, and editorial Syne typography.

Run: streamlit run src/dashboard/streamlit_app.py
"""

import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinSight AI • Personal Finance",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PREMIUM THEME ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-void:     #05060f;
  --bg-deep:     #080b18;
  --bg-card:     rgba(15,20,45,0.78);
  --border:      rgba(120,100,255,0.18);
  --border-glow: rgba(120,100,255,0.42);
  --neon-v:      #9B7FFF;
  --neon-c:      #00E5CC;
  --neon-p:      #FF4FA3;
  --neon-a:      #FFB347;
  --neon-g:      #39FF94;
  --txt:         #F0EFFF;
  --txt-m:       rgba(200,195,255,0.55);
  --txt-d:       rgba(160,155,220,0.38);
  --f-display:   'Syne', sans-serif;
  --f-body:      'DM Sans', sans-serif;
  --f-mono:      'JetBrains Mono', monospace;
  --r-lg: 18px; --r-md: 12px; --r-sm: 8px;
  --shadow: 0 8px 32px rgba(0,0,0,0.55), 0 1px 0 rgba(255,255,255,0.04) inset;
  --glow:   0 0 40px rgba(155,127,255,0.13);
}

html,body,[class*="css"]{font-family:var(--f-body)!important;color:var(--txt)!important}

/* ── Animated gradient background ── */
.stApp{
  background:var(--bg-void)!important;
  background-image:
    radial-gradient(ellipse 90% 60% at 5%  0%,  rgba(91,63,255,.20) 0%,transparent 55%),
    radial-gradient(ellipse 65% 50% at 95% 8%,  rgba(0,229,204,.09) 0%,transparent 50%),
    radial-gradient(ellipse 55% 65% at 50% 100%,rgba(255,79,163,.08) 0%,transparent 55%)!important;
  background-attachment:fixed!important;
}

/* ── Streamlit chrome ── */
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:1.8rem 2.5rem 3rem!important;max-width:1640px!important}

/* ── Hide collapse arrow & keyboard icon ── */
[data-testid="collapsedControl"]{display:none!important}
button[kind="header"]{display:none!important}
.st-emotion-cache-czk5ss{display:none!important}
[data-testid="stSidebarCollapseButton"]{display:none!important}
svg[data-testid="stIconMaterial"]{display:none!important}

/* ── Sidebar toggle button ── */
.sidebar-toggle-btn {
  position:fixed;
  top:14px;
  left:14px;
  z-index:99999;
  width:38px;height:38px;
  background:linear-gradient(135deg,rgba(155,127,255,.25),rgba(0,229,204,.15));
  border:1px solid rgba(155,127,255,.45);
  border-radius:10px;
  cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  font-size:1.1rem;
  backdrop-filter:blur(12px);
  transition:all .2s ease;
  box-shadow:0 4px 16px rgba(0,0,0,.4);
}
.sidebar-toggle-btn:hover{
  background:linear-gradient(135deg,rgba(155,127,255,.45),rgba(0,229,204,.25));
  box-shadow:0 0 20px rgba(155,127,255,.35);
  transform:scale(1.08);
}

/* ── Sidebar ── */
[data-testid="stSidebar"]{
  background:linear-gradient(175deg,rgba(10,8,32,.97) 0%,rgba(6,4,20,.98) 100%)!important;
  border-right:1px solid var(--border)!important;
  transition: all 0.3s ease !important;
}
[data-testid="stSidebar"]>div:first-child{padding:1rem!important}
[data-testid="stSidebar"] *{font-family:var(--f-body)!important}
[data-testid="stSidebar"] label{color:var(--txt-m)!important;font-size:.76rem!important;letter-spacing:.07em;text-transform:uppercase}
[data-testid="stSidebar"] .stNumberInput input{
  background:rgba(155,127,255,.07)!important;border:1px solid var(--border)!important;
  border-radius:var(--r-sm)!important;color:var(--txt)!important;
  font-family:var(--f-mono)!important;font-size:.83rem!important
}

/* ── Metrics ── */
[data-testid="stMetric"]{
  background:var(--bg-card)!important;border:1px solid var(--border)!important;
  border-radius:var(--r-lg)!important;padding:1.15rem 1.35rem!important;
  backdrop-filter:blur(20px)!important;box-shadow:var(--shadow)!important;
  transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease!important
}
[data-testid="stMetric"]:hover{
  transform:translateY(-3px)!important;
  box-shadow:var(--glow),var(--shadow)!important;
  border-color:var(--border-glow)!important
}
[data-testid="stMetric"] label{color:var(--txt-m)!important;font-size:.7rem!important;font-weight:500!important;letter-spacing:.1em!important;text-transform:uppercase!important}
[data-testid="stMetricValue"]{color:var(--txt)!important;font-family:var(--f-display)!important;font-size:1.6rem!important;font-weight:700!important;letter-spacing:-.02em!important}

/* ── Selectboxes ── */
.stSelectbox>div>div{
  background:rgba(155,127,255,.06)!important;border:1px solid var(--border)!important;
  border-radius:var(--r-md)!important;color:var(--txt)!important;font-size:.87rem!important
}

/* ── Tabs ── */
[data-baseweb="tab-list"]{background:transparent!important;gap:3px!important;border-bottom:1px solid var(--border)!important}
[data-baseweb="tab"]{
  background:transparent!important;border:none!important;color:var(--txt-m)!important;
  font-family:var(--f-body)!important;font-size:.84rem!important;font-weight:500!important;
  letter-spacing:.025em!important;padding:.6rem 1.1rem!important;
  border-radius:var(--r-sm) var(--r-sm) 0 0!important;transition:all .2s ease!important
}
[data-baseweb="tab"]:hover{color:var(--txt)!important;background:rgba(155,127,255,.08)!important}
[aria-selected="true"][data-baseweb="tab"]{color:var(--neon-v)!important;background:rgba(155,127,255,.12)!important;border-bottom:2px solid var(--neon-v)!important}

/* ── Headings ── */
h1,h2,h3{font-family:var(--f-display)!important;letter-spacing:-.03em!important}
h1{font-size:2.3rem!important;font-weight:800!important;color:var(--txt)!important}
h2{font-size:1.45rem!important;font-weight:700!important;color:var(--txt)!important}
h3{font-size:1.05rem!important;font-weight:600!important;color:var(--txt-m)!important}
hr{border-color:var(--border)!important;margin:1.1rem 0!important}

/* ── File uploader ── */
[data-testid="stFileUploader"]{background:rgba(155,127,255,.05)!important;border:1px dashed var(--border-glow)!important;border-radius:var(--r-md)!important;padding:.9rem!important}
[data-testid="stFileUploader"]:hover{border-color:var(--neon-v)!important}

/* ── Buttons ── */
.stButton>button{
  background:linear-gradient(135deg,rgba(155,127,255,.2),rgba(0,229,204,.1))!important;
  border:1px solid var(--border-glow)!important;border-radius:var(--r-md)!important;
  color:var(--txt)!important;font-family:var(--f-body)!important;font-size:.87rem!important;
  font-weight:500!important;padding:.58rem 1.3rem!important;
  transition:all .25s ease!important;letter-spacing:.03em!important
}
.stButton>button:hover{
  background:linear-gradient(135deg,rgba(155,127,255,.38),rgba(0,229,204,.2))!important;
  border-color:var(--neon-v)!important;box-shadow:0 0 20px rgba(155,127,255,.3)!important;
  transform:translateY(-1px)!important
}
.stDownloadButton>button{
  background:linear-gradient(135deg,var(--neon-v),#6B4FE8)!important;border:none!important;
  border-radius:var(--r-md)!important;color:#fff!important;font-weight:600!important;
  box-shadow:0 4px 20px rgba(155,127,255,.4)!important
}
.stDownloadButton>button:hover{box-shadow:0 8px 30px rgba(155,127,255,.6)!important;transform:translateY(-2px)!important}

/* ── DataFrames ── */
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:var(--r-md)!important;overflow:hidden!important}

/* ── Expander ── */
[data-testid="stExpander"]{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:var(--r-md)!important;backdrop-filter:blur(12px)!important}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg-deep)}
::-webkit-scrollbar-thumb{background:rgba(155,127,255,.3);border-radius:3px}

/* ─────────── CUSTOM COMPONENTS ─────────── */

.finsight-hero{display:flex;align-items:center;justify-content:space-between;padding:1.8rem 0 1.4rem;margin-bottom:.3rem}
.finsight-logo{display:flex;align-items:center;gap:14px}
.logo-mark{width:50px;height:50px;background:linear-gradient(135deg,var(--neon-v),var(--neon-c));border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:1.55rem;box-shadow:0 0 30px rgba(155,127,255,.42);flex-shrink:0}
.logo-text{font-family:var(--f-display);font-weight:800;font-size:1.65rem;letter-spacing:-.04em;background:linear-gradient(135deg,#fff 35%,var(--neon-v));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo-sub{font-size:.7rem;color:var(--txt-d);letter-spacing:.18em;text-transform:uppercase;margin-top:-2px;font-family:var(--f-body)}
.live-badge{background:linear-gradient(135deg,rgba(155,127,255,.15),rgba(0,229,204,.08));border:1px solid var(--border-glow);border-radius:30px;padding:7px 18px;font-size:.73rem;color:var(--neon-c);letter-spacing:.1em;font-family:var(--f-mono);font-weight:500;display:flex;align-items:center;gap:7px}
.live-dot{width:7px;height:7px;border-radius:50%;background:var(--neon-c);box-shadow:0 0 8px var(--neon-c)}

.eyebrow{font-family:var(--f-mono);font-size:.68rem;color:var(--neon-v);letter-spacing:.2em;text-transform:uppercase;margin-bottom:.75rem;display:flex;align-items:center;gap:8px}
.eyebrow::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,var(--border-glow),transparent)}

.sidebar-top{text-align:center;padding:1.8rem 1rem 1.4rem;border-bottom:1px solid var(--border);margin:-0px 0 1.4rem}
.sb-mark{width:52px;height:52px;background:linear-gradient(135deg,var(--neon-v),var(--neon-c));border-radius:16px;display:inline-flex;align-items:center;justify-content:center;font-size:1.6rem;box-shadow:0 0 22px rgba(155,127,255,.45);margin-bottom:10px}
.sb-name{font-family:var(--f-display);font-size:1.2rem;font-weight:800;background:linear-gradient(135deg,#fff,var(--neon-v));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sb-tag{font-size:.67rem;color:var(--txt-d);letter-spacing:.12em;text-transform:uppercase}
.sb-sec{font-family:var(--f-mono);font-size:.63rem;color:var(--txt-d);letter-spacing:.2em;text-transform:uppercase;padding:1rem 0 .4rem;border-top:1px solid var(--border);margin-top:.4rem}

.stats-bar{display:flex;gap:20px;align-items:center;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-md);padding:9px 18px;margin-bottom:1.4rem;backdrop-filter:blur(12px);flex-wrap:wrap}
.stat-it{display:flex;flex-direction:column}
.stat-v{font-family:var(--f-mono);font-size:.82rem;color:var(--neon-c);font-weight:500}
.stat-l{font-size:.62rem;color:var(--txt-d);letter-spacing:.1em;text-transform:uppercase}
.stat-sep{width:1px;height:24px;background:var(--border);flex-shrink:0}

.insight-card{background:var(--bg-card);border:1px solid var(--border);border-left:3px solid var(--neon-v);border-radius:var(--r-md);padding:13px 17px;margin:9px 0;color:var(--txt);font-size:.89rem;line-height:1.62;backdrop-filter:blur(16px);transition:transform .2s ease,border-left-color .2s ease}
.insight-card:hover{transform:translateX(4px);border-left-color:var(--neon-c)}
.alert-card{background:rgba(255,60,80,.07);border:1px solid rgba(255,60,80,.25);border-left:3px solid #FF3C50;border-radius:var(--r-md);padding:13px 17px;margin:9px 0;color:#FFB3BC;font-size:.87rem;line-height:1.62;backdrop-filter:blur(16px)}
.success-card{background:rgba(57,255,148,.05);border:1px solid rgba(57,255,148,.2);border-left:3px solid var(--neon-g);border-radius:var(--r-md);padding:14px 17px;color:#B3FFD8;font-size:.9rem;line-height:1.6}

.cluster-badge{display:inline-flex;align-items:center;gap:9px;background:linear-gradient(135deg,rgba(155,127,255,.15),rgba(0,229,204,.08));border:1px solid var(--border-glow);border-radius:24px;padding:9px 22px;font-size:.94rem;color:var(--txt);font-weight:500;margin-bottom:1.4rem}

.report-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);padding:26px 24px;margin-bottom:12px;backdrop-filter:blur(16px)}
.report-icon{font-size:2.4rem;margin-bottom:11px}
.report-title{font-family:var(--f-display);font-size:1.05rem;font-weight:700;margin-bottom:5px}
.report-desc{color:var(--txt-m);font-size:.83rem;line-height:1.6}

.welcome-wrap{min-height:68vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:3.5rem 2rem}
.w-title{font-family:var(--f-display);font-size:clamp(2.4rem,5vw,3.8rem);font-weight:800;letter-spacing:-.04em;background:linear-gradient(135deg,#fff 0%,var(--neon-v) 50%,var(--neon-c) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1;margin-bottom:1rem}
.w-sub{font-size:1.05rem;color:var(--txt-m);max-width:530px;line-height:1.72;margin-bottom:2.8rem}
.feat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;max-width:840px;width:100%;margin:0 auto}
.feat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);padding:22px 14px;backdrop-filter:blur(20px);transition:transform .25s ease,box-shadow .25s ease,border-color .25s ease}
.feat-card:hover{transform:translateY(-6px);box-shadow:0 20px 40px rgba(0,0,0,.5),0 0 28px rgba(155,127,255,.12);border-color:var(--border-glow)}
.feat-icon{font-size:1.9rem;margin-bottom:9px}
.feat-t{font-family:var(--f-display);font-size:.88rem;font-weight:700;color:var(--txt);margin-bottom:3px}
.feat-d{font-size:.73rem;color:var(--txt-m);line-height:1.5}
</style>
""", unsafe_allow_html=True)


# ─── Chart global theme ───────────────────────────────────────────────────────
PALETTE = ["#9B7FFF","#00E5CC","#FF4FA3","#FFB347","#39FF94",
           "#7B9CFF","#FF7B9C","#B3FF9B","#FFE57B","#9BFFF5"]

CT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#C8C3FF", size=12),
    title_font=dict(family="Syne, sans-serif", size=16, color="#F0EFFF"),
    title_x=0.02,
    margin=dict(l=16, r=16, t=52, b=16),
    colorway=PALETTE,
    xaxis=dict(gridcolor="rgba(120,100,255,.08)", linecolor="rgba(120,100,255,.15)", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="rgba(120,100,255,.08)", linecolor="rgba(120,100,255,.15)", tickfont=dict(size=11)),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(120,100,255,.18)", borderwidth=1),
    hoverlabel=dict(bgcolor="rgba(10,8,38,.95)", bordercolor="rgba(155,127,255,.4)",
                    font=dict(family="DM Sans", color="#F0EFFF")),
)

def T(fig):
    fig.update_layout(**CT)
    return fig


# ─── Data loaders ─────────────────────────────────────────────────────────────
@st.cache_data
def load_and_process(file, filename):
    from src.data_processing.file_converter import load_file
    from src.data_processing.data_cleaning import DataCleaner
    raw = load_file(file, filename=filename)
    c = DataCleaner()
    return c.clean(raw), c.cleaning_report

@st.cache_data
def load_sample():
    from src.data_processing.data_cleaning import DataCleaner
    # Try multiple possible paths for the sample CSV
    possible_paths = [
        Path(ROOT) / "data" / "sample_transactions.csv",
        Path(__file__).parent.parent.parent / "data" / "sample_transactions.csv",
        Path("data") / "sample_transactions.csv",
        Path("sample_transactions.csv"),
    ]
    raw = None
    for p in possible_paths:
        if p.exists():
            raw = pd.read_csv(p)
            break
    if raw is None:
        # Inline fallback sample data so button ALWAYS works
        raw = pd.DataFrame({
            "Date":["2025-01-03","2025-01-04","2025-01-05","2025-01-06","2025-01-07",
                    "2025-01-08","2025-01-09","2025-01-10","2025-01-11","2025-01-12",
                    "2025-01-13","2025-01-14","2025-01-15","2025-01-16","2025-01-17",
                    "2025-02-01","2025-02-02","2025-02-03","2025-02-04","2025-02-05",
                    "2025-02-06","2025-02-07","2025-02-08","2025-02-09","2025-02-10",
                    "2025-03-01","2025-03-02","2025-03-03","2025-03-04","2025-03-05",
                    "2025-03-06","2025-03-07","2025-03-08","2025-03-09","2025-03-10"],
            "Description":["Swiggy Order","Uber Ride","Amazon Purchase","Netflix Subscription",
                           "Electricity Bill","Zomato Order","Salary Credit","Ola Cab",
                           "Flipkart Shopping","Grocery Store","Medical Pharmacy","Swiggy Order",
                           "Petrol Station","Amazon Purchase","Water Bill",
                           "Swiggy Order","Ola Cab","Flipkart Shopping","Netflix Subscription",
                           "Electricity Bill","Salary Credit","Restaurant Lunch","Amazon Purchase",
                           "Medical Doctor","Zomato Order",
                           "Swiggy Order","Uber Ride","Amazon Purchase","Netflix Subscription",
                           "Electricity Bill","Salary Credit","Grocery Store","Zomato Order",
                           "Medical Pharmacy","Petrol Station"],
            "Category":["Food","Transport","Shopping","Entertainment","Utilities","Food","Income",
                        "Transport","Shopping","Groceries","Healthcare","Food","Transport",
                        "Shopping","Utilities","Food","Transport","Shopping","Entertainment",
                        "Utilities","Income","Food","Shopping","Healthcare","Food",
                        "Food","Transport","Shopping","Entertainment","Utilities","Income",
                        "Groceries","Food","Healthcare","Transport"],
            "Amount":[350,220,1200,649,1800,480,75000,350,2500,1200,650,290,800,3200,400,
                      310,420,4500,649,1950,75000,650,2100,800,490,
                      290,210,980,649,1750,75000,1150,450,320,750],
            "Transaction_Type":["Debit","Debit","Debit","Debit","Debit","Debit","Credit",
                                 "Debit","Debit","Debit","Debit","Debit","Debit","Debit","Debit",
                                 "Debit","Debit","Debit","Debit","Debit","Credit","Debit","Debit",
                                 "Debit","Debit","Debit","Debit","Debit","Debit","Debit","Credit",
                                 "Debit","Debit","Debit","Debit"],
            "Merchant":["Swiggy","Uber","Amazon","Netflix","Tata Power","Zomato","Employer",
                        "Ola","Flipkart","DMart","Apollo Pharmacy","Swiggy","Indian Oil",
                        "Amazon","Municipal Corp","Swiggy","Ola","Flipkart","Netflix",
                        "Tata Power","Employer","Mainland China","Amazon","City Hospital",
                        "Zomato","Swiggy","Uber","Amazon","Netflix","Tata Power","Employer",
                        "DMart","Zomato","Apollo Pharmacy","Indian Oil"],
            "Payment_Method":["UPI","UPI","Credit Card","Credit Card","Net Banking","UPI",
                               "Bank Transfer","UPI","Debit Card","Cash","UPI","UPI",
                               "Debit Card","Credit Card","Net Banking","UPI","UPI",
                               "Credit Card","Credit Card","Net Banking","Bank Transfer",
                               "Credit Card","Credit Card","Cash","UPI","UPI","UPI",
                               "Credit Card","Credit Card","Net Banking","Bank Transfer",
                               "Cash","UPI","UPI","Debit Card"],
        })
    c = DataCleaner()
    return c.clean(raw), c.cleaning_report


# ─── Session state init ───────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state["df"] = None
if "cleaning_report" not in st.session_state:
    st.session_state["cleaning_report"] = {}
if "data_loaded" not in st.session_state:
    st.session_state["data_loaded"] = False
if "sidebar_open" not in st.session_state:
    st.session_state["sidebar_open"] = True

# ─── Sidebar toggle button (fixed top-left) ───────────────────────────────────
toggle_icon = "✕" if st.session_state["sidebar_open"] else "☰"
toggle_label = "Close Sidebar" if st.session_state["sidebar_open"] else "Open Sidebar"

st.markdown(f"""
<div class="sidebar-toggle-btn" title="{toggle_label}" onclick="
  var sidebar = window.parent.document.querySelector('[data-testid=stSidebar]');
  var btn = window.parent.document.querySelector('[data-testid=stSidebarCollapseButton] button');
  if(btn) btn.click();
" id="sidebarToggle">{toggle_icon}</div>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-top">
      <div class="sb-mark">◈</div>
      <div class="sb-name">FinSight AI</div>
      <div class="sb-tag">Personal Finance Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">📂 Data Source</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload bank statement", type=["csv","xlsx","xls","pdf","txt"],
                                 label_visibility="collapsed")

    if st.button("✦ Load Sample Dataset", use_container_width=True):
        with st.spinner("⚡ Loading sample data…"):
            _df, _cr = load_sample()
            st.session_state["df"] = _df
            st.session_state["cleaning_report"] = _cr
            st.session_state["data_loaded"] = True
        st.rerun()

    if st.session_state["data_loaded"]:
        st.success(f"✓ {len(st.session_state['df']):,} transactions loaded")

    st.markdown('<div class="sb-sec">💵 Monthly Budgets (₹)</div>', unsafe_allow_html=True)
    budgets = {
        "Food":          st.number_input("Food",          value=5000,  step=500),
        "Transport":     st.number_input("Transport",     value=2000,  step=500),
        "Shopping":      st.number_input("Shopping",      value=3000,  step=500),
        "Entertainment": st.number_input("Entertainment", value=1500,  step=500),
        "Utilities":     st.number_input("Utilities",     value=3000,  step=500),
        "Groceries":     st.number_input("Groceries",     value=4000,  step=500),
        "Healthcare":    st.number_input("Healthcare",    value=2000,  step=500),
    }
    st.markdown("---")
    st.markdown('<div style="font-size:.65rem;color:rgba(155,127,255,.3);text-align:center;font-family:JetBrains Mono">FinSight AI v2.0 · Python</div>', unsafe_allow_html=True)


# ─── Load data ────────────────────────────────────────────────────────────────
if uploaded is not None:
    with st.spinner("⚡ Processing your file…"):
        _df, _cr = load_and_process(uploaded, uploaded.name)
        st.session_state["df"] = _df
        st.session_state["cleaning_report"] = _cr
        st.session_state["data_loaded"] = True

df             = st.session_state["df"]
cleaning_report = st.session_state["cleaning_report"]


# ─── Welcome screen ───────────────────────────────────────────────────────────
if df is None:
    st.markdown("""
    <div class="welcome-wrap">
      <div class="w-title">Know Where<br>Your Money Goes</div>
      <p class="w-sub">AI-powered financial intelligence. Upload your bank statement to unlock
      interactive analytics, ML predictions, anomaly detection and executive reports.</p>
      <div class="feat-grid">
        <div class="feat-card"><div class="feat-icon">📊</div>
          <div class="feat-t">Smart Analytics</div>
          <div class="feat-d">Category breakdowns, trends &amp; heatmaps</div></div>
        <div class="feat-card"><div class="feat-icon">🤖</div>
          <div class="feat-t">ML Predictions</div>
          <div class="feat-d">LR + Random Forest spending forecasts</div></div>
        <div class="feat-card"><div class="feat-icon">🚨</div>
          <div class="feat-t">Anomaly Alerts</div>
          <div class="feat-d">Z-Score &amp; Isolation Forest detection</div></div>
        <div class="feat-card"><div class="feat-icon">📄</div>
          <div class="feat-t">PDF Reports</div>
          <div class="feat-d">Professional multi-page exports</div></div>
      </div>
      <p style="margin-top:2.4rem;font-size:.76rem;color:rgba(155,127,255,.35);font-family:'JetBrains Mono'">
        ← Upload a file or load sample data from the sidebar</p>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="finsight-hero">
  <div class="finsight-logo">
    <div class="logo-mark">◈</div>
    <div><div class="logo-text">FinSight AI</div>
         <div class="logo-sub">Personal Finance Analyzer</div></div>
  </div>
  <div class="live-badge"><span class="live-dot"></span>Live Dashboard</div>
</div>""", unsafe_allow_html=True)


# ─── Filters ──────────────────────────────────────────────────────────────────
st.markdown('<div class="eyebrow">Filters</div>', unsafe_allow_html=True)
fc1, fc2, fc3, fc4 = st.columns(4)
all_years  = sorted(df["Year"].unique())
month_map  = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
              7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
all_months = sorted(df["Month"].unique())

with fc1: sy  = st.selectbox("Year",             ["All"]+[str(y) for y in all_years])
with fc2: sm  = st.selectbox("Month",            ["All"]+[month_map[m] for m in all_months])
with fc3: sc  = st.selectbox("Category",         ["All"]+sorted(df["Category"].unique().tolist()))
with fc4: stt = st.selectbox("Transaction Type", ["All","Debit","Credit"])

fdf = df.copy()
if sy  != "All": fdf = fdf[fdf["Year"]==int(sy)]
if sm  != "All": fdf = fdf[fdf["Month"]=={v:k for k,v in month_map.items()}[sm]]
if sc  != "All": fdf = fdf[fdf["Category"]==sc]
if stt != "All": fdf = fdf[fdf["Transaction_Type"]==stt]

if fdf.empty:
    st.warning("No transactions match the selected filters."); st.stop()


# ─── Stats bar ────────────────────────────────────────────────────────────────
from src.analytics.expense_analysis import (
    total_spending, total_income, average_daily_spending,
    transaction_count, highest_spending_category, average_transaction_value
)
ds = fdf["Date"].min().strftime("%d %b %Y")
de = fdf["Date"].max().strftime("%d %b %Y")

st.markdown(f"""
<div class="stats-bar">
  <div class="stat-it"><div class="stat-v">{ds} → {de}</div><div class="stat-l">Date Range</div></div>
  <div class="stat-sep"></div>
  <div class="stat-it"><div class="stat-v">{transaction_count(fdf):,}</div><div class="stat-l">Transactions</div></div>
  <div class="stat-sep"></div>
  <div class="stat-it"><div class="stat-v">{len(fdf["Category"].unique())}</div><div class="stat-l">Categories</div></div>
  <div class="stat-sep"></div>
  <div class="stat-it"><div class="stat-v">{len(fdf["Merchant"].unique())}</div><div class="stat-l">Merchants</div></div>
  <div class="stat-sep"></div>
  <div class="stat-it"><div class="stat-v">{cleaning_report.get("removed_rows",0)}</div><div class="stat-l">Rows Cleaned</div></div>
</div>""", unsafe_allow_html=True)


# ─── KPI row ──────────────────────────────────────────────────────────────────
st.markdown('<div class="eyebrow">Key Metrics</div>', unsafe_allow_html=True)
k1,k2,k3,k4,k5,k6 = st.columns(6)
tex = total_spending(fdf); tin = total_income(fdf)
sav = tin - tex; adl = average_daily_spending(fdf)
tct = transaction_count(fdf); atx = average_transaction_value(fdf)
with k1: st.metric("Total Spending",  f"₹{tex:,.0f}")
with k2: st.metric("Total Income",    f"₹{tin:,.0f}")
with k3: st.metric("Net Savings",     f"₹{sav:,.0f}", delta=f"{sav/tin*100:.1f}% rate" if tin>0 else None)
with k4: st.metric("Avg Daily Spend", f"₹{adl:,.0f}")
with k5: st.metric("Top Category",    highest_spending_category(fdf))
with k6: st.metric("Avg Transaction", f"₹{atx:,.0f}")
st.markdown("<br>", unsafe_allow_html=True)


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tabs = st.tabs(["  Overview  ","  Categories  ","  Monthly Trends  ",
                "  Insights  ","  ML & Predictions  ",
                "  Anomaly Detection  ","  Reports  "])


# ════════════════ TAB 1 — OVERVIEW ═══════════════════════════════════════════
with tabs[0]:
    import plotly.graph_objects as go
    import plotly.express as px
    from src.analytics.expense_analysis import (
        category_spending, daily_spending, top_merchants, day_of_week_spending
    )

    c1, c2 = st.columns([1, 1.45])
    with c1:
        cats = category_spending(fdf)
        fig = go.Figure(go.Pie(
            labels=cats["Category"], values=cats["Total"], hole=0.55,
            textposition="outside", textinfo="label+percent",
            textfont=dict(size=10, family="DM Sans"),
            marker=dict(colors=PALETTE, line=dict(color="rgba(0,0,0,.3)", width=2)),
        ))
        fig.update_layout(
            title="Spending Distribution",
            annotations=[dict(text=f"₹{cats['Total'].sum():,.0f}",
                               x=0.5,y=0.5,showarrow=False,
                               font=dict(size=16,family="Syne",color="#F0EFFF"))],
            showlegend=False,
        )
        T(fig); st.plotly_chart(fig, use_container_width=True)

    with c2:
        daily = daily_spending(fdf)
        daily["Rol7"] = daily["Daily_Total"].rolling(7, min_periods=1).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Daily_Total"], fill="tozeroy", name="Daily",
            line=dict(color="rgba(155,127,255,.55)", width=1.5),
            fillcolor="rgba(155,127,255,.06)",
        ))
        fig.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Rol7"], name="7-Day Avg",
            line=dict(color="#00E5CC", width=2.5),
        ))
        fig.update_layout(title="Daily Spending Trend",
                          legend=dict(orientation="h", y=1.1))
        T(fig); st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        mer = top_merchants(fdf, n=8)
        fig = px.bar(mer, x="Total_Spent", y="Merchant", orientation="h",
                     text=mer["Total_Spent"].apply(lambda x: f"₹{x:,.0f}"),
                     color="Total_Spent",
                     color_continuous_scale=[[0,"#2A1A5E"],[.5,"#9B7FFF"],[1,"#00E5CC"]])
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(title="Top Merchants", showlegend=False,
                          yaxis=dict(categoryorder="total ascending"),
                          coloraxis_showscale=False)
        T(fig); st.plotly_chart(fig, use_container_width=True)

    with c4:
        dow = day_of_week_spending(fdf).dropna()
        order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = dow.set_index("Day_of_Week").reindex(order).reset_index().dropna()
        clrs = ["#FF4FA3" if d in ["Saturday","Sunday"] else "#9B7FFF" for d in dow["Day_of_Week"]]
        fig = go.Figure(go.Bar(
            x=dow["Day_of_Week"], y=dow["Average"],
            marker_color=clrs, marker_line_width=0,
            text=dow["Average"].apply(lambda x: f"₹{x:,.0f}"),
            textposition="outside",
        ))
        fig.update_layout(title="Avg Spend by Day of Week")
        T(fig); st.plotly_chart(fig, use_container_width=True)


# ════════════════ TAB 2 — CATEGORIES ══════════════════════════════════════════
with tabs[1]:
    import plotly.graph_objects as go
    import plotly.express as px
    from src.analytics.expense_analysis import (
        category_spending, spending_heatmap_data, payment_method_distribution
    )
    cats = category_spending(fdf)

    cc1, cc2 = st.columns([1.6, 1])
    with cc1:
        fig = px.bar(cats, x="Category", y="Total",
                     color="Percentage",
                     color_continuous_scale=[[0,"#2A1A5E"],[.5,"#9B7FFF"],[1,"#00E5CC"]],
                     text=cats["Total"].apply(lambda x: f"₹{x:,.0f}"))
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(title="Category-wise Spending", coloraxis_showscale=False, showlegend=False)
        T(fig); st.plotly_chart(fig, use_container_width=True)

    with cc2:
        pm = payment_method_distribution(fdf)
        fig = px.pie(pm, names="Payment_Method", values="Total", hole=0.5, title="Payment Methods")
        fig.update_traces(textinfo="label+percent", textposition="outside",
                          marker=dict(colors=PALETTE, line=dict(color="rgba(0,0,0,.3)", width=2)))
        fig.update_layout(showlegend=False)
        T(fig); st.plotly_chart(fig, use_container_width=True)

    pivot = spending_heatmap_data(fdf)
    if not pivot.empty:
        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"W{c}" for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0,"#0A0820"],[.3,"#2A1A6E"],[.6,"#9B7FFF"],[1,"#00E5CC"]],
            colorbar=dict(title="₹ Spent", tickfont=dict(color="#C8C3FF"), titlefont=dict(color="#C8C3FF")),
        ))
        fig.update_layout(title="Spending Intensity Heatmap  (Day × Week)")
        T(fig); st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="eyebrow">Category Details</div>', unsafe_allow_html=True)
    st.dataframe(cats.style.format({"Total":"₹{:,.0f}","Percentage":"{:.1f}%","Avg_Transaction":"₹{:,.0f}"}),
                 use_container_width=True, height=280)

    st.markdown('<div class="eyebrow">Edit Categories</div>', unsafe_allow_html=True)
    eddf = fdf[["Date","Description","Amount","Category","Merchant"]].copy()
    eddf["Date"] = eddf["Date"].dt.strftime("%Y-%m-%d")
    st.data_editor(eddf, num_rows="dynamic",
                   column_config={"Category": st.column_config.SelectboxColumn(
                       "Category", options=sorted(df["Category"].unique().tolist()), required=True)},
                   use_container_width=True, height=260)


# ════════════════ TAB 3 — MONTHLY TRENDS ══════════════════════════════════════
with tabs[2]:
    import plotly.graph_objects as go
    from src.analytics.expense_analysis import monthly_spending, monthly_category_spending, budget_vs_actual
    from src.visualization.charts import budget_gauge_chart

    monthly = monthly_spending(fdf)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["YearMonth"], y=monthly["Total_Spending"],
        marker=dict(color=monthly["Total_Spending"],
                    colorscale=[[0,"#2A1A6E"],[.5,"#9B7FFF"],[1,"#00E5CC"]], line=dict(width=0)),
        text=monthly["Total_Spending"].apply(lambda x:f"₹{x:,.0f}"), textposition="outside",
        name="Spending",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["YearMonth"], y=monthly["Total_Spending"],
        mode="lines+markers", name="Trend",
        line=dict(color="#FF4FA3", width=2, dash="dot"),
        marker=dict(size=8, color="#FF4FA3"),
    ))
    fig.update_layout(title="Monthly Spending Overview", showlegend=True,
                      legend=dict(orientation="h", y=1.12))
    T(fig); st.plotly_chart(fig, use_container_width=True)

    pivot = monthly_category_spending(fdf)
    cat_cols = [c for c in pivot.columns if c != "YearMonth"]
    fig = go.Figure()
    for i,cat in enumerate(cat_cols):
        fig.add_trace(go.Bar(name=cat, x=pivot["YearMonth"], y=pivot[cat],
                             marker_color=PALETTE[i%len(PALETTE)], marker_line_width=0))
    fig.update_layout(barmode="stack", title="Monthly Category Breakdown",
                      legend=dict(orientation="h", y=-0.28))
    T(fig); st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="eyebrow">Budget vs Actual</div>', unsafe_allow_html=True)
    yrs = fdf["Year"].unique(); mths = fdf["Month"].unique()
    if len(yrs) and len(mths):
        bdf = budget_vs_actual(fdf, budgets, int(yrs[-1]), int(mths[-1]))
        if not bdf.empty:
            gcols = st.columns(min(4, len(bdf)))
            for i,(_, row) in enumerate(bdf.iterrows()):
                with gcols[i%4]:
                    fig = budget_gauge_chart(row["Category"], row["Actual"], row["Budget"])
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#C8C3FF")
                    st.plotly_chart(fig, use_container_width=True)
            st.dataframe(bdf.style.format({"Budget":"₹{:,.0f}","Actual":"₹{:,.0f}",
                                            "Remaining":"₹{:,.0f}","Used_Pct":"{:.1f}%"}),
                         use_container_width=True)


# ════════════════ TAB 4 — INSIGHTS ════════════════════════════════════════════
with tabs[3]:
    from src.analytics.insight_generator import generate_insights
    insights = generate_insights(fdf, budgets)
    st.markdown('<div class="eyebrow">Automated Intelligence</div>', unsafe_allow_html=True)

    ic1, ic2 = st.columns([1.2, 1])
    norm  = [i for i in insights if "⚠️" not in i and "🚨" not in i]
    alrts = [i for i in insights if "⚠️" in i or  "🚨" in i]

    with ic1:
        st.markdown("**📡 Financial Insights**")
        for ins in norm:
            st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)

    with ic2:
        st.markdown("**⚠️ Alerts & Warnings**")
        if alrts:
            for ins in alrts:
                st.markdown(f'<div class="alert-card">{ins}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">✅ All budgets within limits — finances look healthy!</div>',
                        unsafe_allow_html=True)

    if cleaning_report:
        st.markdown('<div class="eyebrow">Data Quality</div>', unsafe_allow_html=True)
        qc1,qc2,qc3,qc4 = st.columns(4)
        with qc1: st.metric("Original Rows",  cleaning_report.get("original_rows",0))
        with qc2: st.metric("After Cleaning", cleaning_report.get("cleaned_rows",0))
        with qc3: st.metric("Rows Removed",   cleaning_report.get("removed_rows",0))
        orig = max(cleaning_report.get("original_rows",1),1)
        with qc4: st.metric("Data Quality",
                             f"{(1-cleaning_report.get('removed_rows',0)/orig)*100:.1f}%")


# ════════════════ TAB 5 — ML & PREDICTIONS ════════════════════════════════════
with tabs[4]:
    import plotly.graph_objects as go
    import plotly.express as px
    from src.ml_models.prediction_model import predict_next_month_spending, predict_category_trends
    from src.ml_models.clustering_model import cluster_spending_patterns, get_current_cluster

    st.markdown('<div class="eyebrow">Next Month Forecast</div>', unsafe_allow_html=True)
    with st.spinner("Running models…"):
        pred = predict_next_month_spending(df)

    if pred.get("lr_prediction"):
        pm1,pm2,pm3,pm4 = st.columns(4)
        with pm1: st.metric("Linear Regression",  f"₹{pred['lr_prediction']:,.0f}")
        with pm2: st.metric("Random Forest",       f"₹{pred['rf_prediction']:,.0f}")
        with pm3: st.metric("Ensemble",            f"₹{pred['ensemble_prediction']:,.0f}")
        with pm4: st.metric("RF R² Score",         f"{pred.get('rf_r2',0):.3f}")

        hdf = pd.DataFrame(pred["historical"])
        hdf["Label"] = hdf["Year"].astype(str)+"-"+hdf["Month"].astype(str).str.zfill(2)
        last = hdf["Total_Spending"].iloc[-1]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hdf["Label"], y=hdf["Total_Spending"],
                                  mode="lines+markers", name="Historical",
                                  line=dict(color="#9B7FFF", width=2.5),
                                  marker=dict(size=8,color="#9B7FFF",
                                              line=dict(color="rgba(155,127,255,.4)",width=6))))
        fig.add_trace(go.Scatter(x=[hdf["Label"].iloc[-1],"Next Month"],
                                  y=[last,pred["lr_prediction"]],
                                  mode="lines+markers", name=f"LR ₹{pred['lr_prediction']:,.0f}",
                                  line=dict(color="#00E5CC",width=2,dash="dash"),
                                  marker=dict(size=10,color="#00E5CC")))
        fig.add_trace(go.Scatter(x=[hdf["Label"].iloc[-1],"Next Month"],
                                  y=[last,pred["rf_prediction"]],
                                  mode="lines+markers", name=f"RF ₹{pred['rf_prediction']:,.0f}",
                                  line=dict(color="#FF4FA3",width=2,dash="dot"),
                                  marker=dict(size=10,color="#FF4FA3")))
        fig.update_layout(title="Spending Prediction — Next Month", hovermode="x unified")
        T(fig); st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(pred.get("message","Need ≥ 3 months of data."))

    st.markdown('<div class="eyebrow">Category Forecast</div>', unsafe_allow_html=True)
    with st.spinner("Forecasting categories…"):
        ct = predict_category_trends(df)
    if not ct.empty:
        clrs = ["#39FF94" if x<0 else "#FF4FA3" for x in ct["Change_Pct"]]
        fig = go.Figure(go.Bar(y=ct["Category"], x=ct["Predicted_Next_Month"],
                                orientation="h", marker_color=clrs, marker_line_width=0,
                                text=ct["Predicted_Next_Month"].apply(lambda x:f"₹{x:,.0f}"),
                                textposition="outside"))
        fig.update_layout(title="Predicted Next Month — by Category",
                          yaxis=dict(categoryorder="total ascending"), showlegend=False)
        T(fig); st.plotly_chart(fig, use_container_width=True)
        st.dataframe(ct.style.format({"Last_Month_Spending":"₹{:,.0f}",
                                       "Predicted_Next_Month":"₹{:,.0f}","Change_Pct":"{:+.1f}%"}),
                     use_container_width=True)

    st.markdown('<div class="eyebrow">Spending Clusters</div>', unsafe_allow_html=True)
    nc = st.slider("Number of Clusters", 2, 5, 3)
    with st.spinner("Running K-Means…"):
        cr = cluster_spending_patterns(df, n_clusters=nc)
    if cr["n_clusters"] > 0:
        st.markdown(f'<div class="cluster-badge">🏷️ Your pattern: <strong>{get_current_cluster(cr)}</strong></div>',
                    unsafe_allow_html=True)
        pca = cr["pca_df"]
        if not pca.empty and "PC1" in pca.columns:
            cl1,cl2 = st.columns([1.3,1])
            with cl1:
                fig = px.scatter(pca, x="PC1", y="PC2", color="Cluster_Label",
                                  size=[20]*len(pca),
                                  hover_data=["YearMonth"] if "YearMonth" in pca.columns else None,
                                  title="Spending Pattern Clusters",
                                  color_discrete_sequence=PALETTE[:nc])
                fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,.4)",width=2)))
                T(fig); st.plotly_chart(fig, use_container_width=True)
            with cl2:
                st.dataframe(cr["cluster_stats"], use_container_width=True, height=300)
    else:
        st.info(cr.get("message","Insufficient data."))


# ════════════════ TAB 6 — ANOMALY DETECTION ═══════════════════════════════════
with tabs[5]:
    import plotly.express as px
    from src.ml_models.anomaly_detection import detect_all_anomalies, format_anomaly_alerts

    st.markdown('<div class="eyebrow">Anomaly & Fraud Detection</div>', unsafe_allow_html=True)
    with st.spinner("Scanning transactions…"):
        anom  = detect_all_anomalies(fdf)
        alrts = format_anomaly_alerts(anom)

    an1,an2,an3 = st.columns(3)
    with an1: st.metric("Anomalies Found",     len(anom))
    with an2: st.metric("Detection Methods",   "Z-Score + IsoForest")
    with an3: st.metric("Clean Transactions",  f"{transaction_count(fdf)-len(anom):,}")

    if alrts:
        st.markdown("**🚨 Flagged Transactions**")
        for a in alrts:
            st.markdown(f'<div class="alert-card">{a}</div>', unsafe_allow_html=True)

        debits = fdf[fdf["Transaction_Type"]=="Debit"].copy()
        debits["_flag"] = debits.apply(
            lambda r: "🚨 Anomaly" if ((anom["Date"]==r["Date"])&(anom["Amount"]==r["Amount"])).any()
            else "Normal", axis=1)
        fig = px.scatter(debits, x="Date", y="Amount", color="_flag",
                         color_discrete_map={"Normal":"#9B7FFF","🚨 Anomaly":"#FF4FA3"},
                         size="Amount", size_max=26,
                         hover_data=["Description","Category","Merchant"],
                         title="Transactions — Anomalies Highlighted")
        fig.update_layout(legend=dict(title=""))
        T(fig); st.plotly_chart(fig, use_container_width=True)
        st.dataframe(anom, use_container_width=True)
    else:
        st.markdown("""
        <div class="success-card" style="text-align:center;padding:2.5rem">
          <div style="font-size:3rem;margin-bottom:.8rem">✅</div>
          <div style="font-size:1.05rem;font-weight:600;margin-bottom:.4rem">All Clear</div>
          <div style="color:rgba(160,255,200,.6);font-size:.88rem">
            No suspicious transactions detected. Your finances look clean.</div>
        </div>""", unsafe_allow_html=True)


# ════════════════ TAB 7 — REPORTS ═════════════════════════════════════════════
with tabs[6]:
    from src.reports.report_generator import generate_pdf_report, generate_csv_report

    st.markdown('<div class="eyebrow">Export & Reports</div>', unsafe_allow_html=True)
    rp1, rp2 = st.columns(2)

    with rp1:
        st.markdown("""
        <div class="report-card">
          <div class="report-icon">📑</div>
          <div class="report-title">PDF Executive Report</div>
          <div class="report-desc">3-page report with KPI cards, charts, automated insights,
          category breakdown and merchant analysis.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("⚡ Generate PDF", use_container_width=True, key="gpdf"):
            with st.spinner("Rendering…"):
                pb = generate_pdf_report(fdf, budgets)
            st.download_button("⬇️ Download PDF", data=pb, file_name="finsight_report.pdf",
                               mime="application/pdf", use_container_width=True)

    with rp2:
        st.markdown("""
        <div class="report-card">
          <div class="report-icon">📊</div>
          <div class="report-title">Excel Workbook</div>
          <div class="report-desc">6-sheet workbook: transactions, summary, categories,
          monthly trends, top merchants, and budget tracking.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("⚡ Generate Excel", use_container_width=True, key="gxl"):
            with st.spinner("Building workbook…"):
                xb = generate_csv_report(fdf, budgets)
            st.download_button("⬇️ Download Excel", data=xb, file_name="finsight_report.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

    st.markdown('<div class="eyebrow">Transaction Data</div>', unsafe_allow_html=True)
    disp = fdf.copy(); disp["Date"] = disp["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(disp[["Date","Description","Category","Amount",
                        "Transaction_Type","Merchant","Payment_Method"]],
                 use_container_width=True, height=380)
    st.download_button("⬇️ Export as CSV", data=fdf.to_csv(index=False).encode(),
                       file_name="transactions.csv", mime="text/csv")