"""
$ pip install streamlit streamlit-option-menu streamlit-aggrid

- Bootstrap icons: 
    https://icons.getbootstrap.com/

- This app builds on the following streamlit contributions, Thank you!
    - streamlit-option-menu
    - streamlit-aggrid


## TODO

- parse table schema to get column name/type and build create/update form programmatically

SELECT 
    sql
FROM 
    sqlite_schema
WHERE 
    type ='table'

"""
import streamlit as st
from streamlit_option_menu import option_menu
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode


import sqlite3 as sql
import hashlib
import pandas as pd


# Initial page config
st.set_page_config(
     page_title='Streamlit DB CRUD Demo',
     layout="wide",
     initial_sidebar_state="expanded",
)

# constants
_DEBUG_ = True # False # 
_KEY_PFX_SHOW = "show_"
_KEY_PFX_ADD = "add_"
_KEY_PFX_UPD = "upd_"
_KEY_PFX_DEL = "del_"

_DISABLED_FLAG = {
    "create": False,
    "update": False,
    "show": True,
    "delete": True,
}

_DB_NAME = "users.db"

_SQL_SELECT_TABLE_NAME = """
        SELECT 
        name
    FROM 
        sqlite_schema
    WHERE 
        type ='table'
        order by name
"""

_SQL_CREATE_TABLE = """create table if not exists users (
    id INTEGER PRIMARY KEY,
    username UNIQUE ON CONFLICT REPLACE, 
    password, 
    su, 
    notes
);"""

# Aggrid options
_GRID_OPTIONS = {
    "grid_height": 250,
    "return_mode_value": DataReturnMode.__members__["FILTERED"],
    "update_mode_value": GridUpdateMode.__members__["MODEL_CHANGED"],
    "fit_columns_on_grid_load": True,
    "selection_mode": "single",  # "multiple",
    "fit_columns_on_grid_load": True,
    "allow_unsafe_jscode": True,
    "groupSelectsChildren": True,
    "groupSelectsFiltered": True,
    "enable_pagination": True,
    "paginationPageSize": 6,
}

# @st.experimental_singleton
# def sql_connect(db_name, mode="rw"):
#     return sql.connect(f"file:{db_name}?mode={mode}", uri=True)
#
# will give this error:
# ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 3484 and this is thread id 9876.
def _log_msg(msg):
    if _DEBUG_:
        st.info(msg)

def _hash_it(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def _get_records(conn, table_name, limit=10000):
    sql_stmt = f"""
        select * from {table_name} limit {limit}
    """
    return pd.read_sql(sql_stmt, conn)

def _prepare_grid(conn, table_name, context=None):
    enable_selection=True if context in ["read", "update", "delete"] else False
    df = _get_records(conn, table_name)
    gb = GridOptionsBuilder.from_dataframe(df)
    if enable_selection:
        gb.configure_selection(_GRID_OPTIONS["selection_mode"],
                use_checkbox=True,
                groupSelectsChildren=_GRID_OPTIONS["groupSelectsChildren"], 
                groupSelectsFiltered=_GRID_OPTIONS["groupSelectsFiltered"]
            )
    gb.configure_pagination(paginationAutoPageSize=False, 
        paginationPageSize=_GRID_OPTIONS["paginationPageSize"])
    gb.configure_grid_options(domLayout='normal')
    grid_response = AgGrid(
        df, 
        gridOptions=gb.build(),
        height=_GRID_OPTIONS["grid_height"], 
        # width='100%',
        data_return_mode=_GRID_OPTIONS["return_mode_value"],
        update_mode=_GRID_OPTIONS["update_mode_value"],
        fit_columns_on_grid_load=_GRID_OPTIONS["fit_columns_on_grid_load"],
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
    )

    if enable_selection:
        selected_df = pd.DataFrame(grid_response['selected_rows'])
        return selected_df
    else:
        return None

## Full-text Search
def clear_find_form():
    pass

def _search_record(conn, table_name):
    _prepare_grid(conn, table_name, context="search")

    with st.form(key="find_user"):
        st.text_input("Phrase:", value="", key="find_phrase")
        st.form_submit_button('Search', on_click=clear_find_form)

def _default_val(row, col_name):
    return "" if row is None else row[col_name][0]

def _clear_form_users(key_pfx):
    st.session_state[f"{key_pfx}username"] = ""
    st.session_state[f"{key_pfx}password"] = ""
    st.session_state[f"{key_pfx}su"] = False
    st.session_state[f"{key_pfx}notes"] = ""

def _gen_form_users(key_pfx, ctx, row=None):
    if ctx != "create":
        st.write(f'id: {_default_val(row, "id")}')
    _log_msg(f"key_pfx={key_pfx}, ctx={ctx}, disabled={_DISABLED_FLAG[ctx]}")
    st.text_input("Username(*)", value=_default_val(row, "username"), key=f"{key_pfx}username", disabled=_DISABLED_FLAG[ctx])
    st.text_input("Password(*)", value=_default_val(row, "password"), key=f"{key_pfx}password", disabled=_DISABLED_FLAG[ctx])
    st.checkbox("Is a superuser?", value=_default_val(row, "su"), key=f"{key_pfx}su", disabled=_DISABLED_FLAG[ctx])
    st.text_area('Notes', value=_default_val(row, "notes"), key=f"{key_pfx}notes", disabled=_DISABLED_FLAG[ctx])

## callback for Create
def _clear_form_add_users(*args, **kwargs):
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else ""
    if not table_name:
        st.error("No table is selected!")

    # st.write(f"kwargs: {kwargs}")
    key_pfx = kwargs.get("key_pfx", _KEY_PFX_ADD)
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        user_ = st.session_state[f"{key_pfx}username"]
        pass_ = st.session_state[f"{key_pfx}password"]
        if user_ and pass_:
            su_ = st.session_state[f"{key_pfx}su"]
            notes_ = st.session_state[f"{key_pfx}notes"]
            conn.execute(
                f"INSERT INTO {table_name} (username, password, su, notes) VALUES(?,?,?,?)",
                (user_, _hash_it(pass_), su_, notes_),
            )
        else:
            st.error(f"required inputs are missing")

    _clear_form_users(key_pfx)

## callback for Update
def _clear_form_upd_users(*args, **kwargs):
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else ""
    if not table_name:
        st.error("No table is selected!")

    key_pfx = kwargs.get("key_pfx", _KEY_PFX_UPD)   
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        username_ = st.session_state[f"{key_pfx}username"]
        pass_ = st.session_state[f"{key_pfx}password"]
        su_ = st.session_state[f"{key_pfx}su"]
        notes_ = st.session_state[f"{key_pfx}notes"]
        conn.execute(
                f"update {table_name} set password = ?,su = ?, notes = ? where username = ?", (_hash_it(pass_),su_,notes_,username_)
            )

    _clear_form_users(key_pfx)


## callback for Delete
def _clear_form_del_users(*args, **kwargs):
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else ""
    if not table_name:
        st.error("No table is selected!")
    key_pfx = kwargs.get("key_pfx", _KEY_PFX_DEL)
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        username_ = st.session_state[f"{key_pfx}username"]
        conn.execute(
                f"delete from {table_name} where username = ?", (username_,)
            )

    _clear_form_users(key_pfx)

## Create
def _create_record(conn, table_name, key_pfx=_KEY_PFX_ADD):
    selected_df = _prepare_grid(conn, table_name, context="create")
    with st.form(key=f"{key_pfx}{table_name}"):
        _gen_form_users(key_pfx, "create")
        st.form_submit_button('Add', on_click=_clear_form_add_users, kwargs={"key_pfx": key_pfx})
## Read
def _show_record(conn, table_name, key_pfx=_KEY_PFX_SHOW):
    selected_df = _prepare_grid(conn, table_name, context="read")
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            _gen_form_users(key_pfx, "show", row=row)
## Update   
def _update_record(conn, table_name, key_pfx=_KEY_PFX_UPD):
    selected_df = _prepare_grid(conn, table_name, context="update")
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key=f"{key_pfx}{table_name}"):
                _gen_form_users(key_pfx, "update", row=row)
                st.form_submit_button('Update', on_click=_clear_form_upd_users)
## Delete
def _delete_record(conn, table_name, key_pfx=_KEY_PFX_DEL):
    selected_df = _prepare_grid(conn, table_name, context="delete")
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key=f"{key_pfx}{table_name}"):
                _gen_form_users(key_pfx, "delete", row=row)
                st.form_submit_button('Delete', on_click=_clear_form_del_users)


def _manage_table(table_name):
    # # horizontal radio buttons
    # # https://discuss.streamlit.io/t/horizontal-radio-buttons/2114/7
    # st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
    # st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
    # action = st.radio("Operation: ", action_dict.keys())

    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        # use option-menu
        actions = list(action_dict.keys())
        icons = [action_dict[i]["icon"] for i in actions]
        action = option_menu(None, actions, 
            icons=icons, 
            menu_icon="cast", 
            default_index=0, 
            orientation="horizontal", key=f"table_{table_name}")        
        action_dict[action]["fn"](conn, table_name)

def _manage_db():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    sql_stmt = st.text_area("SQL commands", height=250, value=_SQL_CREATE_TABLE, key="sql_stmt")
    if st.button("Execute"):
        with sql.connect(f"file:{db_name}?mode=rwc", uri=True) as conn:
            if sql_stmt.strip().lower().startswith("select"):
                df = pd.read_sql(sql_stmt, conn)
                st.dataframe(df)
            else:
                res = conn.execute(sql_stmt)
                st.write(res)
    if False:                
        st.image("background_body.png")
        with st.expander("view code"):
            with open(__file__) as f:
                # st.code(inspect.getsource(do_widget))
                st.code(f.read()) 

meta_dict = {
    "Database": {"fn": _manage_db, "icon": "box"}, 
    "Tables": {"fn": _manage_table, "icon": "file-spreadsheet"}, 
}

action_dict =  {
    "View": {"fn": _show_record, "icon": "list-task"}, 
    # "Search": {"fn": _search_record, "icon": "search"},
    "Add": {"fn": _create_record, "icon": "plus-square"},
    "Edit": {"fn": _update_record, "icon": "pencil-square"},
    "Delete": {"fn": _delete_record, "icon": "shield-fill-x"},
}
# SQLite Full-text search requires creating separate virtual table
# One may use trigger to populate the virtual table with data to search
# Design virtual table such that : table_name, row_key, full_text
# where full_text has this format: [col_name_1] col_value_1; ...; [col_name_N] col_value_N
# From search page, one links search result to its source table

def do_sidebar():
    objects = list(meta_dict.keys())
    icons = [meta_dict[i]["icon"] for i in objects]

    with st.sidebar:
        action = option_menu("Manage", objects, 
            icons=icons, 
            menu_icon="columns-gap", 
            default_index=objects.index("Database"),
            key="menu_action")


        c1, c2 = st.columns([1,4])
        with c1:
            pass
        with c2:

            db_name = st.text_input('SQLite database', value=_DB_NAME, key="db_name")    
            if action == "Tables":            
                conn = sql.connect(f"file:{db_name}?mode=rw", uri=True)
                df = pd.read_sql(_SQL_SELECT_TABLE_NAME, conn)
                table_name = st.selectbox("Table:", df["name"].to_list(), key="table_name")


        st.image("background_sidebar.png")

        if st.checkbox('view code'):
            with open(__file__) as f:
                st.code(f.read())

def do_body():
    action = st.session_state["menu_action"] if "menu_action" in st.session_state and st.session_state["menu_action"] else "Database"

    _log_msg(f"action={action}")
    if action == "Database":
        meta_dict[action]["fn"]()
    elif action == "Tables":
        table_name = st.session_state["table_name"] if "table_name" in st.session_state and st.session_state["table_name"] else "users"
        _log_msg(f"table_name={table_name}")
        meta_dict[action]["fn"](table_name)

if __name__ == "__main__":
    do_sidebar()
    do_body()
