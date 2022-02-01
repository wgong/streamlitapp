import streamlit as st
import sqlite3 as sql
import hashlib

def _hashit(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def auth(sidebar=True):

    try:
        conn = sql.connect("file:users.db?mode=ro", uri=True)
    except sql.OperationalError:
        st.error(
            "Authentication Database is Not Found.\n\nConsider running authlib script in standalone mode to generate."
        )
        return None

    input_widget = st.sidebar.text_input if sidebar else st.text_input
    checkbox_widget = st.sidebar.checkbox if sidebar else st.checkbox
    user = input_widget("Username:")

    data = conn.execute("select * from users where username = ?", (user,)).fetchone()
    if user:
        password = input_widget("Enter Password:", type="password")
        if data and password == data[2]:
            if data[3]:
                if checkbox_widget("Check to edit user database"):
                    manage_users()
            return user
        else:
            return None
    return None

## Read
def _list_users(conn):
    db_data = conn.execute("select username,password,su,notes from users").fetchall()
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
    conn = sql.connect("file:users.db?mode=rw", uri=True)
    with conn:
        user_ = st.session_state["add_username"]
        pass_ = st.session_state["add_password"]
        if user_ and pass_:
            super_ = st.session_state["add_su"]
            notes_ = st.session_state["add_notes"]
            conn.execute(
                "INSERT INTO USERS(username, password, su, notes) VALUES(?,?,?,?)",
                (user_, _hashit(pass_), super_, notes_),
            )
            st.text("User added")
    st.session_state["add_username"] = ""
    st.session_state["add_password"] = ""
    st.session_state["add_su"] = False
    st.session_state["add_notes"] = ""

def _create_users(conn):
    with st.form(key="add_user"):
        st.text_input("Enter Username", key="add_username")
        st.text_input("Enter Password (required)", key="add_password")
        st.checkbox("Is this a superuser?", value=False, key="add_su")
        st.text_area('Notes', key="add_notes")
        st.form_submit_button('Add User', on_click=clear_add_form)

    _list_users(conn)



## Update
def clear_upd_form():
    conn = sql.connect("file:users.db?mode=rw", uri=True)
    with conn:
        user_id = st.session_state["user_id"]
        pass_ = st.session_state["upd_password"]
        super_ = st.session_state["upd_su"]
        notes_ = st.session_state["upd_notes"]
        conn.execute(
                "update users set password = ?,su = ?, notes = ? where username = ?", (_hashit(pass_),super_,notes_,user_id)
            )
        st.text("User updated")   
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
    st.write(f"Update user: {user_id}")
    with st.form(key="upd_user"):
        st.text_input("Password:", value=user_dict[user_id][1], key="upd_password")
        st.checkbox("Is superuser?", value=user_dict[user_id][2], key="upd_su")
        st.text_area('Notes', value=user_dict[user_id][3], key="upd_notes")
        st.form_submit_button('Update', on_click=clear_upd_form)

    _list_users(conn)

## Delete
def _delete_users(conn):
    userlist = [x[0] for x in conn.execute("select username from users where username != 'admin'").fetchall()]
    # userlist.insert(0, "")
    user_id = st.selectbox("Select user", options=userlist)
    if user_id:
        if st.button(f"Remove"):
            with conn:
                conn.execute("delete from users where username = ?", (user_id,))
                st.write(f"User {user_id} deleted")
            _list_users(conn)


def manage_users():
    with sql.connect("file:users.db?mode=rwc", uri=True) as conn:
        conn.execute("""
            create table if not exists users (
                id INTEGER PRIMARY KEY,
                username UNIQUE ON CONFLICT REPLACE, 
                password, 
                su, 
                notes
            )
        """)

        modes =  {
            "View": _list_users,
            "Create": _create_users,
            "Update": _update_users,
            "Delete": _delete_users,
        }
        # https://discuss.streamlit.io/t/horizontal-radio-buttons/2114/7
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
        st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
        mode = st.radio("Action", modes.keys())
        modes[mode](conn)


if __name__ == "__main__":
    st.write(
        "Manager users database"
    )
    if st.checkbox("Check to continue"):
        manage_users()