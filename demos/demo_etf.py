import streamlit as st

import pandas as pd

# df = pd.read_csv("./data/wl_futures_etf.csv")
etf_data = [
   {'symbol': 'SPY', 'name': 'S&P 500', 'sector': 'Equity Index', 'order': 0.1} ,
   {'symbol': 'QQQ', 'name': 'Nasdaq 100', 'sector': 'Equity Index', 'order': 0.2} ,
   {'symbol': 'DIA', 'name': 'Dow 30', 'sector': 'Equity Index', 'order': 0.3} ,
   {'symbol': 'IWM', 'name': 'Russell 2000', 'sector': 'Equity Index', 'order': 0.4} ,
   {'symbol': 'XLE', 'name': 'Energy', 'sector': 'Sector', 'order': 1.01} ,
   {'symbol': 'XLK', 'name': 'Technology', 'sector': 'Sector', 'order': 1.01} ,
   {'symbol': 'XLF', 'name': 'Financials', 'sector': 'Sector', 'order': 1.02} ,
   {'symbol': 'XLV', 'name': 'Health-care', 'sector': 'Sector', 'order': 1.03} ,
   {'symbol': 'XLI', 'name': 'Industrials', 'sector': 'Sector', 'order': 1.04} ,
   {'symbol': 'XLB', 'name': 'Materials', 'sector': 'Sector', 'order': 1.05} ,
   {'symbol': 'XLP', 'name': 'Consumer Staples', 'sector': 'Sector', 'order': 1.06} ,
   {'symbol': 'XLY', 'name': 'Consumer Discretionary', 'sector': 'Sector', 'order': 1.07} ,
   {'symbol': 'XLC', 'name': 'Communication Services', 'sector': 'Sector', 'order': 1.08} ,
   {'symbol': 'XLU', 'name': 'Utilities', 'sector': 'Sector', 'order': 1.09} ,
   {'symbol': 'XLRE', 'name': 'Real Estate', 'sector': 'Sector', 'order': 1.11} ,
   {'symbol': 'VGT', 'name': 'Vanguard IT', 'sector': 'Technology', 'order': 2.1} ,
   {'symbol': 'CLOU', 'name': 'Global X Cloud Computing', 'sector': 'Technology', 'order': 2.2} ,
   {'symbol': 'IGV', 'name': 'Tech-Software', 'sector': 'Technology', 'order': 2.3} ,
   {'symbol': 'SMH', 'name': 'Semiconductor Index', 'sector': 'Technology', 'order': 2.4} ,
   {'symbol': 'UUP', 'name': 'US Dollar', 'sector': 'Currency', 'order': 3.01} ,
   {'symbol': 'CYB', 'name': 'China Yuan', 'sector': 'Currency', 'order': 3.02} ,
   {'symbol': 'FXE', 'name': 'Euro', 'sector': 'Currency', 'order': 3.03} ,
   {'symbol': 'FXY', 'name': 'Japan Yen', 'sector': 'Currency', 'order': 3.04} ,
   {'symbol': 'UDN', 'name': 'US Dollar - Short', 'sector': 'Currency', 'order': 3.09} ,
   {'symbol': 'BITO', 'name': 'ProShares Bitcoin Strategy', 'sector': 'Currency', 'order': 3.11} ,
   {'symbol': 'USO', 'name': 'United States Oil Fund LP', 'sector': 'Energy', 'order': 4.01} ,
   {'symbol': 'BNO', 'name': 'United States Brent Oil Fund LP', 'sector': 'Energy', 'order': 4.02} ,
   {'symbol': 'DBO', 'name': 'Invesco DB Oil Fund', 'sector': 'Energy', 'order': 4.03} ,
   {'symbol': 'UNG', 'name': 'United States Natural Gas Fund LP', 'sector': 'Energy', 'order': 4.05} ,
   {'symbol': 'BOIL', 'name': 'ProShares Ultra Bloomberg Natural Gas', 'sector': 'Energy', 'order': 4.06} ,
   {'symbol': 'GRN', 'name': 'iPath Series B Carbon ETN', 'sector': 'Energy-Clean', 'order': 4.11} ,
   {'symbol': 'ICLN', 'name': 'iShares Global Clean Energy', 'sector': 'Energy-Clean', 'order': 4.12} ,
   {'symbol': 'GSG', 'name': 'iShares S&P GSCI Commodity-Indexed Trust', 'sector': 'Commodity', 'order': 5.1} ,
   {'symbol': 'DBC', 'name': 'Invesco DB Commodity Index Tracking Fund', 'sector': 'Commodity', 'order': 5.2} ,
   {'symbol': 'GLD', 'name': 'Gold', 'sector': 'Metal', 'order': 6.1} ,
   {'symbol': 'SLV', 'name': 'Silver', 'sector': 'Metal', 'order': 6.2} ,
   {'symbol': 'GDX', 'name': 'Gold miner', 'sector': 'Metal', 'order': 6.3} ,
   {'symbol': 'SILJ', 'name': 'Silver miner', 'sector': 'Metal', 'order': 6.4} ,
   {'symbol': 'COPX', 'name': 'Copper Fund', 'sector': 'Metal', 'order': 6.5} ,
   {'symbol': 'URA', 'name': 'Global X Uranium', 'sector': 'Metal', 'order': 6.6} ,
   {'symbol': 'PALL', 'name': 'Palladium', 'sector': 'Metal', 'order': 6.7} ,
   {'symbol': 'LIT', 'name': 'Global X Lithium & Battery Tech ', 'sector': 'Metal', 'order': 6.8} ,
   {'symbol': 'DBA', 'name': 'Invesco DB Agriculture Fund', 'sector': 'Agri', 'order': 7.01} ,
   {'symbol': 'MOO', 'name': 'VanEck Vectors Agribusiness', 'sector': 'Agri', 'order': 7.02} ,
   {'symbol': 'RJA', 'name': 'Elements Agriculture', 'sector': 'Agri', 'order': 7.03} ,
   {'symbol': 'CORN', 'name': 'Teucrium Corn Fund', 'sector': 'Agri', 'order': 7.05} ,
   {'symbol': 'WEAT', 'name': 'Teucrium Wheat Fund', 'sector': 'Agri', 'order': 7.06} ,
   {'symbol': 'COW', 'name': 'iPath Bloomberg Livestock', 'sector': 'Agri', 'order': 7.07} ,
   {'symbol': 'JO', 'name': 'iPath Bloomberg Coffee Subindex', 'sector': 'Agri', 'order': 7.08} ,
   {'symbol': 'WOOD', 'name': 'iShares Global Timber & Forestry', 'sector': 'Agri', 'order': 7.09} ,
   {'symbol': 'PHO', 'name': 'Invesco Water Resources', 'sector': 'Agri', 'order': 7.11} ,
   {'symbol': 'SCHF', 'name': 'Schwab International Equity', 'sector': 'International', 'order': 10.1} ,
   {'symbol': 'SCHC', 'name': 'Schwab International Small-Cap Equity', 'sector': 'International', 'order': 10.11} ,
   {'symbol': 'GWX', 'name': 'SPDR S&P International Small Cap', 'sector': 'International', 'order': 10.12} ,
   {'symbol': 'EWG', 'name': 'iShares MSCI Germany', 'sector': 'International', 'order': 10.135} ,
   {'symbol': 'EWQ', 'name': 'iShares MSCI France', 'sector': 'International', 'order': 10.1351} ,
   {'symbol': 'EWU', 'name': 'iShares MSCI United Kingdom', 'sector': 'International', 'order': 10.1352} ,
   {'symbol': 'RSX', 'name': 'VanEck Russia', 'sector': 'International', 'order': 10.1353} ,
   {'symbol': 'SCZ', 'name': 'iShares MSCI EAFE Small-Cap', 'sector': 'International', 'order': 10.21} ,
   {'symbol': 'EFA', 'name': 'iShares MSCI EAFE', 'sector': 'International', 'order': 10.22} ,
   {'symbol': 'FXI', 'name': 'iShares China Large-Cap', 'sector': 'International', 'order': 10.23} ,
   {'symbol': 'MCHI', 'name': 'iShares MSCI China', 'sector': 'International', 'order': 10.24} ,
   {'symbol': 'KWEB', 'name': 'KraneShares CSI China Internet', 'sector': 'International', 'order': 10.25} ,
   {'symbol': 'ASHR', 'name': 'Xtrackers Harvest CSI 300 China A-Shares', 'sector': 'International', 'order': 10.26} ,
   {'symbol': 'EWJ', 'name': 'iShares MSCI Japan', 'sector': 'International', 'order': 10.27} ,
   {'symbol': 'EWY', 'name': 'iShares MSCI South Korea', 'sector': 'International', 'order': 10.28} ,
   {'symbol': 'INDA', 'name': 'iShares MSCI India', 'sector': 'International', 'order': 10.29} ,
   {'symbol': 'ENZL', 'name': 'iShares MSCI New Zealand', 'sector': 'International', 'order': 10.3} ,
   {'symbol': 'EWA', 'name': 'iShares MSCI-Australia', 'sector': 'International', 'order': 10.31} ,
   {'symbol': 'EWC', 'name': 'iShares MSCI Canada', 'sector': 'International', 'order': 10.4} ,
   {'symbol': 'EWW', 'name': 'iShares MSCI Mexico', 'sector': 'International', 'order': 10.41} ,
   {'symbol': 'EWZ', 'name': 'iShares MSCI Brazil', 'sector': 'International', 'order': 10.42} ,
   {'symbol': 'ARGT', 'name': 'Global X MSCI Argentina', 'sector': 'International', 'order': 10.43} ,
   {'symbol': 'IZRL', 'name': 'ARK Israel Innovative Technology', 'sector': 'International', 'order': 10.6} ,
   {'symbol': 'EIS', 'name': 'iShares MSCI Israel', 'sector': 'International', 'order': 10.61} ,
   {'symbol': 'KSA', 'name': 'iShares MSCI Saudi Arabia', 'sector': 'International', 'order': 10.62} ,
   {'symbol': 'TUR', 'name': 'iShares MSCI Turkey', 'sector': 'International', 'order': 10.63} ,
   {'symbol': 'EZA', 'name': 'iShares MSCI South Africa', 'sector': 'International', 'order': 10.64} ,
]

df = pd.DataFrame.from_dict(etf_data)
# sectors = df["sector"].unique().tolist()
# manual order
sectors = ['Equity Index',  'Sector',
 'Currency',  'Commodity',
 'Agri',  'Energy',  'Energy-Clean',
 'Metal',  'Technology',
 'International']

etf_dict = {}
for sect in sectors:
    sym_name = df[df["sector"] == sect][["symbol","name"]]
    etf_dict[sect] = dict(zip(sym_name.symbol, sym_name.name))

period_dict = {"daily":"d", "weekly":"w", "monthly":"m"}

sect_dict = {}

## sidebar Menu
def do_sidebar():
    with st.sidebar:
        st.header("ETF")

        col1, col2 = st.columns([3,2])
        with col1:
            st.checkbox("Show Charts", value=True, key="show_chart")
        with col2:
            st.selectbox('Period:', list(period_dict.keys()), index=0, key="period")

        st.checkbox("Show ETF data", key="show_etf")

        st.subheader("select:")
        for sect in sectors:
            if sect == 'Equity Index':
                sect_dict[sect] = st.checkbox(sect, value=True, key=sect)
            else:
                sect_dict[sect] = st.checkbox(sect, key=sect)    


# @st.cache(ttl=3600, suppress_st_warning=True)
# def _show_chart_img(ticker, period):
#     st.image(f"https://finviz.com/chart.ashx?t={ticker}&p={period}")

# body
def do_body():

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
