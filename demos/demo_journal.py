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

_DB_NAME = "journals.db"

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

# @st.experimental_singleton
# def sql_connect(db_name, mode="rw"):
#     return sql.connect(f"file:{db_name}?mode={mode}", uri=True)
#
# will give this error:
# ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 3484 and this is thread id 9876.

def _hashit(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def _get_records(conn, table_name, limit=10000):
    sql_stmt = f"""
        select * from {table_name} limit {limit}
    """
    return pd.read_sql(sql_stmt, conn)

## Read
def _view_records(conn, table_name, context="read"):
    # return selected_df

    table_name = st.session_state["table_name"] if "table_name" in st.session_state else ""
    if not table_name:
        st.error("No table is selected!")
    df = _get_records(conn, table_name)

    enable_selection=True if context in ["update", "delete"] else False
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

## Full-text Search
def _clear_find_form():
    pass

def _search_record(conn, table_name):
    _view_records(conn, table_name, context="search")

    with st.form(key="find_user"):
        st.text_input("Phrase:", value="", key="find_phrase")
        st.form_submit_button('Search', on_click=_clear_find_form)

## Create
def _clear_add_form():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else ""
    if not table_name:
        st.error("No table is selected!")

    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        user_ = st.session_state["add_username"]
        pass_ = st.session_state["add_password"]
        if user_ and pass_:
            su_ = st.session_state["add_su"]
            notes_ = st.session_state["add_notes"]
            conn.execute(
                f"INSERT INTO {table_name} (username, password, su, notes) VALUES(?,?,?,?)",
                (user_, _hashit(pass_), su_, notes_),
            )

    st.session_state["add_username"] = ""
    st.session_state["add_password"] = ""
    st.session_state["add_su"] = False
    st.session_state["add_notes"] = ""

def _create_record(conn, table_name):

    _view_records(conn, table_name, context="create")
    with st.form(key="add_user"):
        st.text_input("Username (required)", key="add_username")
        st.text_input("Password (required)", key="add_password")
        st.checkbox("Is a superuser?", value=False, key="add_su")
        st.text_area('Notes', key="add_notes")
        st.form_submit_button('Add', on_click=_clear_add_form)
     

## Update
def _clear_upd_form():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else ""
    if not table_name:
        st.error("No table is selected!")

    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        username_ = st.session_state["upd_username"]
        pass_ = st.session_state["upd_password"]
        su_ = st.session_state["upd_su"]
        notes_ = st.session_state["upd_notes"]
        conn.execute(
                f"update {table_name} set password = ?,su = ?, notes = ? where username = ?", (_hashit(pass_),su_,notes_,username_)
            )

    st.session_state["upd_username"] = ""
    st.session_state["upd_password"] = ""
    st.session_state["upd_su"] = False
    st.session_state["upd_notes"] = ""

def _update_record(conn, table_name):
    selected_df = _view_records(conn, table_name, context="update")
    # st.dataframe(selected_df)
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key="upd_user"):
                st.text_input("Username:", value=row["username"][0], key="upd_username")
                st.text_input("Password:", value=row["password"][0], key="upd_password")
                st.checkbox("Is superuser?", value=row["su"][0], key="upd_su")
                st.text_area('Notes', value=row["notes"][0], key="upd_notes")
                st.form_submit_button('Update', on_click=_clear_upd_form)


## Delete
def _clear_del_form():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    table_name = st.session_state["table_name"] if "table_name" in st.session_state else ""
    if not table_name:
        st.error("No table is selected!")

    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        username_ = st.session_state["del_username"]
        conn.execute(
                f"delete from {table_name} where username = ?", (username_,)
            )

    st.session_state["del_username"] = ""


def _delete_record(conn, table_name):
    selected_df = _view_records(conn, table_name, context="delete")
    if selected_df is not None:
        row = selected_df.to_dict()
        if row:
            with st.form(key="del_user"):
                st.text_input("Username:", value=row["username"][0], key="del_username")
                st.form_submit_button('Delete', on_click=_clear_del_form)


           

def _manage_table():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    sql_stmt = """
            SELECT 
            name
        FROM 
            sqlite_schema
        WHERE 
            type ='table'
            order by name
    """

    tables = []
    table_name = ""
    col1, buf, col2  = st.columns([3,1,3])
    with col1:
        db = st.text_input('SQLite database', value=db_name)

        conn = sql.connect(f"file:{db}?mode=rw", uri=True)
        df = pd.read_sql(sql_stmt, conn)
        tables = df["name"].to_list()

    with col2:
        table_name = st.selectbox("Table:", tables, key="table_name")

    if not table_name:
        st.error("No table is selected!")

    else:
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

        action_dict[action]["fn"](conn, table_name)

def _manage_db():
    create_table = """create table if not exists users (
        id INTEGER PRIMARY KEY,
        username UNIQUE ON CONFLICT REPLACE, 
        password, 
        su, 
        notes
    );"""
    db_name = st.text_input('SQLite database', value=_DB_NAME, key="db_name")
    sql_stmt = st.text_area("SQL commands", height=250, value=create_table, key="sql_stmt")
    if st.button("Execute"):
        with sql.connect(f"file:{db_name}?mode=rwc", uri=True) as conn:
            if sql_stmt.strip().lower().startswith("select"):
                df = pd.read_sql(sql_stmt, conn)
                st.dataframe(df)
            else:
                res = conn.execute(sql_stmt)
                st.write(res)
    st.image("whitespace.png")
    with st.expander("view code"):
        with open(__file__) as f:
            # st.code(inspect.getsource(do_widget))
            st.code(f.read()) 




meta_dict = {
    "Tables": {"fn": _manage_table, "icon": "file-spreadsheet"}, 
    "Database": {"fn": _manage_db, "icon": "box"}, 
}

action_dict =  {
    "View  ": {"fn": _view_records, "icon": "list-task"}, 
    # "Search": {"fn": _search_record, "icon": "search"},
    "Create ": {"fn": _create_record, "icon": "plus-square"},
    "Update": {"fn": _update_record, "icon": "pencil-square"},
    "Delete": {"fn": _delete_record, "icon": "shield-fill-x"},
}
# SQLite Full-text search requires creating separate virtual table
# One may use trigger to populate the virtual table with data to search
# Design virtual table such that : table_name, row_key, full_text
# where full_text has this format: [col_name_1] col_value_1; ...; [col_name_N] col_value_N
# From search page, one links search result to its source table


if __name__ == "__main__":
    objects = list(meta_dict.keys())
    icons = [meta_dict[i]["icon"] for i in objects]
    with st.sidebar:
        action = option_menu("Manage", objects, 
            icons=icons, 
            menu_icon="columns-gap", 
            default_index=0)
        st.image("whitespace.png")

        if st.checkbox('view code'):
            with open(__file__) as f:
                st.code(f.read())

    if action:
        meta_dict[action]["fn"]()
