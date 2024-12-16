import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from typing import List

# Initialize session state for match sets
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

# Initialize modal visibility
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False

if 'current_match_set' not in st.session_state:
    st.session_state.current_match_set = None

# Custom CSS for better styling
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

    /* Modal Styling */
    .modal {
        display: block; /* Hidden by default */
        position: fixed;
        z-index: 999;
        padding-top: 100px;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto;
        background-color: rgba(0,0,0,0.4);
    }

    .modal-content {
        background-color: #fefefe;
        margin: auto;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
        border-radius: 10px;
    }

    .close-button {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
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

st.title("🌟 Enhanced Match Management App")

st.sidebar.header("📁 Match Sets")

# Function to display modal
def show_modal(match_set_name: str):
    st.session_state.current_match_set = match_set_name
    st.session_state.show_modal = True

# Display buttons for each match set
for match_set in st.session_state.match_sets.keys():
    if st.sidebar.button(match_set):
        show_modal(match_set)

# Function to save selections
def save_selections(match_set_name: str, df: pd.DataFrame):
    st.session_state.match_sets[match_set_name] = df
    st.session_state.show_modal = False
    st.success(f"✅ Selections saved for **{match_set_name}**!")

# If a modal is to be shown
if st.session_state.show_modal:
    match_set_name = st.session_state.current_match_set
    df = st.session_state.match_sets[match_set_name].copy()

    # Modal HTML structure
    modal_html = f"""
    <div class="modal">
      <div class="modal-content">
        <span class="close-button" onclick="window.location.href = window.location.href.split('?')[0]">&times;</span>
        <h2>🔍 {match_set_name}</h2>
        <div id="ag-grid-container"></div>
      </div>
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)

    # Interactive Table within the Modal
    st.subheader(f"Select the best match for each source in **{match_set_name}**")

    # Prepare data for AgGrid
    grid_data = df.copy()

    # Flatten the list of target options for dropdown
    all_target_options = sorted(list({target for sublist in grid_data['Target Options'] for target in sublist}))

    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(grid_data)
    gb.configure_column("Selected Target", editable=True, 
                        cellEditor='agSelectCellEditor', 
                        cellEditorParams={'values': all_target_options},
                        headerName="Select Target",
                        width=200)
    gb.configure_column("Source", editable=False, headerName="Source")
    gb.configure_column("Target Options", editable=False, headerName="Target Options", hide=True)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    grid_options = gb.build()

    grid_response = AgGrid(
        grid_data,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        height=400,
        width='100%',
        theme='streamlit'  # You can choose other themes like 'light', 'dark', etc.
    )

    # Retrieve the edited data
    edited_data = grid_response['data']
    edited_df = pd.DataFrame(edited_data)

    # Button to save changes
    if st.button("💾 Save Selections"):
        # Update the original DataFrame with selections
        st.session_state.match_sets[match_set_name]['Selected Target'] = edited_df['Selected Target']
        save_selections(match_set_name, st.session_state.match_sets[match_set_name])

    # Button to cancel (close modal without saving)
    if st.button("❌ Cancel"):
        st.session_state.show_modal = False

# Display current selections
st.header("📊 Current Selections")

for match_set, df in st.session_state.match_sets.items():
    st.subheader(match_set)
    display_df = df[['Source', 'Selected Target']].copy()
    display_df['Selected Target'] = display_df['Selected Target'].replace('', 'Not Selected')
    st.table(display_df)
