import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="School Cash Flow Predictor", layout="wide")

st.title("💰 Financial Cash Flow & Fee Revenue Predictor")

# --- SIDEBAR: INPUT PARAMETERS ---
with st.sidebar:
    st.header("Section A: Revenue Sources (Inflow)")
    tuition_base = st.number_input("Avg Tuition Fee per Student", 1000, 50000, 5000)
    transport_fee = st.number_input("Avg Transport Fee", 0, 5000, 500)
    other_fees = st.number_input("Admission/Exam Fees", 0, 5000, 200)
    
    st.header("Section B: Operational Expenses (Outflow)")
    salaries = st.number_input("Monthly Salary Totals", 5000, 500000, 50000)
    fixed_costs = st.number_input("Rent & Utilities", 0, 100000, 15000)
    marketing = st.number_input("Marketing Spend", 0, 50000, 2000)

    st.header("Section C: Strategy & Discounts")
    profit_target_multiplier = st.slider("Profit Markup Level (%)", 1, 200, 20) / 100
    waiver_rate = st.slider("Fee Waiver/Discount Policy (%)", 0, 30, 5) / 100

# --- MAIN ENGINE: SECTION D (PROJECTION) ---
st.header("Section D: Growth & Arrears Projection")
col1, col2 = st.columns(2)

with col1:
    current_enrollment = st.number_input("Current Student Count", 1, 5000, 500)
    growth_rate = st.slider("Expected Enrollment Growth (%)", -20, 50, 10) / 100
    
with col2:
    arrears_rate = st.slider("Expected Arrears (Pending Dues %)", 0, 40, 12) / 100
    projection_months = st.number_input("Projection Period (Months)", 1, 24, 12)

# --- CALCULATION LOGIC ---
months = [f"Month {i+1}" for i in range(projection_months)]
data = []

temp_students = current_enrollment
for m in range(projection_months):
    # Apply monthly growth
    temp_students *= (1 + (growth_rate / 12))
    
    # Gross Revenue
    gross_rev = temp_students * (tuition_base + transport_fee + other_fees)
    # Applying Waivers (Section C) and Arrears (Section D)
    realized_rev = gross_rev * (1 - waiver_rate) * (1 - arrears_rate)
    
    # Total Expenses (Section B)
    total_exp = salaries + fixed_costs + marketing
    
    # Profit Calculation
    net_cash_flow = realized_rev - total_exp
    
    data.append({
        "Month": m + 1,
        "Students": int(temp_students),
        "Gross Revenue": round(gross_rev, 2),
        "Realized Inflow": round(realized_rev, 2),
        "Total Outflow": round(total_exp, 2),
        "Net Cash Flow": round(net_cash_flow, 2)
    })

df = pd.DataFrame(data)

# --- VISUALIZATION ---
st.divider()
m1, m2, m3 = st.columns(3)
total_projected_profit = df["Net Cash Flow"].sum()
m1.metric("Total Projected Profit", f"${total_projected_profit:,.2f}")
m2.metric("Final Student Count", df["Students"].iloc[-1])
m3.metric("Avg Monthly Burn", f"${df['Total Outflow'].mean():,.2f}")

st.subheader("Cash Flow Projection Trend")
st.line_chart(df.set_index("Month")[["Realized Inflow", "Total Outflow", "Net Cash Flow"]])

with st.expander("View Detailed Monthly Breakdown"):

    st.dataframe(df, use_container_width=True)
