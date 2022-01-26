"""
Streamlit app template

The source code: 
    https://github.com/wgong/streamlitapp/blob/main/template_sidebar_body.py

"""

import streamlit as st
import inspect

_DUMMY_ITEM = "_____"
# Initial page config
st.set_page_config(
     page_title='Streamlit Concept Demo',
     layout="wide",
     initial_sidebar_state="expanded",
)

@st.cache
def dummy(a):
    return a

def do_dummy_item():
    st.title("dummy item")

# body
def do_body():
    menu_item = st.session_state.menu_item  

    if menu_item == _DUMMY_ITEM:
        do_dummy_item()


    if st.checkbox('Show code ...', key="do_body"):
        st.code(inspect.getsource(do_body))

def do_sidebar():
    st.sidebar.markdown('''
    [<img src='https://streamlit.io/images/brand/streamlit-mark-color.svg' class='img-fluid' width=64 height=64>](https://streamlit.io/)
    ''', unsafe_allow_html=True)

    st.sidebar.markdown("""
    <span style="color:red">__Streamlit__ </span>: Why-What-How
    """, unsafe_allow_html=True)
    st.sidebar.video("https://www.youtube.com/watch?v=R2nr1uZ8ffc")    

    menu_options = sorted([_DUMMY_ITEM])
    default_ix = menu_options.index(_DUMMY_ITEM)
    menu_item = st.sidebar.selectbox("Select: ", menu_options, index=default_ix, key="menu_item")


    if st.sidebar.checkbox('Show code ...', key="do_sidebar"):
        st.sidebar.code(inspect.getsource(do_sidebar))


def main():
    do_sidebar()
    do_body()

# Run main()
if __name__ == '__main__':
    main()