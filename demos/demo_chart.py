"""
Streamlit app template

The source code: 
    https://github.com/wgong/streamlitapp/blob/main/template_sidebar_body.py

"""

import streamlit as st 

import os.path
import pickle

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


NUM_OF_DAYS_QUOTE = 400
FILE_CACHE_QUOTES = os.path.expanduser("~/df_quotes_cache.pickle")

def download_quote(symbol, num_days=NUM_OF_DAYS_QUOTE):
    return yf.Ticker(symbol).history(f"{num_days}d")

def get_quotes(symbol, num_days=NUM_OF_DAYS_QUOTE, cache=False):
    """
    check cache:
        import pickle
        data = pickle.load(open("df_quotes_cache.pickle", "rb"))
        data.keys()
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

def _MACD(data, fastperiod=12, slowperiod=26, signalperiod=9):
    ema_fast = data["Close"].ewm(span=fastperiod).mean()
    ema_slow = data["Close"].ewm(span=slowperiod).mean()
    data["macd"] = ema_fast - ema_slow
    data["macd_signal"] = data["macd"].ewm(span=signalperiod).mean()
    data["macd_hist"] = data["macd"] - data["macd_signal"]
    return data

def do_dummy_item():
    st.title("dummy item")

def do_chart_1():

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

def do_mpl():
    ticker_name = "QQQ"
    data = get_quotes(ticker_name, cache=True)
    # trim volume to avoid exponential form
    data['Volume'] = data['Volume'] / 1000000

    # macd
    data = _MACD(data)
    # data["macd"], data["macd_signal"], data["macd_hist"] = ta.MACD(data['Close'])

    # macd panel
    colors = ['g' if v >= 0 else 'r' for v in data["macd_hist"]]
    macd_plot = mpf.make_addplot(data["macd"], panel=1, color='fuchsia', title="MACD")
    macd_hist_plot = mpf.make_addplot(data["macd_hist"], type='bar', panel=1, color=colors) # color='dimgray'
    macd_signal_plot = mpf.make_addplot(data["macd_signal"], panel=1, color='b')

    # plot
    plots = [macd_plot, macd_signal_plot, macd_hist_plot]
    file_png = os.path.expanduser(os.path.join("~", f"{ticker_name}.png"))
    mpf.plot(data, type='candle', style='yahoo', 
            mav=(50,100,200), addplot=plots, 
            title=f"{ticker_name}", volume=True, volume_panel=2, 
            ylabel='', ylabel_lower='',
            datetime_format='%m-%d',
            savefig=file_png
        )
    st.image(file_png)


#####################################################
# menu_items
menu_dict = {
    _DUMMY_ITEM : {"fn": do_dummy_item},
    "altchart-1": {"fn": do_chart_1},
    "candlestick": {"fn": do_candlestick},
    "histogram": {"fn": do_hist},
    "mplfinance": {"fn": do_mpl},
}

# body
def do_body():
    menu_item = st.session_state.menu_item  
    menu_dict[menu_item]["fn"]()


    if st.checkbox('Show code ...', key="do_body"):
        st.code(inspect.getsource(do_body))

def do_sidebar():

    menu_options = sorted(list(menu_dict.keys()))
    default_ix = menu_options.index(_DUMMY_ITEM)
    menu_item = st.sidebar.selectbox("Select: ", menu_options, index=default_ix, key="menu_item")


    if st.sidebar.checkbox('Show code ...', key="do_sidebar"):
        st.sidebar.code(inspect.getsource(do_sidebar))


def main():
    do_sidebar()
    do_body()

# Run main()
if __name__ == '__main__':
    main()
    

