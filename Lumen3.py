import calendar
from datetime import date, datetime, timedelta
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. PAGE CONFIG & SESSION STATE SETUP
# ==========================================
st.set_page_config(
    page_title="Lumen - AI Expense Tracker", layout="wide", page_icon="💜"
)

CATEGORIES = [
    "Coffee", "Groceries", "Food", "Transport",
    "Shopping", "Entertainment", "Bills", "Health", "Income",
]

CATEGORY_COLORS = {
    "Food": "#D97706",
    "Groceries": "#16A34A",
    "Transport": "#0891B2",
    "Shopping": "#DB2777",
    "Coffee": "#EA580C",
    "Entertainment": "#9333EA",
    "Bills": "#475569",
    "Health": "#059669",
    "Income": "#16A34A",
}

today = date.today()

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

if "data" not in st.session_state:
    m, y = today.month, today.year
    st.session_state["data"] = pd.DataFrame(
        [
            {"Date": date(y, m, 2), "Category": "Coffee", "Type": "Expense", "Amount": 180.0, "Note": "Morning Latte"},
            {"Date": date(y, m, 4), "Category": "Shopping", "Type": "Expense", "Amount": 1250.0, "Note": "Bought a TV"},
            {"Date": date(y, m, 9), "Category": "Food", "Type": "Expense", "Amount": 450.0, "Note": "Lunch"},
            {"Date": date(y, m, 11), "Category": "Transport", "Type": "Expense", "Amount": 800.0, "Note": "Cab"},
            {"Date": date(y, m, 13), "Category": "Food", "Type": "Expense", "Amount": 650.0, "Note": "Dinner"},
            {"Date": date(y, m, 15), "Category": "Health", "Type": "Expense", "Amount": 950.0, "Note": "Medicines"},
            {"Date": date(y, m, 17), "Category": "Coffee", "Type": "Expense", "Amount": 220.0, "Note": "Cafe"},
            {"Date": date(y, m, 19), "Category": "Income", "Type": "Income", "Amount": 5000.0, "Note": "Freelance Payment"},
            {"Date": date(y, m, 21), "Category": "Entertainment", "Type": "Expense", "Amount": 1800.0, "Note": "Movie"},
            {"Date": date(y, m, 22), "Category": "Income", "Type": "Income", "Amount": 2500.0, "Note": "Refund"},
            {"Date": date(y, m, 24), "Category": "Bills", "Type": "Expense", "Amount": 450.0, "Note": "Wifi Bill"},
            {"Date": date(y, m, 25), "Category": "Health", "Type": "Expense", "Amount": 1200.0, "Note": "Checkup"},
        ]
    )

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Hi! Tell me what you spent or earned, e.g. *'Spent ₹350 on pizza yesterday'* or *'Spent ₹120 coffee on 15th'*" }
    ]

if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"

if "settings" not in st.session_state:
    st.session_state["settings"] = {
        "currency": "₹",
        "income_goal": 50000.0,
        "savings_goal": 10000.0,
        "user_name": "Prakriti",
        "user_email": "prakriti11@gmail.com",
    }

if "budgets" not in st.session_state:
    st.session_state["budgets"] = {
        "Coffee": 1000.0, "Groceries": 4000.0, "Food": 3000.0, "Transport": 2000.0,
        "Shopping": 3000.0, "Entertainment": 2000.0, "Bills": 3000.0, "Health": 2000.0,
    }

# ==========================================
# 2. DYNAMIC THEME ENGINE (CSS OVERRIDES)
# ==========================================
is_dark = st.session_state["dark_mode"]

theme_css = f"""
<style>
    /* Dynamic Variables */
    :root {{
        --bg-color: {'#0F172A' if is_dark else '#F8F9FE'};
        --card-bg: {'#1E293B' if is_dark else '#FFFFFF'};
        --text-primary: {'#F8FAFC' if is_dark else '#0F172A'};
        --text-secondary: {'#94A3B8' if is_dark else '#475569'};
        --border-color: {'#334155' if is_dark else '#CBD5E1'};
        --chat-msg-bg: {'#0F172A' if is_dark else '#F8FAFC'};
        --input-bg: {'#1E293B' if is_dark else '#FFFFFF'};
    }}

    /* Base Body Styling */
    .stApp {{
        background-color: var(--bg-color) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary) !important;
    }}

    .block-container {{
        padding-top: 4.5rem !important;
        padding-bottom: 2rem !important;
    }}

    /* Global Typography */
    h1, h2, h3, h4, h5, h6, p, label {{
        color: var(--text-primary) !important;
    }}

    /* CHAT INPUT TEXT HIGH-CONTRAST FIX */
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInputContainer"] textarea,
    div[data-baseweb="textarea"] textarea,
    [data-testid="stBottomBlockContainer"] textarea {{
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }}

    div[data-testid="stChatInput"] textarea::placeholder,
    div[data-testid="stChatInputContainer"] textarea::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder,
    [data-testid="stBottomBlockContainer"] textarea::placeholder {{
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
    }}

    /* High-Contrast Dialog / Modal Styling */
    div[role="dialog"], 
    div[data-testid="stDialog"], 
    [data-testid="stModal"] {{
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
    }}

    div[role="dialog"] h1, 
    div[role="dialog"] h2, 
    div[role="dialog"] h3, 
    div[role="dialog"] h4, 
    div[role="dialog"] p, 
    div[role="dialog"] span, 
    div[role="dialog"] div,
    div[role="dialog"] label,
    div[data-testid="stDialogHeader"] *,
    div[data-testid="stDialog"] h1,
    div[data-testid="stDialog"] h2,
    div[data-testid="stDialog"] h3,
    div[data-testid="stDialog"] h4,
    div[data-testid="stDialog"] p,
    div[data-testid="stDialog"] span {{
        color: #F8FAFC !important;
    }}

    /* SELECTBOX & MONTH DROPDOWN CRISP WHITE OVERRIDE */
    div[data-baseweb="select"],
    div[data-baseweb="select"] *,
    div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] *,
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background-color: {'#1E293B' if is_dark else '#FFFFFF'} !important;
        color: {'#F8FAFC' if is_dark else '#0F172A'} !important;
        fill: {'#F8FAFC' if is_dark else '#0F172A'} !important;
        border-color: var(--border-color) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }}

    /* Dropdown Options Popup Menu */
    ul[role="listbox"],
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"] {{
        background-color: {'#1E293B' if is_dark else '#FFFFFF'} !important;
        border: 1px solid var(--border-color) !important;
    }}

    ul[role="listbox"] li,
    ul[role="listbox"] li *,
    [data-baseweb="menu"] * {{
        color: {'#F8FAFC' if is_dark else '#0F172A'} !important;
        background-color: {'#1E293B' if is_dark else '#FFFFFF'} !important;
    }}

    ul[role="listbox"] li:hover,
    ul[role="listbox"] li[aria-selected="true"] {{
        background-color: {'#334155' if is_dark else '#F1F5F9'} !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: {'#1E293B' if is_dark else '#FFFFFF'} !important;
        border-right: 1px solid var(--border-color) !important;
    }}

    /* Device Recommendation Banner */
    .device-banner {{
        background: linear-gradient(135deg, #5B42F3 0%, #8034FF 100%);
        color: #FFFFFF !important;
        padding: 14px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 0 4px 15px rgba(91, 66, 243, 0.3);
        border-left: 4px solid rgba(255, 255, 255, 0.3);
    }}

    .device-banner p, .device-banner strong {{
        color: #FFFFFF !important;
    }}

    .device-banner-icon {{
        font-size: 1.4rem;
        flex-shrink: 0;
    }}

    .device-banner-text {{
        margin: 0;
        line-height: 1.4;
    }}

    /* Input Labels */
    [data-testid="stWidgetLabel"] p, label, .stWidgetLabel {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }}

    /* Button Styling */
    div.stButton > button, 
    div.stDownloadButton > button,
    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primary"] {{
        color: #FFFFFF !important;
        background: linear-gradient(135deg, #5B42F3 0%, #7C3AED 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 12px rgba(91, 66, 243, 0.25) !important;
    }}

    div.stButton > button p, 
    div.stDownloadButton > button p,
    div.stButton > button span,
    div.stDownloadButton > button span {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}

    div.stButton > button:hover, 
    div.stDownloadButton > button:hover,
    [data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {{
        color: #FFFFFF !important;
        background: linear-gradient(135deg, #4C1D95 0%, #6D28D9 100%) !important;
        transform: translateY(-1px);
    }}

    .purple-text {{
        background: linear-gradient(135deg, #818CF8 0%, #C084FC 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 800;
    }}

    /* Container Cards Override */
    div[data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {{
        border-color: var(--border-color) !important;
    }}

    div[data-testid="stForm"] {{
        background: var(--card-bg) !important;
        border-color: var(--border-color) !important;
    }}

    /* Metric Cards Styling */
    [data-testid="stMetric"] {{
        background: var(--card-bg) !important;
        padding: 16px 20px;
        border-radius: 18px;
        border: 1px solid var(--border-color) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }}

    [data-testid="stMetricLabel"] {{ color: var(--text-secondary) !important; font-weight: 700 !important; }}
    [data-testid="stMetricValue"] {{ color: var(--text-primary) !important; font-weight: 800 !important; }}

    /* Progress bar gradient */
    .progress-container {{
        background: {'#334155' if is_dark else '#E2E8F0'};
        border-radius: 12px;
        height: 12px;
        width: 100%;
        overflow: hidden;
        margin-top: 10px;
    }}
    
    .progress-bar-fill {{
        height: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #5B42F3 0%, #A855F7 50%, #EC4899 100%);
    }}

    div.quick-add-wrap button {{
        border-radius: 20px !important;
        padding: 10px 20px !important;
    }}

    /* AI Chat Box Container */
    .ai-chat-box-wrapper {{
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }}

    /* Individual Chat Bubble Styling */
    [data-testid="stChatMessage"] {{
        background-color: var(--chat-msg-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        padding: 12px !important;
    }}

    [data-testid="stChatMessage"] p {{
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }}

    /* Lumi Chat Bubble */
    .lumi-flex-container {{ display: flex; align-items: center; gap: 12px; }}
    .lumi-bubble {{
        background: {'#3B0764' if is_dark else '#F3E8FF'};
        color: {'#F3E8FF' if is_dark else '#3B0764'} !important;
        font-size: 0.85rem;
        font-weight: 700;
        padding: 10px 16px;
        border-radius: 16px 16px 16px 2px;
        border: 1px solid {'#581C87' if is_dark else '#DDD6FE'};
        box-shadow: 0 2px 8px rgba(108, 93, 211, 0.08);
    }}

    .dash-card-title {{ font-size: 1.1rem; font-weight: 800; color: var(--text-primary); margin: 0; }}
    .dash-card-sub {{ color: var(--text-secondary); font-size: 0.82rem; font-weight: 600; margin-top: 2px; margin-bottom: 12px; }}

    /* Transactions Row Styling */
    .tx-row {{ display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-color); }}
    .tx-avatar {{
        width: 38px; height: 38px; border-radius: 50%; color: white; font-weight: 800;
        display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;
    }}
    .tx-row-title {{ font-weight: 700; color: var(--text-primary); font-size: 0.9rem; }}
    .tx-row-sub {{ color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; }}
    .tx-row-amt {{ margin-left: auto; font-weight: 800; font-size: 0.9rem; }}

    .insight-tips {{ margin-top: 10px; padding-left: 18px; }}
    .insight-tips li {{ color: var(--text-primary); font-size: 0.88rem; margin-bottom: 8px; line-height: 1.5; font-weight: 500; }}

    /* Calendar Grid Specific Styles */
    .cal-grid-header {{
        text-align: center;
        font-size: 12px;
        font-weight: 700;
        color: var(--text-secondary);
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    div[data-testid="stHorizontalBlock"] {{
        margin-bottom: 12px !important;
    }}

    div[data-testid="stColumn"] {{
        position: relative !important;
    }}

    .cal-day-box {{
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        height: 125px;
        padding: 12px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease;
        box-sizing: border-box;
    }}

    /* SOFT PASTEL INDICATOR COLORS */
    .cal-day-box.card-saved {{
        background-color: {'#064E3B' if is_dark else '#DCFCE7'} !important;
        border-color: {'#34D399' if is_dark else '#86EFAC'} !important;
    }}
    .cal-day-box.card-normal {{
        background-color: {'#451A03' if is_dark else '#FEF3C7'} !important;
        border-color: {'#FBBF24' if is_dark else '#FDE047'} !important;
    }}
    .cal-day-box.card-over {{
        background-color: {'#4C0519' if is_dark else '#FEE2E2'} !important;
        border-color: {'#F87171' if is_dark else '#FCA5A5'} !important;
    }}

    .cal-day-num {{
        font-size: 13px;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .tx-count-badge {{
        font-size: 10px;
        background: rgba(91, 66, 243, 0.2);
        color: var(--text-primary);
        padding: 2px 7px;
        border-radius: 10px;
        font-weight: 600;
    }}

    .card-amount-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        flex-grow: 1;
    }}

    .card-amount-text {{
        font-size: 15px;
        font-weight: 800;
        letter-spacing: -0.3px;
    }}

    .text-saved {{ color: {'#6EE7B7' if is_dark else '#15803D'} !important; }}
    .text-normal {{ color: {'#FDE047' if is_dark else '#92400E'} !important; }}
    .text-over {{ color: {'#FCA5A5' if is_dark else '#B91C1C'} !important; }}

    .cal-empty-box {{
        background: var(--card-bg);
        border-radius: 16px;
        height: 125px;
        opacity: 0.3;
    }}

    div[class*="st-key-overlay_"] {{
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 125px !important;
        z-index: 10 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    div[class*="st-key-overlay_"] button {{
        width: 100% !important;
        height: 125px !important;
        opacity: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }}

    div[data-testid="stColumn"]:hover .cal-day-box {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(108, 93, 211, 0.22) !important;
        border: 2px solid #6C5DD3 !important;
    }}

    .cal-legend {{
        display: flex;
        flex-wrap: wrap;
        gap: 24px;
        margin-top: 25px;
        padding: 18px;
        background: var(--card-bg);
        border-radius: 14px;
        border: 1px solid var(--border-color);
        justify-content: flex-start;
    }}
    .legend-item {{ display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-secondary); font-weight: 500; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; }}

    .badge-card {{
        background: var(--card-bg);
        border-radius: 18px; padding: 24px; text-align: center;
        border: 1px solid var(--border-color); box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }}
    .badge-emoji {{ font-size: 40px; margin-bottom: 10px; }}
    .badge-locked {{ opacity: 0.4; filter: grayscale(1); }}
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# ==========================================
# 3. DEVICE RECOMMENDATION BANNER
# ==========================================
st.markdown(
    """
    <div class="device-banner">
        <span class="device-banner-icon">💻</span>
        <p class="device-banner-text">
            <strong>💜 Pro Tip:</strong> For the best experience, use Lumen on a <strong>laptop or desktop</strong> to unlock all features and interactive visualizations!
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 4. HELPER FUNCTIONS & DIALOGS
# ==========================================
def parse_and_add_transaction(prompt):
    amount_match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)', prompt, re.IGNORECASE)
    if not amount_match:
        return False, "I couldn't find a valid amount in your message. Try saying something like: *'Spent 450 on groceries yesterday'*"

    amount = float(amount_match.group(1))
    lower_p = prompt.lower()

    target_date = today
    if "yesterday" in lower_p:
        target_date = today - timedelta(days=1)
    else:
        day_match = re.search(r'\b(?:on\s+)?(\d{1,2})(?:st|nd|rd|th)?\b', lower_p)
        if day_match:
            try:
                parsed_day = int(day_match.group(1))
                if 1 <= parsed_day <= 31:
                    target_date = date(today.year, today.month, parsed_day)
            except ValueError:
                pass

    income_keywords = ["received", "earned", "salary", "income", "freelance", "refund", "got", "added"]
    is_income = any(kw in lower_p for kw in income_keywords)
    tx_type = "Income" if is_income else "Expense"

    category = "Bills"
    if is_income:
        category = "Income"
    elif any(kw in lower_p for kw in ["coffee", "cafe", "starbucks", "latte", "tea", "chai"]):
        category = "Coffee"
    elif any(kw in lower_p for kw in ["pizza", "burger", "food", "lunch", "dinner", "swiggy", "zomato", "restaurant"]):
        category = "Food"
    elif any(kw in lower_p for kw in ["grocery", "groceries", "supermarket", "vegetables", "fruits"]):
        category = "Groceries"
    elif any(kw in lower_p for kw in ["uber", "ola", "cab", "transport", "bus", "train", "flight", "petrol", "fuel"]):
        category = "Transport"
    elif any(kw in lower_p for kw in ["clothes", "shopping", "amazon", "flipkart", "shoes", "mall"]):
        category = "Shopping"
    elif any(kw in lower_p for kw in ["movie", "cinema", "entertainment", "netflix", "game"]):
        category = "Entertainment"
    elif any(kw in lower_p for kw in ["medicine", "doctor", "pharmacy", "health", "hospital"]):
        category = "Health"

    note = f"Quick Add: {category}"

    new_row = pd.DataFrame([{"Date": target_date, "Category": category, "Type": tx_type, "Amount": amount, "Note": note}])
    st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)

    sign = "+" if is_income else "-"
    curr = st.session_state["settings"]["currency"]
    msg = f"Added **{category}** ({tx_type}) of **{sign}{curr}{amount:,.2f}** for **{target_date.strftime('%b %d')}**."
    return True, msg

@st.dialog("💬 Quick Add Assistant")
def quick_add_chatbot():
    st.caption("Add multiple entries on any date in plain text.")
    st.markdown('<div class="ai-chat-box-wrapper">', unsafe_allow_html=True)
    chat_container = st.container(height=300)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            st.chat_message(msg["role"]).write(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    if user_input := st.chat_input("Type your transaction...", key="dialog_chat_input"):
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        _, reply = parse_and_add_transaction(user_input)
        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
        st.rerun()

@st.dialog("📅 Daily Transactions")
def show_day_details_modal(selected_date):
    st.markdown(
        f"<div style='color: #E2E8F0 !important; font-weight: 600; font-size: 1.05rem; margin-bottom: 20px;'>Transactions for {selected_date.strftime('%B %d, %Y')}</div>", 
        unsafe_allow_html=True
    )
    
    day_txs = st.session_state["data"][st.session_state["data"]["Date"] == selected_date]
    
    if day_txs.empty:
        st.info("No transactions logged for this day.")
    else:
        for idx, row in day_txs.iterrows():
            col_info, col_del = st.columns([4, 1])
            with col_info:
                sign = "+" if row["Type"] == "Income" else "-"
                curr = st.session_state["settings"]["currency"]
                st.markdown(f"**{row['Category']}** ({row['Type']}): {sign}{curr}{row['Amount']:,.2f} — *{row['Note']}*")
            with col_del:
                if st.button("Delete", key=f"del_tx_{idx}"):
                    st.session_state["data"] = st.session_state["data"].drop(index=idx).reset_index(drop=True)
                    st.success("Transaction deleted!")
                    st.rerun()
                    st.divider()

# ==========================================
# 5. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    try:
        st.image("Lumen.jpeg", use_container_width=True)
    except Exception:
        try:
            st.image("assets/Lumen.jpeg", use_container_width=True)
        except Exception:
            st.caption("🖼️ *(Lumen.jpeg)*")

    st.markdown("## 💜 **Lumen**")
    st.caption("AI Expense Tracker")
    st.markdown("---")

    nav_items = [
        ("🏠 Dashboard", "Dashboard"),
        ("💬 AI Chat", "AI Chat"),
        ("📅 Calendar", "Calendar"),
        ("📑 Transactions", "Transactions"),
        ("🎯 Budgets", "Budgets"),
        ("📊 Reports", "Reports"),
        ("🎁 Rewards", "Rewards"),
        ("⚙️ Settings", "Settings"),
    ]
    for label, target in nav_items:
        is_current = st.session_state["page"] == target
        if st.button(label, use_container_width=True, type="primary" if is_current else "secondary", key=f"nav_{target}"):
            st.session_state["page"] = target
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write(f"👤 **{st.session_state['settings']['user_name']}**")
    st.caption(st.session_state["settings"]["user_email"])

# Calculations
curr_symbol = st.session_state["settings"]["currency"]
df_data = st.session_state["data"].copy()
df_data["Date"] = pd.to_datetime(df_data["Date"]).dt.date

this_month_mask = (df_data["Date"].apply(lambda d: d.month) == today.month) & (df_data["Date"].apply(lambda d: d.year) == today.year)
this_month_df = df_data[this_month_mask]
month_spend = this_month_df[this_month_df["Type"] == "Expense"]["Amount"].sum()
month_income = this_month_df[this_month_df["Type"] == "Income"]["Amount"].sum()
total_balance = month_income - month_spend

# ==========================================
# 6. FULL PAGE RENDERERS
# ==========================================

def render_dashboard_page():
    col_header, col_quickadd = st.columns([4, 1], vertical_alignment="top")

    with col_header:
        head_text_col, head_mascot_col, _ = st.columns([4, 1.5, 0.5], vertical_alignment="center")
        with head_text_col:
            st.markdown(
                f"""
                <div style='margin-top: 5px;'>
                    <h1 style='margin:0; padding:0; font-size:2.4rem; font-weight:800; line-height: 1.2;'>
                        Hi {st.session_state["settings"]["user_name"]}, <br>
                        <span class='purple-text'>here's your money in motion.</span>
                    </h1>
                    <p style='margin-top:8px; font-size:1rem; font-weight:600;'>
                        Every smart choice builds your bigger tomorrow. 💜
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with head_mascot_col:
            st.markdown("<div style='display: flex; justify-content: center; align-items: center;'>", unsafe_allow_html=True)
            try:
                st.image("Lumi.png", width=110)
            except Exception:
                try:
                    st.image("assets/Lumi.png", width=110)
                except Exception:
                    st.write("🍋 *(Lumi.png)*")
            st.markdown("</div>", unsafe_allow_html=True)

    with col_quickadd:
        st.markdown('<div class="quick-add-wrap" style="margin-top: 10px;">', unsafe_allow_html=True)
        if st.button("+ Quick Add", use_container_width=True, key="quick_add_dash"):
            quick_add_chatbot()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    
    # --- Top Metric Cards ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Balance", f"{curr_symbol}{total_balance:,.2f}")
    m2.metric("Monthly Income", f"{curr_symbol}{month_income:,.2f}")
    m3.metric("Monthly Expenses", f"{curr_symbol}{month_spend:,.2f}", delta="-88.5%", delta_color="inverse")
    m4.metric("Savings Goal", "100%")

    st.write("")

    # --- Savings Goal Progress Container ---
    target_savings = st.session_state["settings"]["savings_goal"]
    pct_saved = min(100, int((total_balance / target_savings) * 100)) if target_savings > 0 else 100
    
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 0.95rem;">🌱 Savings Goal Progress</strong>
                <span style="font-size: 0.85rem; font-weight: 800; color: #5B42F3;">{curr_symbol}{total_balance:,.2f} / {curr_symbol}{target_savings:,.2f}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar-fill" style="width: {pct_saved}%;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    
    # --- Visualizations Row ---
    row1_left, row1_right = st.columns([1.4, 1], vertical_alignment="top")

    plot_text_color = "#F8FAFC" if is_dark else "#000000"
    plot_grid_color = "#334155" if is_dark else "#CBD5E1"

    with row1_left:
        with st.container(border=True):
            st.markdown('<p class="dash-card-title">Weekly Spending</p><p class="dash-card-sub">Last 7 days</p>', unsafe_allow_html=True)

            days_last_7 = [today - timedelta(days=i) for i in range(6, -1, -1)]
            week_spend = [df_data[(df_data["Date"] == d) & (df_data["Type"] == "Expense")]["Amount"].sum() for d in days_last_7]
            day_labels = [d.strftime("%a") for d in days_last_7]

            fig_week = go.Figure(
                data=[
                    go.Bar(
                        x=day_labels,
                        y=week_spend,
                        marker=dict(
                            color=week_spend,
                            colorscale=[[0, '#8B5CF6'], [1, '#5B42F3']],
                            line=dict(color='rgba(0,0,0,0)', width=0)
                        ),
                        width=0.45
                    )
                ]
            )
            fig_week.update_layout(
                height=160,
                margin=dict(l=5, r=5, t=5, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont=dict(color=plot_text_color, size=12)),
                yaxis=dict(showgrid=True, gridcolor=plot_grid_color, tickfont=dict(color=plot_text_color, size=12)),
            )
            st.plotly_chart(fig_week, use_container_width=True, config={"displayModeBar": False})

            lumi_mascot_col, lumi_msg_col = st.columns([1.2, 3], vertical_alignment="center")
            with lumi_mascot_col:
                try:
                    st.image("assets/Dashboard.png", width=160)
                except Exception:
                    st.write("🍋 *(Dashboard.png)*")
            with lumi_msg_col:
                st.markdown(
                    """
                    <div class="lumi-flex-container">
                        <div class="lumi-bubble">You're doing great!<br>Keep going ✨</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with row1_right:
        with st.container(border=True):
            st.markdown('<p class="dash-card-title">Spending by Category</p><p class="dash-card-sub">This month</p>', unsafe_allow_html=True)

            cat_totals = this_month_df[this_month_df["Type"] == "Expense"].groupby("Category")["Amount"].sum()
            if not cat_totals.empty:
                colors = [CATEGORY_COLORS.get(c, "#64748B") for c in cat_totals.index]
                fig_donut = go.Figure(go.Pie(
                    labels=cat_totals.index, values=cat_totals.values,
                    hole=0.65, marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=2)),
                    textinfo="none", showlegend=False
                ))
                fig_donut.update_layout(height=160, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

                legend_html = "".join(
                    f"""<div style="display:inline-flex; align-items:center; gap:6px; font-size:12px; font-weight:700; color:{plot_text_color}; margin-right:12px; margin-bottom:6px;"><div style="width:10px; height:10px; background:{CATEGORY_COLORS.get(cat, '#64748B')}; border-radius:3px;"></div>{cat}</div>"""
                    for cat in cat_totals.index
                )
                st.markdown(f'<div style="margin-top:10px;">{legend_html}</div>', unsafe_allow_html=True)

    st.write("")
    
    # --- Recent Transactions & AI Insights ---
    row2_left, row2_right = st.columns([1.4, 1], vertical_alignment="top")

    with row2_left:
        with st.container(border=True):
            st.markdown('<p class="dash-card-title">Recent Transactions</p><p class="dash-card-sub">Latest entries</p>', unsafe_allow_html=True)

            recent_txs = df_data.sort_values("Date", ascending=False).head(3)
            for _, row in recent_txs.iterrows():
                sign = "+" if row["Type"] == "Income" else "-"
                color = "#16A34A" if row["Type"] == "Income" else "#DC2626"
                avatar_bg = CATEGORY_COLORS.get(row["Category"], "#5B42F3")
                st.markdown(
                    f"""
                    <div class="tx-row">
                        <div class="tx-avatar" style="background:{avatar_bg};">{row['Category'][0]}</div>
                        <div>
                            <div class="tx-row-title">{row.get('Note', row['Category'])}</div>
                            <div class="tx-row-sub">{row['Category']} · {row['Date']}</div>
                        </div>
                        <div class="tx-row-amt" style="color:{color};">{sign}{curr_symbol}{row['Amount']:,.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with row2_right:
        with st.container(border=True):
            head_col, lumi_col = st.columns([2.5, 1], vertical_alignment="center")
            
            with head_col:
                st.markdown(
                    '<p class="dash-card-sub" style="color:#A855F7; font-weight:800; margin:0;">✨ AI INSIGHTS</p>'
                    '<p class="dash-card-title">Lumi\'s tips 🍋</p>',
                    unsafe_allow_html=True
                )
            
            with lumi_col:
                try:
                    st.image("assets/LumiCoach.png", width=100)
                except Exception:
                    st.write("🍋")

            st.markdown(
                """
                <ul class="insight-tips">
                    <li><strong>Shopping</strong> accounts for most spending; review large purchases and pause nonessentials for 30 days.</li>
                    <li>Set a weekly cap and enable instant alerts for any purchase over ₹500.</li>
                </ul>
                """,
                unsafe_allow_html=True,
            )

def render_ai_chat_page():
    col_text, col_character = st.columns([1.8, 1], vertical_alignment="center", gap="small")
    
    with col_text:
        st.markdown("# 💬 AI Chat")
        st.caption("Tell Lumi what you spent or earned in plain language.")
    
    with col_character:
        try:
            st.image("assets/LUMI(AI).PNG", width=130)
        except Exception:
            try:
                st.image("LUMI(AI).PNG", width=130)
            except Exception:
                st.write("🍋")

    st.markdown('<div class="ai-chat-box-wrapper">', unsafe_allow_html=True)
    chat_container = st.container(height=450)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            st.chat_message(msg["role"]).write(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    if user_input := st.chat_input("Type your transaction... e.g. 'Spent 350 on pizza yesterday'", key="page_chat_input"):
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        _, reply = parse_and_add_transaction(user_input)
        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
        st.rerun()

def render_calendar_page():
    col_title, col_actions = st.columns([3, 1], vertical_alignment="center")

    with col_title:
        title_text_col, title_lumi_col = st.columns([2.5, 1], vertical_alignment="center")
        with title_text_col:
            st.markdown(
                """<div style='text-align: left;'>
                    <h1 style='margin: 0; padding: 0; font-size: 2.3rem; font-weight: 800;'>
                        <span class='purple-text'>Spending Map</span>
                    </h1>
                    <p style='margin-top: 4px; font-size:0.95rem; font-weight: 600;'>
                        See where your money goes, day by day.
                    </p>
                </div>""",
                unsafe_allow_html=True,
            )
        with title_lumi_col:
            try:
                st.image("assets/Upper.png", width=120)
            except Exception:
                try:
                    st.image("upper.png", width=120)
                except Exception:
                    st.caption("🍋 *(assets/upper.png)*")

    with col_actions:
        st.markdown('<div class="quick-add-wrap">', unsafe_allow_html=True)
        if st.button("+ Quick Add", use_container_width=True, key="quick_add_cal"):
            quick_add_chatbot()
        st.markdown('</div>', unsafe_allow_html=True)

    # Selection Row
    c1, _, _ = st.columns([1.8, 3, 5])
    view_month_name = c1.selectbox(
        "Month",
        list(calendar.month_name)[1:],
        index=today.month - 1,
        label_visibility="collapsed",
    )
    month_idx = list(calendar.month_name).index(view_month_name)

    income_goal = st.session_state["settings"].get("income_goal", 50000.0)
    daily_threshold = income_goal / 30

    cal = calendar.Calendar(firstweekday=6)  # Sunday start
    weeks = cal.monthdayscalendar(today.year, month_idx)

    # Weekday Headers
    h_cols = st.columns(7)
    for i, d in enumerate(["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]):
        h_cols[i].markdown(
            f"<div class='cal-grid-header'>{d}</div>", unsafe_allow_html=True
        )

    # Render Calendar Grid Days
    for week in weeks:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].markdown(
                    "<div class='cal-empty-box'></div>",
                    unsafe_allow_html=True,
                )
            else:
                cur_date = date(today.year, month_idx, day)
                day_data = df_data[df_data["Date"] == cur_date]

                card_class = ""
                amount_content = ""
                count_badge = ""
                has_tx = not day_data.empty

                if has_tx:
                    tx_count = len(day_data)
                    if tx_count > 1:
                        count_badge = f"<span class='tx-count-badge'>{tx_count} items</span>"

                    expense = day_data[day_data["Type"] == "Expense"]["Amount"].sum()
                    income = day_data[day_data["Type"] == "Income"]["Amount"].sum()

                    if income > expense:
                        card_class = "card-saved"
                        txt_cls, sign, val = "text-saved", "+", (income - expense)
                    elif expense > daily_threshold:
                        card_class = "card-over"
                        txt_cls, sign, val = "text-over", "-", expense
                    else:
                        card_class = "card-normal"
                        txt_cls, sign, val = "text-normal", "-", expense

                    amount_content = f"""
                    <div class="card-amount-container">
                        <span class="card-amount-text {txt_cls}">{sign}{curr_symbol}{val:,.2f}</span>
                    </div>
                    """

                card_html = f"""
                <div class="cal-day-box {card_class}">
                    <div class="cal-day-num"><span>{day}</span>{count_badge}</div>
                    {amount_content}
                </div>
                """

                with cols[i]:
                    st.markdown(card_html.replace("\n", ""), unsafe_allow_html=True)
                    # Overlay button rendered for EVERY day to trigger modal details
                    if st.button(" ", key=f"overlay_{cur_date}"):
                        show_day_details_modal(cur_date)

    # Calendar Legend Footer (With Matching Pastel Indicators)
    st.markdown(
        """<div class="cal-legend">
            <div class="legend-item"><div class="dot" style="background:#86EFAC; border: 1px solid #4ADE80;"></div>Net Saved</div>
            <div class="legend-item"><div class="dot" style="background:#FDE047; border: 1px solid #FACC15;"></div>Normal Spending</div>
            <div class="legend-item"><div class="dot" style="background:#FCA5A5; border: 1px solid #F87171;"></div>Over Threshold</div>
            <div class="legend-item"><div class="dot" style="background:#E2E8F0; border: 1px solid #CBD5E1;"></div>No Activity</div>
        </div>""",
        unsafe_allow_html=True,
    )

def render_transactions_page():
    col_title, col_lumi = st.columns([0.85, 0.15])
    
    with col_title:
        st.markdown("# 📑 Transactions")
        st.caption("View, filter, and add transactions to your ledger.")
        
    with col_lumi:
        try:
            st.image("assets/Upper.png", width=65)
        except Exception:
            pass

    with st.expander("➕ Add New Transaction", expanded=False):
        with st.form("add_tx_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                tx_date_input = st.date_input("Date", value=today)
            with col2:
                tx_category = st.selectbox("Category", CATEGORIES)
                tx_amount = st.number_input("Amount", min_value=0.0, step=10.0, value=100.0)
            with col3:
                tx_type = st.selectbox("Type", ["Expense", "Income"])
                tx_note = st.text_input("Note", value="")
                
            submitted = st.form_submit_button("Add Transaction", use_container_width=True)

            if submitted:
                tx_date = pd.to_datetime(tx_date_input).date()
                new_entry = pd.DataFrame([{
                    "Date": tx_date,
                    "Category": tx_category,
                    "Type": tx_type,
                    "Amount": tx_amount,
                    "Note": tx_note if tx_note else f"Manual Add: {tx_category}"
                }])
                st.session_state["data"] = pd.concat([st.session_state["data"], new_entry], ignore_index=True)
                st.success("Transaction added successfully!")
                st.rerun()

    col_filter1, col_filter2 = st.columns([2, 2])
    with col_filter1:
        selected_cat = st.multiselect("Filter by Category", CATEGORIES, default=[])
    with col_filter2:
        selected_type = st.multiselect("Filter by Type", ["Expense", "Income"], default=[])

    filtered_df = st.session_state["data"].copy()
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"]).dt.date

    if selected_cat:
        filtered_df = filtered_df[filtered_df["Category"].isin(selected_cat)]
    if selected_type:
        filtered_df = filtered_df[filtered_df["Type"].isin(selected_type)]

    filtered_df = filtered_df.sort_values("Date", ascending=False)

    st.dataframe(
        filtered_df,
        column_config={
            "Amount": st.column_config.NumberColumn(format=f"{curr_symbol}%.2f"),
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
        },
        use_container_width=True,
        hide_index=True
    )

def render_budget_card(item):
    pct = min(int((item["spent"] / item["total"]) * 100), 100)
    
    with st.container():
        c1, c2, c3 = st.columns([0.5, 0.3, 0.2])
        
        with c1:
            st.markdown(f"**{item['name']}**")
            st.markdown(f"### ${item['spent']:.2f}")

        with c2:
            st.write("")
            st.caption(f"of ${item['total']:.2f}")
            st.write(f"**{pct}%**")

        with c3:
            try:
                st.image(item["lumi"], width=65)
            except Exception:
                st.write("⭐")

        st.progress(pct / 100)

def render_budget_page():
    st.caption("BUDGETS")
    
    head_col1, head_col2, head_col3 = st.columns([0.55, 0.25, 0.20])
    with head_col1:
        st.markdown("<h1 style='margin:0;'>Plan the month, own it 🪄</h1>", unsafe_allow_html=True)
        st.caption("Smart budgets today, stress-free tomorrow. 💜")
    with head_col2:
        try:
            st.image("assets/Upper.png", width=90)
        except Exception:
            pass
    with head_col3:
        if st.button("➕ New budget", type="primary", use_container_width=True):
            pass

    st.write("")

    categories_data = [
        {"name": "Food", "spent": 56.00, "total": 600.00, "lumi": "assets/Food.png"},
        {"name": "Transport", "spent": 40.50, "total": 250.00, "lumi": "assets/Travel.png"},
        {"name": "Shopping", "spent": 134.99, "total": 400.00, "lumi": "assets/Shoping.png"},
        {"name": "Bills", "spent": 120.00, "total": 250.00, "lumi": "assets/Bills.png"},
        {"name": "Entertainment", "spent": 15.99, "total": 200.00, "lumi": "assets/entertainment.png"},
        {"name": "Groceries", "spent": 107.40, "total": 500.00, "lumi": "assets/Groceries.png"},
    ]

    for i in range(0, len(categories_data), 2):
        col_left, col_right = st.columns(2)
        with col_left:
            render_budget_card(categories_data[i])
        if i + 1 < len(categories_data):
            with col_right:
                render_budget_card(categories_data[i+1])

def render_reports_page():
    # Asset paths
    lumi_coach_path = "assets/LumiCoach.png"
    trend_path = "assets/Trend.png"
    bottom_r_path = "assets/Bottom(R).png"

    # --- Top Banner Header ---
    col_rt_txt, col_rt_img = st.columns([3, 1], vertical_alignment="center")
    with col_rt_txt:
        st.markdown(
            f"""
            <div>
                <p style="color: #8B5CF6; font-size: 12px; font-weight: 800; letter-spacing: 1.2px; margin: 0; text-transform: uppercase;">REPORTS & ANALYTICS</p>
                <h1 style="margin: 0; font-weight: 800; font-size: 32px; color: var(--text-primary);">
                    Trends that tell <span class="purple-text">your story 🪄</span>
                </h1>
                <p style="color: var(--text-secondary); margin-top: 4px; font-size: 14px;">Data doesn't lie, but it does help! 💜</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_rt_img:
        try:
            st.image(trend_path, width=160)
        except Exception:
            try:
                st.image("Trend.png", width=160)
            except Exception:
                pass

    st.write("")

    # --- Top Summary Cards ---
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f"""
            <div style="background: var(--card-bg); padding: 18px; border-radius: 16px; border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <div style="background: #F3E8FF; padding: 8px; border-radius: 10px; font-size: 16px;">👛</div>
                    <span style="font-size: 11px; font-weight: 800; color: var(--text-secondary); letter-spacing: 0.5px;">THIS MONTH SPEND</span>
                </div>
                <h2 style="margin: 0; font-size: 28px; font-weight: 800; color: var(--text-primary);">{curr_symbol}{month_spend:,.2f}</h2>
                <p style="color: #16A34A; font-size: 12px; font-weight: 700; margin-top: 4px;">▼ 0.0% vs May</p>
            </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
            <div style="background: var(--card-bg); padding: 18px; border-radius: 16px; border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <div style="background: #DCFCE7; padding: 8px; border-radius: 10px; font-size: 16px;">📈</div>
                    <span style="font-size: 11px; font-weight: 800; color: var(--text-secondary); letter-spacing: 0.5px;">THIS MONTH INCOME</span>
                </div>
                <h2 style="margin: 0; font-size: 28px; font-weight: 800; color: #16A34A;">{curr_symbol}{month_income:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
            <div style="background: var(--card-bg); padding: 18px; border-radius: 16px; border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <div style="background: #FEF3C7; padding: 8px; border-radius: 10px; font-size: 16px;">👑</div>
                    <span style="font-size: 11px; font-weight: 800; color: var(--text-secondary); letter-spacing: 0.5px;">NET THIS MONTH</span>
                </div>
                <h2 style="margin: 0; font-size: 28px; font-weight: 800; color: var(--text-primary);">{curr_symbol}{total_balance:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    # --- Section: 6-Month Trend Chart ---
    with st.container(border=True):
        c_head, c_opt = st.columns([4, 1])
        with c_head:
            st.markdown("### 6-month trend")
        with c_opt:
            st.selectbox("Range", ["Last 6 months", "Last 12 months"], label_visibility="collapsed")

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
        exp_data = [100, 150, 180, 200, 220, 300, 750]
        inc_data = [200, 200, 200, 200, 4800, 4800, 4800]

        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=months, y=exp_data, name="expenses",
            mode="lines+markers", line=dict(color="#F43F5E", width=3, shape='spline'),
            marker=dict(size=8, color="#FFFFFF", line=dict(width=2, color="#F43F5E"))
        ))

        fig_trend.add_trace(go.Scatter(
            x=months, y=inc_data, name="income",
            mode="lines+markers", line=dict(color="#10B981", width=3, shape='spline'),
            marker=dict(size=8, color="#FFFFFF", line=dict(width=2, color="#10B981"))
        ))

        fig_trend.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[-200, 6500])
        )

        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

    st.write("")

    # --- Bottom Section: Income vs Expense & Coach's Notes ---
    col_bot_l, col_bot_r = st.columns(2, vertical_alignment="top")

    with col_bot_l:
        with st.container(border=True):
            st.markdown("### Income vs Expense")
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=months, y=exp_data, name="expenses", marker_color="#5B42F3"))
            fig_bar.add_trace(go.Bar(x=months, y=inc_data, name="income", marker_color="#10B981"))
            
            fig_bar.update_layout(
                barmode='group',
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    with col_bot_r:
        with st.container(border=True):
            col_cn_txt, col_cn_img = st.columns([3, 1], vertical_alignment="center")
            with col_cn_txt:
                st.markdown("### ✨ AI Analysis\n#### Coach's notes")
            with col_cn_img:
                try:
                    st.image(lumi_coach_path, width=90)
                except Exception:
                    try:
                        st.image("LumiCoach.png", width=90)
                    except Exception:
                        pass

            st.markdown(
                """
                <ul class="insight-tips">
                    <li>🛍️ <strong>Shopping is your biggest category ($134.99);</strong> set a $100 cap and wait 24 hours before purchases.</li>
                    <li>🌱 <strong>Automate saving 10% of expenses (~$55)</strong> into a separate account right after payday.</li>
                    <li>💡 <strong>Review all subscriptions and small recurring charges;</strong> cancel or downgrade anything unused this month.</li>
                </ul>
                """,
                unsafe_allow_html=True
            )
def render_rewards_page():
    st.markdown("# 🎁 Financial Health & Badges")
    st.caption("Unlock milestones as you build healthy financial habits.")

    b1, b2, b3 = st.columns(3)
    
    with b1:
        st.markdown(
            f"""
            <div class="badge-card">
                <div class="badge-emoji">🌱</div>
                <h4>Budget Novice</h4>
                <p>Tracked over 10 transactions successfully.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with b2:
        savings_reached = total_balance >= st.session_state["settings"]["savings_goal"]
        locked_class = "" if savings_reached else "badge-locked"
        st.markdown(
            f"""
            <div class="badge-card {locked_class}">
                <div class="badge-emoji">🎯</div>
                <h4>Goal Saver</h4>
                <p>Reached 100% of your savings goal.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with b3:
        st.markdown(
            """
            <div class="badge-card badge-locked">
                <div class="badge-emoji">🔥</div>
                <h4>30-Day Streak</h4>
                <p>Log expenses every day for a whole month.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_settings_page():
    st.markdown("# ⚙️ Settings")
    st.caption("Personalize your profile and application preferences.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Profile Settings")
        u_name = st.text_input("Name", value=st.session_state["settings"]["user_name"])
        u_email = st.text_input("Email", value=st.session_state["settings"]["user_email"])
        u_curr = st.selectbox("Currency Symbol", ["₹", "$", "€", "£", "¥"], index=["₹", "$", "€", "£", "¥"].index(st.session_state["settings"]["currency"]))
        
        st.markdown("### Goals")
        s_goal = st.number_input("Savings Goal Cap", value=st.session_state["settings"]["savings_goal"], step=1000.0)

        if st.button("Save Settings", type="primary"):
            st.session_state["settings"]["user_name"] = u_name
            st.session_state["settings"]["user_email"] = u_email
            st.session_state["settings"]["currency"] = u_curr
            st.session_state["settings"]["savings_goal"] = s_goal
            st.success("Settings updated successfully!")
            st.rerun()

    with col2:
        st.markdown("### Appearance")
        dark_toggle = st.toggle("Enable Dark Mode", value=st.session_state["dark_mode"])
        if dark_toggle != st.session_state["dark_mode"]:
            st.session_state["dark_mode"] = dark_toggle
            st.rerun()

# ==========================================
# 7. MAIN ROUTER
# ==========================================
page_map = {
    "Dashboard": render_dashboard_page,
    "AI Chat": render_ai_chat_page,
    "Calendar": render_calendar_page,
    "Transactions": render_transactions_page,
    "Budgets": render_budget_page,
    "Reports": render_reports_page,
    "Rewards": render_rewards_page,
    "Settings": render_settings_page,
}

# Execute active page function
page_map.get(st.session_state["page"], render_dashboard_page)()
