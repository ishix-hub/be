import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="UP EV Policy Dashboard", layout="wide")

DATA_DIR = "data"
POLICY_DATE = {
    "UP": pd.Timestamp("2022-10-14"),
    "TN": pd.Timestamp("2023-02-14"),
    "KA": pd.Timestamp("2017-09-25"),
}
STATE_NAMES = {"UP": "Uttar Pradesh", "TN": "Tamil Nadu", "KA": "Karnataka"}


@st.cache_data
def load_csv(name, **kwargs):
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path, **kwargs)


master = load_csv("master_long.csv", parse_dates=["Date"])
growth = load_csv("b_growth_comparison.csv")
cat_share = load_csv("c_up_category_share.csv", index_col=0)
segment = load_csv("extra1_segment_growth.csv")
forecast = load_csv("d_forecast_12m.csv", parse_dates=["Date"])
policy_compare = load_csv("extra2_policy_design_comparison.csv")

st.title("UP Electric Vehicle Policy — Evidence Dashboard")

# ---------------- KPI row ----------------
if growth is not None:
    cols = st.columns(len(growth))
    for c, (_, row) in zip(cols, growth.iterrows()):
        c.metric(row["State"], f"{row['PctGrowth']:.0f}% growth",
                 f"{row['PreAvgMonthly']:.0f} → {row['PostAvgMonthly']:.0f} /mo")

st.divider()

# ---------------- Trend ----------------
st.subheader("EV Registration Trend")
if master is not None:
    state_sel = st.selectbox("State", options=list(POLICY_DATE.keys()),
                              format_func=lambda s: STATE_NAMES[s])
    ts = (master[master["State"] == state_sel]
          .groupby("Date")["Registrations"].sum().reset_index()
          .sort_values("Date"))
    ts["RollingAvg"] = ts["Registrations"].rolling(3, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts["Date"], y=ts["Registrations"], name="Monthly",
                              mode="lines", line=dict(color="lightgray")))
    fig.add_trace(go.Scatter(x=ts["Date"], y=ts["RollingAvg"], name="3-month avg",
                              mode="lines", line=dict(color="green", width=2.5)))
    fig.add_vline(x=POLICY_DATE[state_sel], line_dash="dash", line_color="red",
                  annotation_text="Policy notified")
    fig.update_layout(height=420, margin=dict(t=10, b=10),
                       yaxis_title="Registrations", xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Add master_long.csv to the data/ folder.")

st.divider()

# ---------------- Cross-state growth ----------------
left, right = st.columns(2)

with left:
    st.subheader("Pre vs Post-Policy Growth (24-month window)")
    if growth is not None:
        fig = px.bar(growth, x="State", y="PctGrowth", text="PctGrowth",
                      color="State", color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        fig.update_layout(height=380, margin=dict(t=10, b=10), showlegend=False,
                           yaxis_title="% growth")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(growth.set_index("State"), use_container_width=True)

with right:
    st.subheader("UP — Segment-Level Growth")
    if segment is not None:
        fig = px.bar(segment, x="Bucket", y="PctGrowth", text="PctGrowth",
                      color="Bucket", color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        fig.update_layout(height=380, margin=dict(t=10, b=10), showlegend=False,
                           yaxis_title="% growth")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(segment.set_index("Bucket"), use_container_width=True)

st.divider()

# ---------------- Category mix ----------------
st.subheader("UP — Category Mix by Year")
if cat_share is not None:
    fig = px.bar(cat_share, x=cat_share.index, y=cat_share.columns,
                  labels={"x": "Year", "value": "% share"})
    fig.update_layout(height=420, margin=dict(t=10, b=10), barmode="stack",
                       legend_title="Category")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------- Forecast ----------------
st.subheader("UP — 12-Month Forward Projection")
if master is not None and forecast is not None:
    up_actual = (master[master["State"] == "UP"]
                 .groupby("Date")["Registrations"].sum().reset_index())
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=up_actual["Date"], y=up_actual["Registrations"],
                              name="Actual", mode="lines", line=dict(color="steelblue")))
    fig.add_trace(go.Scatter(x=forecast["Date"], y=forecast["ForecastRegistrations"],
                              name="Projected (linear, post-policy trend)",
                              mode="lines", line=dict(color="darkorange", dash="dash")))
    fig.update_layout(height=380, margin=dict(t=10, b=10), yaxis_title="Registrations")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------- Policy design comparison ----------------
st.subheader("Policy Design Comparison")
if policy_compare is not None:
    st.dataframe(policy_compare.set_index("Feature"), use_container_width=True)
