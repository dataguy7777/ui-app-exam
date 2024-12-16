import streamlit as st
import pandas as pd

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

    /* Modal Overlay */
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
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
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

    /* Button Styling Inside Modal */
    .modal-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        margin: 10px 5px 0 0;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
    }

    .modal-button.cancel {
        background-color: #f44336;
    }

    /* Responsive Design */
    @media (max-width: 600px) {
        .modal-content {
            width: 95%;
        }
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

# Placeholder for the modal
modal_placeholder = st.empty()

if st.session_state.show_modal and st.session_state.current_match_set:
    match_set_name = st.session_state.current_match_set
    df = st.session_state.match_sets[match_set_name].copy()

    # Render the modal
    with modal_placeholder.container():
        st.markdown("""
        <div class="modal-overlay">
            <div class="modal-content">
                <span class="close-button" onclick="window.location.reload()">&times;</span>
                <h2>🔍 {}</h2>
                <p>Select the best target for each source below:</p>
        """.format(match_set_name), unsafe_allow_html=True)

        # Interactive Selection: For each source, provide a selectbox to choose the target
        with st.form(key='selection_form'):
            selections = {}
            for idx, row in df.iterrows():
                source = row['Source']
                target_options = row['Target Options']
                selected = row['Selected Target']
                if selected not in target_options:
                    selected = target_options[0]  # Default to first option if current selection is invalid
                selection = st.selectbox(
                    f"{source}",
                    options=target_options,
                    index=target_options.index(selected) if selected in target_options else 0,
                    key=f"select_{idx}"
                )
                selections[idx] = selection

            # Buttons for Save and Cancel
            col1, col2 = st.columns([1, 1])
            with col1:
                save_button = st.form_submit_button(label="💾 Save Selections", on_click=None)
            with col2:
                cancel_button = st.form_submit_button(label="❌ Cancel", on_click=None)

        # Handle Save Selections
        if save_button:
            # Update the DataFrame with selections
            for idx, selection in selections.items():
                st.session_state.match_sets[match_set_name].at[idx, 'Selected Target'] = selection
            st.session_state.show_modal = False
            st.experimental_rerun()
            st.success(f"✅ Selections saved for **{match_set_name}**!")

        # Handle Cancel
        if cancel_button:
            st.session_state.show_modal = False
            st.experimental_rerun()

        # Append the closing HTML tags for the modal
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------
# Display Current Selections
# ---------------------------

st.header("📊 Current Selections")

for match_set, df in st.session_state.match_sets.items():
    st.subheader(match_set)
    display_df = df[['Source', 'Selected Target']].copy()
    display_df['Selected Target'] = display_df['Selected Target'].replace('', 'Not Selected')
    
    # Apply styling to the 'Selected Target' column
    def color_selected_target(val):
        color = '#d4edda' if val != 'Not Selected' else '#f8d7da'
        return f'background-color: {color}'

    styled_display_df = display_df.style.applymap(color_selected_target, subset=['Selected Target'])
    st.table(styled_display_df)
