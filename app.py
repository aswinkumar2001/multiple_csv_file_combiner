import streamlit as st
import pandas as pd
from io import BytesIO

# Page config
st.set_page_config(page_title="CSV Combiner App", page_icon="📊", layout="wide")

st.title("📊 CSV to Excel Combiner")
st.markdown("""
Upload multiple CSV files (each with 4 columns) to combine them into a single Excel file. 
The app assumes all CSVs have the same column structure and will concatenate them vertically.
""")

# File uploader for multiple CSVs
uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    dfs = []
    for file in uploaded_files:
        try:
            df = pd.read_csv(file)
            if df.shape[1] != 4:
                st.warning(f"File '{file.name}' does not have exactly 4 columns. Skipping.")
                continue
            dfs.append(df)
        except Exception as e:
            st.error(f"Error reading '{file.name}': {e}")

    if dfs:
        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Display preview
        st.subheader("Combined Data Preview")
        st.dataframe(combined_df.head(10), use_container_width=True)
        st.info(f"Total rows: {len(combined_df)}")

        # Prepare Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            combined_df.to_excel(writer, index=False, sheet_name='Combined')
        output.seek(0)

        # Download button
        st.download_button(
            label="Download Combined Excel",
            data=output,
            file_name="combined_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No valid CSV files uploaded.")
else:
    st.info("Upload CSV files to get started! 🚀")

# Footer
st.markdown("---")
st.caption("Built with Streamlit. Host this on GitHub and deploy to Streamlit Sharing for online access.")
