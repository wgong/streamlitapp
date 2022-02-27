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

import os.path
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
_DEBUG_ = False # True # 

# CRUD form config dict
_FORM_CONFIG = {
    "view": {"read_only": True, "key_pfx": "view", "selectable": True},
    "create": {"read_only": False, "key_pfx": "add", "selectable": False},
    "update": {"read_only": False, "key_pfx": "upd", "selectable": True},
    "delete": {"read_only": True, "key_pfx": "del", "selectable": True},
}

_DB_NAME = "journals.db"



_SQL_SELECT_TABLE_NAME = """
SELECT 
    name
FROM 
    sqlite_schema
WHERE 
    type ='table'
    order by name
;
"""

_FILE_SCHEMA = "schema.sql"
if os.path.exists(_FILE_SCHEMA):
    _SQL_CREATE_TABLES = open(_FILE_SCHEMA).read()
else:
    _SQL_CREATE_TABLES = """
create table if not exists s_user (
    id INTEGER PRIMARY KEY,
    username UNIQUE ON CONFLICT REPLACE, 
    password, 
    notes,
    flag_admin
);
"""

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

## helper functions
def _log_msg(msg):
    if _DEBUG_:
        st.info(msg)

def _hash_it(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def _get_records(conn, table_name, limit=1000):
    sql_stmt = f"""
        select * from {table_name} limit {limit};
    """
    return pd.read_sql(sql_stmt, conn)

def _prepare_grid(conn, table_name, context=None):
    # enable_selection=True if context in ["view", "update", "delete"] else False
    enable_selection = _FORM_CONFIG[context]["selectable"]
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

def _gen_key(key_pfx, table_name, key_name=""):
    return f"{key_pfx}_{table_name}_{key_name}"

def _default_val(row, col_name):
    return "" if row is None else row[col_name][0]


## ================================ customize BELOW for each table to be added ========================================
_SCHEMA_DICT = {
    "s_user" : ["username", "password", "notes", "flag_admin"],
    "s_person" : ["full_name", "email", "phone", "notes", 'url_twit', 'url_fb', 'address', 'related_persons', 'attachments', 'flag_active', 'added_at', 'edited_at', 'added_by', 'edited_by'],
}

def _get_form_state(key_pfx, table_name):
    form_data = {}
    if table_name in ["s_user", "s_person"]:
        for col in _SCHEMA_DICT[table_name]:
            form_key = _gen_key(key_pfx, table_name, col)
            form_data[col] = st.session_state[form_key] if form_key in st.session_state  else ""
    return form_data


def _clear_form(key_pfx, table_name):

    for col in _SCHEMA_DICT[table_name]:
        form_key = _gen_key(key_pfx, table_name, col)
        if form_key in st.session_state:
            st.session_state[_gen_key(key_pfx, table_name, col)] = False if col.startswith("flag_") else ""

def _generate_form(ctx, row=None):
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else "s_user"
    key_pfx = _FORM_CONFIG[ctx]["key_pfx"]
    if ctx != "create":
        st.write(f'id: {_default_val(row, "id")}')
    
    _disabled = _FORM_CONFIG[ctx]["read_only"]
    _log_msg(f"table_name={table_name}, key_pfx={key_pfx}, ctx={ctx}, disabled={_disabled}")
    if table_name == "s_user":
        st.text_input("Username(*)", value=_default_val(row, "username"), key=_gen_key(key_pfx, table_name, "username"), disabled=_disabled)
        st.text_input("Password(*)", value=_default_val(row, "password"), key=_gen_key(key_pfx, table_name, "password"), disabled=_disabled)
        st.text_area('Notes', value=_default_val(row, "notes"), key=_gen_key(key_pfx, table_name, "notes"), disabled=_disabled)
        st.checkbox("Is admin?", value=_default_val(row, "flag_admin"), key=_gen_key(key_pfx, table_name, "flag_admin"), disabled=_disabled)
    elif table_name == "s_person":
        st.text_input("Full name(*)", value=_default_val(row, "full_name"), key=_gen_key(key_pfx, table_name, "full_name"), disabled=_disabled)
        st.text_input("Email(s)", value=_default_val(row, "email"), key=_gen_key(key_pfx, table_name, "email"), disabled=_disabled)
        st.text_input("Phone number(s)", value=_default_val(row, "phone"), key=_gen_key(key_pfx, table_name, "phone"), disabled=_disabled)
        st.text_area('Notes', value=_default_val(row, "notes"), key=_gen_key(key_pfx, table_name, "notes"), disabled=_disabled)
        st.text_input("Twitter link", value=_default_val(row, "url_twit"), key=_gen_key(key_pfx, table_name, "url_twit"), disabled=_disabled)
        st.text_input("Facebook link", value=_default_val(row, "url_fb"), key=_gen_key(key_pfx, table_name, "url_fb"), disabled=_disabled)
        st.text_area('Address', value=_default_val(row, "address"), key=_gen_key(key_pfx, table_name, "address"), disabled=_disabled)
        st.text_area('Related person(s)', value=_default_val(row, "related_persons"), key=_gen_key(key_pfx, table_name, "related_persons"), disabled=_disabled)


## callback for Create
def _clear_form_add_(*args, **kwargs):
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else "s_user"
    # st.write(f"kwargs: {kwargs}")
    key_pfx = kwargs.get("key_pfx")
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        if table_name == "s_user":
            form_data = _get_form_state(key_pfx, table_name)
            username = form_data["username"]
            password = form_data["password"]
            if username and password:
                notes = form_data["notes"]
                flag_admin = form_data["flag_admin"]
                conn.execute(
                    f"INSERT INTO {table_name} (username, password, notes, flag_admin) VALUES(?,?,?,?)",
                    (username, _hash_it(password), notes, flag_admin),
                )
            else:
                st.error(f"required inputs are missing")

        elif table_name == "s_person":
            form_data = _get_form_state(key_pfx, table_name)
            full_name = form_data["full_name"]
            if full_name:
                email = form_data["email"]
                phone = form_data["phone"]
                notes = form_data["notes"]
                url_twit = form_data["url_twit"]
                url_fb = form_data["url_fb"]
                address = form_data["address"]
                related_persons = form_data["related_persons"]
                conn.execute(
                    f"""INSERT INTO {table_name} (full_name, email, phone, notes, url_twit, url_fb, address, related_persons) 
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                    (full_name, email, phone, notes, url_twit, url_fb, address, related_persons),
                )
            else:
                st.error(f"required inputs are missing")


        _clear_form(key_pfx, table_name)


## callback for Update
def _clear_form_upd_(*args, **kwargs):
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else "s_user"
    key_pfx = kwargs.get("key_pfx")   
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        if table_name == "s_user": 
            form_data = _get_form_state(key_pfx, table_name)       
            username = form_data["username"]
            password = form_data["password"]
            notes = form_data["notes"]
            flag_admin = form_data["flag_admin"]
            conn.execute(
                    f"""update {table_name} set password = ?, notes = ?, flag_admin = ? where username = ?""", 
                    (_hash_it(password),notes,flag_admin,username)
                )
        elif table_name == "s_person": 
            form_data = _get_form_state(key_pfx, table_name)       
            full_name = form_data["full_name"]
            email = form_data["email"]
            phone = form_data["phone"]
            notes = form_data["notes"]
            url_twit = form_data["url_twit"]
            url_fb = form_data["url_fb"]
            address = form_data["address"]
            related_persons = form_data["related_persons"]

            conn.execute(
                    f"""update {table_name} set email = ?, phone = ?, notes = ?, url_twit = ?, url_fb = ?, address = ? , related_persons = ?
                    where full_name = ?""", 
                    (email, phone , notes , url_twit , url_fb , address, related_persons, full_name)
                )

        _clear_form(key_pfx, table_name)


## callback for Delete
def _clear_form_del_(*args, **kwargs):
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else "s_user"
    key_pfx = kwargs.get("key_pfx")
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        if table_name == "s_user":  
            form_data = _get_form_state(key_pfx, table_name)           
            username = form_data["username"]
            conn.execute(
                    f"delete from {table_name} where username = ?", (username,)
                )
        elif table_name == "s_person":  
            form_data = _get_form_state(key_pfx, table_name)           
            full_name = form_data["full_name"]
            conn.execute(
                    f"delete from {table_name} where full_name = ?", (full_name,)
                )

        _clear_form(key_pfx, table_name)

## ================================ customize ABOVE for each table to be added ========================================


## Create
def _create_record(conn, table_name):
    ctx = "create"
    key_pfx = _FORM_CONFIG[ctx]["key_pfx"]
    selected_df = _prepare_grid(conn, table_name, context=ctx)
    with st.form(key=_gen_key(key_pfx, table_name)): 
        _generate_form(ctx)
        st.form_submit_button('Add', on_click=_clear_form_add_, kwargs={"key_pfx": key_pfx})
## view
def _view_record(conn, table_name):
    ctx = "view"
    selected_df = _prepare_grid(conn, table_name, context=ctx)
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            _generate_form(ctx, row=row)
## Update   
def _update_record(conn, table_name):
    ctx = "update"
    key_pfx = _FORM_CONFIG[ctx]["key_pfx"]    
    selected_df = _prepare_grid(conn, table_name, context=ctx)
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key=_gen_key(key_pfx, table_name)):
                _generate_form(ctx, row=row)
                st.form_submit_button('Update', on_click=_clear_form_upd_, kwargs={"key_pfx": key_pfx})
## Delete
def _delete_record(conn, table_name):
    ctx = "delete"
    key_pfx = _FORM_CONFIG[ctx]["key_pfx"]        
    selected_df = _prepare_grid(conn, table_name, context=ctx)
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key=_gen_key(key_pfx, table_name)):
                _generate_form(ctx, row=row)
                st.form_submit_button('Delete', on_click=_clear_form_del_, kwargs={"key_pfx": key_pfx})


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
    sql_stmts = st.text_area("SQL commands", height=250, value=_SQL_CREATE_TABLES, key="sql_stmt")
    if st.button("Execute"):
        with sql.connect(f"file:{db_name}?mode=rwc", uri=True) as conn:
            if sql_stmts.strip().lower().startswith("select"):
                df = pd.read_sql(sql_stmts, conn)
                st.dataframe(df)
            else:
                for sql_stmt in sql_stmts.split(";"):
                    if not sql_stmt.strip():
                        continue
                    res = conn.execute(sql_stmt)
                    st.write(res)
    if False:                
        st.image("https://user-images.githubusercontent.com/329928/155828764-b19a08e4-5346-4567-bba0-0ceeb5c2b241.png")
        with st.expander("view code"):
            with open(__file__) as f:
                # st.code(inspect.getsource(do_widget))
                st.code(f.read()) 

meta_dict = {
    "Database": {"fn": _manage_db, "icon": "box"}, 
    "Tables": {"fn": _manage_table, "icon": "file-spreadsheet"}, 
}

action_dict =  {
    "View": {"fn": _view_record, "icon": "list-task"}, 
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


        st.image("https://user-images.githubusercontent.com/329928/155828764-b19a08e4-5346-4567-bba0-0ceeb5c2b241.png")

        if st.checkbox('view code'):
            with open(__file__) as f:
                st.code(f.read())

def do_body():
    action = st.session_state["menu_action"] if "menu_action" in st.session_state and st.session_state["menu_action"] else "Database"

    _log_msg(f"action={action}")
    if action == "Database":
        meta_dict[action]["fn"]()
    elif action == "Tables":
        table_name = st.session_state["table_name"] if "table_name" in st.session_state and st.session_state["table_name"] else "s_user"
        _log_msg(f"table_name={table_name}")
        meta_dict[action]["fn"](table_name)

if __name__ == "__main__":
    do_sidebar()
    do_body()
