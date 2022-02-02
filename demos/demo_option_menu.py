"""
- streamlit-option-menu:
    https://discuss.streamlit.io/t/streamlit-option-menu-is-a-simple-streamlit-component-that-allows-users-to-select-a-single-item-from-a-list-of-options-in-a-menu/20514/20

- Bootstrap icons: 
    https://icons.getbootstrap.com/

    $ npm i bootstrap-icons
"""

import streamlit as st
from streamlit_option_menu import option_menu

with st.sidebar:
    selected = option_menu("Menu", ["Home", "Horizontal", "Settings"], 
        icons=["house", "arrow-bar-right", "gear"], menu_icon="cast", 
        default_index=0)

if selected == "Home":
    st.write("home is where the heart is")
elif selected == "Horizontal":
    selected2 = option_menu(None, ["Upload", "Tasks", "Settings"], 
        icons=["cloud-upload", "list-task", "gear"], menu_icon="cast", 
        default_index=0, orientation="horizontal")
    selected2
else:
    st.write("settings is my bettings")
