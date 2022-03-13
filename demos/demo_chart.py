"""
Streamlit app template

The source code: 
    https://github.com/wgong/streamlitapp/blob/main/template_sidebar_body.py

"""

import streamlit as st 

import os.path
import pickle
import glob

import yfinance as yf
import mplfinance as mpf
# import talib as ta

import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data
import inspect

_DUMMY_ITEM = "_____"
# Initial page config
st.set_page_config(
     page_title='Streamlit Chart Demo',
     layout="wide",
     initial_sidebar_state="expanded",
)

MAX_NUM_TICKERS  = 20
NUM_OF_DAYS_QUOTE = 400
FILE_CACHE_QUOTES = os.path.expanduser("~/df_quotes_cache.pickle")

def download_quote(symbol, num_days=NUM_OF_DAYS_QUOTE):
    return yf.Ticker(symbol).history(f"{num_days}d")

def get_quotes(symbol, num_days=NUM_OF_DAYS_QUOTE, cache=False):
    """
    check cache:
        import pickle
        df = pickle.load(open("df_quotes_cache.pickle", "rb"))
        df.keys()
    """
    if not cache:
        return download_quote(symbol, num_days=num_days)
        
    if os.path.exists(FILE_CACHE_QUOTES):
        quote_data = pickle.load(open(FILE_CACHE_QUOTES, "rb"))
        if symbol in quote_data and num_days == quote_data[symbol]["num_days"]:
            df = quote_data[symbol]["df"]
        else:
            df = download_quote(symbol, num_days=num_days)
            quote_data[symbol] = dict(num_days=num_days, df=df)
            pickle.dump(quote_data, open(FILE_CACHE_QUOTES, "wb"))
    else:
        df = download_quote(symbol, num_days=num_days)
        quote_data = {}
        quote_data[symbol] = dict(num_days=num_days, df=df)
        pickle.dump(quote_data, open(FILE_CACHE_QUOTES, "wb"))

    return df

def _MACD(df, fastperiod=12, slowperiod=26, signalperiod=9):
    ema_fast = df["Close"].ewm(span=fastperiod).mean()
    ema_slow = df["Close"].ewm(span=slowperiod).mean()
    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signalperiod).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df

def do_dummy_item():
    st.title("dummy item")

def do_alt_chart():

    df = pd.DataFrame(
        np.random.randn(200, 3),
        columns=['a', 'b', 'c'])

    c = alt.Chart(df).mark_circle().encode(
        x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])

    st.altair_chart(c, use_container_width=True)    
    
def do_candlestick():


    source = data.ohlc()

    open_close_color = alt.condition("datum.open <= datum.close",
                                    alt.value("#06982d"),
                                    alt.value("#ae1325"))

    base = alt.Chart(source).encode(
        alt.X('date:T',
            axis=alt.Axis(
                format='%m/%d',
                labelAngle=-45,
                title='Date in 2009'
            )
        ),
        color=open_close_color
    )

    rule = base.mark_rule().encode(
        alt.Y(
            'low:Q',
            title='Price',
            scale=alt.Scale(zero=False),
        ),
        alt.Y2('high:Q')
    )

    bar = base.mark_bar().encode(
        alt.Y('open:Q'),
        alt.Y2('close:Q')
    )

    rule + bar
    try:
        st.altair_chart(base, use_container_width=True) 
    except:
        pass   


def do_hist():
    
    source = data.cars()

    h = alt.Chart(source).mark_bar().encode(
        alt.X("Horsepower:Q", bin=True),
        y='count()',
        row='Origin'
    ) 
    st.altair_chart(h, use_container_width=True)

@st.cache(ttl=7200)
def _chart(ticker):
    try:
        df = get_quotes(ticker)
    except:
        return ""
    
    # trim volume to avoid exponential form
    df['Volume'] = df['Volume'] / 1000000

    # macd
    df = _MACD(df)
    # df["macd"], df["macd_signal"], df["macd_hist"] = ta.MACD(df['Close'])

    # macd panel
    colors = ['g' if v >= 0 else 'r' for v in df["macd_hist"]]
    macd_plot = mpf.make_addplot(df["macd"], panel=1, color='fuchsia', title="MACD")
    macd_hist_plot = mpf.make_addplot(df["macd_hist"], type='bar', panel=1, color=colors) # color='dimgray'
    macd_signal_plot = mpf.make_addplot(df["macd_signal"], panel=1, color='b')

    # plot
    plots = [macd_plot, macd_signal_plot, macd_hist_plot]
    file_png = os.path.expanduser(os.path.join("~", f"chart_{ticker}.png"))
    mpf.plot(df, type='candle', style='yahoo', 
            mav=(20,50,150), addplot=plots, 
            title=f"{ticker}", 
            volume=True, volume_panel=2, 
            ylabel="", ylabel_lower='',
            datetime_format='%m-%d',
            savefig=file_png
        )
    return file_png

def _parse_tickers(s):
    tmp = {}
    s = s.replace(",", " ")
    for t in s.split():
        tmp[t.upper()] = 1
    return list(tmp.keys())

def do_mpl_chart():
    images = {}
    tickers = st.text_input('Enter ticker(s)', "QQQ") 
    for ticker in _parse_tickers(tickers)[:MAX_NUM_TICKERS]:
        try:
            file_img = _chart(ticker)
            if file_img:
                images[ticker] = file_img
                st.image(file_img)
        except:
            st.error(f"invalid ticker: {ticker}")
        
    # st.json(images)
    
def do_review():
    dir = os.path.expanduser("~")
    files = [f for f in os.listdir(os.path.expanduser("~")) if f.startswith("chart_") and f.endswith(".png")]
    tickers = [i.replace("chart_", "").replace(".png", "") for i in files]
    selected_tickers = st.multiselect("Select tickers", tickers, [])
    for ticker in selected_tickers:
        file_png = os.path.expanduser(os.path.join("~", f"chart_{ticker}.png"))
        st.image(file_png)

#####################################################
# menu_items
menu_dict = {
    _DUMMY_ITEM : {"fn": do_dummy_item},
    "altchart": {"fn": do_alt_chart},
    "histogram": {"fn": do_hist},
    "candlestick": {"fn": do_candlestick},
    "mplfinance": {"fn": do_mpl_chart},
    "review": {"fn": do_review},
}

# body
def do_body():
    menu_item = st.session_state.menu_item  
    menu_dict[menu_item]["fn"]()


    # if st.checkbox('Show code ...', key="do_body"):
    #     st.code(inspect.getsource(do_body))

def do_sidebar():

    menu_options = sorted(list(menu_dict.keys()))
    default_ix = menu_options.index(_DUMMY_ITEM)
    menu_item = st.sidebar.selectbox("Select: ", menu_options, index=default_ix, key="menu_item")


    # if st.sidebar.checkbox('Show code ...', key="do_sidebar"):
    #     st.sidebar.code(inspect.getsource(do_sidebar))


def main():
    do_sidebar()
    do_body()

# Run main()
if __name__ == '__main__':
    main()
    

