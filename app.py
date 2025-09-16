import streamlit as st
import pandas as pd
from io import BytesIO

# Page config
st.set_page_config(page_title="CSV Combiner with MPAN Query", page_icon="📊", layout="wide")

st.title("📊 CSV Combiner with MPAN Query")
st.markdown("""
Upload multiple CSV files (each with 4 columns, no headers). 
The app will combine them and allow querying by MPAN (first column).
""")

# Initialize session state
if 'combined_df' not in st.session_state:
    uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        dfs = []
        for file in uploaded_files:
            try:
                df = pd.read_csv(file, header=None)
                if df.shape[1] != 4:
                    st.warning(f"File '{file.name}' does not have exactly 4 columns. Skipping.")
                    continue
                dfs.append(df)
            except Exception as e:
                st.error(f"Error reading '{file.name}': {e}")

        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            combined_df.columns = ['MPAN', 'Column2', 'Column3', 'Column4']
            st.session_state.combined_df = combined_df
            st.session_state.phase = 'input'
            st.rerun()
        else:
            st.warning("No valid CSV files uploaded.")
else:
    df = st.session_state.combined_df
    st.info(f"Data loaded: {len(df)} rows")

    # Manage phase
    if 'phase' not in st.session_state:
        st.session_state.phase = 'input'

    if st.session_state.phase == 'input':
        mpan = st.text_input("Which MPAN data you require shiso?")
        if st.button("Submit"):
            if mpan:
                st.session_state.mpan = mpan
                st.session_state.phase = 'result'
                st.rerun()
            else:
                st.warning("Please enter an MPAN.")

    elif st.session_state.phase == 'result':
        mpan = st.session_state.mpan
        filtered = df[df['MPAN'].astype(str) == str(mpan)]  # Handle possible type differences

        if not filtered.empty:
            st.subheader(f"Filtered Data for MPAN: {mpan}")
            st.dataframe(filtered, use_container_width=True)

            # Prepare Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered.to_excel(writer, index=False, sheet_name='Filtered')
            output.seek(0)

            # Download button
            st.download_button(
                label="Download Filtered Excel",
                data=output,
                file_name=f"{mpan}_filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning(f"No data found for MPAN: {mpan}")

        # Continue option
        st.markdown("---")
        st.write("Do you want to continue?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes"):
                st.session_state.phase = 'input'
                if 'mpan' in st.session_state:
                    del st.session_state.mpan
                st.rerun()
        with col2:
            if st.button("No"):
                st.write("Session ended. You can upload new files by refreshing the page.")
                st.session_state.phase = 'done'

    elif st.session_state.phase == 'done':
        st.info("Query session ended. Refresh the page to start over.")

# Footer
st.markdown("---")
st.caption("Built with Streamlit. For GitHub: Save as app.py, add requirements.txt, and deploy to Streamlit Cloud.")
