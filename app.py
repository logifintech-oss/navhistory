import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

st.set_page_config(page_title="Power of Compounding - Lumpsum", layout="wide")

def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            # Try different headers to handle different file formats
            for h in [0, 4, 3, 2, 1]:
                if uploaded_file.name.endswith('.xls'):
                    temp_df = pd.read_excel(uploaded_file, engine='xlrd', header=h)
                else:
                    temp_df = pd.read_excel(uploaded_file, engine='openpyxl', header=h)
                
                if 'Scheme Name' in temp_df.columns:
                    return temp_df
            return None
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return None
    return None

def format_currency(val):
    if pd.isna(val):
        return "-"
    try:
        return f"₹ {int(val):,}"
    except:
        return val

def format_nav(val):
    if pd.isna(val):
        return "-"
    try:
        return f"{val:.4f}"
    except:
        return val

st.title("🚀 Power of Compounding - Lumpsum Investment")

# Sidebar for file upload
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload NAV Changes Excel File", type=["xls", "xlsx"])
    
    persistent_file = "last_updated_nav_data.xls"
    
    # Logic to keep the last updated file
    if uploaded_file is not None:
        # Save the uploaded file locally to persist it
        with open(persistent_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded and saved as default!")
        df = load_data(uploaded_file)
    else:
        # If no file is uploaded, try the last saved persistent file first
        if os.path.exists(persistent_file):
            try:
                for h in [3, 0, 4, 2, 1]:
                    temp_df = pd.read_excel(persistent_file, engine='xlrd', header=h)
                    if 'Scheme Name' in temp_df.columns:
                        df = temp_df
                        st.info("Using last updated data.")
                        break
            except:
                df = None
        
        # Fallback to original default file if no persistent file or if loading failed
        if df is None:
            default_file = "NAV-Changes.xls"
            if os.path.exists(default_file):
                try:
                    for h in [3, 0, 4, 2, 1]:
                        temp_df = pd.read_excel(default_file, engine='xlrd', header=h)
                        if 'Scheme Name' in temp_df.columns:
                            df = temp_df
                            st.info(f"Using default file: {default_file}")
                            break
                except:
                    df = None
        
        if df is None:
            st.warning("Please upload an Excel file or ensure 'NAV-Changes.xls' exists.")

    if df is not None:
        view_mode = st.radio("Select View Mode", ["Power of Compounding", "52 Week High/Low Analysis"])

if df is not None:
    # Clean up column names
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    
    fund_name = st.selectbox("Select Fund Name", df['Scheme Name'].dropna().unique())
    fund_data = df[df['Scheme Name'] == fund_name].iloc[0]
    
    if view_mode == "Power of Compounding":
        # Extract data for the image layout
        launch_date = fund_data.get('Inception Date')
        if isinstance(launch_date, datetime):
            launch_date_str = launch_date.strftime("%d-%m-%Y")
        else:
            launch_date_str = str(launch_date)
            
        nav_date = fund_data.get('Latest NAV Date')
        if isinstance(nav_date, datetime):
            nav_date_str = nav_date.strftime("%d-%m-%Y")
        else:
            nav_date_str = str(nav_date)
            
        latest_nav = fund_data.get('Latest NAV')
        initial_nav = 10.0 # Standard initial NAV is usually 10
        
        # Display fund name with reduced yellow box size
        st.markdown(f"""
        <div style="background-color: #FFD700; padding: 5px; text-align: center; border-radius: 5px; margin-bottom: 10px; width: fit-content; margin-left: auto; margin-right: auto;">
            <h4 style="color: black; margin: 0; padding: 0 20px;">{fund_name}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Exact table format for details as per user request
        details_table_data = [
            [f"LAUNCH DATE {launch_date_str}", f"NAV AS ON {nav_date_str}"],
            [f"NAV ₹ {initial_nav:.2f}", f"NAV ₹ {latest_nav:.2f}"]
        ]
        details_df = pd.DataFrame(details_table_data)
        
        # Display as a proper table with no headers for exact look
        st.dataframe(details_df, use_container_width=True, hide_index=True, column_config={})
        
        st.markdown("""
        <div style="display: flex; background-color: #FFD700; padding: 10px; border-radius: 5px 5px 0 0; margin-top: 10px;">
            <div style="flex: 1; text-align: center; font-weight: bold; color: black;">ONE TIME INVESTMENT</div>
            <div style="flex: 1; text-align: center; font-weight: bold; color: black;">MARKET VALUE</div>
        </div>
        """, unsafe_allow_html=True)
        
        investment_amounts = [1000, 5000, 10000, 25000, 50000, 100000, 500000, 1000000, 10000000]
        
        # Calculation: Market Value = Investment * (Latest NAV / Initial NAV)
        if not pd.isna(latest_nav) and latest_nav > 0:
            multiplier = latest_nav / initial_nav
            
            table_data = []
            for amt in investment_amounts:
                market_val = int(amt * multiplier)
                table_data.append({
                    "ONE TIME INVESTMENT": format_currency(amt),
                    "MARKET VALUE": format_currency(market_val)
                })
            
            display_df = pd.DataFrame(table_data)
            
            # Display as a proper Streamlit table for easy copying
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
        else:
            st.error("Latest NAV data missing or invalid.")

    elif view_mode == "52 Week High/Low Analysis":
        st.header("📉 52 Week High/Low Analysis")
        
        # Display fund name
        st.markdown(f"""
        <div style="background-color: #FFD700; padding: 5px; text-align: center; border-radius: 5px; margin-bottom: 10px; width: fit-content; margin-left: auto; margin-right: auto;">
            <h4 style="color: black; margin: 0; padding: 0 20px;">{fund_name}</h4>
        </div>
        """, unsafe_allow_html=True)

        # Helper to format dates
        def fmt_date(d):
            if isinstance(d, datetime): return d.strftime("%d-%m-%Y")
            return str(d) if not pd.isna(d) else "-"

        # Prepare High/Low Data for Shorts - Vertical format for better reading
        latest_nav = fund_data.get('Latest NAV')
        latest_date = fmt_date(fund_data.get('Latest NAV Date'))
        
        high_nav = fund_data.get('52 Week Highest NAV')
        high_date = fmt_date(fund_data.get('52 Week Highest NAV Date'))
        pct_from_high = fund_data.get('Percentage (%) lower than 52 wk high')
        
        low_nav = fund_data.get('52 Week Lowest NAV')
        low_date = fmt_date(fund_data.get('52 Week Lowest NAV Date'))
        pct_from_low = fund_data.get('Percentage (%) higher than 52 wk low')

        highest_nav = fund_data.get('Highest NAV')
        highest_date = fmt_date(fund_data.get('Highest NAV Date'))
        
        lowest_nav = fund_data.get('Lowest NAV')
        lowest_date = fmt_date(fund_data.get('Lowest NAV Date'))

        # Helper to format display strings with dates
        def fmt_nav_with_date(nav, date):
            if date == "-": return f"₹ {nav:.2f}"
            return f"₹ {nav:.2f} ({date})"

        # Main Table for Shorts
        shorts_data = [
            ["METRIC", "DETAILS"],
            ["LATEST NAV", fmt_nav_with_date(latest_nav, latest_date)],
            ["52 WEEK HIGH", fmt_nav_with_date(high_nav, high_date)],
            ["DISTANCE FROM HIGH", f"{pct_from_high:.2f}% LOWER"],
            ["52 WEEK LOW", fmt_nav_with_date(low_nav, low_date)],
            ["DISTANCE FROM LOW", f"{pct_from_low:.2f}% HIGHER"],
            ["ALL-TIME HIGHEST NAV", fmt_nav_with_date(highest_nav, highest_date)],
            ["ALL-TIME LOWEST NAV", fmt_nav_with_date(lowest_nav, lowest_date)]
        ]
        
        shorts_df = pd.DataFrame(shorts_data[1:], columns=shorts_data[0])
        
        st.subheader("📱 YouTube Shorts Data Format")
        st.dataframe(shorts_df, use_container_width=True, hide_index=True)
        
        # Grid format for quick copy-pasting
        st.subheader("📋 Quick Copy Grid")
        grid_data = [
            [f"52 WK HIGH: ₹ {high_nav:.2f}", f"DATE: {high_date}"],
            [f"% FROM HIGH: {pct_from_high:.2f}%", f"LATEST: ₹ {latest_nav:.2f}"],
            [f"52 WK LOW: ₹ {low_nav:.2f}", f"DATE: {low_date}"],
            [f"% FROM LOW: {pct_from_low:.2f}%", f"DATE: {latest_date}"],
            [f"ALL-TIME HIGH: ₹ {highest_nav:.2f}", f"DATE: {highest_date}"],
            [f"ALL-TIME LOW: ₹ {lowest_nav:.2f}", f"DATE: {lowest_date}"]
        ]
        st.dataframe(pd.DataFrame(grid_data), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Mutual Fund investments are subject to market risks, read all scheme related documents carefully. The past performance of the mutual funds is not necessarily indicative of future performance of the schemes.")

else:
    st.info("Please ensure the Excel file is correctly uploaded and contains 'Scheme Name' and 'Latest NAV' columns.")
