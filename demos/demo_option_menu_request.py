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

def do_home():
    st.write("home is where the heart is")

def do_setting():
    st.write("settings is my bettings")

menu_dict = {
    "Home" : {"fn": do_home},
    "Settings" : {"fn": do_setting},
}

selected = option_menu(None, 
    ["Home", "Settings"], 
    icons=["house", "gear"],
    default_index=0,
    orientation="horizontal")

if selected in menu_dict.keys():
    menu_dict[selected]["fn"]()

