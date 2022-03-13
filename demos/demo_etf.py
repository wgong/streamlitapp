"""
Streamlit ETF app

- source: 
    https://github.com/wgong/streamlitapp/blob/main/demos/demo_etf.py

- app:
    https://share.streamlit.io/wgong/streamlitapp/main/demos/demo_etf.py

"""


import streamlit as st

from os import mkdir, listdir
from os.path import exists, join, expanduser
import pickle
from traceback import format_exc

import pandas as pd
import numpy as np

import yfinance as yf
import mplfinance as mpf

# Initial page config
st.set_page_config(
     page_title='Streamlit Chart Demo',
     layout="wide",
     initial_sidebar_state="expanded",
)

# settings 
MAX_NUM_TICKERS  = 20
NUM_DAYS_QUOTE = 450
NUM_DAYS_PLOT = 300
RSI_PERIOD, RSI_AVG = 150, 30
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
MA_FAST, MA_SLOW, MA_LONG = 15, 50, 150
EMA_SLOW_SCALE = 2.0 
MA_VOL = 20

CHART_ROOT = expanduser("~/charts")
if not exists(CHART_ROOT):
    mkdir(CHART_ROOT)
FILE_CACHE_QUOTES = join(CHART_ROOT, "df_quotes_cache.pickle")

DEFAULT_SECTORS = ['Equity Index']
PERIOD_DICT = {"daily":"d", "weekly":"w", "monthly":"m"}

## i18n strings
_STR_HOME = "home"
_STR_CHART = "chart"
_STR_ETF_CHART = "ETF chart"
_STR_REVIEW_CHART = "review chart"
_STR_ETF_DATA = "ETF data"
_STR_APP_NAME = "MplFinance App"



##############################################
## helper functions
##############################################
def _parse_tickers(s):
    tmp = {}
    s = s.replace(",", " ")
    for t in s.split():
        tmp[t.upper()] = 1
    return list(tmp.keys())

def _download_quote(symbol, num_days=NUM_DAYS_QUOTE):
    return yf.Ticker(symbol).history(f"{num_days}d")

def _get_quotes(symbol, num_days=NUM_DAYS_QUOTE, cache=False):
    """
    check cache:
        import pickle
        df = pickle.load(open("df_quotes_cache.pickle", "rb"))
        df.keys()
    """
    if not cache:
        return _download_quote(symbol, num_days=num_days)
        
    if exists(FILE_CACHE_QUOTES):
        quote_data = pickle.load(open(FILE_CACHE_QUOTES, "rb"))
        if symbol in quote_data and num_days == quote_data[symbol]["num_days"]:
            df = quote_data[symbol]["df"]
        else:
            df = _download_quote(symbol, num_days=num_days)
            quote_data[symbol] = dict(num_days=num_days, df=df)
            pickle.dump(quote_data, open(FILE_CACHE_QUOTES, "wb"))
    else:
        df = _download_quote(symbol, num_days=num_days)
        quote_data = {}
        quote_data[symbol] = dict(num_days=num_days, df=df)
        pickle.dump(quote_data, open(FILE_CACHE_QUOTES, "wb"))

    return df

def _ta_MACD(df, fast_period=MACD_FAST, slow_period=MACD_SLOW, signal_period=MACD_SIGNAL):
    ema_fast = df["Close"].ewm(span=fast_period).mean()
    ema_slow = df["Close"].ewm(span=slow_period).mean()
    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal_period).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df

def _ta_RSI(df, n=RSI_PERIOD, rsi_avg=RSI_AVG, band_width=0.5):
    # https://github.com/wgong/mplfinance/blob/master/examples/rsi.py
    diff = df.w_p.diff().values
    gains = diff
    losses = -diff
    with np.errstate(invalid='ignore'):
        gains[(gains<0)|np.isnan(gains)] = 0.0
        losses[(losses<=0)|np.isnan(losses)] = 1e-10 # we don't want divide by zero/NaN
    m = (n-1) / n
    ni = 1 / n
    g = gains[n] = np.nanmean(gains[:n])
    l = losses[n] = np.nanmean(losses[:n])
    gains[:n] = losses[:n] = np.nan
    for i,v in enumerate(gains[n:],n):
        g = gains[i] = ni*v + m*g
    for i,v in enumerate(losses[n:],n):
        l = losses[i] = ni*v + m*l
    rs = gains / losses
    df['rsi'] = 100 - (100/(1+rs))
    df["rsi_avg"] = df.rsi.ewm(span=rsi_avg).mean()
    df["rsi_u"] = df["rsi_avg"] + band_width
    df["rsi_d"] = df['rsi_avg'] - band_width
    return df

def _calculate_ta(df):
    df["w_p"] = 0.25*(2*df["Close"] + df["High"] + df["Low"])
    df["ema_slow"]  = df.w_p.ewm(span=MA_SLOW).mean()

    # range
    h_l_mean25 = (df.High - df.Low).ewm(span=int(MA_SLOW/2)).mean()
    df["ema_slow"] = df.w_p.ewm(span=MA_SLOW).mean()
    df["ema_slow_u"] =  df.ema_slow + 0.5*h_l_mean25 * EMA_SLOW_SCALE
    df["ema_slow_d"] =  df.ema_slow - 0.5*h_l_mean25 * EMA_SLOW_SCALE
    df["ema_long"] = df.w_p.ewm(span=MA_LONG).mean()

    # trim volume to avoid exponential form
    df['Volume'] = df['Volume'] / 1000000
    df["vol_avg"] = df.Volume.ewm(span=MA_VOL).mean()
    df = _ta_RSI(df)
    return df    

@st.cache(ttl=7200)
def _chart(ticker, chart_root=CHART_ROOT):
    try:
        df = _get_quotes(ticker)
    except:
        return "", format_exc()
    
    df = _calculate_ta(df)
    df = df.iloc[-NUM_DAYS_PLOT:, :]  # slice after done with calculating TA   

    # # macd panel
    # df = _ta_MACD(df)
    # # df["macd"], df["macd_signal"], df["macd_hist"] = ta.MACD(df['Close'])
    # colors = ['g' if v >= 0 else 'r' for v in df["macd_hist"]]
    # macd_plot = mpf.make_addplot(df["macd"], panel=1, color='fuchsia', title="MACD")
    # macd_hist_plot = mpf.make_addplot(df["macd_hist"], type='bar', panel=1, color=colors) # color='dimgray'
    # macd_signal_plot = mpf.make_addplot(df["macd_signal"], panel=1, color='b')

    # candle overlay
    ema_slow_plot = mpf.make_addplot(df["ema_slow"], panel=0, color='red', linestyle="dashed")
    ema_slow_u_plot = mpf.make_addplot(df["ema_slow_u"], panel=0, color='b')
    ema_slow_d_plot = mpf.make_addplot(df["ema_slow_d"], panel=0, color='b')
    ema_long_plot = mpf.make_addplot(df["ema_long"], panel=0, color='green')
    
    # RSI
    rsi_plot = mpf.make_addplot(df["rsi"], panel=1, color='black', width=1, title=f"{ticker} - RSI")
    rsi_avg_plot = mpf.make_addplot(df["rsi_avg"], panel=1, color='red', linestyle="dashed")
    rsi_u_plot = mpf.make_addplot(df["rsi_u"], panel=1, color='b')
    rsi_d_plot = mpf.make_addplot(df["rsi_d"], panel=1, color='b')
    
    # volume
    vol_avg_plot = mpf.make_addplot(df["vol_avg"], panel=2, color='k')

    # plot
    plots = [
        # panel-0
        ema_slow_plot, ema_slow_u_plot, ema_slow_d_plot, ema_long_plot 
        #,macd_plot, macd_signal_plot, macd_hist_plot, 
        # panel-1
        ,rsi_plot, rsi_avg_plot, rsi_u_plot, rsi_d_plot 
        # panel-2
        ,vol_avg_plot                                   
    ]
    # custom style
    # https://stackoverflow.com/questions/68296296/customizing-mplfinance-plot-python
    
    file_png = join(chart_root, f"{ticker}.png")
    mpf.plot(df, type='candle', 
            style='yahoo', 
            panel_ratios=(4,3,1),
            mav=(MA_FAST), addplot=plots, 
            # title=f"{ticker}", 
            volume=True, volume_panel=2, 
            ylabel="", ylabel_lower='',
            datetime_format='%m-%d',
            savefig=file_png,
            figsize=(10,8),
            show_nontrading=True
        )
    return file_png


@st.cache
def _load_etf_df():
    # etf_df = pd.read_csv("./data/wl_futures_etf.csv")
    etf_data = [
        {'symbol': 'SPY', 'name': 'S&P 500', 'sector': 'Equity Index', 'order': 0.1} ,
        {'symbol': 'QQQ', 'name': 'Nasdaq 100', 'sector': 'Equity Index', 'order': 0.2} ,
        {'symbol': 'DIA', 'name': 'Dow 30', 'sector': 'Equity Index', 'order': 0.3} ,
        {'symbol': 'IWM', 'name': 'Russell 2000', 'sector': 'Equity Index', 'order': 0.4} ,
        {'symbol': 'SDS', 'name': 'Short S&P 500', 'sector': 'Equity Index', 'order': 0.7} ,
        {'symbol': 'QID', 'name': 'Short Nasdaq 100', 'sector': 'Equity Index', 'order': 0.8} ,
        {'symbol': 'DXD', 'name': 'Short Dow 30', 'sector': 'Equity Index', 'order': 0.9} ,
        {'symbol': 'XLE', 'name': 'Energy', 'sector': 'Sector', 'order': 1.001} ,
        {'symbol': 'XME', 'name': 'Metal', 'sector': 'Sector', 'order': 1.002} ,
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
        {'symbol': 'EWT', 'name': 'iShares MSCI Taiwan', 'sector': 'International', 'order': 10.281} ,
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
    etf_df = pd.DataFrame.from_dict(etf_data)
    
    # etf_sectors = etf_df["sector"].unique().tolist()
    # manual order
    etf_sectors = ['Equity Index',  'Sector',
        'Currency',  'Commodity',
        'Agri',  'Energy',  'Energy-Clean',
        'Metal',  'Technology',
        'International']

    etf_dict = {}
    for sect in etf_sectors:
        sym_name = etf_df[etf_df["sector"] == sect][["symbol","name"]]
        etf_dict[sect] = dict(zip(sym_name.symbol, sym_name.name))
    
    return etf_df, etf_sectors, etf_dict

etf_df, etf_sectors, etf_dict = _load_etf_df()

##############################################
## st handlers
##############################################

def do_dummy_item():
    st.title("Welcome")
    st.markdown("""
    This app is built on 
    - [yahoo-finance](https://github.com/ranaroussi/yfinance) for datafeed
    - [pandas](https://github.com/pandas-dev/pandas) for data-processing & analysis
    - [mplfinance](https://github.com/matplotlib/mplfinance) for charting
    - [streamlit](https://github.com/streamlit): an easy web-framework
    
    See [source code](https://github.com/wgong/streamlitapp/blob/main/demos/demo_etf.py)
    """)
    
def do_mpl_chart():
    """ chart new ticker
    """
    images = {}
    tickers = st.text_input(f'Enter ticker(s) (max {MAX_NUM_TICKERS})', "QQQ,SPY") 
    for ticker in _parse_tickers(tickers)[:MAX_NUM_TICKERS]:
        try:
            file_img = _chart(ticker)
            if file_img:
                images[ticker] = file_img
                st.image(file_img)
        except:
            st.error(f"invalid ticker: {ticker}\n{format_exc()}")
        
    # st.json(images)

def do_review(chart_root=CHART_ROOT):
    """ review existing charts
    """
    files = [f for f in listdir(chart_root) if f.endswith(".png")]
    tickers = [i.replace(".png", "") for i in files]
    selected_tickers = st.multiselect("Select tickers", tickers, [])
    for ticker in selected_tickers:
        file_png = join(chart_root, f"{ticker}.png")
        st.image(file_png)

def do_show_etf_data():
    st.dataframe(etf_df)

def do_show_etf_chart():
    """ ETF charts
    """
    period_item = st.session_state.get("period", "daily")
    period = PERIOD_DICT[period_item]

    for sect in st.session_state.get("selected_sectors", DEFAULT_SECTORS):
        st.subheader(sect)
        for k,v in etf_dict[sect].items():
            st.image(f"https://finviz.com/chart.ashx?t={k}&p={period}")
            st.markdown(f" [{k}](https://finviz.com/quote.ashx?t={k}&p={period}) : {v} ", unsafe_allow_html=True)
            # don't know how to get futures chart img


#####################################################
# menu_items
#####################################################

menu_dict = {
    _STR_HOME : {"fn": do_dummy_item},
    _STR_CHART: {"fn": do_mpl_chart},
    _STR_REVIEW_CHART: {"fn": do_review},
    _STR_ETF_CHART: {"fn": do_show_etf_chart},
    _STR_ETF_DATA: {"fn": do_show_etf_data},
}

## sidebar Menu
def do_sidebar():
    menu_options = list(menu_dict.keys())
    default_ix = menu_options.index(_STR_HOME)
    
    with st.sidebar:
        st.header(_STR_APP_NAME)

        menu_item = st.selectbox("Select", menu_options, index=default_ix, key="menu_item")

        if menu_item == _STR_ETF_CHART:
            col_sector, col_period = st.columns([4,2])
            with col_sector:
                selected_sectors = st.multiselect("Sectors", etf_sectors, DEFAULT_SECTORS, key="selected_sectors")

            with col_period:
                st.selectbox('Period:', list(PERIOD_DICT.keys()), index=0, key="period")


# @st.cache(ttl=3600, suppress_st_warning=True)
# def _show_chart_img(ticker, period):
#     st.image(f"https://finviz.com/chart.ashx?t={ticker}&p={period}")

  

# body
def do_body():
    menu_item = st.session_state.menu_item  
    menu_dict[menu_item]["fn"]()


def main():
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
