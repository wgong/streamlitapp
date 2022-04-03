"""
- streamlit-option-menu:
    https://discuss.streamlit.io/t/streamlit-option-menu-is-a-simple-streamlit-component-that-allows-users-to-select-a-single-item-from-a-list-of-options-in-a-menu/20514/20

- Bootstrap icons: 
    https://icons.getbootstrap.com/

    $ npm i bootstrap-icons

- upgrade from 0.2.10 to 0.3.2 on 2022-03-27

    $ pip install --upgrade streamlit-option-menu
"""

import streamlit as st
from streamlit_option_menu import option_menu

# Initial page config
st.set_page_config(
     page_title="demo streamlit-option-menu",
     layout="wide",
     initial_sidebar_state="expanded",
)

with st.sidebar:
    selected = option_menu("Menu", ["Home", "Horizontal", "Settings"], 
        icons=["house", "arrow-bar-right", "gear"], menu_icon="cast", 
        default_index=0)

if selected == "Home":
    st.write("home is where the heart is")
elif selected == "Horizontal":
    selected2 = option_menu(None, ["Upload", "Tasks", "Settings"], 
        icons=["cloud-upload", "list-task", "gear"], 
        menu_icon="cast", 
        default_index=0, 
        orientation="horizontal")
    selected2
else:
    st.write("settings is my bettings")

    st.info("upgrade from 0.2.10 to 0.3.2 on 2022-03-27")
    selected3 = option_menu(None, 
        ["Home", "Upload",  "Tasks", 'Settings'], 
        icons=['house', 'cloud-upload', "list-task", 'gear'], 
        menu_icon="cast", 
        default_index=0, 
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "25px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "green"},
        }
    )
