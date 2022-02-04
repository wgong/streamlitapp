"""
$ pip install streamlit streamlit-option-menu streamlit-aggrid

- Bootstrap icons: 
    https://icons.getbootstrap.com/

- This app is inspired by the following streamlit contributors, Thank you!
    - streamlit-option-menu
    - streamlit-aggrid
    - https://discuss.streamlit.io/t/authentication-script/14111

"""
import streamlit as st
from streamlit_option_menu import option_menu
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode


import sqlite3 as sql
import hashlib
import pandas as pd

_DB_NAME = "users.db"

# Aggrid options
grid_dict = {
    "grid_height": 300,
    "return_mode_value": DataReturnMode.__members__["FILTERED"],
    "update_mode_value": GridUpdateMode.__members__["MODEL_CHANGED"],
    "fit_columns_on_grid_load": True,
    "selection_mode": "single",  # "multiple",
    "fit_columns_on_grid_load": True,
    "allow_unsafe_jscode": True,
    "groupSelectsChildren": True,
    "groupSelectsFiltered": True,
    "enable_pagination": True,
    "paginationPageSize": 8,


}

def _hashit(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def get_users(conn):
    select_sql = """
        select username,password,su,notes from users
    """
    return pd.read_sql(select_sql, conn)

## Read
def _read_users(conn, context="read"):
    # return selected_df

    enable_selection=True if context in ["update", "delete"] else False

    df = get_users(conn)

    ## grid options
    gb = GridOptionsBuilder.from_dataframe(df)
    if enable_selection:
        gb.configure_selection(grid_dict["selection_mode"],
                use_checkbox=True,
                groupSelectsChildren=grid_dict["groupSelectsChildren"], 
                groupSelectsFiltered=grid_dict["groupSelectsFiltered"]
            )
    gb.configure_pagination(paginationAutoPageSize=False, 
        paginationPageSize=grid_dict["paginationPageSize"])
    gb.configure_grid_options(domLayout='normal')
    grid_response = AgGrid(
        df, 
        gridOptions=gb.build(),
        height=grid_dict["grid_height"], 
        # width='100%',
        data_return_mode=grid_dict["return_mode_value"],
        update_mode=grid_dict["update_mode_value"],
        fit_columns_on_grid_load=grid_dict["fit_columns_on_grid_load"],
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
    )

    if enable_selection:
        selected_df = pd.DataFrame(grid_response['selected_rows'])
        return selected_df
    else:
        return None

## Create
def clear_add_form():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        user_ = st.session_state["add_username"]
        pass_ = st.session_state["add_password"]
        if user_ and pass_:
            su_ = st.session_state["add_su"]
            notes_ = st.session_state["add_notes"]
            conn.execute(
                "INSERT INTO USERS(username, password, su, notes) VALUES(?,?,?,?)",
                (user_, _hashit(pass_), su_, notes_),
            )

    st.session_state["add_username"] = ""
    st.session_state["add_password"] = ""
    st.session_state["add_su"] = False
    st.session_state["add_notes"] = ""

def _create_users(conn):

    _read_users(conn, context="create")
    with st.form(key="add_user"):
        st.text_input("Username (required)", key="add_username")
        st.text_input("Password (required)", key="add_password")
        st.checkbox("Is a superuser?", value=False, key="add_su")
        st.text_area('Notes', key="add_notes")
        st.form_submit_button('Add', on_click=clear_add_form)
     

## Update
def clear_upd_form():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        username_ = st.session_state["upd_username"]
        pass_ = st.session_state["upd_password"]
        su_ = st.session_state["upd_su"]
        notes_ = st.session_state["upd_notes"]
        conn.execute(
                "update users set password = ?,su = ?, notes = ? where username = ?", (_hashit(pass_),su_,notes_,username_)
            )

    st.session_state["upd_username"] = ""
    st.session_state["upd_password"] = ""
    st.session_state["upd_su"] = False
    st.session_state["upd_notes"] = ""

def _update_users(conn):
    selected_df = _read_users(conn, context="update")
    # st.dataframe(selected_df)
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key="upd_user"):
                st.text_input("Username:", value=row["username"][0], key="upd_username")
                st.text_input("Password:", value=row["password"][0], key="upd_password")
                st.checkbox("Is superuser?", value=row["su"][0], key="upd_su")
                st.text_area('Notes', value=row["notes"][0], key="upd_notes")
                st.form_submit_button('Update', on_click=clear_upd_form)


## Delete
def clear_del_form():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        username_ = st.session_state["del_username"]
        conn.execute(
                "delete from users where username = ?", (username_,)
            )

    st.session_state["del_username"] = ""


def _delete_users(conn):
    selected_df = _read_users(conn, context="delete")
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key="del_user"):
                st.text_input("Username:", value=row["username"][0], key="del_username")
                st.form_submit_button('Delete', on_click=clear_del_form)


def _manage_db():
    create_table = """create table if not exists users (
        id INTEGER PRIMARY KEY,
        username UNIQUE ON CONFLICT REPLACE, 
        password, 
        su, 
        notes
    );"""
    db_name = st.text_input('SQLite database name', value=_DB_NAME, key="db_name")
    ddl_sql = st.text_area("DDL SQL", height=250, value=create_table, key="ddl_sql")
    if st.button("Execute"):
        with sql.connect(f"file:{db_name}?mode=rwc", uri=True) as conn:
            conn.execute(ddl_sql)

    with st.expander("Show code"):
        with open(__file__) as f:
            # st.code(inspect.getsource(do_widget))
            st.code(f.read())            

def _manage_users():

    # use option-menu
    actions = list(action_dict.keys())
    icons = [action_dict[i]["icon"] for i in actions]
    action = option_menu(None, actions, 
        icons=icons, 
        menu_icon="cast", 
        default_index=0, 
        orientation="horizontal")

    # # horizontal radio buttons
    # # https://discuss.streamlit.io/t/horizontal-radio-buttons/2114/7
    # st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
    # st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    # action = st.radio("Operation: ", action_dict.keys())
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        action_dict[action]["fn"](conn)


# icons : https://icons.getbootstrap.com/

meta_dict = {
    "Table": {"fn": _manage_users, "icon": "file-spreadsheet"}, 
    "Database": {"fn": _manage_db, "icon": "box"}, 
}

action_dict =  {
    "View": {"fn": _read_users, "icon": "list-task"}, 
    "Add": {"fn": _create_users, "icon": "plus-square"},
    "Update": {"fn": _update_users, "icon": "pencil-square"},
    "Delete": {"fn": _delete_users, "icon": "shield-fill-x"},
}


if __name__ == "__main__":
    objects = list(meta_dict.keys())
    icons = [meta_dict[i]["icon"] for i in objects]
    with st.sidebar:
        action = option_menu("Manage", objects, 
            icons=icons, 
            menu_icon="columns-gap", 
            default_index=0)

        if st.checkbox('view source'):
            with open(__file__) as f:
                st.code(f.read())

    if action:
        meta_dict[action]["fn"]()
