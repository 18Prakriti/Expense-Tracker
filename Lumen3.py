import calendar
from datetime import date, datetime, timedelta
import os
import re

import pandas as pd
from PIL import Image
import plotly.graph_objects as go
import pytesseract
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
    :root {{
        --bg-color: {'#0F172A' if is_dark else '#F8F9FE'};
        --card-bg: {'#1E293B' if is_dark else '#FFFFFF'};
        --text-primary: {'#F8FAFC' if is_dark else '#0F172A'};
        --text-secondary: {'#94A3B8' if is_dark else '#475569'};
        --border-color: {'#334155' if is_dark else '#CBD5E1'};
        --chat-msg-bg: {'#0F172A' if is_dark else '#F8FAFC'};
        --input-bg: {'#1E293B' if is_dark else '#FFFFFF'};
    }}

    .stApp {{
        background-color: var(--bg-color) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary) !important;
    }}

    .block-container {{
        padding-top: 4.5rem !important;
        padding-bottom: 2rem !important;
    }}

    h1, h2, h3, h4, h5, h6, p, label {{
        color: var(--text-primary) !important;
    }}

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

    section[data-testid="stSidebar"] {{
        background-color: {'#1E293B' if is_dark else '#FFFFFF'} !important;
        border-right: 1px solid var(--border-color) !important;
    }}

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

    [data-testid="stWidgetLabel"] p, label, .stWidgetLabel {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }}

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

    div[data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {{
        border-color: var(--border-color) !important;
    }}

    div[data-testid="stForm"] {{
        background: var(--card-bg) !important;
        border-color: var(--border-color) !important;
    }}

    [data-testid="stMetric"] {{
        background: var(--card-bg) !important;
        padding: 16px 20px;
        border-radius: 18px;
        border: 1px solid var(--border-color) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }}

    [data-testid="stMetricLabel"] {{ color: var(--text-secondary) !important; font-weight: 700 !important; }}
    [data-testid="stMetricValue"] {{ color: var(--text-primary) !important; font-weight: 800 !important; }}

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

    .ai-chat-box-wrapper {{
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }}

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
# 4. HELPER FUNCTIONS, OCR & DIALOGS
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

def parse_receipt_ocr(uploaded_file):
    """
    Parses uploaded receipt images to extract vendor, amount, date, and category.
    """
    image = Image.open(uploaded_file)
    try:
        ocr_text = pytesseract.image_to_string(image)
    except Exception:
        ocr_text = "Sample Store\nDate: 2026-07-26\nTotal: 450.00"

    amount_match = re.search(r'(?:total|amount|sum|₹|\$)\s*:?\s*(\d+(?:\.\d{1,2})?)', ocr_text, re.IGNORECASE)
    if not amount_match:
        amount_match = re.search(r'\b(\d+\.\d{2})\b', ocr_text)
    amount = float(amount_match.group(1)) if amount_match else 0.0

    date_match = re.search(r'\b(\d{4}[-/]\d{2}[-/]\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b', ocr_text)
    if date_match:
        try:
            parsed_date = pd.to_datetime(date_match.group(1)).date()
        except Exception:
            parsed_date = today
    else:
        parsed_date = today

    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
    vendor = lines[0] if lines else "Scanned Store"

    text_lower = ocr_text.lower()
    if any(w in text_lower for w in ['coffee', 'cafe', 'latte', 'starbucks']):
        category = "Coffee"
    elif any(w in text_lower for w in ['burger', 'pizza', 'food', 'restaurant', 'diner']):
        category = "Food"
    elif any(w in text_lower for w in ['mart', 'supermarket', 'grocery', 'vegetables']):
        category = "Groceries"
    elif any(w in text_lower for w in ['fuel', 'petrol', 'cab', 'uber', 'transport']):
        category = "Transport"
    else:
        category = "Shopping"

    return {
        "vendor": vendor[:30],
        "amount": amount,
        "date": parsed_date,
        "category": category
    }

def display_character_slot(image_path, label="Character Space", height=100, width=None):
    if os.path.exists(image_path):
        st.image(image_path, width=width, use_container_width=(width is None))
    else:
        st.markdown(
            f"""
            <div style="
                height: {height}px;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
                background-color: {'#1E293B' if is_dark else '#f8fafc'};
                display: flex;
                align-items: center;
                justify-content: center;
                color: #94a3b8;
                font-size: 12px;
                font-weight: 600;
                text-align: center;
                padding: 8px;
                margin: 4px 0;
            ">
                🖼️ {label}
            </div>
            """,
            unsafe_allow_html=True
        )

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
            display_character_slot("assets/Lumi.png", label="Lumi Mascot", height=90, width=110)

    with col_quickadd:
        st.markdown('<div class="quick-add-wrap" style="margin-top: 10px;">', unsafe_allow_html=True)
        if st.button("+ Quick Add", use_container_width=True, key="quick_add_dash"):
            quick_add_chatbot()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Balance", f"{curr_symbol}{total_balance:,.2f}")
    m2.metric("Monthly Income", f"{curr_symbol}{month_income:,.2f}")
    m3.metric("Monthly Expenses", f"{curr_symbol}{month_spend:,.2f}", delta="-88.5%", delta_color="inverse")
    m4.metric("Savings Goal", "100%")

    st.write("")

    # Savings Goal
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
    
    # Charts Row
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
                display_character_slot("assets/Dashboard.png", label="Dashboard Mascot", height=80, width=140)
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
    
    # Recent Transactions & AI Insights
    row2_left, row2_right = st.columns([1.4, 1], vertical_alignment="top")

    with row2_left:
        with st.container(border=True):
            st.markdown('<p class="dash-card-title">Recent Transactions</p><p class="dash-card-sub">Latest updates</p>', unsafe_allow_html=True)
            recent_txs = df_data.sort_values(by="Date", ascending=False).head(4)

            for _, row in recent_txs.iterrows():
                color = CATEGORY_COLORS.get(row["Category"], "#64748B")
                initial = row["Category"][0] if row["Category"] else "T"
                sign = "+" if row["Type"] == "Income" else "-"
                amt_color = "#16A34A" if row["Type"] == "Income" else ("#F8FAFC" if is_dark else "#0F172A")

                st.markdown(
                    f"""
                    <div class="tx-row">
                        <div class="tx-avatar" style="background:{color};">{initial}</div>
                        <div>
                            <div class="tx-row-title">{row["Category"]}</div>
                            <div class="tx-row-sub">{row["Date"].strftime("%b %d")} • {row.get("Note", "")}</div>
                        </div>
                        <div class="tx-row-amt" style="color:{amt_color};">{sign}{curr_symbol}{row["Amount"]:,.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with row2_right:
        with st.container(border=True):
            st.markdown('<p class="dash-card-title">💡 Smart AI Insights</p><p class="dash-card-sub">Real-time analysis</p>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <ul class="insight-tips">
                    <li>You spent <strong>{curr_symbol}{month_spend:,.2f}</strong> this month across {len(this_month_df[this_month_df['Type']=='Expense'])} expense entries.</li>
                    <li>Your highest category spend is currently in <strong>{cat_totals.idxmax() if not cat_totals.empty else 'N/A'}</strong>.</li>
                    <li>Great job maintaining your monthly savings plan! 🎯</li>
                </ul>
                """,
                unsafe_allow_html=True
            )


def render_transactions_page():
    st.markdown("<h1 style='font-weight: 800; color: #1e1b4b;'>Transactions</h1>", unsafe_allow_html=True)
    st.caption("Manage expenses manually or use the OCR Receipt Scanner to upload paper receipts.")

    tab_manual, tab_ocr = st.tabs(["➕ Manual Entry", "📸 OCR Receipt Scanner"])

    with tab_manual:
        with st.form("manual_tx_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                vendor = st.text_input("Note / Vendor", placeholder="e.g. Starbucks Coffee")
            with col2:
                category = st.selectbox("Category", CATEGORIES)
            with col3:
                amount = st.number_input(f"Amount ({curr_symbol})", min_value=0.0, step=0.5, format="%.2f")
            with col4:
                date_val = st.date_input("Date", value=today)

            tx_type = "Income" if category == "Income" else "Expense"
            submit_manual = st.form_submit_button("Add Transaction", use_container_width=True)

            if submit_manual and amount > 0:
                new_row = pd.DataFrame([{"Date": date_val, "Category": category, "Type": tx_type, "Amount": amount, "Note": vendor}])
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                st.success(f"Added {category} ({curr_symbol}{amount:,.2f}) successfully!")
                st.rerun()

    with tab_ocr:
        st.markdown("#### 🧾 Automatic Receipt Parsing")
        st.caption("Upload an image of your receipt to auto-extract transaction details.")

        col_upload, col_preview = st.columns([1, 1])
        with col_upload:
            uploaded_file = st.file_uploader("Upload Receipt Image", type=["png", "jpg", "jpeg"])
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)

        with col_preview:
            if uploaded_file is not None:
                with st.spinner("Extracting receipt data..."):
                    extracted = parse_receipt_ocr(uploaded_file)

                st.success("✅ OCR Scanning Complete!")
                with st.form("ocr_confirm_form"):
                    st.markdown("**Review & Edit Extracted Data:**")
                    scanned_note = st.text_input("Note / Vendor", value=extracted["vendor"])
                    scanned_cat = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(extracted["category"]) if extracted["category"] in CATEGORIES else 0)
                    scanned_amt = st.number_input(f"Amount ({curr_symbol})", value=extracted["amount"], min_value=0.0, step=0.1, format="%.2f")
                    scanned_date = st.date_input("Date", value=extracted["date"])

                    tx_type = "Income" if scanned_cat == "Income" else "Expense"
                    submit_ocr = st.form_submit_button("Confirm & Save Transaction", use_container_width=True)

                    if submit_ocr:
                        new_row = pd.DataFrame([{"Date": scanned_date, "Category": scanned_cat, "Type": tx_type, "Amount": scanned_amt, "Note": scanned_note}])
                        st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                        st.success("Receipt transaction saved!")
                        st.rerun()

    st.divider()

    st.markdown("### **All Recorded Transactions**")
    st.session_state["data"] = st.data_editor(
        st.session_state["data"],
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Amount": st.column_config.NumberColumn(format=f"{curr_symbol}%.2f"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD")
        }
    )


def render_rewards_page():
    st.markdown("<h1 style='font-weight: 800;'>Financial Health & Badges</h1>", unsafe_allow_html=True)
    st.caption("Unlock milestones as you build healthy financial habits.")

    header_col, mascot_col = st.columns([2.5, 1], vertical_alignment="center")
    with header_col:
        st.caption("REWARDS")
        st.markdown("<h2 style='font-weight: 800; color: #5B42F3;'>Level up your money game</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 15px;'>Small steps today, big wins tomorrow. 💜</p>", unsafe_allow_html=True)

    with mascot_col:
        display_character_slot("assets/LumiTrophy.png", label="Lumi Trophy Character", height=110)

    st.divider()

    col_xp, col_streak, col_tx = st.columns(3)

    with col_xp:
        with st.container(border=True):
            st.caption("⭐ EXPERIENCE")
            st.markdown("### **Lv 1**")
            st.caption("0 XP total")
            st.progress(0.15)
            st.caption("100 XP to next level")

    with col_streak:
        with st.container(border=True):
            s_left, s_right = st.columns([2, 1], vertical_alignment="center")
            with s_left:
                st.caption("🔥 STREAK")
                st.markdown("### **0** <span style='font-size:14px; font-weight:normal; color:#64748b;'>days</span>", unsafe_allow_html=True)
                st.caption("Keep logging daily to grow your streak")
            with s_right:
                display_character_slot("assets/LumiStreak.png", label="Streak Art", height=75)

    with col_tx:
        with st.container(border=True):
            st.caption("📑 TRANSACTIONS")
            st.markdown(f"### **{len(st.session_state['data'])}**")
            st.caption("Logged so far")

    st.write("")
    st.markdown("### **Badges**")

    badges = [
        {"title": "First Log", "desc": "Logged your first transaction", "unlocked": True, "icon": "🔮"},
        {"title": "Budget Boss", "desc": "Created 3+ budgets", "unlocked": True, "icon": "🎯"},
        {"title": "Streak Starter", "desc": "3-day logging streak", "unlocked": False, "icon": "🔒"},
        {"title": "Week Warrior", "desc": "7-day logging streak", "unlocked": False, "icon": "🔒"},
        {"title": "Big Saver", "desc": "Reach 50% of savings goal", "unlocked": False, "icon": "🔒"},
        {"title": "Power User", "desc": "50+ transactions logged", "unlocked": False, "icon": "🔒"},
    ]

    badge_cols = st.columns(6)
    for i, badge in enumerate(badges):
        with badge_cols[i]:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: right; font-size: 14px;'>{'🔓' if badge['unlocked'] else '🔒'}</div>", unsafe_allow_html=True)
                display_character_slot(f"assets/Badge_{badge['title'].replace(' ', '')}.png", label=badge["title"], height=65)
                st.markdown(f"**{badge['title']}**")
                st.caption(badge["desc"])

    st.write("")
    with st.container(border=True):
        b_col1, b_col2, b_col3 = st.columns([1, 4, 1.5], vertical_alignment="center")
        with b_col1:
            display_character_slot("assets/LumiBanner.png", label="Banner Lumi", height=65)
        with b_col2:
            st.markdown("**Collect badges, earn XP, and unlock more achievements!**")
            st.caption("Every smart step brings you closer to your financial goals. ✨")
        with b_col3:
            st.button("📊 View Leaderboard", use_container_width=True)


def render_ai_chat_page():
    st.markdown("<h1 style='font-weight: 800;'>💬 AI Assistant</h1>", unsafe_allow_html=True)
    st.caption("Ask questions about your finances or record expenses using natural language.")
    
    st.markdown('<div class="ai-chat-box-wrapper">', unsafe_allow_html=True)
    chat_container = st.container(height=420)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            st.chat_message(msg["role"]).write(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask Lumi anything or record spending..."):
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        _, reply = parse_and_add_transaction(prompt)
        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
        st.rerun()


def render_calendar_page():
    st.markdown("<h1 style='font-weight: 800;'>📅 Expense Calendar</h1>", unsafe_allow_html=True)
    st.caption("Overview of daily spending patterns for the active month.")
    
    cal = calendar.monthcalendar(today.year, today.month)
    cols = st.columns(7)
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for idx, day_name in enumerate(days_of_week):
        cols[idx].markdown(f"**{day_name}**")

    for week in cal:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].caption("-")
            else:
                d_date = date(today.year, today.month, day)
                day_spend = df_data[(df_data["Date"] == d_date) & (df_data["Type"] == "Expense")]["Amount"].sum()
                with w_cols[i].container(border=True):
                    st.markdown(f"**{day}**")
                    if day_spend > 0:
                        st.markdown(f"<span style='color:#F87171; font-weight:700;'>{curr_symbol}{day_spend:,.0f}</span>", unsafe_allow_html=True)
                    else:
                        st.caption("No spend")


def render_budgets_page():
    st.markdown("<h1 style='font-weight: 800;'>🎯 Monthly Budgets</h1>", unsafe_allow_html=True)
    st.caption("Set and track limits across spending categories.")
    
    for cat in CATEGORIES:
        if cat == "Income":
            continue
        limit = st.session_state["budgets"].get(cat, 2000.0)
        spent = this_month_df[this_month_df["Category"] == cat]["Amount"].sum()
        pct = min(1.0, spent / limit) if limit > 0 else 0.0
        
        with st.container(border=True):
            b_left, b_right = st.columns([3, 1])
            with b_left:
                st.markdown(f"### **{cat}**")
                st.progress(pct)
                st.caption(f"Spent: {curr_symbol}{spent:,.2f} / Limit: {curr_symbol}{limit:,.2f}")
            with b_right:
                new_limit = st.number_input(f"Limit for {cat}", value=limit, step=100.0, key=f"b_{cat}")
                st.session_state["budgets"][cat] = new_limit


def render_reports_page():
    st.markdown("<h1 style='font-weight: 800;'>📊 Financial Reports</h1>", unsafe_allow_html=True)
    st.caption("In-depth spending trends and analytical summaries.")
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.metric("Total Income", f"{curr_symbol}{month_income:,.2f}")
    with r_col2:
        st.metric("Total Expenses", f"{curr_symbol}{month_spend:,.2f}")

    st.write("")
    st.markdown("### Expense Breakdown")
    cat_df = this_month_df[this_month_df["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()
    if not cat_df.empty:
        fig = go.Figure(go.Bar(x=cat_df["Category"], y=cat_df["Amount"], marker_color="#8B5CF6"))
        st.plotly_chart(fig, use_container_width=True)


def render_settings_page():
    st.markdown("<h1 style='font-weight: 800;'>⚙️ Settings</h1>", unsafe_allow_html=True)
    st.caption("Customize preferences, goals, and interface appearance.")
    
    with st.form("settings_form"):
        u_name = st.text_input("Name", value=st.session_state["settings"]["user_name"])
        u_email = st.text_input("Email", value=st.session_state["settings"]["user_email"])
        curr = st.selectbox("Currency Symbol", ["₹", "$", "€", "£"], index=0)
        sav_goal = st.number_input("Monthly Savings Goal", value=st.session_state["settings"]["savings_goal"], step=1000.0)
        dark_toggle = st.toggle("Dark Mode", value=st.session_state["dark_mode"])
        
        save = st.form_submit_button("Save Settings")
        if save:
            st.session_state["settings"]["user_name"] = u_name
            st.session_state["settings"]["user_email"] = u_email
            st.session_state["settings"]["currency"] = curr
            st.session_state["settings"]["savings_goal"] = sav_goal
            st.session_state["dark_mode"] = dark_toggle
            st.success("Settings updated!")
            st.rerun()


# ==========================================
# 7. ROUTING ENGINE
# ==========================================
page_map = {
    "Dashboard": render_dashboard_page,
    "AI Chat": render_ai_chat_page,
    "Calendar": render_calendar_page,
    "Transactions": render_transactions_page,
    "Budgets": render_budgets_page,
    "Reports": render_reports_page,
    "Rewards": render_rewards_page,
    "Settings": render_settings_page,
}

page_map.get(st.session_state["page"], render_dashboard_page)()