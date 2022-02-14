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
## sidebar Menu
def do_sidebar():
    for sect in sectors:
        sect_dict[sect] = st.sidebar.checkbox(sect)

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

    if show_df:
        st.dataframe(df)


def main():
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
