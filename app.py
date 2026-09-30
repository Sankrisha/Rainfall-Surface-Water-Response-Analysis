import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Rainfall–Surface Water Analysis",
    page_icon="🌧️",
    layout="wide"
)

st.title("🌧️ Rainfall–Surface Water Analysis")
st.markdown(
    "### GIS & Remote Sensing Dashboard"
)
st.write(
    "This dashboard analyzes the relationship between rainfall and "
    "surface-water availability and identifies drought-sensitive water bodies."
)

# ---------------------------------------------------------
# Sample Data
# ---------------------------------------------------------

sample_data = pd.DataFrame({
    "Date": pd.date_range("2024-01-01", periods=12, freq="MS"),
    "Rainfall_mm": [
        45, 52, 70, 85, 110, 145,
        180, 160, 120, 90, 60, 40
    ],
    "Water_Area_km2": [
        1.20, 1.25, 1.35, 1.48, 1.70, 2.05,
        2.40, 2.30, 2.00, 1.72, 1.45, 1.25
    ]
})

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload rainfall and water-area CSV",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Date",
            "Rainfall_mm",
            "Water_Area_km2"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            st.error(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )
            st.stop()

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Rainfall_mm"] = pd.to_numeric(
            df["Rainfall_mm"], errors="coerce"
        )
        df["Water_Area_km2"] = pd.to_numeric(
            df["Water_Area_km2"], errors="coerce"
        )

        df = df.dropna(
            subset=[
                "Date",
                "Rainfall_mm",
                "Water_Area_km2"
            ]
        )

    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()

else:
    df = sample_data.copy()

# Sort data

df = df.sort_values("Date").reset_index(drop=True)

# ---------------------------------------------------------
# KPI Calculations
# ---------------------------------------------------------

total_rainfall = df["Rainfall_mm"].sum()
average_rainfall = df["Rainfall_mm"].mean()
maximum_water = df["Water_Area_km2"].max()
minimum_water = df["Water_Area_km2"].min()

if maximum_water > 0:
    water_reduction = (
        (maximum_water - minimum_water)
        / maximum_water
    ) * 100
else:
    water_reduction = 0

# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Rainfall",
    f"{total_rainfall:.1f} mm"
)

col2.metric(
    "Average Rainfall",
    f"{average_rainfall:.1f} mm"
)

col3.metric(
    "Maximum Water Area",
    f"{maximum_water:.2f} km²"
)

col4.metric(
    "Water Area Reduction",
    f"{water_reduction:.1f}%"
)

st.divider()

# ---------------------------------------------------------
# Rainfall Trend
# ---------------------------------------------------------

st.subheader("🌧️ Rainfall Trend")

fig_rainfall = px.line(
    df,
    x="Date",
    y="Rainfall_mm",
    markers=True,
    title="Monthly Rainfall"
)

fig_rainfall.update_layout(
    xaxis_title="Date",
    yaxis_title="Rainfall (mm)"
)

st.plotly_chart(
    fig_rainfall,
    use_container_width=True
)

# ---------------------------------------------------------
# Surface Water Trend
# ---------------------------------------------------------

st.subheader("💧 Surface Water Area Trend")

fig_water = px.line(
    df,
    x="Date",
    y="Water_Area_km2",
    markers=True,
    title="Monthly Surface Water Area"
)

fig_water.update_layout(
    xaxis_title="Date",
    yaxis_title="Water Area (km²)"
)

st.plotly_chart(
    fig_water,
    use_container_width=True
)

# ---------------------------------------------------------
# Rainfall vs Water Area
# ---------------------------------------------------------

st.subheader("📊 Rainfall vs Surface Water Area")

correlation = df["Rainfall_mm"].corr(
    df["Water_Area_km2"]
)

try:
    fig_scatter = px.scatter(
        df,
        x="Rainfall_mm",
        y="Water_Area_km2",
        trendline="ols",
        title="Rainfall vs Surface Water Availability",
        labels={
            "Rainfall_mm": "Rainfall (mm)",
            "Water_Area_km2": "Water Area (km²)"
        }
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

except Exception:
    fig_scatter = px.scatter(
        df,
        x="Rainfall_mm",
        y="Water_Area_km2",
        title="Rainfall vs Surface Water Availability"
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

# ---------------------------------------------------------
# Correlation Analysis
# ---------------------------------------------------------

st.subheader("🔎 Correlation Analysis")

if pd.isna(correlation):
    st.write("Correlation could not be calculated.")
else:
    st.metric(
        "Correlation Coefficient",
        f"{correlation:.3f}"
    )

    if correlation >= 0.7:
        correlation_text = "Strong positive relationship"
    elif correlation >= 0.3:
        correlation_text = "Moderate positive relationship"
    elif correlation >= -0.3:
        correlation_text = "Weak relationship"
    elif correlation >= -0.7:
        correlation_text = "Moderate negative relationship"
    else:
        correlation_text = "Strong negative relationship"

    st.info(
        f"Interpretation: {correlation_text}"
    )

# ---------------------------------------------------------
# Drought Vulnerability
# ---------------------------------------------------------

st.subheader("⚠️ Drought Sensitivity Assessment")

if water_reduction >= 50:
    vulnerability = "HIGH"
elif water_reduction >= 25:
    vulnerability = "MEDIUM"
else:
    vulnerability = "LOW"

st.metric(
    "Water Body Vulnerability",
    vulnerability
)

st.write(
    f"The observed reduction in surface-water area is "
    f"{water_reduction:.1f}% from the maximum recorded area."
)

# ---------------------------------------------------------
# Monthly Change
# ---------------------------------------------------------

df["Water_Area_Change_%"] = (
    df["Water_Area_km2"]
    .pct_change()
    * 100
)

st.subheader("📉 Monthly Surface Water Change")

fig_change = px.bar(
    df,
    x="Date",
    y="Water_Area_Change_%",
    title="Monthly Percentage Change in Water Area"
)

fig_change.update_layout(
    xaxis_title="Date",
    yaxis_title="Change (%)"
)

st.plotly_chart(
    fig_change,
    use_container_width=True
)

# ---------------------------------------------------------
# Data Table
# ---------------------------------------------------------

st.subheader("📋 Analysis Data")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# Download Data
# ---------------------------------------------------------

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Analysis CSV",
    data=csv_data,
    file_name="rainfall_surface_water_analysis.csv",
    mime="text/csv"
)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "Rainfall–Surface Water Analysis | GIS & Remote Sensing Dashboard"
)