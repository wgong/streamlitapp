import streamlit as st
from streamlit_ace import st_ace
from io import StringIO
from os.path import splitext

# add more using https://github.com/okld/streamlit-ace/blob/main/streamlit_ace/__init__.py
lang_dict = {
    ".py": "python",
    ".js": "javascript",
    ".java": "java",
    ".json": "json",
    ".html": "html",
    ".c": "c_cpp",
    ".cpp": "c_cpp",
    ".css": "css",
}

def _get_lang(file_ext, file_type):
    "return lang for accepted files: text, sql, py"
    if file_type == 'application/octet-stream' and file_ext.lower() == ".sql":
        lang = "sql"
    elif file_type == 'text/plain':
        lang = lang_dict.get(file_ext.lower(), "plain_text")
    else:
        lang = None
    return lang

def _show_editor_settings():
    with st.expander("Ace editor settings"):
        st.selectbox("Language", options=["plain_text"]+sorted(list(lang_dict.values())), index=0, key="ace_lang")
        st.selectbox("Theme", options=["pastel_on_dark", "chrome"], index=0, key="ace_theme")
        st.select_slider("Height", options=[str(i*100) for i in range(4,9)], key="ace_height")
        st.select_slider("Font", options=[str(i) for i in range(12,19,2)], key="ace_font")
        st.select_slider("Tab", options=[2,4,8], key="ace_tab")
        st.checkbox("Readonly", value=False, key="ace_readonly")
        st.checkbox("Auto-update", value=False, key="ace_autoupdate")
        st.checkbox("Wrap", value=False, key="ace_wrap")
        st.checkbox("Show gutter", value=True, key="ace_gutter")

def do_sidebar():
    pass
    # with st.sidebar:
    #     _show_editor_settings()

def do_body():
    orig_text = ""
    col_ace, col_fileupload = st.columns([4,1])
    lang = st.session_state.get("ace_lang", "plain_text")
    with col_fileupload:
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            # st.write(uploaded_file)
            file_name = uploaded_file.name
            file_ext = splitext(file_name)[-1]
            file_type = uploaded_file.type
            file_size = uploaded_file.size

            # To read file as bytes:
            # bytes_data = uploaded_file.getvalue()
            # st.write(bytes_data)
            lang_detected = _get_lang(file_ext, file_type)
            if not lang_detected:
                st.error("File not supported by ACE editor: type={file_type}, ext={file_ext}")
            else:
                lang = lang_detected
                # To read file as string:
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                #  st.write(stringio)
                orig_text = stringio.read()
                # st.code(orig_text)

    with col_ace:
        # display text in ACE editor
        st.write("Ace editor")
        edited_text = st_ace(value=orig_text, 
            language=lang, 
            theme=st.session_state.get("ace_theme", "pastel_on_dark"), 
            height=int(st.session_state.get("ace_height", "400")),
            font_size=int(st.session_state.get("ace_font", "14")),
            tab_size=int(st.session_state.get("ace_tab", "4")),
            readonly=st.session_state.get("ace_readonly", False),
            auto_update=st.session_state.get("ace_autoupdate", False),
            wrap=st.session_state.get("ace_wrap", False),
            show_gutter=st.session_state.get("ace_gutter", True),
        )
        if not st.session_state.get("ace_readonly") and edited_text:
            file_name = st.text_input("Filename",value=file_name, key="ace_file_name")
            if st.button("Save"):
                open(file_name, "w").write(edited_text)


    _show_editor_settings()

def main():
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
