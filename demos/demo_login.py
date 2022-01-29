import streamlit as st
import pandas as pd
import keyring

# import os
# import platform
# import subprocess
# from functools import partial
# import getpass

# if platform.system().casefold() == "windows":
#     import pythoncom
#     import win32com.client
#     xl = win32com.client.Dispatch("Excel.Application", pythoncom.CoInitialize())

# user_name = getpass.getuser()
# pass_word = getpass.getpass()

def do_greeting():
    st.title("Greeting from Streamlit")

def do_data():
    st.header("df")
    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    })    
    st.dataframe(df)
    st.download_button("Download", data=df.to_csv(), mime="text/csv", file_name="my_df.csv")

def do_nothing():
    pass

def is_valid_cred(username, password):
    # system = platform.system().casefold()
    # validator = partial(subprocess.run, shell=True, check=True)
    # if system == "windows":
    #     proc = validator([
    #             "powershell.exe", "-command", 
    #             f'(new-object directoryservices.directoryentry "", {username}, {password}).psbase.name -ne $null'
    #             ], stdout=subprocess.PIPE)
    #     retcode = 0 if b"True" in proc.stdout else 1
    # elif system == "darwin":
    #     retcode = validator([f'dscl /Local/Default -authonly {username} {password}']).returncode
    # elif system == "linux":
    #     retcode = validator([f'su {username}'], input=password.encode())
    # else:
    #     raise OSError(f"unknown OS {system}")
    # return True if retcode == 0 else False
    pwd = keyring.get_password("login_app", username)
    return True if pwd is not None and pwd == password else False

def clear_login_form():
    # keyring.delete_password("login_app", st.session_state["username"])
    st.session_state["username"] = ""
    st.session_state["password"] = ""



menu_dict = {
    "Data": do_data,
    "Greet": do_greeting
}

def do_body():
    logged_in = is_valid_cred(st.session_state["username"], st.session_state["password"])
    

    if logged_in:
        menu_item = st.session_state["menu_item"]
        if menu_item == "____":
            do_nothing()

def do_sidebar():
    with st.sidebar.form(key="login_form"):
        username = st.text_input("Username", value="", key="username")
        password = st.text_input("Password", type="password", key="password")
        col1,col2,col3 = st.columns(3)
        with col1:
            if st.form_submit_button("Login"):
                logged_in = is_valid_cred(username,password)
                if not logged_in:
                    st.sidebar.text("Invalid cred")
        with col2:
            if st.form_submit_button("Logout", on_click=clear_login_form):
                logged_in = False
                # st.sidebar.text("Logged out")
        with col3:
            if st.form_submit_button("Signup"):
                keyring.set_password("login_app", username, password)
                logged_in = True
                st.sidebar.text("Thank you for signup")

    menu_item = st.empty()
    logged_in = is_valid_cred(st.session_state["username"], st.session_state["password"])
    if logged_in:
        st.sidebar.text("You are logged in")

        menu_option = ["____"] + list(menu_dict.keys())
        default_item = menu_option.index("____")
        menu_item = st.sidebar.selectbox("Select", menu_option, index=default_item, key="menu_item")
        if menu_item in menu_dict.keys():
            menu_dict[menu_item]()

    else:
        st.sidebar.text("You are not logged in")

def main():
    do_sidebar()
    do_body()

if __name__ == "__main__":
    main()
