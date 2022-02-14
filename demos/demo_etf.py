import streamlit as st

import pandas as pd

# df = pd.read_csv("./data/wl_futures_etf.csv")
etf_data = {'symbol': {0: 'DIA',
  1: 'SPY',
  2: 'QQQ',
  3: 'IWM',
  4: 'GSG',
  5: 'DBC',
  6: 'USO',
  7: 'UNG',
  8: 'BOIL',
  9: 'DBA',
  10: 'MOO',
  11: 'DBO',
  12: 'BNO',
  13: 'GRN',
  14: 'ICLN',
  15: 'CORN',
  16: 'WEAT',
  17: 'COW',
  18: 'SMH',
  19: 'VGT',
  20: 'WOOD',
  21: 'JO',
  22: 'RJA',
  23: 'GLD',
  24: 'SLV',
  25: 'GDX',
  26: 'SILJ',
  27: 'COPX',
  28: 'URA',
  29: 'PALL',
  30: 'UUP',
  31: 'UDN',
  32: 'BITO',
  33: 'XLC',
  34: 'XLY',
  35: 'XLP',
  36: 'XLE',
  37: 'XLF',
  38: 'XLV',
  39: 'XLI',
  40: 'XLB',
  41: 'XLK',
  42: 'XLU',
  43: 'XLRE'},
 'name': {0: 'Dow 30',
  1: 'S&P 500',
  2: 'Nasdaq 100',
  3: 'Russell 2000',
  4: 'iShares S&P GSCI Commodity-Indexed Trust',
  5: 'Invesco DB Commodity Index Tracking Fund',
  6: 'United States Oil Fund LP',
  7: 'United States Natural Gas Fund LP',
  8: 'ProShares Ultra Bloomberg Natural Gas',
  9: 'Invesco DB Agriculture Fund',
  10: 'VanEck Vectors Agribusiness',
  11: 'Invesco DB Oil Fund',
  12: 'United States Brent Oil Fund LP',
  13: 'iPath Series B Carbon ETN',
  14: 'iShares Global Clean Energy',
  15: 'Teucrium Corn Fund',
  16: 'Teucrium Wheat Fund',
  17: 'iPath Bloomberg Livestock',
  18: 'Semiconductor Index',
  19: 'Vanguard IT',
  20: 'iShares Global Timber & Forestry',
  21: 'iPath Bloomberg Coffee Subindex',
  22: 'Elements Agriculture',
  23: 'Gold',
  24: 'Silver',
  25: 'Gold miner',
  26: 'Silver miner',
  27: 'Copper Fund',
  28: 'Global X Uranium',
  29: 'Palladium',
  30: 'US Dollar',
  31: 'US Dollar - Short',
  32: 'ProShares Bitcoin Strategy',
  33: 'Communication Services',
  34: 'Consumer Discretionary',
  35: 'Consumer Staples',
  36: 'Energy',
  37: 'Fi""cials',
  38: 'Health-care',
  39: 'Industrials',
  40: 'Materials',
  41: 'Technology',
  42: 'Utilities',
  43: 'Real Estate'},
 'sector': {0: 'Equity Index',
  1: 'Equity Index',
  2: 'Equity Index',
  3: 'Equity Index',
  4: 'Commodity',
  5: 'Commodity',
  6: 'Energy',
  7: 'Energy',
  8: 'Energy',
  9: 'Agri',
  10: 'Agri',
  11: 'Energy',
  12: 'Energy',
  13: 'Energy-Clean',
  14: 'Energy-Clean',
  15: 'Agri',
  16: 'Agri',
  17: 'Agri',
  18: 'Technology',
  19: 'Technology',
  20: 'Agri',
  21: 'Agri',
  22: 'Agri',
  23: 'Metal',
  24: 'Metal',
  25: 'Metal',
  26: 'Metal',
  27: 'Metal',
  28: 'Metal',
  29: 'Metal',
  30: 'Currency',
  31: 'Currency',
  32: 'Currency',
  33: 'Sector Fund',
  34: 'Sector Fund',
  35: 'Sector Fund',
  36: 'Sector Fund',
  37: 'Sector Fund',
  38: 'Sector Fund',
  39: 'Sector Fund',
  40: 'Sector Fund',
  41: 'Sector Fund',
  42: 'Sector Fund',
  43: 'Sector Fund'},
 'rank': {0: 0,
  1: 0,
  2: 0,
  3: 0,
  4: 0,
  5: 0,
  6: 0,
  7: 0,
  8: 0,
  9: 0,
  10: 0,
  11: 0,
  12: 0,
  13: 0,
  14: 0,
  15: 0,
  16: 0,
  17: 0,
  18: 0,
  19: 0,
  20: 0,
  21: 0,
  22: 0,
  23: 0,
  24: 0,
  25: 0,
  26: 0,
  27: 0,
  28: 0,
  29: 0,
  30: 0,
  31: 0,
  32: 0,
  33: 0,
  34: 0,
  35: 0,
  36: 0,
  37: 0,
  38: 0,
  39: 0,
  40: 0,
  41: 0,
  42: 0,
  43: 0},
 'notes': {0: "",
  1: "",
  2: "",
  3: "",
  4: "",
  5: "",
  6: "",
  7: "",
  8: "",
  9: "",
  10: "",
  11: "",
  12: "",
  13: "",
  14: "",
  15: "",
  16: "",
  17: "",
  18: "",
  19: "",
  20: "",
  21: "",
  22: "",
  23: "",
  24: "",
  25: "",
  26: "",
  27: "",
  28: "",
  29: "",
  30: "",
  31: "",
  32: "",
  33: "",
  34: "",
  35: "",
  36: "",
  37: "",
  38: "",
  39: "",
  40: "",
  41: "",
  42: "",
  43: ""}}


df = pd.DataFrame.from_dict(etf_data)
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
