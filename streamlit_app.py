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

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌟 Enhanced Match Management App")

st.sidebar.header("📁 Match Sets")

# Function to display modal (using expander as a workaround)
def show_modal(match_set_name: str):
    st.session_state.current_match_set = match_set_name
    st.session_state.show_modal = True

# Function to save selections
def save_selections(match_set_name: str, df: pd.DataFrame):
    st.session_state.match_sets[match_set_name] = df
    st.session_state.show_modal = False
    st.success(f"✅ Selections saved for **{match_set_name}**!")

# Display buttons for each match set
for match_set in st.session_state.match_sets.keys():
    if st.sidebar.button(match_set):
        show_modal(match_set)

# If a modal is to be shown
if 'show_modal' in st.session_state and st.session_state.show_modal:
    match_set_name = st.session_state.current_match_set
    df = st.session_state.match_sets[match_set_name].copy()

    st.subheader(f"🔍 {match_set_name}")

    # Prepare data for AgGrid
    grid_data = df.copy()
    # Convert list of target options to a string for display
    grid_data['Target Options'] = grid_data['Target Options'].apply(lambda x: ', '.join(x))

    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(grid_data)
    gb.configure_selection('single')
    gb.configure_column("Selected Target", editable=True, 
                        cellEditor='agSelectCellEditor', 
                        cellEditorParams={'values': [option for sublist in df['Target Options'] for option in sublist]},
                        headerName="Select Target")
    gb.configure_column("Target Options", editable=False)
    gb.configure_column("Source", editable=False)
    grid_options = gb.build()

    grid_response = AgGrid(
        grid_data,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.FILTERING_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        height=400,
        width='100%',
    )

    # Retrieve the edited data
    edited_data = grid_response['data']
    edited_df = pd.DataFrame(edited_data)

    # Button to save changes
    if st.button("💾 Save Selections"):
        # Update the original DataFrame with selections
        st.session_state.match_sets[match_set_name]['Selected Target'] = edited_df['Selected Target']
        save_selections(match_set_name, st.session_state.match_sets[match_set_name])

    # Button to cancel
    if st.button("❌ Cancel"):
        st.session_state.show_modal = False

# Display current selections
st.header("📊 Current Selections")

for match_set, df in st.session_state.match_sets.items():
    st.subheader(match_set)
    display_df = df[['Source', 'Selected Target']].copy()
    display_df['Selected Target'] = display_df['Selected Target'].replace('', 'Not Selected')
    st.table(display_df)
