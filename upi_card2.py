import time
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Page setup
st.set_page_config(page_title="UPI vs Card — Payment Rails Infra", layout="wide")

# Styling Palette
MINT = "#1D9E75"
AMBER = "#BA7517"
RED = "#FF4B4B"
BG = "#0D1210"
PANEL = "#131A17"
LINE = "#263029"

st.markdown(
    """
    <style>
    .stApp { background-color: #0D1210; color: #E6EDE9; }
    .eyebrow { font-family: monospace; color: #4FE8A6; letter-spacing: 0.12em;
               text-transform: uppercase; font-size: 12px; margin-bottom: 4px; }
    .subtext { color: #8A968E; font-size: 15px; max-width: 750px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="eyebrow">Payment rails // live comparison & debugging lab</p>', unsafe_allow_html=True)
st.title("💳 UPI vs Card Infrastructure Simulator")
st.markdown(
    '<p class="subtext">Same amount leaving the same wallet, two completely different architectural journeys. '
    'Run a transaction to visualize node hops, or select a bug scenario to test your backend debugging skills!</p>',
    unsafe_allow_html=True,
)
st.write("")

# Nodes definitions
UPI_NODES = [
    ("Customer", "UPI app / VPA"),
    ("NPCI Switch", "Routes request"),
    ("Remitter Bank", "Debits customer"),
    ("Merchant", "Credited"),
]

CARD_NODES = [
    ("Customer", "Taps / swipes card"),
    ("POS / Gateway", "Captures txn"),
    ("Acquiring Bank", "Merchant's bank"),
    ("Card Network", "Visa / MC / RuPay"),
    ("Issuing Bank", "Approves & holds"),
    ("Merchant", "Authorized"),
]

# Helper function to render payment rail graphics
def draw_rail(nodes, color, active_upto=-1, pulse_frac=None, error_at=-1):
    n = len(nodes)
    fig, ax = plt.subplots(figsize=(9, 1.8), facecolor=PANEL)
    ax.set_facecolor(PANEL)

    # Base background line
    ax.plot([0, n - 1], [0, 0], color=LINE, linewidth=2, zorder=1)

    # Active progress line
    if active_upto >= 0:
        end_x = active_upto
        if pulse_frac is not None and active_upto < n - 1:
            end_x = active_upto + pulse_frac
        ax.plot([0, end_x], [0, 0], color=color if error_at < 0 else RED, linewidth=2.5, zorder=2)

    # Draw nodes
    for i, (label, sub) in enumerate(nodes):
        if i == error_at:
            node_color = RED
        elif i <= active_upto:
            node_color = color
        else:
            node_color = LINE

        ax.scatter([i], [0], s=140, facecolors=PANEL, edgecolors=node_color, linewidths=2, zorder=3)
        ax.text(i, 0.35, label, ha="center", va="bottom", fontsize=9, color="#E6EDE9", fontweight="bold")
        ax.text(i, -0.35, sub, ha="center", va="top", fontsize=7.5, color="#8A968E")

    # Animated pulse dot
    if pulse_frac is not None and active_upto < n - 1 and error_at < 0:
        px = active_upto + pulse_frac
        ax.scatter([px], [0], s=90, color=color, zorder=4)

    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-0.7, 0.7)
    ax.axis("off")
    fig.tight_layout(pad=0.3)
    return fig


# Dashboard Top Controls
col1, col2, col3, col4 = st.columns([1.5, 3, 1, 3])
with col1:
    amount = st.number_input("Amount (₹)", min_value=1.0, value=1000.0, step=50.0)
with col2:
    scenario = st.selectbox("Scenario Execution", [
        "Normal Transaction",
        "UPI Bug: The Reverse Heist",
        "UPI Bug: Race to the Scanner",
        "Card Bug: Interchange Fee Reversal",
        "Card Bug: The Missing Penny"
    ])
with col3:
    st.write("")
    st.write("")
    run = st.button("Run ▶️", type="primary")
with col4:
    status = st.empty()
    if not run:
        status.markdown("`Status: Idle`")

st.write("")

# Visual Render Areas
st.markdown("**UPI Rail (3 Hops)**")
upi_chart = st.empty()
upi_meta = st.empty()
fig_init_upi = draw_rail(UPI_NODES, MINT)
upi_chart.pyplot(fig_init_upi)
plt.close(fig_init_upi) # Avoid memory leak
upi_meta.caption("3 hops · ~2-3 sec settlement")

st.markdown("**Debit / Credit Card Rail (6 Hops)**")
card_chart = st.empty()
card_meta = st.empty()
fig_init_card = draw_rail(CARD_NODES, AMBER)
card_chart.pyplot(fig_init_card)
plt.close(fig_init_card) # Avoid memory leak
card_meta.caption("6 hops · authorization instant, settlement T+1/T+2")

st.write("")
st.markdown("**Transaction Terminal Log**")
log_box = st.empty()
log_lines = ["$ system ready. click 'Run' to execute scenario..."]
log_box.code("\n".join(log_lines), language=None)

def append_log(line):
    log_lines.append(line)
    log_box.code("\n".join(log_lines), language=None)

# ==========================
# SCENARIO EXECUTION ENGINE
# ==========================
if run:
    log_lines.clear()
    append_log(f"$ initiating transaction of ₹{amount:,.2f} | Scenario: {scenario}")

    # --- UPI RUNNER ---
    status.markdown("`Running UPI Rail...`")

    if scenario == "UPI Bug: The Reverse Heist":
        # Animate up to NPCI Switch, then fail at Remitter Bank
        for i in range(2):
            fig = draw_rail(UPI_NODES, MINT, active_upto=i)
            upi_chart.pyplot(fig)
            plt.close(fig)
            time.sleep(0.2)

        fig_err = draw_rail(UPI_NODES, MINT, active_upto=2, error_at=2)
        upi_chart.pyplot(fig_err)
        plt.close(fig_err)

        append_log("[INFO] Initiating UPI P2M Transfer...")
        append_log("[INFO] Remitter: student@ybl (Bal: ₹1,000.00) | Payee: canteen@sbi (Bal: ₹5,000.00)")
        append_log("[INFO] Validating UPI PIN... -> SUCCESS")
        time.sleep(0.3)
        neg_amount = -amount
        append_log(f"[INFO] Payload Intercepted: Amount = ₹{neg_amount:.2f}")
        append_log("[INFO] Executing: remitter_balance -= amount")
        append_log(f"[INFO] New Remitter Balance: ₹{1000 - neg_amount:.2f}")
        append_log("[INFO] Executing: payee_balance += amount")
        append_log(f"[INFO] New Payee Balance: ₹{5000 + neg_amount:.2f}")
        append_log("[CRITICAL FAIL] Merchant Alert: Balance decreased after receiving payment!")

    elif scenario == "UPI Bug: Race to the Scanner":
        for i in range(3):
            fig = draw_rail(UPI_NODES, MINT, active_upto=i)
            upi_chart.pyplot(fig)
            plt.close(fig)
            time.sleep(0.2)

        fig_err = draw_rail(UPI_NODES, MINT, active_upto=3, error_at=3)
        upi_chart.pyplot(fig_err)
        plt.close(fig_err)

        append_log("[THREAD A] Fetching Order #992 status...")
        append_log("[THREAD B] Fetching Order #992 status...")
        time.sleep(0.3)
        append_log("[THREAD A] Order #992 status: PENDING -> Debiting ₹" + f"{amount:.2f}")
        append_log("[THREAD B] Order #992 status: PENDING -> Debiting ₹" + f"{amount:.2f}")
        time.sleep(0.3)
        append_log("[THREAD A] Deduction SUCCESS -> Order marked PAID.")
        append_log("[THREAD B] Deduction SUCCESS -> Order marked PAID.")
        append_log("[CRITICAL FAIL] Double-spend anomaly! Order paid twice without DB lock.")

    else:
        # Normal UPI Animation
        t0 = time.time()
        for i in range(len(UPI_NODES) - 1):
            append_log(f"[UPI] {UPI_NODES[i][0]} → {UPI_NODES[i+1][0]}")
            for f in (0.34, 0.67, 1.0):
                fig = draw_rail(UPI_NODES, MINT, active_upto=i, pulse_frac=f)
                upi_chart.pyplot(fig)
                plt.close(fig)
                time.sleep(0.04)
            fig = draw_rail(UPI_NODES, MINT, active_upto=i + 1)
            upi_chart.pyplot(fig)
            plt.close(fig)

        upi_time = time.time() - t0
        append_log(f"[UPI] Approved in {upi_time:.1f}s — funds settled near-instantly")
        upi_meta.caption(f"3 hops · approved in {upi_time:.1f}s")

    time.sleep(0.3)

    # --- CARD RUNNER ---
    status.markdown("`Running Card Rail...`")

    if scenario == "Card Bug: Interchange Fee Reversal":
        for i in range(2):
            fig = draw_rail(CARD_NODES, AMBER, active_upto=i)
            card_chart.pyplot(fig)
            plt.close(fig)
            time.sleep(0.2)

        fig_err = draw_rail(CARD_NODES, AMBER, active_upto=2, error_at=2)
        card_chart.pyplot(fig_err)
        plt.close(fig_err)

        append_log("[CARD] Customer → POS / Gateway")
        append_log(f"[INFO] Gateway MDR Fee (2%): ₹{amount * 0.02:.2f}")
        append_log("[INFO] Logic Executed: settlement_amount = principal + fee")
        append_log(f"[INFO] Calculated Settlement: ₹{amount + (amount * 0.02):.2f}")
        append_log("[CRITICAL FAIL] Acquirer Rejection: settlement_exceeds_principal")

    elif scenario == "Card Bug: The Missing Penny":
        for i in range(5):
            fig = draw_rail(CARD_NODES, AMBER, active_upto=i)
            card_chart.pyplot(fig)
            plt.close(fig)
            time.sleep(0.15)

        fig_err = draw_rail(CARD_NODES, AMBER, active_upto=5, error_at=5)
        card_chart.pyplot(fig_err)
        plt.close(fig_err)

        append_log(f"[INFO] Splitting Bill of ₹{amount:.2f} evenly across 3 cards...")
        split = round(amount / 3, 2)
        collected = split * 3
        append_log(f"[INFO] Calculated per-person charge: ₹{split:.2f}")
        append_log(f"[INFO] Total Collected across 3 cards: ₹{collected:.2f}")
        diff = round((amount - collected) * 100)
        
        if diff != 0:
            append_log(f"[CRITICAL FAIL] Reconciliation Error: Ledger off by {abs(diff)} paise!")
        else:
            append_log("[WARN] Selected amount divides cleanly by 3. Try ₹1000.00 to trigger the rounding bug!")

    else:
        # Normal Card Animation
        t0 = time.time()
        for i in range(len(CARD_NODES) - 1):
            append_log(f"[CARD] {CARD_NODES[i][0]} → {CARD_NODES[i+1][0]}")
            for f in (0.34, 0.67, 1.0):
                fig = draw_rail(CARD_NODES, AMBER, active_upto=i, pulse_frac=f)
                card_chart.pyplot(fig)
                plt.close(fig)
                time.sleep(0.04)
            fig = draw_rail(CARD_NODES, AMBER, active_upto=i + 1)
            card_chart.pyplot(fig)
            plt.close(fig)

        card_time = time.time() - t0
        mdr = amount * 0.018
        append_log(f"[CARD] Authorized in {card_time:.1f}s — batch settlement T+1/T+2")
        append_log(f"$ Card MDR fee on this transaction ≈ ₹{mdr:.2f} (1.8%), UPI MDR = ₹0")
        card_meta.caption(f"6 hops · authorized in {card_time:.1f}s, settles T+1/T+2")

    append_log("$ execution finished.")
    status.markdown("`Status: Complete`")

# ==========================
# CODE INSPECTOR (EDUCATIONAL)
# ==========================
st.write("")
if scenario != "Normal Transaction":
    with st.expander("🔍 Inspect Vulnerable Backend Code"):
        if scenario == "UPI Bug: The Reverse Heist":
            st.code("""
# VULNERABLE CODE: Missing input validation for negative numbers
def process_upi_transfer(remitter_vpa, payee_vpa, amount):
    # BUG: Forgot to validate `if amount <= 0:`
    remitter.balance -= amount  # 1000 - (-1000) = 2000
    payee.balance += amount     # 5000 + (-1000) = 4000
            """, language="python")
        elif scenario == "UPI Bug: Race to the Scanner":
            st.code("""
# VULNERABLE CODE: Missing database lock / atomic transaction
def handle_payment_webhook(order_id, amount):
    order = db.get_order(order_id)
    if order.status == "PENDING":
        # Race condition occurs here if two requests hit simultaneously!
        db.deduct_wallet(order.user_id, amount)
        order.status = "PAID"
        db.save(order)
            """, language="python")
        elif scenario == "Card Bug: Interchange Fee Reversal":
            st.code("""
# VULNERABLE CODE: Incorrect mathematical operation on MDR fee
def calculate_settlement(principal_amount, fee_rate=0.02):
    fee = principal_amount * fee_rate
    # BUG: Adding fee instead of subtracting from merchant payout!
    settlement_payout = principal_amount + fee 
    return settlement_payout
            """, language="python")
        elif scenario == "Card Bug: The Missing Penny":
            st.code("""
# VULNERABLE CODE: Floating point division & premature rounding
def split_bill(total_amount, num_people=3):
    # BUG: Rounding each split causes lost fractions of a cent/paise
    per_person = round(total_amount / num_people, 2)
    return [per_person] * num_people
            """, language="python")

# ==========================
# DEBUG CHALLENGE / CTF
# ==========================
st.markdown("---")
st.subheader("🕵️ HackerRank Lab: Submit Your Fix")
st.write("Analyze the logs and code above, then submit your numerical answer below to earn points.")

with st.form("multi_bug_form"):
    team_name = st.text_input("Team / Student Name")
    bug_selected = st.selectbox("Which bug are you submitting a fix for?", [
        "Select a Bug...",
        "UPI Bug: The Reverse Heist",
        "UPI Bug: Race to the Scanner",
        "Card Bug: Interchange Fee Reversal",
        "Card Bug: The Missing Penny"
    ])
    answer = st.text_input("Enter your numerical answer:")
    submitted = st.form_submit_button("Submit Solution")

    if submitted:
        if bug_selected == "Select a Bug...":
            st.warning("Please select a bug from the dropdown first!")
        else:
            try:
                ans_val = float(answer.strip())
            except ValueError:
                ans_val = None

            if bug_selected == "UPI Bug: The Reverse Heist":
                if ans_val == amount:
                    st.success(f"🎉 Correct, {team_name}! The merchant lost exactly ₹{amount}. Always enforce `amount > 0` checks!")
                    st.balloons()
                else:
                    st.error("Incorrect. Check how much money was wrongly transferred out of the merchant's balance.")

            elif bug_selected == "UPI Bug: Race to the Scanner":
                if ans_val == amount:
                    st.success(f"🎉 Spot on, {team_name}! The system debited ₹{amount} twice due to a missing atomic DB lock.")
                    st.balloons()
                else:
                    st.error("Incorrect. Look at the duplicate amount charged across both threads.")

            elif bug_selected == "Card Bug: Interchange Fee Reversal":
                expected = amount - (amount * 0.02)
                if ans_val == expected:
                    st.success(f"🎉 Perfect, {team_name}! The merchant should receive ₹{expected:.2f} after deducting the 2% fee.")
                    st.balloons()
                else:
                    st.error(f"Incorrect. Subtract the 2% fee from ₹{amount:.2f} instead of adding it.")

            elif bug_selected == "Card Bug: The Missing Penny":
                split = round(amount / 3, 2)
                collected = split * 3
                expected_diff = round(abs(amount - collected) * 100) # In paise
                
                if expected_diff == 0:
                    st.warning("The amount you ran divides perfectly by 3. Re-run the scenario with ₹1000.00 first!")
                elif ans_val == expected_diff:
                    st.success(f"🎉 Excellent, {team_name}! Floating-point rounding leaves the ledger short by {expected_diff} paise!")
                    st.balloons()
                else:
                    st.error("Incorrect. Calculate how many paise (0.01) the system is short when multiplying the rounded split by 3.")

# ==========================
# COMPARISON TABLE
# ==========================
st.write("")
st.markdown("### 📊 Infrastructure & Cost Comparison")

data = {
    "Metric": [
        "Parties in Chain",
        "Merchant Fee (MDR)",
        "Merchant Settlement",
        "Hardware Needed",
        "Credit Facility",
        "Dispute Process",
    ],
    "UPI Rail": [
        "3 (NPCI + 2 Banks)",
        "0% on P2M (Govt Subsidized)",
        "Near-Instant (Real-time)",
        "QR Code / VPA (Zero Hardware)",
        "No (Direct Account Debit)",
        "NPCI Grievance Redressal",
    ],
    "Card Rail (Debit/Credit)": [
        "5–6 (POS/Gateway, Acquirer, Network, Issuer)",
        "~1.5% - 2.0% (Interchange + Network + Markup)",
        "T+1 / T+2 (Batch Settlement)",
        "POS Terminal (Hardware Cost/Rent)",
        "Yes (Credit Card Revolving Debt)",
        "Formal Chargeback / Card Network Rules",
    ],
}
df = pd.DataFrame(data)
st.dataframe(df, hide_index=True, use_container_width=True)
