"""
$ pip install streamlit streamlit-option-menu streamlit-aggrid

- Bootstrap icons: 
    https://icons.getbootstrap.com/

- This app builds on the following streamlit contributions, Thank you!
    - streamlit-option-menu
    - streamlit-aggrid


## TODO - streamlit-crud

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
import re


# Initial page config
st.set_page_config(
     page_title='Streamlit CRUD Demo',
     layout="wide",
     initial_sidebar_state="expanded",
)



# constants
_DEBUG_ = False # True # 
_IS_ADMIN = False # True # 

# strings for i8n
_STR_MENU_TITLE = "Streamlit CRUD"
_STR_MENU_DATABASE = "Database"
_STR_MENU_TABLES = "Tables"
_STR_ACTION_VIEW = "View"
_STR_ACTION_ADD = "Add"
_STR_ACTION_EDIT = "Edit"
_STR_ACTION_DELETE = "Delete"
_STR_BUTTON_DELETE = "Delete"
_STR_BUTTON_CREATE = "Create"
_STR_BUTTON_UPDATE = "Update"
_STR_BUTTON_EXECUTE = "Execute"

# CRUD form config dict
_FORM_CONFIG = {
    "view": {"read_only": True, "key_pfx": "view", "selectable": True},
    "create": {"read_only": False, "key_pfx": "add", "selectable": False},
    "update": {"read_only": False, "key_pfx": "upd", "selectable": True},
    "delete": {"read_only": True, "key_pfx": "del", "selectable": True},
}

_DB_NAME = "journals.db"
_FILE_SCHEMA = "schema_create.sql"
_BAD_SQL_PAT = re.compile('\s*(drop|delete)\s+')
_COLS_PAT = re.compile('\((.*)\)')

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
    "fit_columns_on_grid_load": False,
    "selection_mode": "single",  # "multiple",
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

@st.experimental_memo
def _prepare_table_list():
    if "TABLE_LIST" in st.session_state:
        return st.session_state["TABLE_LIST"]

    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        df = pd.read_sql(_SQL_SELECT_TABLE_NAME, conn)
        st.session_state["TABLE_LIST"] = df["name"].to_list()

    return st.session_state["TABLE_LIST"]

@st.experimental_memo
def _prepare_table_column_dict():
    if "SCHEMA_DICT" in st.session_state:
        return st.session_state["SCHEMA_DICT"]

    tab_col_dic = {}
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        for table in _prepare_table_list():
            df2 = pd.read_sql(f"""
                    SELECT sql FROM sqlite_schema where type = 'table' and name='{table}';
                """, conn)
            sqls = df2["sql"].to_list()
            if sqls:
                matched = _COLS_PAT.findall(sqls[0].replace('\n', ''))
                if matched:
                    tab_col_dic[table] = [c.strip().split()[0] for c in matched[0].split(",") if c.strip()]
    st.session_state["SCHEMA_DICT"] = tab_col_dic
    return st.session_state["SCHEMA_DICT"] 

def _query_records(conn, table_name, limit=1000):
    sql_stmt = f"""
        select * from {table_name} limit {limit};
    """
    return pd.read_sql(sql_stmt, conn)


def _prepare_grid(conn, table_name, context=None):
    # enable_selection=True if context in ["view", "update", "delete"] else False
    enable_selection = _FORM_CONFIG[context]["selectable"]
    df = _query_records(conn, table_name)
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

# ## Full-text Search
# def clear_find_form():
#     pass

# def _search_record(conn, table_name):
#     _prepare_grid(conn, table_name, context="search")

#     with st.form(key="find_user"):
#         st.text_input("Phrase:", value="", key="find_phrase")
#         st.form_submit_button('Search', on_click=clear_find_form)

def _gen_key(key_pfx, table_name, key_name=""):
    return f"{key_pfx}_{table_name}_{key_name}"

def _default_val(row, col_name):
    return "" if row is None else row[col_name][0]

## ================================ customize BELOW for each table to be added ========================================

def _form__read(key_pfx, table_name):
    # fetch form field values and store them into form_data dict
    _SCHEMA_DICT = _prepare_table_column_dict()
    form_data = {}
    if table_name in ["s_user", "s_person"]:
        for col in _SCHEMA_DICT[table_name]:
            form_key = _gen_key(key_pfx, table_name, col)
            form_data[col] = st.session_state[form_key] if form_key in st.session_state  else ""
    return form_data

def _form__clear(key_pfx, table_name):
    _SCHEMA_DICT = _prepare_table_column_dict()
    # clear form
    for col in _SCHEMA_DICT[table_name]:
        form_key = _gen_key(key_pfx, table_name, col)
        if form_key in st.session_state:
            st.session_state[_gen_key(key_pfx, table_name, col)] = False if col.startswith("flag_") else ""

def _form__create(ctx, row=None):
    # create form for a given table
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else "s_user"
    key_pfx = _FORM_CONFIG[ctx]["key_pfx"]
    if ctx != "create":
        st.write(f'id: {_default_val(row, "id")}')
    
    _disabled = _FORM_CONFIG[ctx]["read_only"]
    _log_msg(f"table_name={table_name}, key_pfx={key_pfx}, ctx={ctx}, disabled={_disabled}")
    # TODO - get ui hints from schema
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

def _onclick_create(*args, **kwargs):
    ## Create callback
    # st.write(f"kwargs: {kwargs}")
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else "s_user"
    key_pfx = kwargs.get("key_pfx")
    form_data = _form__read(key_pfx, table_name)
    if not form_data:
        st.warning(f"_form__read({key_pfx}, {table_name}): no data")
        return

    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        if table_name == "s_user":
            username, password = form_data["username"], form_data["password"]
            if username and password:
                conn.execute(
                    f"""INSERT INTO {table_name} 
                    (username, password, notes, flag_admin) 
                    VALUES(?,?,?,?)""",
                    (username, _hash_it(password), form_data["notes"], form_data["flag_admin"]),
                )
            else:
                st.error(f"required inputs are missing")

        elif table_name == "s_person":
            full_name = form_data["full_name"]
            if full_name:
                conn.execute(
                    f"""INSERT INTO {table_name} 
                    (full_name, email, phone, notes, url_twit, url_fb, address, related_persons) 
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                    (full_name, form_data["email"], form_data["phone"], form_data["notes"], 
                        form_data["url_twit"], form_data["url_fb"], form_data["address"], form_data["related_persons"]),
                )
            else:
                st.error(f"required inputs are missing")

        _form__clear(key_pfx, table_name)

def _onclick_update(*args, **kwargs):
    ## callback for Update
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else "s_user"
    key_pfx = kwargs.get("key_pfx")
    form_data = _form__read(key_pfx, table_name)  
    if not form_data:
        st.warning(f"_form__read({key_pfx}, {table_name}): no data")
        return

    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        if table_name == "s_user":     
            conn.execute(
                    f"""UPDATE {table_name} 
                    SET password = ?, notes = ?, flag_admin = ? 
                    WHERE username = ?""", 
                    (_hash_it(form_data["password"]),form_data["notes"],form_data["flag_admin"], 
                        form_data["username"])
                )
        elif table_name == "s_person":   
            conn.execute(
                    f"""UPDATE {table_name} 
                    SET email = ?, phone = ?, notes = ?, url_twit = ?, url_fb = ?, address = ? , related_persons = ?
                    WHERE full_name = ?""", 
                    (form_data["email"], form_data["phone"], form_data["notes"], 
                        form_data["url_twit"], form_data["url_fb"], form_data["address"], form_data["related_persons"], 
                        form_data["full_name"])
                )

        _form__clear(key_pfx, table_name)

def _onclick_delete(*args, **kwargs):
    ## callback for Delete
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else "s_user"
    key_pfx = kwargs.get("key_pfx")
    form_data = _form__read(key_pfx, table_name)  
    if not form_data:
        st.warning(f"_form__read({key_pfx}, {table_name}): no data")
        return

    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        if table_name == "s_user":         
            conn.execute(
                    f"DELETE FROM {table_name} WHERE username = ?", (form_data["username"],)
                )
        elif table_name == "s_person":  
            conn.execute(
                    f"DELETE FROM {table_name} WHERE full_name = ?", (form_data["full_name"],)
                )

        _form__clear(key_pfx, table_name)

## ================================ customize ABOVE for each table to be added ========================================


def _record__create(conn, table_name):
    ctx = "create"
    key_pfx = _FORM_CONFIG[ctx]["key_pfx"]
    selected_df = _prepare_grid(conn, table_name, context=ctx)
    with st.form(key=_gen_key(key_pfx, table_name)): 
        _form__create(ctx)
        st.form_submit_button(_STR_BUTTON_CREATE, on_click=_onclick_create, kwargs={"key_pfx": key_pfx})

def _record__view(conn, table_name):
    ctx = "view"
    selected_df = _prepare_grid(conn, table_name, context=ctx)
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            _form__create(ctx, row=row)

def _record__update(conn, table_name):
    ctx = "update"
    key_pfx = _FORM_CONFIG[ctx]["key_pfx"]    
    selected_df = _prepare_grid(conn, table_name, context=ctx)
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key=_gen_key(key_pfx, table_name)):
                _form__create(ctx, row=row)
                st.form_submit_button(_STR_BUTTON_UPDATE, on_click=_onclick_update, kwargs={"key_pfx": key_pfx})

def _record__delete(conn, table_name):
    ctx = "delete"
    key_pfx = _FORM_CONFIG[ctx]["key_pfx"]        
    selected_df = _prepare_grid(conn, table_name, context=ctx)
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key=_gen_key(key_pfx, table_name)):
                _form__create(ctx, row=row)
                st.form_submit_button(_STR_BUTTON_DELETE, on_click=_onclick_delete, kwargs={"key_pfx": key_pfx})



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
    if st.button(_STR_BUTTON_EXECUTE):
        with sql.connect(f"file:{db_name}?mode=rwc", uri=True) as conn:
            if sql_stmts.strip().lower().startswith("select"):
                df = pd.read_sql(sql_stmts, conn)
                st.dataframe(df)
            else:
                for sql_stmt in sql_stmts.split(";"):
                    if not sql_stmt.strip():
                        continue
                    if not _IS_ADMIN and _BAD_SQL_PAT.findall(sql_stmt.lower()):
                        st.warning(f"SQL not allowed: '{sql_stmt}'")
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
    _STR_MENU_DATABASE: {"fn": _manage_db, "icon": "box"}, 
    _STR_MENU_TABLES: {"fn": _manage_table, "icon": "file-spreadsheet"}, 
}



action_dict =  {
    _STR_ACTION_VIEW: {"fn": _record__view, "icon": "list-task"}, 
    _STR_ACTION_ADD: {"fn": _record__create, "icon": "plus-square"},
    _STR_ACTION_EDIT: {"fn": _record__update, "icon": "pencil-square"},
    _STR_ACTION_DELETE: {"fn": _record__delete, "icon": "shield-fill-x"},
    # "Search": {"fn": _search_record, "icon": "search"},
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
        action = option_menu(_STR_MENU_TITLE, objects, 
            icons=icons, 
            menu_icon="columns-gap", 
            default_index=objects.index(_STR_MENU_DATABASE),
            key="menu_action")


        c1, c2 = st.columns([1,4])
        with c1:
            pass
        with c2:

            db_name = st.text_input('SQLite database:', value=_DB_NAME, key="db_name")    
            if action == _STR_MENU_TABLES:            
                tables = _prepare_table_list()
                table_name = st.selectbox("Table:", tables, 
                    index=tables.index("s_user"),
                    key="table_name")


        st.image("https://user-images.githubusercontent.com/329928/155828764-b19a08e4-5346-4567-bba0-0ceeb5c2b241.png")

        if _IS_ADMIN:
            if st.checkbox('view code'):
                with open(__file__) as f:
                    st.code(f.read())



def do_body():
    action = st.session_state["menu_action"] if "menu_action" in st.session_state and st.session_state["menu_action"] else _STR_MENU_DATABASE

    _log_msg(f"action={action}")
    if action == _STR_MENU_DATABASE:
        meta_dict[action]["fn"]()



    elif action == _STR_MENU_TABLES:
        table_name = st.session_state["table_name"] if "table_name" in st.session_state and st.session_state["table_name"] else "s_user"
        _log_msg(f"table_name={table_name}")
        meta_dict[action]["fn"](table_name)

        # verify
        # st.json(_prepare_table_column_dict())


if __name__ == "__main__":
    do_sidebar()
    do_body()
