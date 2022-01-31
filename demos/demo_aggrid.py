import streamlit as st
import pandas as pd 
# import inspect
# import numpy as np
# import altair as alt
# from itertools import cycle

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode


@st.cache(allow_output_mutation=True)
def load_data(url):
    if url.endswith(".csv"):
        return pd.read_csv(url)
    if url.endswith(".xls") or url.endswith(".xlsx"):
        return pd.read_excel(url)
    else:
        st.error(f"[load_data] unsupported data file: {url}, must be .csv, .xls, .xlsx")
        return None

# config Grid Options
st.sidebar.subheader("St-AgGrid example options")

page_size = st.sidebar.number_input("rows", min_value=10, value=10)
grid_height = st.sidebar.number_input("Grid height", min_value=200, max_value=800, value=350)

return_mode = st.sidebar.selectbox("Return Mode", list(DataReturnMode.__members__), index=1)
return_mode_value = DataReturnMode.__members__[return_mode]
return_mode_value = DataReturnMode.FILTERED
st.sidebar.write(f"return_mode_value: {return_mode_value}")

update_mode = st.sidebar.selectbox("Update Mode", list(GridUpdateMode.__members__), index=6)
update_mode_value = GridUpdateMode.__members__[update_mode]
update_mode_value = GridUpdateMode.MODEL_CHANGED
st.sidebar.write(f"update_mode_value: {update_mode_value}")

fit_columns_on_grid_load = True # st.sidebar.checkbox("Fit Grid Columns on Load")
st.sidebar.write(f"fit_columns_on_grid_load: {fit_columns_on_grid_load}")

enable_selection=st.sidebar.checkbox("Enable row selection", value=True)
if enable_selection:
    st.sidebar.subheader("Selection options")
    selection_mode = st.sidebar.radio("Selection Mode", ['multiple', 'single'])
    
    use_checkbox = st.sidebar.checkbox("Use check box for selection", value=True)
    if use_checkbox:
        groupSelectsChildren = st.sidebar.checkbox("Group checkbox select children", value=True)
        groupSelectsFiltered = st.sidebar.checkbox("Group checkbox includes filtered", value=True)

    if ((selection_mode == 'multiple') & (not use_checkbox)):
        rowMultiSelectWithClick = st.sidebar.checkbox("Multiselect with click (instead of holding CTRL)", value=False)
        if not rowMultiSelectWithClick:
            suppressRowDeselection = st.sidebar.checkbox("Suppress deselection (while holding CTRL)", value=False)
        else:
            suppressRowDeselection=False
    st.sidebar.text("___")

enable_pagination = st.sidebar.checkbox("Enable pagination", value=True)

st.header("Streamlit Ag-Grid demo")
data_options = ["https://raw.githubusercontent.com/fivethirtyeight/data/master/airline-safety/airline-safety.csv",
    "data/generic-food.csv","data/generic-food.xls"]
data_url = st.selectbox("Select data: ", data_options, key="data_url")

# create df
df = load_data(data_url)

#Infer basic colDefs from dataframe types
gb = GridOptionsBuilder.from_dataframe(df)

#customize gridOptions
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)

# gb.configure_column("date_tz_aware", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd HH:mm zzz', pivot=True)
# gb.configure_column("apple", type=["numericColumn","numberColumnFilter","customNumericFormat"], precision=2, aggFunc='sum')
# gb.configure_column("banana", type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=1, aggFunc='avg')
# gb.configure_column("chocolate", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="R$", aggFunc='max')

#configures last row to use custom styles based on cell's value, injecting JsCode on components front end
# cellsytle_jscode = JsCode("""
# function(params) {
#     if (params.value.startswith("Air")) {
#         return {
#             'color': 'white',
#             'backgroundColor': 'darkred'
#         }
#     } else {
#         return {
#             'color': 'black',
#             'backgroundColor': 'white'
#         }
#     }
# };
# """)
# gb.configure_column("airline", cellStyle=cellsytle_jscode)

if enable_selection:
    gb.configure_selection(selection_mode)
    if use_checkbox:
        gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)
    if ((selection_mode == 'multiple') & (not use_checkbox)):
        gb.configure_selection(selection_mode, use_checkbox=False, rowMultiSelectWithClick=rowMultiSelectWithClick, suppressRowDeselection=suppressRowDeselection)

if enable_pagination:
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=page_size)

gb.configure_grid_options(domLayout='normal')
gridOptions = gb.build()

#Display the grid


# instantiate AgGrid

grid_response = AgGrid(
    df, 
    gridOptions=gridOptions,
    height=grid_height, 
    width='100%',
    data_return_mode=return_mode_value, 
    update_mode=update_mode_value,
    fit_columns_on_grid_load=fit_columns_on_grid_load,
    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
)

df = grid_response['data']
selected = grid_response['selected_rows']
selected_df = pd.DataFrame(selected)


# st.subheader("Returned grid data:") 
# #returning as HTML table bc streamlit has issues when rendering dataframes with timedeltas:
# # https://github.com/streamlit/streamlit/issues/3781
# st.markdown(grid_response['data'].to_html(), unsafe_allow_html=True)

# Show selected rows

st.subheader("grid selection:")
st.write(grid_response['selected_rows'])


st.subheader("grid options:")
st.write(f"gridOptions type: {type(gridOptions)}")
st.write(gridOptions)


with st.expander("Show code"):
    with open(__file__) as f:
        st.code(f.read())       