import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("pages/login.py")
# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Energy Platform", layout="wide")

st.markdown("""
<style>
body { background-color: #0e1117; }
h1, h2, h3 { color: #00FF9D; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ AI-Based Energy Consumption Optimizer")
st.markdown("### Residential & Industrial Energy Intelligence Platform")
st.markdown("---")

# ---------------------------
# SIDEBAR
# ---------------------------
mode = st.sidebar.radio("User Type", ["Residential", "Industrial"])
uploaded_file = st.sidebar.file_uploader("Upload cleaned_hourly_data.csv", type=["csv"])
num_houses = st.sidebar.slider("Number of Houses (Residential)", 10, 1500, 500)

tabs = st.tabs(["🏠 Dashboard", "📊 Monthly Analytics", "🌐 Grid & Optimization", "📄 Download Report"])

if uploaded_file:

    data = pd.read_csv(uploaded_file)

    # ---------------------------
    # MODEL TRAINING
    # ---------------------------
    X = data[["hour", "day", "month"]]
    y = data["energy"]

    model = RandomForestRegressor(n_estimators=150, random_state=42)
    model.fit(X, y)

    # ---------------------------
    # 24-HOUR FORECAST
    # ---------------------------
    future_data = pd.DataFrame({
        "hour": np.arange(0, 24),
        "day": 1,
        "month": 1
    })

    future_data["Predicted Energy"] = model.predict(future_data)

    # ---------------------------
    # REAL TIME-OF-USE TARIFF
    # ---------------------------
    def get_tariff(hour):
        if 0 <= hour <= 6:
            return 4
        elif 7 <= hour <= 17:
            return 6
        elif 18 <= hour <= 22:
            return 10
        else:
            return 5

    future_data["Tariff"] = future_data["hour"].apply(get_tariff)
    future_data["Cost"] = future_data["Predicted Energy"] * future_data["Tariff"]

    # ---------------------------
    # LOAD SHIFTING OPTIMIZATION
    # ---------------------------
    optimized_future = future_data.copy()
    top_peaks = optimized_future.nlargest(3, "Predicted Energy")
    low_hours = optimized_future.nsmallest(3, "Predicted Energy")

    for i in range(3):
        shift = top_peaks.iloc[i]["Predicted Energy"] * 0.3
        optimized_future.loc[top_peaks.index[i], "Predicted Energy"] -= shift
        optimized_future.loc[low_hours.index[i], "Predicted Energy"] += shift

    # ---------------------------
    # GRID LOSS (Hourly I²R)
    # ---------------------------
    R = 0.00005

    if mode == "Residential":
        hourly_before = future_data["Predicted Energy"] * num_houses
        hourly_after = optimized_future["Predicted Energy"] * num_houses
    else:
        multiplier = 20
        variation = np.linspace(1.2, 1.5, 24)
        hourly_before = future_data["Predicted Energy"] * multiplier * variation
        hourly_after = optimized_future["Predicted Energy"] * multiplier * variation

    loss_before = np.sum(R * (hourly_before ** 2))
    loss_after = np.sum(R * (hourly_after ** 2))
    carbon_saved = (loss_before - loss_after) * 0.82

    # ===========================
    # TAB 1: DASHBOARD
    # ===========================
    with tabs[0]:

        st.markdown("## 📊 24-Hour Forecast")
        fig = px.line(future_data, x="hour", y="Predicted Energy",
                      markers=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        if mode == "Residential":
            cheapest_hour = future_data.loc[future_data["Cost"].idxmin()]
            greenest_hour = future_data.loc[future_data["Predicted Energy"].idxmin()]

            st.success(f"Cheapest Hour: {int(cheapest_hour['hour'])}:00")
            st.success(f"Greenest Hour: {int(greenest_hour['hour'])}:00")

            st.markdown("## 🏠 Smart Appliance Scheduling")

            appliance = st.selectbox(
                "Select Appliance",
                [
                    "Washing Machine (2 kWh)",
                    "Dishwasher (1.5 kWh)",
                    "EV Charging (7 kWh)",
                    "Air Conditioner (3 kWh)"
                ]
            )

            appliance_load = float(appliance.split("(")[1].split(" ")[0])
            future_data["Appliance Cost"] = appliance_load * future_data["Tariff"]

            best_hour = future_data.loc[future_data["Appliance Cost"].idxmin()]
            worst_hour = future_data.loc[future_data["Appliance Cost"].idxmax()]

            savings_percent = (
                (worst_hour["Appliance Cost"] - best_hour["Appliance Cost"])
                / worst_hour["Appliance Cost"]
            ) * 100

            st.info(
                f"Run {appliance.split('(')[0]} at {int(best_hour['hour'])}:00 "
                f"to save {round(savings_percent,2)}%"
            )

    # ===========================
    # TAB 2: MONTHLY ANALYTICS
    # ===========================
    with tabs[1]:

        st.markdown("## 📊 Monthly Energy with Seasonal Impact")

        monthly = data.copy()

        def seasonal_factor(month):
            if month in [3,4,5,6]:
                return 1.35
            elif month in [7,8,9]:
                return 1.05
            else:
                return 0.95

        monthly["seasonal"] = monthly["month"].apply(seasonal_factor)
        monthly["adjusted_energy"] = monthly["energy"] * monthly["seasonal"]

        if mode == "Residential":
            monthly["scaled"] = monthly["adjusted_energy"] * num_houses
        else:
            monthly["scaled"] = monthly["adjusted_energy"] * 20

        monthly_summary = monthly.groupby("month")["scaled"].sum().reset_index()
        monthly_summary["bill"] = monthly_summary["scaled"] * 6

        fig_month = px.bar(monthly_summary,
                           x="month",
                           y="scaled",
                           template="plotly_dark",
                           color="scaled")
        st.plotly_chart(fig_month, use_container_width=True)

        if len(monthly_summary) > 1:
            current = monthly_summary.iloc[-1]
            previous = monthly_summary.iloc[-2]
            change = ((previous["scaled"] - current["scaled"]) / previous["scaled"]) * 100

            st.metric("Current Month Usage (kWh)", round(current["scaled"],2))
            st.metric("Estimated Monthly Bill (₹)", round(current["bill"],2))

            if change > 0:
                st.success(f"Energy reduced by {round(change,2)}% vs last month.")
            else:
                st.warning("Energy usage increased compared to last month.")

    # ===========================
    # TAB 3: GRID & OPTIMIZATION
    # ===========================
    with tabs[2]:

        st.markdown("## 🌐 Grid & Carbon Impact")

        c1, c2 = st.columns(2)
        c1.metric("Transmission Loss Before", round(loss_before,2))
        c2.metric("Transmission Loss After", round(loss_after,2))
        st.metric("Carbon Saved (kg CO₂)", round(carbon_saved,2))

        if mode == "Industrial":
            peak = max(hourly_before)
            demand_charge = peak * 300
            load_factor = np.mean(hourly_before) / peak

            st.metric("Peak Demand (kW)", round(peak,2))
            st.metric("Demand Charge (₹)", round(demand_charge,2))
            st.metric("Load Factor", round(load_factor,3))

    # ===========================
    # TAB 4: PDF REPORT
    # ===========================
    with tabs[3]:

        st.markdown("## 📄 Generate Professional Report")

        file_path = "Energy_Report.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("AI Energy Optimization Report", styles["Heading1"]))
        elements.append(Spacer(1, 12))

        report_data = [
            ["User Type", mode],
            ["Transmission Loss Before", str(round(loss_before,2))],
            ["Transmission Loss After", str(round(loss_after,2))],
            ["Carbon Saved (kg)", str(round(carbon_saved,2))]
        ]

        table = Table(report_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))

        elements.append(table)
        doc.build(elements)

        with open(file_path, "rb") as f:
            st.download_button("Download Styled PDF Report", f, file_name="Energy_Report.pdf")

else:
    st.warning("Upload dataset to start.")