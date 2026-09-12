import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

import plotly.graph_objects as go


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="FinTech Lab | Can You Beat the Machine?",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #0b1120;
}

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero {
    padding: 35px;
    border-radius: 20px;
    background: linear-gradient(
        135deg,
        #111827,
        #172554
    );
    border: 1px solid #263554;
    margin-bottom: 25px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 18px;
    color: #aab6cc;
}

.signal-card {
    background: #111827;
    border: 1px solid #263554;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    height: 150px;
}

.signal-title {
    font-size: 13px;
    color: #8996ad;
    text-transform: uppercase;
}

.signal-value {
    font-size: 28px;
    font-weight: 700;
    margin-top: 12px;
}

.signal-description {
    font-size: 14px;
    color: #9ca8bd;
}

.prediction-box {
    background: #111827;
    border: 1px solid #263554;
    border-radius: 18px;
    padding: 30px;
    text-align: center;
    margin-top: 20px;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 15px;
}

.score {
    font-size: 48px;
    font-weight: 800;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
📈 Can You Beat the Machine?
</div>

<div class="hero-subtitle">
FinTech Lab · Machine Learning in Finance
<br>
Look at the market signals. Make your prediction. 
Then see what the ML model thinks.
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Lab Controls")

ticker = st.sidebar.selectbox(
    "Choose an asset",
    ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
)

period = st.sidebar.selectbox(
    "Historical data",
    ["2y", "5y"]
)


# ============================================================
# DOWNLOAD DATA
# ============================================================

@st.cache_data
def download_data(ticker, period):

    df = yf.download(
        ticker,
        period=period,
        auto_adjust=True,
        progress=False
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.reset_index(inplace=True)

    return df


df = download_data(ticker, period)


# ============================================================
# FEATURES
# ============================================================

df["Return"] = df["Close"].pct_change()

df["MA5"] = df["Close"].rolling(5).mean()

df["MA20"] = df["Close"].rolling(20).mean()

df["Volatility"] = (
    df["Return"].rolling(10).std()
)

df["VolumeChange"] = (
    df["Volume"].pct_change()
)

df["Tomorrow"] = df["Close"].shift(-1)

df["Target"] = (
    df["Tomorrow"] > df["Close"]
).astype(int)


features = [
    "Return",
    "MA5",
    "MA20",
    "Volatility",
    "VolumeChange"
]

df = df.dropna().copy()


# ============================================================
# TRAIN MODEL
# ============================================================

X = df[features]
y = df["Target"]

split = int(len(df) * 0.8)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split]
y_test = y.iloc[split:]

model = LogisticRegression(
    max_iter=1000
)

model.fit(X_train, y_train)

test_prediction = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    test_prediction
)


# ============================================================
# PRICE CHART
# ============================================================

st.markdown(
    '<div class="section-title">📊 Market Overview</div>',
    unsafe_allow_html=True
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["Date"],
        y=df["Close"],
        mode="lines",
        name=ticker
    )
)

fig.update_layout(
    height=380,
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis_title="",
    yaxis_title="Price",
    template="plotly_dark"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CHOOSE RANDOM TEST DAY
# ============================================================

if "round" not in st.session_state:
    st.session_state.round = 1

if "day" not in st.session_state:

    st.session_state.day = np.random.randint(
        split,
        len(df) - 1
    )


row = df.iloc[
    st.session_state.day
]


# ============================================================
# SIGNALS
# ============================================================

st.markdown(
    '<div class="section-title">🔎 What does the market look like?</div>',
    unsafe_allow_html=True
)


# Signal 1
if row["MA5"] > row["MA20"]:
    trend = "↑"
    trend_text = "Short-term bullish"
else:
    trend = "↓"
    trend_text = "Short-term bearish"


# Signal 2
if row["Close"] > row["MA20"]:
    position = "↑"
    position_text = "Above long-term average"
else:
    position = "↓"
    position_text = "Below long-term average"


# Signal 3
if row["Return"] > 0:
    momentum = "↑"
    momentum_text = "Positive momentum"
else:
    momentum = "↓"
    momentum_text = "Negative momentum"


# Signal 4
if row["VolumeChange"] > 0:
    volume = "HIGH"
    volume_text = "More activity"
else:
    volume = "LOW"
    volume_text = "Less activity"


c1, c2, c3, c4 = st.columns(4)


with c1:
    st.markdown(f"""
    <div class="signal-card">
    <div class="signal-title">5D vs 20D Trend</div>
    <div class="signal-value">{trend}</div>
    <div class="signal-description">{trend_text}</div>
    </div>
    """, unsafe_allow_html=True)


with c2:
    st.markdown(f"""
    <div class="signal-card">
    <div class="signal-title">Price vs MA20</div>
    <div class="signal-value">{position}</div>
    <div class="signal-description">{position_text}</div>
    </div>
    """, unsafe_allow_html=True)


with c3:
    st.markdown(f"""
    <div class="signal-card">
    <div class="signal-title">Today's Return</div>
    <div class="signal-value">
        {row["Return"] * 100:.2f}%
    </div>
    <div class="signal-description">{momentum_text}</div>
    </div>
    """, unsafe_allow_html=True)


with c4:
    st.markdown(f"""
    <div class="signal-card">
    <div class="signal-title">Volume</div>
    <div class="signal-value">{volume}</div>
    <div class="signal-description">{volume_text}</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HUMAN PREDICTION
# ============================================================

st.markdown(
    '<div class="section-title">🧑‍💻 Your Prediction</div>',
    unsafe_allow_html=True
)

st.write(
    "Use the four signals above. You don't need to calculate "
    "anything — just decide whether you think the next day "
    "will be UP or DOWN."
)


col1, col2 = st.columns(2)


if "user_prediction" not in st.session_state:

    with col1:

        if st.button(
            "🟢  I THINK IT WILL GO UP",
            use_container_width=True
        ):

            st.session_state.user_prediction = 1
            st.rerun()


    with col2:

        if st.button(
            "🔴  I THINK IT WILL GO DOWN",
            use_container_width=True
        ):

            st.session_state.user_prediction = 0
            st.rerun()


# ============================================================
# REVEAL
# ============================================================

if "user_prediction" in st.session_state:

    st.divider()

    st.markdown(
        '<div class="section-title">🤖 Machine Prediction</div>',
        unsafe_allow_html=True
    )

    example = row[features].values.reshape(1, -1)

    machine_prediction = model.predict(example)[0]

    probabilities = model.predict_proba(example)[0]

    confidence = max(probabilities) * 100

    actual = row["Target"]


    if machine_prediction == 1:

        st.success(
            f"🤖 MACHINE SAYS: **UP**  ·  Confidence: {confidence:.1f}%"
        )

    else:

        st.error(
            f"🤖 MACHINE SAYS: **DOWN**  ·  Confidence: {confidence:.1f}%"
        )


    # --------------------------------------------------------
    # Human result
    # --------------------------------------------------------

    if st.session_state.user_prediction == actual:

        st.success(
            "🎉 Your prediction was correct!"
        )

    else:

        st.warning(
            "Your prediction was incorrect."
        )


    # --------------------------------------------------------
    # Actual result
    # --------------------------------------------------------

    if actual == 1:

        st.info(
            "📈 ACTUAL RESULT: The next day's price was HIGHER."
        )

    else:

        st.info(
            "📉 ACTUAL RESULT: The next day's price was LOWER."
        )


    # --------------------------------------------------------
    # Next round
    # --------------------------------------------------------

    if st.session_state.round < 3:

        if st.button(
            "➡️ NEXT ROUND",
            use_container_width=True
        ):

            st.session_state.round += 1

            st.session_state.day = np.random.randint(
                split,
                len(df) - 1
            )

            del st.session_state.user_prediction

            st.rerun()

    else:

        st.divider()

        st.subheader("🏁 Three rounds complete!")

        st.write(
            "Now let's look at something very important in Machine Learning."
        )

        st.metric(
            "Model Test Accuracy",
            f"{accuracy * 100:.1f}%"
        )

        st.warning(
            "A model can perform very well on historical data "
            "but still struggle to predict unseen market data."
        )


# ============================================================
# LEARNING BOX
# ============================================================

st.divider()

with st.expander("🧠 How does the ML model actually work?"):

    st.markdown("""
    The model receives the same kinds of information you just saw:

    **Return + Moving Averages + Volatility + Volume**

    ↓

    **Machine Learning Model**

    ↓

    **Probability of UP / DOWN**

    The important difference is that the model has learned
    relationships between these features and historical outcomes.

    ### The complete pipeline

    **Historical Data**
    
    ↓

    **Features**

    ↓

    **Training**

    ↓

    **Testing on unseen data**

    ↓

    **Prediction**
    """)


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Educational demonstration only — this is not financial advice "
    "and historical performance does not guarantee future results."
)