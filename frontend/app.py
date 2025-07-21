# app.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Backend API URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("Receipt and Bill Processor")

# --- Use session state to prevent re-processing the same file ---
if 'last_processed_file' not in st.session_state:
    st.session_state.last_processed_file = None

# --- File Uploader ---
st.header("1. Upload a Receipt")
uploaded_file = st.file_uploader(
    "Choose a receipt file (.pdf, .png, .jpg, .txt)",
    type=['pdf', 'png', 'jpg', 'jpeg', 'txt']
)

if uploaded_file is not None:
    # Only process if the file is new
    if uploaded_file.name != st.session_state.last_processed_file:
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        with st.spinner('Processing file...'):
            try:
                response = requests.post(f"{API_URL}/upload/", files=files)
                if response.status_code == 200:
                    st.success("File processed successfully!")
                    st.json(response.json())
                    # Store the name of the file we just processed
                    st.session_state.last_processed_file = uploaded_file.name
                    # Rerun the app once to refresh the charts automatically
                    st.rerun()
                else:
                    st.error(f"Error processing file: {response.text}")
                    st.session_state.last_processed_file = None # Clear on error
            except requests.exceptions.ConnectionError as e:
                st.error(f"Connection Error: Could not connect to the backend at {API_URL}. Is the backend running?")
                st.session_state.last_processed_file = None # Clear on error
            except Exception as e:
                st.error(f"An unexpected error occurred on upload: {e}")
                st.session_state.last_processed_file = None # Clear on error

st.divider()

# --- Data Display and Visualization ---
st.header("2. View and Analyze Receipts")

try:
    response = requests.get(f"{API_URL}/receipts/?limit=1000")
    if response.status_code == 200:
        receipts_data = response.json()
        df = pd.DataFrame(receipts_data)

        if not df.empty:
            st.subheader("All Uploaded Receipts")
            
            df_display = df.copy()
            df_display['sub_categories'] = df_display['sub_categories'].apply(
                lambda x: ', '.join(x.keys()) if isinstance(x, dict) and x else str(x)
            )
            st.dataframe(df_display[['vendor', 'date', 'amount', 'category', 'sub_categories']])

            st.subheader("Spending Insights")
            col1, col2 = st.columns(2)

            with col1:
                # --- MODIFIED: This entire block is updated for the new chart ---
                st.write("#### Spend by Vendor")
                # Call the new endpoint for vendor spend
                vendor_spend_resp = requests.get(f"{API_URL}/stats/vendor_spend/")
                if vendor_spend_resp.status_code == 200 and vendor_spend_resp.text:
                    vendor_data = vendor_spend_resp.json()
                    if vendor_data:
                        # Create DataFrame from the new data structure
                        vendor_df = pd.DataFrame(vendor_data)
                        # Create a bar chart with total_spend on y-axis and color by vendor
                        fig_vendor = px.bar(
                            vendor_df,
                            x='vendor',
                            y='total_spend',
                            color='vendor',  # This assigns a different color to each vendor
                            title="Total Spend per Vendor",
                            labels={'total_spend': 'Total Spend', 'vendor': 'Vendor'}
                        )
                        st.plotly_chart(fig_vendor, use_container_width=True)
                    else:
                        st.info("No vendor data to display yet. Upload a receipt.")
                else:
                    st.info("Could not retrieve vendor spend data.")
                # --- End of modification ---

            with col2:
                st.write("#### Spend by Category")
                
                category_totals = {}
                for index, row in df.iterrows():
                    sub_categories = row.get('sub_categories', {})
                    if isinstance(sub_categories, dict) and sub_categories:
                        for cat, amount in sub_categories.items():
                            category_totals[cat] = category_totals.get(cat, 0) + amount
                    elif row['category'] != 'Mixed':
                         cat_to_use = row['category'] if row['category'] else "Uncategorized"
                         category_totals[cat_to_use] = category_totals.get(cat_to_use, 0) + row['amount']

                if category_totals:
                    category_df = pd.DataFrame(list(category_totals.items()), columns=['Category', 'Amount'])
                    fig_cat = px.pie(category_df, names='Category', values='Amount', title="Total Spend by Category")
                    st.plotly_chart(fig_cat, use_container_width=True)
                else:
                    st.info("No category data to display.")
            
            st.write("#### Monthly Spending Trend")
            monthly_spend_resp = requests.get(f"{API_URL}/stats/monthly_spend/")
            if monthly_spend_resp.status_code == 200 and monthly_spend_resp.text:
                monthly_data = monthly_spend_resp.json()
                if monthly_data:
                    monthly_df = pd.DataFrame(monthly_data)
                    if not monthly_df.empty and 'month' in monthly_df.columns:
                        monthly_df['month'] = pd.to_datetime(monthly_df['month'])
                        fig_monthly = px.line(monthly_df, x='month', y='total_spend', markers=True, title="Total Spend Over Time")
                        fig_monthly.update_layout(xaxis_title="Month", yaxis_title="Total Spend")
                        st.plotly_chart(fig_monthly, use_container_width=True)
                else:
                    st.info("No monthly spend data to display yet.")
            else:
                st.info("Could not retrieve monthly spend data.")

        else:
            st.info("No receipts found. Please upload a receipt to get started.")

    else:
        st.error(f"Could not fetch receipt data from the backend. Status Code: {response.status_code}")

except requests.exceptions.ConnectionError:
    st.warning(f"Could not connect to the backend to fetch data.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")

