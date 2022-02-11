How to map table schema to streamlit widget


SQLite has the following types

Input widgets mapping

Int

    - boolean-type: 0, 1
        st_ui: checkbox

    - range
        st_ui: slider

    - any
        st_ui: number_input

    - color
        st_ui: color_picker

Real

Text

    - LOV (List of Value) or Categorical
        st_ui: selectbox, radio, multiselect, select_slider

    - short Text
        st_ui: text_input

    - long text
        st_ui: text_area

    - datetime
        st_ui: date_input, time_input


Blob

    - attachment
        st_ui: file_uploader

    - image
        st_ui: camera_input


Output widget mapping

Text

    st_ui:
        title
        header
        subheader
        caption
        text
        markdown
        code
        latex

Int/Real

    st_ui
        line_chart
        bar_chart
        map
        pyplot
        altair_chart
        graphviz_chart

Blob
    st_ui
        text
        image
        audio
        video


Layout
    st_ui
        sidebar
        columns
        expander
        container
        empty

        form
        form_submit_button

Status/control
    st_ui
        progress
        spinner
        balloons

        error
        warning
        info

        success
        exception

        stop

session_state (global dict)

performance

        st.cache(ttl=3600)
        st.experimental_memo
        st.experimental_singleton


Example schema:

```
Tasks:
    id
    name
    description
    category
    due_date
    priority
    completion_pct
    related_tasks
    related_persons
    attachments
    created_by
    created_at
    modified_by
    modified_at

Journal:
    id
    name
    description
    category
    attachments

Events:
    id
    name
    description
    category
    when
    where
    related_persons
    attachments

Persons:
    id
    first_name
    mid_name
    last_name
    email
    phone
    address
    description
    related_persons
    attachments

```