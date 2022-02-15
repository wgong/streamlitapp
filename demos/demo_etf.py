import streamlit as st

import pandas as pd

# df = pd.read_csv("./data/wl_futures_etf.csv")
etf_data = {'symbol': {0: 'SPY',
  1: 'QQQ',
  2: 'DIA',
  3: 'IWM',
  4: 'XLE',
  5: 'XLK',
  6: 'XLF',
  7: 'XLV',
  8: 'XLI',
  9: 'XLB',
  10: 'XLP',
  11: 'XLY',
  12: 'XLC',
  13: 'XLU',
  14: 'XLRE',
  15: 'VGT',
  16: 'CLOU',
  17: 'IGV',
  18: 'SMH',
  19: 'UUP',
  20: 'CYB',
  21: 'FXE',
  22: 'FXY',
  23: 'UDN',
  24: 'BITO',
  25: 'USO',
  26: 'BNO',
  27: 'DBO',
  28: 'UNG',
  29: 'BOIL',
  30: 'GRN',
  31: 'ICLN',
  32: 'GSG',
  33: 'DBC',
  34: 'GLD',
  35: 'SLV',
  36: 'GDX',
  37: 'SILJ',
  38: 'COPX',
  39: 'URA',
  40: 'PALL',
  41: 'DBA',
  42: 'MOO',
  43: 'RJA',
  44: 'CORN',
  45: 'WEAT',
  46: 'COW',
  47: 'JO',
  48: 'WOOD',
  49: 'SCHF',
  50: 'SCHC',
  51: 'GWX',
  52: 'SCZ',
  53: 'EFA',
  54: 'FXI',
  55: 'MCHI',
  56: 'KWEB',
  57: 'ASHR',
  58: 'EWJ',
  59: 'EWY',
  60: 'INDA',
  61: 'ENZL',
  62: 'EWA',
  63: 'EWC',
  64: 'EWW',
  65: 'EWZ',
  66: 'ARGT',
  67: 'EWG',
  68: 'EWQ',
  69: 'EWU',
  70: 'RSX',
  71: 'IZRL',
  72: 'EIS',
  73: 'KSA',
  74: 'TUR',
  75: 'EZA'},
 'name': {0: 'S&P 500',
  1: 'Nasdaq 100',
  2: 'Dow 30',
  3: 'Russell 2000',
  4: 'Energy',
  5: 'Technology',
  6: 'Financials',
  7: 'Health-care',
  8: 'Industrials',
  9: 'Materials',
  10: 'Consumer Staples',
  11: 'Consumer Discretionary',
  12: 'Communication Services',
  13: 'Utilities',
  14: 'Real Estate',
  15: 'Vanguard IT',
  16: 'Global X Cloud Computing',
  17: 'Tech-Software',
  18: 'Semiconductor Index',
  19: 'US Dollar',
  20: 'China Yuan',
  21: 'Euro',
  22: 'Japan Yen',
  23: 'US Dollar - Short',
  24: 'ProShares Bitcoin Strategy',
  25: 'United States Oil Fund LP',
  26: 'United States Brent Oil Fund LP',
  27: 'Invesco DB Oil Fund',
  28: 'United States Natural Gas Fund LP',
  29: 'ProShares Ultra Bloomberg Natural Gas',
  30: 'iPath Series B Carbon ETN',
  31: 'iShares Global Clean Energy',
  32: 'iShares S&P GSCI Commodity-Indexed Trust',
  33: 'Invesco DB Commodity Index Tracking Fund',
  34: 'Gold',
  35: 'Silver',
  36: 'Gold miner',
  37: 'Silver miner',
  38: 'Copper Fund',
  39: 'Global X Uranium',
  40: 'Palladium',
  41: 'Invesco DB Agriculture Fund',
  42: 'VanEck Vectors Agribusiness',
  43: 'Elements Agriculture',
  44: 'Teucrium Corn Fund',
  45: 'Teucrium Wheat Fund',
  46: 'iPath Bloomberg Livestock',
  47: 'iPath Bloomberg Coffee Subindex',
  48: 'iShares Global Timber & Forestry',
  49: 'Schwab International Equity',
  50: 'Schwab International Small-Cap Equity',
  51: 'SPDR S&P International Small Cap',
  52: 'iShares MSCI EAFE Small-Cap',
  53: 'iShares MSCI EAFE',
  54: 'iShares China Large-Cap',
  55: 'iShares MSCI China',
  56: 'KraneShares CSI China Internet',
  57: 'Xtrackers Harvest CSI 300 China A-Shares',
  58: 'iShares MSCI Japan',
  59: 'iShares MSCI South Korea',
  60: 'iShares MSCI India',
  61: 'iShares MSCI New Zealand',
  62: 'iShares MSCI-Australia',
  63: 'iShares MSCI Canada',
  64: 'iShares MSCI Mexico',
  65: 'iShares MSCI Brazil',
  66: 'Global X MSCI Argentina',
  67: 'iShares MSCI Germany',
  68: 'iShares MSCI France',
  69: 'iShares MSCI United Kingdom',
  70: 'VanEck Russia',
  71: 'ARK Israel Innovative Technology',
  72: 'iShares MSCI Israel',
  73: 'iShares MSCI Saudi Arabia',
  74: 'iShares MSCI Turkey',
  75: 'iShares MSCI South Africa'},
 'sector': {0: 'Equity Index',
  1: 'Equity Index',
  2: 'Equity Index',
  3: 'Equity Index',
  4: 'Sector',
  5: 'Sector',
  6: 'Sector',
  7: 'Sector',
  8: 'Sector',
  9: 'Sector',
  10: 'Sector',
  11: 'Sector',
  12: 'Sector',
  13: 'Sector',
  14: 'Sector',
  15: 'Technology',
  16: 'Technology',
  17: 'Technology',
  18: 'Technology',
  19: 'Currency',
  20: 'Currency',
  21: 'Currency',
  22: 'Currency',
  23: 'Currency',
  24: 'Currency',
  25: 'Energy',
  26: 'Energy',
  27: 'Energy',
  28: 'Energy',
  29: 'Energy',
  30: 'Energy-Clean',
  31: 'Energy-Clean',
  32: 'Commodity',
  33: 'Commodity',
  34: 'Metal',
  35: 'Metal',
  36: 'Metal',
  37: 'Metal',
  38: 'Metal',
  39: 'Metal',
  40: 'Metal',
  41: 'Agri',
  42: 'Agri',
  43: 'Agri',
  44: 'Agri',
  45: 'Agri',
  46: 'Agri',
  47: 'Agri',
  48: 'Agri',
  49: 'International',
  50: 'International',
  51: 'International',
  52: 'International',
  53: 'International',
  54: 'International',
  55: 'International',
  56: 'International',
  57: 'International',
  58: 'International',
  59: 'International',
  60: 'International',
  61: 'International',
  62: 'International',
  63: 'International',
  64: 'International',
  65: 'International',
  66: 'International',
  67: 'International',
  68: 'International',
  69: 'International',
  70: 'International',
  71: 'International',
  72: 'International',
  73: 'International',
  74: 'International',
  75: 'International'},
 'order': {0: 0.1,
  1: 0.2,
  2: 0.3,
  3: 0.4,
  4: 1.01,
  5: 1.01,
  6: 1.02,
  7: 1.03,
  8: 1.04,
  9: 1.05,
  10: 1.06,
  11: 1.07,
  12: 1.08,
  13: 1.09,
  14: 1.11,
  15: 2.1,
  16: 2.2,
  17: 2.3,
  18: 2.4,
  19: 3.01,
  20: 3.02,
  21: 3.03,
  22: 3.04,
  23: 3.09,
  24: 3.11,
  25: 4.01,
  26: 4.02,
  27: 4.03,
  28: 4.05,
  29: 4.06,
  30: 4.11,
  31: 4.12,
  32: 5.1,
  33: 5.2,
  34: 6.1,
  35: 6.2,
  36: 6.3,
  37: 6.4,
  38: 6.5,
  39: 6.6,
  40: 6.7,
  41: 7.01,
  42: 7.02,
  43: 7.03,
  44: 7.05,
  45: 7.06,
  46: 7.07,
  47: 7.08,
  48: 7.09,
  49: 10.1,
  50: 10.11,
  51: 10.12,
  52: 10.21,
  53: 10.22,
  54: 10.23,
  55: 10.24,
  56: 10.25,
  57: 10.26,
  58: 10.27,
  59: 10.28,
  60: 10.29,
  61: 10.3,
  62: 10.31,
  63: 10.4,
  64: 10.41,
  65: 10.42,
  66: 10.43,
  67: 10.5,
  68: 10.51,
  69: 10.52,
  70: 10.53,
  71: 10.6,
  72: 10.61,
  73: 10.62,
  74: 10.63,
  75: 10.64}}

df = pd.DataFrame.from_dict(etf_data)
# sectors = df["sector"].unique().tolist()
# manual order
sectors = ['Equity Index',
 'Sector',
 'Technology',
 'Currency',
 'Energy',
 'Energy-Clean',
 'Commodity',
 'Metal',
 'Agri',
 'International']

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

    with st.sidebar:
        st.selectbox('Period:', list(period_dict.keys()), index=0, key="period")
        st.checkbox("Show Charts", value=True, key="show_chart")
        st.checkbox("Show ETF data", key="show_etf")

# body
def do_body():

    # col0, col1, col2, col3 = st.columns(4)

    # with col0:
    #     show_chart = st.checkbox("Show Charts", value=True, key="show_chart")

    # with col1:
    #     period_item = st.selectbox(
    #         'Period:', list(period_dict.keys()), index=0, key="period")
    #     period = period_dict[period_item]

    # with col3:
    #     show_df = st.checkbox("Show ETF data", key="show_etf")


    if st.session_state.get("show_etf", False):
        st.dataframe(df)

    if st.session_state.get("show_chart", False):
        period_item = st.session_state.get("period", "daily")
        period = period_dict[period_item]
        for sect in sectors:
            if not sect_dict[sect]: continue
            st.subheader(sect)
            for k,v in etf_dict[sect].items():
                st.image(f"https://finviz.com/chart.ashx?t={k}&p={period}")
                st.markdown(f" [{k}](https://finviz.com/quote.ashx?t={k}&p={period}) : {v} ", unsafe_allow_html=True)
                # don't know how to get futures chart img


def main():
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
