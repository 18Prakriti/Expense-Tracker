import calendar
from datetime import date, datetime, timedelta
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. PAGE CONFIG & UI STYLING
# ==========================================
st.set_page_config(
    page_title="Lumen - AI Expense Tracker", layout="wide"
)

st.markdown(
    """
<style>
    /* Clean Top Padding */
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 2rem !important;
    }

    .stApp {
        background-color: #F6F7FB !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1A202C !important;
    }

    /* Device Recommendation Banner */
    .device-banner {
        background: linear-gradient(135deg, #5B42F3 0%, #8034FF 100%);
        color: #FFFFFF;
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
    }

    .device-banner-icon {
        font-size: 1.4rem;
        flex-shrink: 0;
    }

    .device-banner-text {
        margin: 0;
        line-height: 1.4;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
    }

    [data-testid="stSidebar"] h2 {
        color: #0F172A !important;
    }

    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p {
        color: #1A202C !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaption"] {
        color: #334155 !important;
    }

    /* Make all Streamlit input labels dark & clearly visible */
    [data-testid="stWidgetLabel"] p, label, .stWidgetLabel {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    /* Button and Download Button Visibility */
    div.stButton > button, 
    div.stDownloadButton > button,
    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primary"] {
        color: #FFFFFF !important;
        background: linear-gradient(135deg, #5B42F3 0%, #7C3AED 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 12px rgba(91, 66, 243, 0.25) !important;
    }

    div.stButton > button p, 
    div.stDownloadButton > button p,
    div.stButton > button span,
    div.stDownloadButton > button span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    div.stButton > button:hover, 
    div.stDownloadButton > button:hover,
    [data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {
        color: #FFFFFF !important;
        background: linear-gradient(135deg, #4C1D95 0%, #6D28D9 100%) !important;
        transform: translateY(-1px);
    }

    .purple-text {
        background: linear-gradient(135deg, #5B42F3 0%, #8034FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Metric Cards Styling */
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        padding: 16px 20px;
        border-radius: 18px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 15px rgba(108, 93, 211, 0.03);
    }

    [data-testid="stMetricLabel"] { color: #475569 !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] { color: #0F172A !important; }

    /* Progress bar gradient */
    .progress-container {
        background: #E2E8F0;
        border-radius: 12px;
        height: 12px;
        width: 100%;
        overflow: hidden;
        margin-top: 10px;
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #5B42F3 0%, #A855F7 50%, #EC4899 100%);
    }

    div.quick-add-wrap button {
        border-radius: 20px !important;
        padding: 10px 20px !important;
    }

    /* Lumi Chat Bubble */
    .lumi-flex-container { display: flex; align-items: center; gap: 12px; }
    .lumi-bubble {
        background: #F3E8FF;
        color: #3B0764;
        font-size: 0.85rem;
        font-weight: 700;
        padding: 10px 16px;
        border-radius: 16px 16px 16px 2px;
        border: 1px solid #DDD6FE;
        box-shadow: 0 2px 8px rgba(108, 93, 211, 0.08);
    }

    .dash-card-title { font-size: 1.1rem; font-weight: 800; color: #0F172A; margin: 0; }
    .dash-card-sub { color: #475569; font-size: 0.82rem; font-weight: 600; margin-top: 2px; margin-bottom: 12px; }

    /* AI Chat Container */
    .ai-chat-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .ai-chat-container h1, 
    .ai-chat-container h2, 
    .ai-chat-container p {
        color: #0F172A !important;
    }

    /* ================= CALENDAR TAB SPECIFIC STYLES ================= */
    .cal-grid-header {
        text-align: center;
        font-size: 12px;
        font-weight: 700;
        color: #A0AEC0;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div[data-testid="stHorizontalBlock"] {
        margin-bottom: 12px !important;
    }

    div[data-testid="stColumn"] {
        position: relative !important;
    }

    .cal-day-box {
        background-color: #FFFFFF;
        border: 1px solid #F0F0F5;
        border-radius: 16px;
        height: 125px;
        padding: 12px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease;
        box-sizing: border-box;
    }

    .cal-day-box.card-saved {
        background-color: #E1F9E9 !important;
        border-color: #A3E635 !important;
    }
    .cal-day-box.card-normal {
        background-color: #FEF9C3 !important;
        border-color: #FDE047 !important;
    }
    .cal-day-box.card-over {
        background-color: #FFECEC !important;
        border-color: #FCA5A5 !important;
    }

    .cal-day-num {
        font-size: 13px;
        font-weight: 600;
        color: #4A5568;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .tx-count-badge {
        font-size: 10px;
        background: rgba(255, 255, 255, 0.7);
        color: #2D3748;
        padding: 2px 7px;
        border-radius: 10px;
        font-weight: 600;
        backdrop-filter: blur(4px);
    }

    .card-amount-container {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-grow: 1;
    }

    .card-amount-text {
        font-size: 15px;
        font-weight: 800;
        letter-spacing: -0.3px;
    }

    .text-saved { color: #27AE60 !important; }
    .text-normal { color: #854D0E !important; }
    .text-over { color: #E74C3C !important; }

    .cal-empty-box {
        background: #F8F9FE;
        border-radius: 16px;
        height: 125px;
    }

    /* INVISIBLE OVERLAY BUTTON */
    div[class*="st-key-overlay_"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 125px !important;
        z-index: 10 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[class*="st-key-overlay_"] button {
        width: 100% !important;
        height: 125px !important;
        opacity: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }

    div[data-testid="stColumn"]:hover .cal-day-box {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(108, 93, 211, 0.22) !important;
        border: 2px solid #6C5DD3 !important;
    }

    .cal-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 24px;
        margin-top: 25px;
        padding: 18px;
        background: #FFFFFF;
        border-radius: 14px;
        border: 1px solid #EDF2F7;
        justify-content: flex-start;
    }
    .legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #718096; font-weight: 500; }
    .dot { width: 10px; height: 10px; border-radius: 50%; }

    /* Transactions Row Styling */
    .tx-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #E2E8F0; }
    .tx-avatar {
        width: 38px; height: 38px; border-radius: 50%; color: white; font-weight: 800;
        display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;
    }
    .tx-row-title { font-weight: 700; color: #0F172A; font-size: 0.9rem; }
    .tx-row-sub { color: #475569; font-size: 0.8rem; font-weight: 500; }
    .tx-row-amt { margin-left: auto; font-weight: 800; font-size: 0.9rem; }

    .insight-tips { margin-top: 10px; padding-left: 18px; }
    .insight-tips li { color: #1E293B; font-size: 0.88rem; margin-bottom: 8px; line-height: 1.5; }

    /* Badges / Rewards */
    .badge-card {
        background: #FFFFFF;
        border-radius: 18px; padding: 24px; text-align: center;
        border: 1px solid #CBD5E1; box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }
    .badge-emoji { font-size: 40px; margin-bottom: 10px; }
    .badge-locked { opacity: 0.55; filter: grayscale(1); }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. SHARED DATA & SESSION STATE
# ==========================================
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

    # Target Date Parser
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
    chat_container = st.container(height=300)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("Type your transaction...", key="dialog_chat_input"):
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        _, reply = parse_and_add_transaction(user_input)
        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
        st.rerun()

@st.dialog("📅 Daily Transactions")
def show_day_details_modal(selected_date):
    st.write(f"### Transactions for {selected_date.strftime('%B %d, %Y')}")
    day_txs = st.session_state["data"][st.session_state["data"]["Date"] == selected_date]

    if day_txs.empty:
        st.info("No transactions logged for this day.")
        return

    curr = st.session_state["settings"]["currency"]
    for idx, row in day_txs.iterrows():
        c_desc, c_amt, c_del = st.columns([3, 2, 1])
        sign = "+" if row["Type"] == "Income" else "-"
        color = "#16A34A" if row["Type"] == "Income" else "#DC2626"

        c_desc.markdown(f"**{row['Category']}**  \n<small style='color:#475569;'>{row.get('Note', '')}</small>", unsafe_allow_html=True)
        c_amt.markdown(f"<span style='color:{color}; font-weight:800;'>{sign}{curr}{row['Amount']:,.2f}</span>", unsafe_allow_html=True)

        if c_del.button("🗑️", key=f"del_{idx}"):
            st.session_state["data"] = st.session_state["data"].drop(idx).reset_index(drop=True)
            st.rerun()
        st.divider()

# ==========================================
# 5. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    # Sidebar Header with Logo
    try:
        st.image("assets/Lumen.jpeg", width=200)
    except:
        try:
            st.image("Lumen.jpeg", width=200)
        except:
            st.markdown("## 💜 **Lumen**")
    
    st.markdown("## 💜 **Lumen**", unsafe_allow_html=True)
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
daily_threshold = (st.session_state["settings"]["income_goal"]) / 30

# ==========================================
# 6. FULL PAGE RENDERERS
# ==========================================

def render_dashboard_page():
    col_header, col_quickadd = st.columns([4, 1], vertical_alignment="top")

    with col_header:
        head_text_col, head_mascot_col = st.columns([3.5, 1.2], vertical_alignment="top")
        with head_text_col:
            st.markdown(
                f"""
                <div style='margin-top: 10px;'>
                    <h1 style='margin:0; padding:0; font-size:2.4rem; font-weight:800; color:#0F172A; line-height: 1.2;'>
                        Hi {st.session_state["settings"]["user_name"]}, <br>
                        <span class='purple-text'>here's your money in motion.</span>
                    </h1>
                    <p style='color:#334155; margin-top:8px; font-size:1rem; font-weight:600;'>
                        Every smart choice builds your bigger tomorrow. 💜
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with head_mascot_col:
            try:
                st.image("Lumi.png", width=160)
            except Exception:
                try:
                    st.image("assets/Lumi.png", width=160)
                except Exception:
                    st.write("🍋 *(Lumi.png)*")

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
                <strong style="font-size: 0.95rem; color: #0F172A;">🌱 Savings Goal Progress</strong>
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
                xaxis=dict(showgrid=False, tickfont=dict(color="#334155", size=12)),
                yaxis=dict(showgrid=True, gridcolor="#CBD5E1", tickfont=dict(color="#334155", size=12)),
            )
            st.plotly_chart(fig_week, use_container_width=True, config={"displayModeBar": False})

            # Bottom Left Mascot & Speech
            lumi_mascot_col, lumi_msg_col = st.columns([1, 3.5], vertical_alignment="center")
            with lumi_mascot_col:
                try:
                    st.image("assets/Dashboard.png", width=110)
                except:
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
                    hole=0.65, marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                    textinfo="none", showlegend=False
                ))
                fig_donut.update_layout(height=160, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

                legend_html = "".join(
                    f"""<div style="display:inline-flex; align-items:center; gap:6px; font-size:12px; font-weight:600; color:#1E293B; margin-right:12px; margin-bottom:6px;"><div style="width:10px; height:10px; border-radius:50%; background:{CATEGORY_COLORS.get(c, '#64748B')};"></div>{c}</div>"""
                    for c in cat_totals.index
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
            head_col, lumi_col = st.columns([3, 1], vertical_alignment="center")
            
            with head_col:
                st.markdown(
                    '<p class="dash-card-sub" style="color:#4C1D95; font-weight:800; margin:0;">✨ AI INSIGHTS</p>'
                    '<p class="dash-card-title">Lumi\'s tips 🍋</p>',
                    unsafe_allow_html=True
                )
            
            with lumi_col:
                try:
                    st.image("assets/LumiCoach.png", width=65)
                except:
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
    st.markdown("# 💬 AI Chat")
    st.caption("Tell Lumi what you spent or earned in plain language.")

    # Add container with border for chat
    with st.container(border=True):
        st.markdown('<div class="ai-chat-container">', unsafe_allow_html=True)
        
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
    col_title, col_actions = st.columns([3, 1])

    with col_title:
        st.markdown(
            """
            <div style='text-align: left;'>
                <h1 style='margin: 0; padding: 0; font-size: 2.3rem; font-weight: 800; color: #1A202C;'>
                    <span class='purple-text'>Spending Map</span>
                </h1>
                <p style='color:#718096; margin-top: 4px; font-size:0.95rem; font-weight: 500;'>
                    See where your money goes, day by day.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_actions:
        st.markdown('<div class="quick-add-wrap">', unsafe_allow_html=True)
        if st.button("+ Quick Add", use_container_width=True, key="quick_add_cal"):
            quick_add_chatbot()
        st.markdown('</div>', unsafe_allow_html=True)

    c1, _, _ = st.columns([1.8, 3, 5])
    view_month_name = c1.selectbox(
        "Month",
        list(calendar.month_name)[1:],
        index=today.month - 1,
        label_visibility="collapsed",
    )
    month_idx = list(calendar.month_name).index(view_month_name)

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(today.year, month_idx)

    # Weekday headers
    h_cols = st.columns(7)
    for i, d in enumerate(["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]):
        h_cols[i].markdown(
            f"<div class='cal-grid-header'>{d}</div>", unsafe_allow_html=True
        )

    # Render Calendar Days
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
                    if st.button(" ", key=f"overlay_{cur_date}"):
                        show_day_details_modal(cur_date)

    # Footer Legend
    st.markdown(
        """<div class="cal-legend">
            <div class="legend-item"><div class="dot" style="background:#27AE60"></div>Net Saved</div>
            <div class="legend-item"><div class="dot" style="background:#FEF9C3; border: 1px solid #CA8A04;"></div>Normal Spending</div>
            <div class="legend-item"><div class="dot" style="background:#E74C3C"></div>Over Threshold</div>
            <div class="legend-item"><div class="dot" style="background:#EDF2F7; border: 1px solid #A0AEC0;"></div>No Activity</div>
        </div>""",
        unsafe_allow_html=True,
    )

def render_transactions_page():
    st.markdown("# 📑 Transactions")
    st.caption("Complete history of all logged income and expenses.")
    st.dataframe(st.session_state["data"], use_container_width=True)

def render_budgets_page():
    st.markdown("# 🎯 Category Budgets")
    st.markdown("<p style='color:#334155; font-weight:600; font-size:1rem; margin-bottom: 20px;'>Adjust monthly limits for each spending category.</p>", unsafe_allow_html=True)
    
    for cat, val in st.session_state["budgets"].items():
        st.session_state["budgets"][cat] = st.number_input(
            f"Budget limit for {cat}", 
            value=val, 
            step=100.0,
            key=f"budget_input_{cat}"
        )

def render_reports_page():
    st.markdown("# 📊 Financial Reports & Analytics")
    st.caption("In-depth analysis of your financial performance.")

    # High-level Summary Metrics
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Total Income", f"{curr_symbol}{month_income:,.2f}")
    r2.metric("Total Expense", f"{curr_symbol}{month_spend:,.2f}")
    r3.metric("Net Savings", f"{curr_symbol}{total_balance:,.2f}")
    savings_rate = (total_balance / month_income * 100) if month_income > 0 else 0
    r4.metric("Savings Rate", f"{savings_rate:.1f}%")

    st.write("")

    # Visual Charts Section
    col1, col2 = st.columns([1, 1], vertical_alignment="top")

    with col1:
        with st.container(border=True):
            st.markdown('<p class="dash-card-title">Income vs. Expenses</p><p class="dash-card-sub">Comparison overview</p>', unsafe_allow_html=True)
            fig_cf = go.Figure([
                go.Bar(name='Income', x=['Current Month'], y=[month_income], marker_color='#16A34A', width=0.3),
                go.Bar(name='Expense', x=['Current Month'], y=[month_spend], marker_color='#DC2626', width=0.3)
            ])
            fig_cf.update_layout(
                height=260,
                barmode='group',
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(tickfont=dict(color="#334155", size=12)),
                yaxis=dict(showgrid=True, gridcolor="#CBD5E1", tickfont=dict(color="#334155", size=12))
            )
            st.plotly_chart(fig_cf, use_container_width=True, config={"displayModeBar": False})

    with col2:
        with st.container(border=True):
            st.markdown('<p class="dash-card-title">Top Expense Categories</p><p class="dash-card-sub">Spending concentration</p>', unsafe_allow_html=True)
            cat_df = this_month_df[this_month_df["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()
            if not cat_df.empty:
                fig_bar = go.Figure(go.Bar(
                    x=cat_df["Amount"],
                    y=cat_df["Category"],
                    orientation='h',
                    marker=dict(color='#5B42F3')
                ))
                fig_bar.update_layout(
                    height=260,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis=dict(tickfont=dict(color="#334155", size=12)),
                    xaxis=dict(showgrid=True, gridcolor="#CBD5E1", tickfont=dict(color="#334155", size=12))
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No expenses logged for this month yet.")

    st.write("")

    # Export Data Section
    with st.container(border=True):
        st.markdown('<p class="dash-card-title">📥 Export Financial Data</p><p class="dash-card-sub">Download your transaction history as CSV</p>', unsafe_allow_html=True)
        csv_data = df_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV Report",
            data=csv_data,
            file_name=f"lumen_report_{today.strftime('%Y_%m_%d')}.csv",
            mime="text/csv",
        )

def render_rewards_page():
    st.markdown("# 🎁 Rewards & Badges")
    c1, c2 = st.columns(2, vertical_alignment="top")
    with c1:
        with st.container(border=True):
            st.markdown('<div style="text-align:center;"><div class="badge-emoji">🌟</div><h3 style="color:#0F172A;">Consistent Tracker</h3><p style="color:#334155;">Logged expenses 7 days in a row!</p></div>', unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown('<div style="text-align:center;" class="badge-locked"><div class="badge-emoji">🏆</div><h3 style="color:#0F172A;">Saver Master</h3><p style="color:#334155;">Keep overall spending below budget!</p></div>', unsafe_allow_html=True)

def render_settings_page():
    st.markdown("# ⚙️ Settings")
    s = st.session_state["settings"]
    s["user_name"] = st.text_input("Name", s["user_name"])
    s["user_email"] = st.text_input("Email", s["user_email"])
    s["currency"] = st.text_input("Currency Symbol", s["currency"])
    s["savings_goal"] = st.number_input("Monthly Savings Goal Target", value=s["savings_goal"], step=1000.0)

# ==========================================
# 7. ROUTER (WIRED TO FULL FUNCTIONS)
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
