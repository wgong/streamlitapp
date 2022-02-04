import streamlit as st
from streamlit_option_menu import option_menu

import sqlite3 as sql
import hashlib

_DB_NAME = "users.db"

def _hashit(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

## Read
def _read_users(conn):
    db_data = conn.execute("select username,password,su,notes from users order by username").fetchall()
    if db_data:
        table_data = list(zip(*db_data))
        st.table(
            {
                "Username": table_data[0],
                "Password": table_data[1],
                "Superuser?": table_data[2],
                "Notes": table_data[3],
            }
        )
    else:
        st.write("No row in table: users")

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
    with st.form(key="add_user"):
        st.text_input("Username (required)", key="add_username")
        st.text_input("Password (required)", key="add_password")
        st.checkbox("Is a superuser?", value=False, key="add_su")
        st.text_area('Notes', key="add_notes")
        st.form_submit_button('Add', on_click=clear_add_form)

    _read_users(conn)



## Update
def clear_upd_form():
    db_name = st.session_state["db_name"] if "db_name" in st.session_state else _DB_NAME
    with sql.connect(f"file:{db_name}?mode=rw", uri=True) as conn:
        user_id = st.session_state["user_id"]
        pass_ = st.session_state["upd_password"]
        su_ = st.session_state["upd_su"]
        notes_ = st.session_state["upd_notes"]
        conn.execute(
                "update users set password = ?,su = ?, notes = ? where username = ?", (_hashit(pass_),su_,notes_,user_id)
            )

    st.session_state["upd_password"] = ""
    st.session_state["upd_su"] = False
    st.session_state["upd_notes"] = ""

def _update_users(conn):
    db_data = conn.execute("select username,password,su,notes from users where username != 'admin'").fetchall()
    if len(db_data) < 1:
        return
    user_dict = {}
    for row in db_data:
        user_dict[row[0]] = row
    user_id = st.selectbox("Select user", options=sorted(list(user_dict.keys())), key="user_id")
    # st.write(f"user: {user_id}")
    with st.form(key="upd_user"):
        st.text_input("Password:", value=user_dict[user_id][1], key="upd_password")
        st.checkbox("Is superuser?", value=user_dict[user_id][2], key="upd_su")
        st.text_area('Notes', value=user_dict[user_id][3], key="upd_notes")
        st.form_submit_button('Update', on_click=clear_upd_form)

    _read_users(conn)

## Delete
def _delete_users(conn):
    userlist = [x[0] for x in conn.execute("select username from users where username != 'admin'").fetchall()]
    # userlist.insert(0, "")
    user_id = st.selectbox("Select user", options=userlist)
    if user_id:
        if st.button(f"Delete"):
            with conn:
                conn.execute("delete from users where username = ?", (user_id,))
                st.write(f"User {user_id} deleted")
            _read_users(conn)

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
        action_dict[action]["op"](conn)


# icons : https://icons.getbootstrap.com/

meta_dict = {
    "Table": {"op": _manage_users, "icon": "file-spreadsheet"}, 
    "Database": {"op": _manage_db, "icon": "box"}, 
}

action_dict =  {
    "View": {"op": _read_users, "icon": "list-task"}, 
    "Add": {"op": _create_users, "icon": "plus-square-fill"},
    "Update": {"op": _update_users, "icon": "pencil-square"},
    "Delete": {"op": _delete_users, "icon": "shield-fill-x"},
}


if __name__ == "__main__":
    objects = list(meta_dict.keys())
    icons = [meta_dict[i]["icon"] for i in objects]
    with st.sidebar:
        action = option_menu("Manage", objects, 
            icons=icons, 
            menu_icon="columns-gap", 
            default_index=0)

    if action:
        meta_dict[action]["op"]()
