import streamlit as st

st.set_page_config(page_title="AI Energy Platform", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("pages/login.py")
st.title("⚡ AI-Based Energy Consumption Optimizer")
st.markdown("### Residential & Industrial Energy Intelligence Platform")
st.markdown("---")

st.markdown("## 1️⃣ Problem Statement")

st.write("""
Electricity consumption in homes and industries is highly inefficient due to:

* Running high-load appliances during peak tariff hours  
* Lack of demand forecasting  
* Grid transmission losses (I²R losses)  
* No visibility into peak-load patterns  

This results in:
- Higher electricity bills  
- Increased carbon emissions  
- Grid congestion during peak hours  
""")

st.markdown("## 2️⃣ Objective")

st.write("""
Our AI-based Energy Consumption Optimizer solves this challenge by analyzing historical smart meter data 
and predicting short-term energy demand using a Random Forest machine learning model. The system identifies 
peak consumption hours, suggests the cheapest and greenest time to operate high-load appliances, and 
simulates grid transmission losses (I²R model) to reduce peak-load stress. By enabling intelligent 
load shifting and demand forecasting for both residential and industrial users, the platform helps 
reduce electricity bills, lower carbon emissions, and improve overall grid efficiency.  
""")

st.markdown("Transforming raw energy data into intelligent decisions that reduce bills, cut carbon emissions, and stabilize the power grid.")


st.markdown("---")

if st.button("🚀 Proceed to Energy Dashboard"):
    st.switch_page("pages/2_Dashboard.py")