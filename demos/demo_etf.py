import streamlit as st

import pandas as pd

df = pd.read_csv("./data/wl_futures_etf.csv")

# sectors = df["sector"].unique().tolist()
# manual order
sectors = ['Equity Index', 'Sector Fund',
    'Commodity', 'Metal', 'Agri', 'Energy', 'Energy-Clean',
    'Technology', 'Currency']

etf_dict = {}
for sect in sectors:
    sym_name = df[df["sector"] == sect][["symbol","name"]]
    etf_dict[sect] = dict(zip(sym_name.symbol, sym_name.name))

period_dict = {"daily":"d", "weekly":"w", "monthly":"m"}

sect_dict = {}

def reset_sector():
    for sect in sectors:
        if sect == 'Equity Index':
            sect_dict[sect] = st.sidebar.checkbox(sect, value=True, key=sect)
        else:
            sect_dict[sect] = st.sidebar.checkbox(sect, key=sect)
## sidebar Menu
def do_sidebar():
    reset_sector()

    ## not working due to this error: StreamlitAPIException: st.session_state.Agri cannot be modified after the widget with key Agri is instantiated
    # if st.sidebar.button("Reset"):
    #     for sect in sectors:
    #         if sect in st.session_state and st.session_state[sect] and sect != 'Equity Index':
    #             st.session_state[sect] = False

# body
def do_body():
    col0, col1, col2, col3 = st.columns(4)

    with col0:
        show_chart = st.checkbox("Show Charts", value=True)

    with col1:
        period_item = st.selectbox(
            'Period:', list(period_dict.keys()), index=0)
        period = period_dict[period_item]

    with col3:
        show_df = st.checkbox("Show ETF data")


    if show_chart:  
        for sect in sectors:
            if not sect_dict[sect]: continue
            st.subheader(sect)
            for k,v in etf_dict[sect].items():
                st.markdown(f"[{k}](https://finviz.com/quote.ashx?t={k}&p={period}) : {v}")
                st.image(f"https://finviz.com/chart.ashx?t={k}&p={period}")
                # don't know how to get futures chart img

    if show_df:
        st.dataframe(df)


def main():
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
