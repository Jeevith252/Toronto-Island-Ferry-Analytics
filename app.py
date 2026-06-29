import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Toronto Ferry Analytics",
    page_icon="⛴️",
    layout="wide"
)

# -------------------------------
# Dashboard Title
# -------------------------------
st.title("⛴️ Toronto Island Ferry Analytics Dashboard")

st.markdown("""
Welcome to the Toronto Island Ferry Analytics Dashboard.

This dashboard provides insights into:
- Ticket Sales
- Ticket Redemptions
- Passenger Demand
- Peak Hours
- Seasonal Trends
""")

# -------------------------------
# Load Dataset
# -------------------------------
@st.cache_data
def load_data():

    df = pd.read_csv("data/clean_ferry_dataset.csv")

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    df = df.sort_values("Timestamp")

    return df


df = load_data()

# -------------------------------
# Sidebar
# -------------------------------

st.sidebar.title("Filters")

# -------------------------------
# Sidebar Filters
# -------------------------------

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All"] + sorted(df["Year"].unique().tolist())
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    ["All"] + list(df["Month"].unique())
)

selected_weekend = st.sidebar.selectbox(
    "Weekend",
    ["All", "Weekday", "Weekend"]
)

# -------------------------------
# Filter Data
# -------------------------------

filtered_df = df.copy()

if selected_year != "All":
    filtered_df = filtered_df[
        filtered_df["Year"] == selected_year
    ]

if selected_month != "All":
    filtered_df = filtered_df[
        filtered_df["Month"] == selected_month
    ]

if selected_weekend == "Weekday":
    filtered_df = filtered_df[
        filtered_df["Weekend"] == False
    ]

elif selected_weekend == "Weekend":
    filtered_df = filtered_df[
        filtered_df["Weekend"] == True
    ]

# Display filtered record count
st.sidebar.write(f"Filtered Records : {len(filtered_df):,}")
# -------------------------------
# KPI Calculations
# -------------------------------

total_sales = filtered_df["Sales Count"].sum()

total_redemption = filtered_df["Redemption Count"].sum()

average_sales = filtered_df["Sales Count"].mean()

peak_hour = (
    filtered_df.groupby("Hour")["Sales Count"]
    .mean()
    .idxmax()
)

# -------------------------------
# KPI Section
# -------------------------------

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🎟️ Total Tickets Sold",
        f"{total_sales:,.0f}"
    )

with col2:
    st.metric(
        "🎫 Total Tickets Redeemed",
        f"{total_redemption:,.0f}"
    )

with col3:
    st.metric(
        "⏰ Peak Hour",
        f"{peak_hour}:00 hrs"
    )

with col4:
    st.metric(
        "📈 Average Sales",
        f"{average_sales:.2f} Tickets"
    )
st.divider()

# =====================================================
# Hourly Ticket Sales Trend
# =====================================================

hourly_sales = (
    filtered_df.groupby("Hour")["Sales Count"]
    .mean()
    .reset_index()
)



fig_sales = px.line(
    hourly_sales,
    x="Hour",
    y="Sales Count",
    markers=True,
    title="Average Ticket Sales by Hour"
)

fig_sales.update_layout(
    template="plotly_dark",
    xaxis_title="Hour of Day",
    yaxis_title="Average Tickets Sold"
)

# =====================================================
# Hourly Redemption Trend
# =====================================================

hourly_redemption = (
    filtered_df.groupby("Hour")["Redemption Count"]
    .mean()
    .reset_index()
)

fig_redemption = px.line(
    hourly_redemption,
    x="Hour",
    y="Redemption Count",
    markers=True,
    title="Average Ticket Redemptions by Hour"
)

fig_redemption.update_layout(
    template="plotly_dark",
    xaxis_title="Hour of Day",
    yaxis_title="Average Tickets Redeemed"
)

# =====================================================
# Display Both Charts Side by Side
# =====================================================

left, right = st.columns(2)

with left:
    st.subheader("📈 Hourly Ticket Sales Trend")
    st.plotly_chart(fig_sales, use_container_width=True)

with right:
    st.subheader("📉 Hourly Ticket Redemption Trend")
    st.plotly_chart(fig_redemption, use_container_width=True)

# =====================================================
# Sales vs Redemption Comparison
# =====================================================

st.subheader("📊 Sales vs Redemption Comparison")

comparison = (
    filtered_df.groupby("Hour")[["Sales Count", "Redemption Count"]]
    .mean()
    .reset_index()
)

fig_comparison = px.line(
    comparison,
    x="Hour",
    y=["Sales Count", "Redemption Count"],
    markers=True,
    title="Sales vs Redemption Throughout the Day"
)

fig_comparison.update_layout(
    template="plotly_dark",
    xaxis_title="Hour of Day",
    yaxis_title="Average Count",
    legend_title="Metrics"
)

st.plotly_chart(fig_comparison, use_container_width=True)
st.divider()

# =====================================================
# Monthly Sales Trend
# =====================================================

# =====================================================
# Monthly Trend & Weekend Analysis
# =====================================================

left, right = st.columns(2)

# ---------------- Monthly Sales ----------------

with left:

    st.subheader("📅 Monthly Sales Trend")

    month_order = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    monthly_sales = (
        filtered_df.groupby("Month")["Sales Count"]
        .mean()
        .reindex(month_order)
        .dropna()
        .reset_index()
    )

    fig_monthly = px.bar(
        monthly_sales,
        x="Month",
        y="Sales Count",
        title="Average Monthly Ticket Sales"
    )

    fig_monthly.update_layout(
        template="plotly_dark",
        xaxis_title="Month",
        yaxis_title="Average Tickets Sold"
    )

    st.plotly_chart(fig_monthly, use_container_width=True)

    st.divider()

# ---------------- Weekend Analysis ----------------

with right:

    st.subheader("📦 Weekend vs Weekday")

    weekend_sales = (
        filtered_df.groupby("Weekend")["Sales Count"]
        .mean()
        .reset_index()
    )

    weekend_sales["Weekend"] = weekend_sales["Weekend"].map({
        False: "Weekday",
        True: "Weekend"
    })

    fig_weekend = px.bar(
        weekend_sales,
        x="Weekend",
        y="Sales Count",
        color="Weekend",
        title="Average Ticket Sales"
    )

    fig_weekend.update_layout(
        template="plotly_dark",
        xaxis_title="Day Type",
        yaxis_title="Average Tickets Sold",
        showlegend=False
    )

    st.plotly_chart(fig_weekend, use_container_width=True)

    st.divider()

# =====================================================
# Net Passenger Movement
# =====================================================

st.subheader("🚢 Net Passenger Movement")

net_movement = (
    filtered_df.groupby("Hour")["Net Movement"]
    .mean()
    .reset_index()
)

fig_net = px.line(
    net_movement,
    x="Hour",
    y="Net Movement",
    markers=True,
    title="Average Net Passenger Movement by Hour"
)

fig_net.update_layout(
    template="plotly_dark",
    xaxis_title="Hour of Day",
    yaxis_title="Net Passenger Movement"
)

st.plotly_chart(fig_net, use_container_width=True)
st.divider()

# =====================================================
# Executive Insights
# =====================================================

st.subheader("💡 Executive Insights")

peak_month = (
    monthly_sales.loc[
        monthly_sales["Sales Count"].idxmax(),
        "Month"
    ]
)

peak_sales = monthly_sales["Sales Count"].max()

weekday_avg = weekend_sales.loc[
    weekend_sales["Weekend"] == "Weekday",
    "Sales Count"
].values[0]

weekend_avg = weekend_sales.loc[
    weekend_sales["Weekend"] == "Weekend",
    "Sales Count"
].values[0]

st.success(f"""
### Key Findings

• 🕛 Peak passenger demand occurs around **{peak_hour}:00 hrs**.

• 📅 **{peak_month}** has the highest average ticket sales (**{peak_sales:.1f} tickets**).

• {'📈 Weekend demand is higher than weekday demand.' if weekend_avg > weekday_avg else '📉 Weekday demand is higher than weekend demand.'}

• 🚢 Net passenger movement becomes negative during the afternoon, indicating higher ticket redemption than sales.

### Recommendations

- Increase ferry frequency during peak hours.
- Deploy additional staff during high-demand months.
- Optimize ferry schedules based on passenger movement.
- Plan maintenance during low-demand seasons.
""")
# -------------------------------
# Dataset Information
# -------------------------------

st.header("Dataset Overview")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Rows",
        filtered_df.shape[0]
    )

with col2:
    st.metric(
        "Columns",
        filtered_df.shape[1]
    )

with st.expander("📂 View Dataset Preview"):

    st.dataframe(
        filtered_df.head(10),
        use_container_width=True
    )

csv = filtered_df.to_csv(index=False).encode("utf-8")

col1, col2 = st.columns([1,4])

with col1:
    st.download_button(
        "📥 Download CSV",
        data=csv,
        file_name="filtered_ferry_data.csv",
        mime="text/csv"
    )

st.divider()

st.caption(
    "Toronto Island Ferry Analytics Dashboard | Built with Streamlit, Plotly & Pandas | © 2026"
)

