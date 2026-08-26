import time
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="UPI vs Card — Payment Rails Infra", layout="wide")

MINT = "#1D9E75"
AMBER = "#BA7517"
BG = "#0D1210"
PANEL = "#131A17"
LINE = "#263029"

st.markdown(
    """
    <style>
    .stApp { background-color: #0D1210; color: #E6EDE9; }
    .eyebrow { font-family: monospace; color: #4FE8A6; letter-spacing: 0.12em;
               text-transform: uppercase; font-size: 12px; margin-bottom: 4px; }
    .subtext { color: #8A968E; font-size: 15px; max-width: 700px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="eyebrow">Payment rails // live comparison</p>', unsafe_allow_html=True)
st.title("UPI vs Card infrastructure")
st.markdown(
    '<p class="subtext">Same ₹ leaving the same wallet, two completely different journeys. '
    'Run a transaction below and watch how many parties each rail passes through before '
    'money actually moves.</p>',
    unsafe_allow_html=True,
)
st.write("")

UPI_NODES = [
    ("Customer", "UPI app / VPA"),
    ("NPCI switch", "routes the request"),
    ("Remitter bank", "debits customer"),
    ("Merchant", "credited"),
]

CARD_NODES = [
    ("Customer", "taps / swipes card"),
    ("POS / gateway", "captures txn"),
    ("Acquiring bank", "merchant's bank"),
    ("Card network", "Visa / MC / RuPay"),
    ("Issuing bank", "approves & holds"),
    ("Merchant", "authorized"),
]


def draw_rail(nodes, color, active_upto=-1, pulse_frac=None):
    """active_upto = index of last fully-reached node. pulse_frac (0-1) shows
    progress of the pulse travelling from active_upto to active_upto+1."""
    n = len(nodes)
    xs = list(range(n))
    fig, ax = plt.subplots(figsize=(9, 1.8), facecolor=PANEL)
    ax.set_facecolor(PANEL)

    # base connecting line
    ax.plot([0, n - 1], [0, 0], color=LINE, linewidth=2, zorder=1)

    # completed segment, highlighted
    if active_upto >= 0:
        end_x = active_upto
        if pulse_frac is not None and active_upto < n - 1:
            end_x = active_upto + pulse_frac
        ax.plot([0, end_x], [0, 0], color=color, linewidth=2.5, zorder=2)

    for i, (label, sub) in enumerate(nodes):
        reached = i <= active_upto
        node_color = color if reached else LINE
        ax.scatter([i], [0], s=140, facecolors=PANEL, edgecolors=node_color,
                   linewidths=2, zorder=3)
        ax.text(i, 0.35, label, ha="center", va="bottom", fontsize=9,
                color="#E6EDE9", fontweight="bold")
        ax.text(i, -0.35, sub, ha="center", va="top", fontsize=7.5, color="#8A968E")

    if pulse_frac is not None and active_upto < n - 1:
        px = active_upto + pulse_frac
        ax.scatter([px], [0], s=90, color=color, zorder=4)

    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-0.7, 0.7)
    ax.axis("off")
    fig.tight_layout(pad=0.3)
    return fig


col1, col2, col3 = st.columns([2, 1, 3])
with col1:
    amount = st.number_input("Amount (₹)", min_value=1, value=500, step=50)
with col2:
    st.write("")
    st.write("")
    run = st.button("Run transaction ▶", type="primary")
with col3:
    status = st.empty()
    if not run:
        status.markdown("`Idle`")

st.write("")

st.markdown("**UPI**")
upi_chart = st.empty()
upi_meta = st.empty()
upi_chart.pyplot(draw_rail(UPI_NODES, MINT))
upi_meta.caption("3 hops · ~2-3 sec settlement")

st.markdown("**Debit / Credit card**")
card_chart = st.empty()
card_meta = st.empty()
card_chart.pyplot(draw_rail(CARD_NODES, AMBER))
card_meta.caption("6 hops · authorization instant, settlement T+1/T+2")

st.write("")
st.markdown("**Transaction log**")
log_box = st.empty()
log_lines = ["$ waiting for transaction..."]
log_box.code("\n".join(log_lines), language=None)


def append_log(line):
    log_lines.append(line)
    log_box.code("\n".join(log_lines), language=None)


if run:
    log_lines.clear()
    log_lines.append(f"$ initiating transaction of ₹{amount:,.0f}")
    log_box.code("\n".join(log_lines), language=None)

    status.markdown("`Running UPI rail...`")
    t0 = time.time()
    for i in range(len(UPI_NODES) - 1):
        append_log(f"[UPI]  {UPI_NODES[i][0]} → {UPI_NODES[i+1][0]}")
        for f in (0.34, 0.67, 1.0):
            upi_chart.pyplot(draw_rail(UPI_NODES, MINT, active_upto=i, pulse_frac=f))
            time.sleep(0.05)
        upi_chart.pyplot(draw_rail(UPI_NODES, MINT, active_upto=i + 1))
    upi_time = time.time() - t0
    append_log(f"[UPI]  approved in {upi_time:.1f}s, funds settle near-instantly")
    upi_meta.caption(f"3 hops · approved in {upi_time:.1f}s")

    time.sleep(0.2)

    status.markdown("`Running Card rail...`")
    t0 = time.time()
    for i in range(len(CARD_NODES) - 1):
        append_log(f"[CARD] {CARD_NODES[i][0]} → {CARD_NODES[i+1][0]}")
        for f in (0.34, 0.67, 1.0):
            card_chart.pyplot(draw_rail(CARD_NODES, AMBER, active_upto=i, pulse_frac=f))
            time.sleep(0.05)
        card_chart.pyplot(draw_rail(CARD_NODES, AMBER, active_upto=i + 1))
    card_time = time.time() - t0
    append_log(f"[CARD] authorized in {card_time:.1f}s — settlement to merchant is still T+1/T+2 (batch)")
    card_meta.caption(f"6 hops · authorized in {card_time:.1f}s, settles T+1/T+2")

    mdr = amount * 0.018
    append_log(f"$ card MDR on this transaction ≈ ₹{mdr:.2f} (1.8%), UPI MDR ≈ ₹0")
    append_log("$ done.")
    status.markdown("`Idle`")

st.write("")
st.markdown("### Infra & cost comparison")

data = {
    "Metric": [
        "Parties in the chain",
        "Merchant fee (MDR)",
        "Settlement to merchant",
        "Hardware needed",
        "Credit available?",
        "Dispute process",
    ],
    "UPI": [
        "3 (NPCI switch + 2 banks)",
        "~0% on P2M (govt subsidised)",
        "Near-instant",
        "Just a QR code / VPA",
        "No — pulls from bank balance",
        "NPCI grievance redressal",
    ],
    "Card (debit/credit)": [
        "5-6 (POS/gateway, acquirer, network, issuer)",
        "~1.5-2% (interchange + network + acquirer markup)",
        "T+1 / T+2 (batch settlement)",
        "POS machine (rented/purchased)",
        "Yes (credit card) — this is where interest kicks in",
        "Formal chargeback via card network",
    ],
}
df = pd.DataFrame(data)
st.dataframe(df, hide_index=True, use_container_width=True)
