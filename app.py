import os
import pandas as pd
import re
import streamlit as st
from datetime import datetime

# Function to extract test set
def extract_test_set(row_value):
    if pd.isna(row_value):
        return None
    
    value = str(row_value).lower()
    
    test_set_mapping = {
        "hep a igm": "hep_a_igm",
        "hepatitis a igm": "hep_a_igm",
        "hep a igg": "hep_a_igg",
        "hepatitis a igg": "hep_a_igg",
        "hiv viral load": "hiv_vl",
        "hiv vl": "hiv_vl",
        "hiv pcr": "hiv_pcr",
        "cmv igm": "cmv_igm",
        "cmv igg": "cmv_igg",
        "rubella igm": "rubella_igm",
        "rubella igg": "rubella_igg",
        "hep b pcr": "hep_b_pcr",
        "hep b igg": "hep_b_igg",
        "hep c pcr": "hep_c_pcr",
        "hep c viral load": "hep_c_vl",
        "hbsag": "hbsag",
        "ebv igg": "ebv_igg",
        "ebv igm": "ebv_igm",
        "hsv igm": "hsv_igm",
        "hsv igg": "hsv_igg",
    }

    for test_pattern, standardized_name in test_set_mapping.items():
        if test_pattern in value:
            return standardized_name

    cleaned = re.sub(r'[^a-z0-9]', '_', value)
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    
    return cleaned if cleaned else "unknown_test"

# Function to format date
def format_date(date_str):
    if pd.isna(date_str):
        return "unknown_date"
    
    date_str = str(date_str).strip()
    date_formats = [
        '%d/%m/%Y', '%d/%m/%y', '%m/%d/%Y', '%m/%d/%y',
        '%Y-%m-%d', '%d-%m-%Y', '%d-%m-%y', '%d %b %Y', '%d %B %Y'
    ]

    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%d%b%Y').upper()
        except ValueError:
            continue
    
    return date_str.replace('/', '_').replace('-', '_').replace(' ', '_')

# Function to rename CSV file
def rename_csv_file(uploaded_file):
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read the CSV file into DataFrame
        df = pd.read_csv(uploaded_file, nrows=15, header=None, encoding='utf-8', encoding_errors='ignore')

        from_date = None
        to_date = None
        test_set = None

        # Scan first 5 rows for 'Date From' and 'Date To'
        for row in range(min(5, len(df))):
            for col in range(min(10, len(df.columns))):
                cell_value = df.iloc[row, col]
                if isinstance(cell_value, str):
                    if "date from" in cell_value.lower():
                        from_date = df.iloc[row, col + 1] if col + 1 < len(df.columns) else None
                    if "date to" in cell_value.lower():
                        to_date = df.iloc[row, col + 1] if col + 1 < len(df.columns) else None

        # Extract test set from first 10 rows
        for row in range(min(10, len(df))):
            for col in range(min(5, len(df.columns))):
                cell_value = df.iloc[row, col]
                if pd.notna(cell_value):
                    cell_str = str(cell_value).lower()
                    if any(term in cell_str for term in ["igm", "igg", "pcr", "viral load", "antibody"]):
                        test_set = extract_test_set(cell_str)
                        break
            if test_set:
                break

        # Format the extracted values
        from_date_str = format_date(from_date) if from_date else "unknown_start"
        to_date_str = format_date(to_date) if to_date else "unknown_end"
        test_set_str = test_set if test_set else "unknown_test"

        new_filename = f"{test_set_str}_Date_From|{from_date_str}_Date_To|{to_date_str}.csv"
        
        return df, new_filename

    except Exception as e:
        return None, str(e)

# Streamlit Web App
st.title("CSV File Renamer")
st.write("Upload your CSV file, and the app will rename it based on test set and date.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df, new_filename = rename_csv_file(uploaded_file)
    
    if df is not None:
        st.success(f"File renamed to: **{new_filename}**")
        
        # Provide download link
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download renamed CSV",
            data=csv,
            file_name=new_filename,
            mime="text/csv"
        )
    else:
        st.error(f"Error: {new_filename}")
