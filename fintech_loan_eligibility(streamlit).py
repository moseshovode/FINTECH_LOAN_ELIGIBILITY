
# fintech_loan_eligibility_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
import random

# --- Streamlit Page Config ---
st.set_page_config(page_title="Loan Eligibility Checker", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>💰 Fintech Loan Eligibility Assessor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Assess your loan eligibility based on cash inflow trends and risk metrics.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Simulate Transaction Data ---
def generate_user_data(user_id, num_months=12):
    dates = pd.date_range(end='2024-12-31', periods=num_months, freq='M')
    if user_id % 3 == 0:
        inflows = [random.randint(2000, 5000) - (i * 150) for i in range(num_months)]
    elif user_id % 3 == 1:
        inflows = [random.randint(1000, 3000) + (i * 200) for i in range(num_months)]
    else:
        inflows = [random.randint(2500, 4500) + (i * 50) for i in range(num_months)]

    inflows = [max(500, x) for x in inflows]
    balances = [sum(inflows[:i + 1]) - random.randint(500, 1500) for i in range(num_months)]
    balances = [max(100, x) for x in balances]

    return pd.DataFrame({
        'user_id': [f'user {user_id}'] * num_months,
        'transaction_date': dates,
        'cash_inflow_month': inflows,
        'current_balance': balances
    })

# Generate sample data for 10 users
all_user_data = [generate_user_data(i) for i in range(1, 11)]
data = pd.concat(all_user_data).reset_index(drop=True)
data['user_id'] = data['user_id'].str.lower()

# --- Loan Assessment Function ---
def assess_loan_eligibility(customer_name, loan_amount, transaction_data):
    user_data = transaction_data[transaction_data['user_id'] == customer_name].sort_values(by='transaction_date')
    if user_data.empty:
        return {'eligible': False, 'message': f"Customer '{customer_name}' not found in records.", 'trend': 'N/A', 'probability_of_approval': 0.0, 'plot_generated': False}

    x = np.arange(len(user_data))
    y = user_data['cash_inflow_month'].values
    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    # Trend interpretation
    if slope > 100:
        trend = "📈 Strong Uptrend"
        probability = 0.95
    elif slope > 20:
        trend = "↗️ Moderate Uptrend"
        probability = 0.75
    elif slope > -20:
        trend = "➖ Stable"
        probability = 0.50
    elif slope > -100:
        trend = "↘️ Moderate Downtrend"
        probability = 0.20
    else:
        trend = "📉 Strong Downtrend"
        probability = 0.05

    avg_inflow = user_data['cash_inflow_month'].mean()
    max_loan = avg_inflow * 3
    loan_ok = loan_amount <= max_loan

    if not loan_ok:
        probability *= 0.1
        message = f"❌ Requested loan NGN {loan_amount:,.2f} exceeds max recommended (NGN {max_loan:,.2f}). "
    else:
        message = ""

    eligible = probability >= 0.60
    message += "✅ Likely eligible." if eligible else "⚠️ Unlikely to be eligible."

    # Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(user_data['transaction_date'], y, marker='o', linestyle='-', color='skyblue', label='Monthly Cash Inflow')
    ax.plot(user_data['transaction_date'], intercept + slope * x, color='red', linestyle='--', label=f'Trend Line (Slope: {slope:.2f})')
    ax.set_title(f'Cash Inflow Trend for {customer_name}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Cash Inflow (NGN)')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    return {
        'eligible': eligible,
        'message': message,
        'trend': trend,
        'calculated_slope': slope,
        'average_monthly_inflow': avg_inflow,
        'max_recommended_loan': max_loan,
        'probability_of_approval': probability,
        'plot_generated': True
    }

# --- UI Form Input Section ---
st.markdown("### 📝 Loan Request Form")

with st.form("loan_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_id_input_raw = st.text_input("Customer ID (e.g., user 1)")
    with col2:
        loan_amount_input = st.number_input("Loan Amount (NGN)", min_value=1000.0, step=500.0, value=5000.0)

    submitted = st.form_submit_button("Check Eligibility")

if submitted:
    customer_id_input = customer_id_input_raw.strip().lower()
    if customer_id_input in data['user_id'].unique():
        result = assess_loan_eligibility(customer_id_input, loan_amount_input, data)

        with st.expander("📊 Loan Assessment Details", expanded=True):
            st.markdown(f"**Customer:** `{customer_id_input_raw}`")
            st.markdown(f"**Loan Amount:** NGN {loan_amount_input:,.2f}")
            st.markdown(f"**Trend:** {result['trend']} _(Slope: {result['calculated_slope']:.2f})_")
            st.markdown(f"**Average Monthly Inflow:** NGN {result['average_monthly_inflow']:,.2f}")
            st.markdown(f"**Max Recommended Loan:** NGN {result['max_recommended_loan']:,.2f}")
            st.markdown(f"**Probability of Approval:** `{result['probability_of_approval']:.0%}`")
            st.info(result['message'])
    else:
        st.error(f"🚫 Customer ID `{customer_id_input_raw}` not found. Please check and try again.")

st.markdown("---")
st.caption("© 2025 Fintech Loan Intelligence | Streamlit UI Enhanced by OpenAI")
