import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from typing import List

# ---------------------------
# Initialize Session State
# ---------------------------

# Initialize match sets if not already present
if 'match_sets' not in st.session_state:
    st.session_state.match_sets = {
        'Match Set 1': pd.DataFrame({
            'Source': [f'Source {i}' for i in range(1, 11)],
            'Target Options': [
                ['Target A', 'Target B', 'Target C'] for _ in range(10)
            ],
            'Selected Target': [''] * 10
        }),
        'Match Set 2': pd.DataFrame({
            'Source': [f'Source {i}' for i in range(11, 21)],
            'Target Options': [
                ['Target D', 'Target E', 'Target F'] for _ in range(10)
            ],
            'Selected Target': [''] * 10
        }),
        # Add more match sets as needed
    }

# Initialize modal visibility and current match set
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False

if 'current_match_set' not in st.session_state:
    st.session_state.current_match_set = None

# ---------------------------
# Custom CSS for Styling
# ---------------------------

st.markdown(
    """
    <style>
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }

    /* Main Title Styling */
    .main .block-container h1 {
        text-align: center;
        color: #4CAF50;
        font-family: 'Arial', sans-serif;
    }

    /* Button Styling */
    .custom-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border: none;
        border-radius: 12px;
    }

    /* Modal Background */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    /* Modal Content */
    .modal-content {
        background-color: #fefefe;
        padding: 20px;
        border-radius: 10px;
        width: 80%;
        max-width: 800px;
        position: relative;
    }

    /* Close Button */
    .close-button {
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 30px;
        font-weight: bold;
        color: #aaa;
        cursor: pointer;
    }

    .close-button:hover,
    .close-button:focus {
        color: black;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# App Title
# ---------------------------

st.title("🌟 Enhanced Match Management App")

# ---------------------------
# Sidebar with Match Set Buttons
# ---------------------------

st.sidebar.header("📁 Match Sets")

def show_modal(match_set_name: str):
    st.session_state.current_match_set = match_set_name
    st.session_state.show_modal = True

# Display buttons for each match set in the sidebar
for match_set in st.session_state.match_sets.keys():
    if st.sidebar.button(match_set):
        show_modal(match_set)

# ---------------------------
# Modal Implementation
# ---------------------------

if st.session_state.show_modal and st.session_state.current_match_set:
    match_set_name = st.session_state.current_match_set
    df = st.session_state.match_sets[match_set_name].copy()

    # Modal HTML Structure
    modal_html = f"""
    <div class="modal-overlay">
        <div class="modal-content">
            <span class="close-button" onclick="window.location.reload()">&times;</span>
            <h2>🔍 {match_set_name}</h2>
            <p>Select the best target for each source below:</p>
            <div id="ag-grid-container"></div>
        </div>
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)

    # Prepare data for AgGrid
    grid_data = df.copy()

    # Extract all unique target options
    all_target_options = sorted(list({target for sublist in grid_data['Target Options'] for target in sublist}))

    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(grid_data)
    gb.configure_column(
        "Selected Target",
        headerName="Select Target",
        editable=True,
        cellEditor='agSelectCellEditor',
        cellEditorParams={'values': all_target_options},
        cellStyle={'backgroundColor': '#F0F8FF'},
        width=200
    )
    gb.configure_column("Source", editable=False, headerName="Source", cellStyle={'fontWeight': 'bold'})
    gb.configure_column("Target Options", hide=True)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    grid_options = gb.build()

    # Display AgGrid
    grid_response = AgGrid(
        grid_data,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        height=400,
        width='100%',
        theme='streamlit'  # Choose from 'streamlit', 'light', 'dark', etc.
    )

    # Retrieve the edited data
    edited_data = grid_response['data']
    edited_df = pd.DataFrame(edited_data)

    # Save and Cancel Buttons
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("💾 Save Selections"):
            # Update the original DataFrame with selections
            st.session_state.match_sets[match_set_name]['Selected Target'] = edited_df['Selected Target']
            st.session_state.show_modal = False
            st.success(f"✅ Selections saved for **{match_set_name}**!")

    with col2:
        if st.button("❌ Cancel"):
            st.session_state.show_modal = False
            st.experimental_rerun()

# ---------------------------
# Display Current Selections
# ---------------------------

st.header("📊 Current Selections")

for match_set, df in st.session_state.match_sets.items():
    st.subheader(match_set)
    display_df = df[['Source', 'Selected Target']].copy()
    display_df['Selected Target'] = display_df['Selected Target'].replace('', 'Not Selected')
    st.table(display_df)
