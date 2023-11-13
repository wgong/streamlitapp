"""
bard.google.com 

"""

import pandas as pd
import streamlit as st


st.title("Demo Pagination")
# Load data
data = pd.read_csv('data/generic-food.csv')

c1, c2, c3, c4, _, c5 = st.columns([2,2,2,2,1,2])
# Create an input field for page size
with c5:
    page_size = st.number_input('Page Size', min_value=1, value=10, step=5)

# Create a session state to store the current page number
if "page" not in st.session_state:
    st.session_state['page'] = 0

# Get the current page number
page_number = st.session_state['page']
at_begin = (page_number<=0)
at_end = (page_number + 1 >= len(data) // page_size + 1)

# Create buttons for navigating to previous, next, first, and last pages
with c1:
    if st.button('First <<', disabled=at_begin):
        st.session_state['page'] = 0
with c2:
    if st.button('Prev <', disabled=at_begin):
        st.session_state['page'] -= 1
with c3:
    if st.button('Next >', disabled=at_end):
        st.session_state['page'] += 1
with c4:
    if st.button('Last >>', disabled=at_end):
        st.session_state['page'] = len(data) // page_size


# Calculate the starting and ending indices for the current page
start_index = page_number * page_size
end_index = start_index + page_size

# Get the data for the current page
page_data = data[start_index:end_index]

# Display the data for the current page
st.dataframe(page_data)

