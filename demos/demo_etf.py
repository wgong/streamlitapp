"""
Streamlit ETF app

# source: 
    - https://github.com/wgong/streamlitapp/blob/main/demos/demo_etf.py

# app:
    - http://etf.s8s.cloud/
    - https://share.streamlit.io/wgong/streamlitapp/main/demos/demo_etf.py

"""

import streamlit as st

from PIL import Image
from pathlib import Path
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
MAX_NUM_TICKERS  = 30
NUM_DAYS_QUOTE = 390
NUM_DAYS_PLOT = 250
RSI_PERIOD, RSI_AVG = 100, 25
RSI_BAND_WIDTH = 0.9

MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
EMA_FAST, EMA_SLOW, EMA_LONG = 15, 50, 150
EMA_FAST_SCALE = 1.1  # EMA10 band half-width factor
EMA_SLOW_SCALE = 2.0 
MA_VOL = 20

CHART_ROOT = Path.home() / "charts"
if not Path.exists(CHART_ROOT):
    Path.mkdir(CHART_ROOT)
FILE_CACHE_QUOTES = Path.joinpath(CHART_ROOT, "df_quotes_cache.pickle")

DEFAULT_SECTORS = ['Equity Index']
PERIOD_DICT = {"daily":"d", "weekly":"w", "monthly":"m"}
QUOTE_COLS = ["Date", "Ticker", "%Chg", "Close", "Low", "High", "Close-1", "Low-1", "High-1"]

## i18n strings
_STR_HOME = "home"
_STR_CHART = "chart"
_STR_ETF_CHART = "ETF chart"
_STR_REVIEW_CHART = "review chart"
_STR_ETF_DATA = "ETF data"
_STR_APP_NAME = "Mplfinance App"


##############################################
## helper functions
##############################################
def _parse_tickers(s):
    tmp = {}
    s = s.replace(",", " ")
    for t in s.split():
        tmp[t.upper()] = 1
    return list(tmp.keys())

def _title_xy(ticker):
    # position title manually
    return {"title": f"{ticker}",  "x": 0.85, "y": 0.95}

def _finviz_chart_url(ticker, period="d"):
    return f"https://finviz.com/quote.ashx?t={ticker}&p={period}"

def _download_quote(symbol, num_days=NUM_DAYS_QUOTE):
    return yf.Ticker(symbol).history(f"{num_days}d")

@st.experimental_memo(ttl=7200)
def _get_quotes(symbol, num_days=NUM_DAYS_QUOTE, cache=False):
    """
    check cache:
        import pickle
        df = pickle.load(open("df_quotes_cache.pickle", "rb"))
        df.keys()
    """
    if not cache:
        return _download_quote(symbol, num_days=num_days)
        
    if Path.exists(FILE_CACHE_QUOTES):
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

def _ta_RSI(df, n=RSI_PERIOD, avg_period=RSI_AVG, band_width=RSI_BAND_WIDTH):
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
    # df["rsi_50"] = 50
    df['rsi'] = 100 - (100/(1+rs)) - 50
    df["rsi_avg"] = df.rsi.ewm(span=avg_period).mean()
    df["rsi_u"] = df["rsi_avg"] + band_width
    df["rsi_d"] = df['rsi_avg'] - band_width
    return df

def _calculate_ta(df):
    df["w_p"] = 0.25*(2*df["Close"] + df["High"] + df["Low"])
    df["ema_fast"] = df.w_p.ewm(span=EMA_FAST).mean()
    df["ema_slow"] = df.w_p.ewm(span=EMA_SLOW).mean()
    df["ema_long"] = df.w_p.ewm(span=EMA_LONG).mean()

    # range
    hl_mean_fast = (df.High - df.Low).ewm(span=int(EMA_FAST/2)).mean()
    df["ema_fast_u"] =  df.ema_fast + 0.5*hl_mean_fast * EMA_FAST_SCALE
    df["ema_fast_d"] =  df.ema_fast - 0.5*hl_mean_fast * EMA_FAST_SCALE

    hl_mean_slow = (df.High - df.Low).ewm(span=int(EMA_SLOW/2)).mean()
    df["ema_slow_u"] =  df.ema_slow + 0.5*hl_mean_slow * EMA_SLOW_SCALE
    df["ema_slow_d"] =  df.ema_slow - 0.5*hl_mean_slow * EMA_SLOW_SCALE

    # trim volume to avoid exponential form
    df['Volume'] = df['Volume'] / 1000000
    df["vol_avg"] = df.Volume.ewm(span=MA_VOL).mean()
    df = _ta_RSI(df)
    return df    

# @st.experimental_memo(ttl=7200)
def _chart(ticker, chart_root=CHART_ROOT):
    try:
        df = _get_quotes(ticker)
    except:
        return {"ticker": ticker, "err_msg": format_exc()}

    try:
        df = _calculate_ta(df)
    except:
        return {"ticker": ticker, "err_msg": format_exc()}

    # slice after done with calculating TA 
    df = df.iloc[-NUM_DAYS_PLOT:, :]    

    # # macd panel
    # df = _ta_MACD(df)
    # # df["macd"], df["macd_signal"], df["macd_hist"] = ta.MACD(df['Close'])
    # colors = ['g' if v >= 0 else 'r' for v in df["macd_hist"]]
    # macd_plot = mpf.make_addplot(df["macd"], panel=1, color='fuchsia', title="MACD")
    # macd_hist_plot = mpf.make_addplot(df["macd_hist"], type='bar', panel=1, color=colors) # color='dimgray'
    # macd_signal_plot = mpf.make_addplot(df["macd_signal"], panel=1, color='b')

    # candle overlay
    light_black = '#8F8E83'
    # ema_fast_plot = mpf.make_addplot(df["ema_fast"], panel=0, color='c', linestyle="dashed")
    ema_fast_u_plot = mpf.make_addplot(df["ema_fast_u"], panel=0, color=light_black, linestyle="solid")
    ema_fast_d_plot = mpf.make_addplot(df["ema_fast_d"], panel=0, color=light_black, linestyle="solid")
    ema_slow_plot = mpf.make_addplot(df["ema_slow"], panel=0, color='red', linestyle="dashed")
    # ema_slow_u_plot = mpf.make_addplot(df["ema_slow_u"], panel=0, color='b')
    # ema_slow_d_plot = mpf.make_addplot(df["ema_slow_d"], panel=0, color='b')
    ema_long_plot = mpf.make_addplot(df["ema_long"], panel=0, width=3, color='b')  # magenta '#ED8CEB'
    
    # RSI
    # make sure ylim are the same
    rsi_min = df.min(axis=0)[["rsi"]].min()
    rsi_max = df.max(axis=0)[["rsi"]].max()
    # rsi_50_color = "#F0DC16"  # yellow
    # if rsi_min >= 50:
    #     df["rsi_50"] = rsi_min
    #     rsi_50_color = "g"
    # if rsi_max <= 50:
    #     df["rsi_50"] = rsi_max
    #     rsi_50_color = "r"
    # rsi_50_plot = mpf.make_addplot(df["rsi_50"], panel=1, color=rsi_50_color, width=3, linestyle="solid", ylim=(rsi_min,rsi_max))
    rsi_plot = mpf.make_addplot(df["rsi"], panel=1, color='black', width=1, title="RSI", ylim=(rsi_min,rsi_max))
    rsi_avg_plot = mpf.make_addplot(df["rsi_avg"], panel=1, color='red', linestyle="dashed", ylim=(rsi_min,rsi_max))
    rsi_u_plot = mpf.make_addplot(df["rsi_u"], panel=1, color='b', ylim=(rsi_min,rsi_max))
    rsi_d_plot = mpf.make_addplot(df["rsi_d"], panel=1, color='b', ylim=(rsi_min,rsi_max))
    
    # volume
    vol_avg_plot = mpf.make_addplot(df["vol_avg"], panel=2, color='k')

    # plot
    plots = [
        # panel-0
        ema_fast_u_plot, ema_fast_d_plot, 
        ema_slow_plot, ema_long_plot # , ema_slow_u_plot, ema_slow_d_plot
        #,macd_plot, macd_signal_plot, macd_hist_plot, 
        # panel-1
        # , rsi_50_plot
        ,rsi_plot, rsi_avg_plot, rsi_u_plot, rsi_d_plot 
        # panel-2
        ,vol_avg_plot                              
    ]
    # custom style
    # https://stackoverflow.com/questions/68296296/customizing-mplfinance-plot-python
    
    file_img = Path.joinpath(chart_root, f"{ticker}.png")
    mpf.plot(df, type='candle', 
            style='yahoo', 
            fill_between=dict(y1=df["ema_slow_d"].values,y2=df["ema_slow_u"].values,alpha=0.15,color='b'),
            panel_ratios=(4,3,1),
            # mav=(EMA_FAST), 
            addplot=plots, 
            title=_title_xy(ticker),
            volume=True, volume_panel=2, 
            ylabel="", ylabel_lower='',
            xrotation=0,
            datetime_format='%m-%d',
            savefig=file_img,
            figsize=(st.session_state["FIGURE_WIDTH"],st.session_state["FIGURE_HEIGHT"]),
            tight_layout=True,
            show_nontrading=True
        )
    # # del [df]   # remove df
    # # del plots
    # st.dataframe(df)   # ["Close", "Low", "High", "Volume"]
    today_quote = df.iloc[-1, :].to_dict()
    prev_day_quote = df.iloc[-2, :].to_dict()
    return {"ticker": ticker, "file_img": file_img, "date": df.iloc[-1, :].name, "today_quote": today_quote, "prev_day_quote": prev_day_quote, "err_msg": None}


@st.experimental_memo
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

def go_home():
    st.subheader("Welcome")
    st.markdown("""
    This app is built on 
    - [yahoo-finance](https://github.com/ranaroussi/yfinance) for datafeed
    - [pandas](https://github.com/pandas-dev/pandas) for data-processing & analysis
    - [mplfinance](https://github.com/matplotlib/mplfinance) for chart
    - [streamlit](https://github.com/streamlit) (an easy framework) for application layout
    
    View [source code](https://github.com/wgong/streamlitapp/blob/main/demos/demo_etf.py)
    """, unsafe_allow_html=True)
    
def _reformat_quote(ticker_dict):
    date = pd.to_datetime(ticker_dict["date"]).date()  # convert timestamp to datetime
    ticker = ticker_dict["ticker"]
    low_1 = f'{ticker_dict["prev_day_quote"]["Low"]:.2f}'
    high_1 = f'{ticker_dict["prev_day_quote"]["High"]:.2f}'
    close_1 = f'{ticker_dict["prev_day_quote"]["Close"]:.2f}'
    low = f'{ticker_dict["today_quote"]["Low"]:.2f}'
    high = f'{ticker_dict["today_quote"]["High"]:.2f}'
    close = f'{ticker_dict["today_quote"]["Close"]:.2f}'
    chg = f'{100*(1- ticker_dict["prev_day_quote"]["Close"] / ticker_dict["today_quote"]["Close"]):.2f} %'
    # per QUOTE_COLS
    return [date, ticker, chg, close, low, high, close_1, low_1, high_1]

def do_mpl_chart():
    """ chart new ticker
    """
    quote_data = []
    images = {}
    tickers = st.text_input(f'Enter ticker(s) (max {MAX_NUM_TICKERS})', "SPY") 
    for ticker in _parse_tickers(tickers)[:MAX_NUM_TICKERS]:
        ticker_dict = _chart(ticker)
        err_msg = ticker_dict["err_msg"]
        if err_msg:
            st.error(f"Failed ticker: {ticker}\n{err_msg}")
            continue
        # st.write(ticker_dict)
        quote_data.append(_reformat_quote(ticker_dict))
        file_img = ticker_dict["file_img"]
        if file_img:
            images[ticker] = file_img
            st.image(Image.open(file_img))
            st.markdown(f"[{ticker}]({_finviz_chart_url(ticker)})", unsafe_allow_html=True)
            
    st.dataframe(pd.DataFrame(quote_data, columns=QUOTE_COLS), height=800)

def do_review(chart_root=CHART_ROOT):
    """ review existing charts
    """
    tickers = sorted([f.stem for f in Path(chart_root).glob("*.png")])
    selected_tickers = st.multiselect("Select tickers", tickers, [])
    for ticker in selected_tickers:
        file_img = Path.joinpath(chart_root, f"{ticker}.png")
        st.image(Image.open(file_img))
        st.markdown(f"[{ticker}]({_finviz_chart_url(ticker)})", unsafe_allow_html=True)

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
            st.markdown(f" [{k}]({_finviz_chart_url(k, period)}) : {v} ", unsafe_allow_html=True)
            # don't know how to get futures chart img


#####################################################
# menu_items
#####################################################

menu_dict = {
    _STR_HOME : {"fn": go_home},
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
            st.selectbox('Period:', list(PERIOD_DICT.keys()), index=0, key="period")
            selected_sectors = st.multiselect("Sectors", etf_sectors, DEFAULT_SECTORS, key="selected_sectors")


        if menu_item == _STR_REVIEW_CHART:
            st.image("https://user-images.githubusercontent.com/329928/158516907-5ba1e280-c40b-47c8-9f8c-4f96f7b6b411.PNG")
            st.image("https://user-images.githubusercontent.com/329928/158516907-5ba1e280-c40b-47c8-9f8c-4f96f7b6b411.PNG")
            btn_cleanup = st.button("Cleanup charts")
            if btn_cleanup:
                for f in Path(CHART_ROOT).glob("*.png"):
                    f.unlink()

        if menu_item == _STR_CHART:
            st.number_input("Figure width", value=16, key="FIGURE_WIDTH")
            st.number_input("Figure height", value=10, key="FIGURE_HEIGHT")

# body
def do_body():
    menu_item = st.session_state.menu_item  
    menu_dict[menu_item]["fn"]()


def main():
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
