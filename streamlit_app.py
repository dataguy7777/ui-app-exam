import streamlit as st
import pandas as pd

# Initialize session state
if 'df' not in st.session_state:
    # Sample data
    st.session_state.df = pd.DataFrame({
        'Source': ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry'],
        'Target': ['Red', 'Yellow', 'Red', 'Brown', 'Purple']
    })

# Function to switch a subset of matches
def switch_matches(indices):
    # For simplicity, we'll switch the targets within the selected indices
    selected_targets = st.session_state.df.loc[indices, 'Target'].tolist()
    reversed_targets = selected_targets[::-1]
    st.session_state.df.loc[indices, 'Target'] = reversed_targets

# Function to update a match based on user selection
def update_match(index, new_target):
    st.session_state.df.at[index, 'Target'] = new_target

st.title("Match Management App")

st.header("Current Matches")

# Display the DataFrame
st.dataframe(st.session_state.df)

st.header("Switch Subset of Matches")

# Select subset to switch
with st.form(key='switch_form'):
    subset = st.multiselect(
        'Select the matches you want to switch:',
        options=st.session_state.df.index,
        format_func=lambda x: f"{st.session_state.df.at[x, 'Source']} → {st.session_state.df.at[x, 'Target']}"
    )
    submit_switch = st.form_submit_button(label='Switch Selected Matches')

if submit_switch and subset:
    switch_matches(subset)
    st.success(f"Switched matches for indices: {subset}")

st.header("Manual Match Selection")

# Display each row with a dropdown for manual matching
for idx in st.session_state.df.index:
    source = st.session_state.df.at[idx, 'Source']
    current_target = st.session_state.df.at[idx, 'Target']
    
    # Assume targets are unique for selection; adjust as needed
    possible_targets = st.session_state.df['Target'].unique().tolist()
    
    new_target = st.selectbox(
        f"Select target for '{source}':",
        options=possible_targets,
        index=possible_targets.index(current_target) if current_target in possible_targets else 0,
        key=f"select_{idx}"
    )
    
    if new_target != current_target:
        update_match(idx, new_target)
        st.success(f"Updated '{source}' to match with '{new_target}'")

st.header("Updated Matches")

st.dataframe(st.session_state.df)
