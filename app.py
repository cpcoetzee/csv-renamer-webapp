import streamlit as st
import pandas as pd
import os
from datetime import datetime

def extract_info_from_csv(file):
    # Read the first few rows of the CSV
    df = pd.read_csv(file, nrows=10)
    
    # Get date_from from first row and split if it contains a prefix
    date_from_raw = str(df.iloc[0, 0])
    date_from = date_from_raw.split('|')[-1] if '|' in date_from_raw else date_from_raw
    
    # Get date_to from second row and split if it contains a prefix
    date_to_raw = str(df.iloc[1, 0])
    date_to = date_to_raw.split('|')[-1] if '|' in date_to_raw else date_to_raw
    
    # Get test code from row 10 (e.g., V001, V435, V125)
    test_code = str(df.iloc[9, 0])
    
    # Convert dates to desired format (DDMMMYYYY)
    try:
        date_from_formatted = datetime.strptime(date_from, '%d/%m/%Y').strftime('%d%b%Y').upper()
        date_to_formatted = datetime.strptime(date_to, '%d/%m/%Y').strftime('%d%b%Y').upper()
    except ValueError:
        try:
            # Try alternative format if needed
            date_from_formatted = datetime.strptime(date_from, '%Y-%m-%d').strftime('%d%b%Y').upper()
            date_to_formatted = datetime.strptime(date_to, '%Y-%m-%d').strftime('%d%b%Y').upper()
        except ValueError as e:
            raise ValueError(f"Unable to parse dates. Found: '{date_from}' and '{date_to}'") from e
    
    return test_code, date_from_formatted, date_to_formatted

def rename_csv_file(uploaded_file):
    # Get original file name and extension
    original_name = uploaded_file.name
    file_extension = os.path.splitext(original_name)[1]
    
    # Extract information
    test_code, date_from, date_to = extract_info_from_csv(uploaded_file)
    
    # Create new filename using just the code from row 10
    new_filename = f"{test_code}_{date_from}_{date_to}{file_extension}"
    
    return new_filename, uploaded_file.getvalue()

# Streamlit app
def main():
    st.title("CSV File Renamer")
    st.write("Upload a CSV file to rename it based on test code and dates")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        # Process the file
        try:
            new_filename, file_content = rename_csv_file(uploaded_file)
            
            # Display original and new filename
            st.write(f"Original filename: {uploaded_file.name}")
            st.write(f"New filename: {new_filename}")
            
            # Download button
            st.download_button(
                label="Download renamed file",
                data=file_content,
                file_name=new_filename,
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Please check your CSV file format. It should have:")
            st.write("- Date From in first row (format: DD/MM/YYYY or 'Date From|DD/MM/YYYY')")
            st.write("- Date To in second row (format: DD/MM/YYYY or 'Date To|DD/MM/YYYY')")
            st.write("- Test code (e.g., V001, V435, V125) in row 10")

if __name__ == "__main__":
    main()
