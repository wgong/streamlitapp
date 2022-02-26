#when we import hydralit, we automatically get all of Streamlit
import hydralit as hy
import pandas as pd
import numpy as np

app = hy.HydraApp(title='Simple Multi-Page App')

@app.addapp()
def page_markdown():
    hy.info('Hello from Markdown page')
    hy.markdown("<h2> Hello Streamlit, <br/> what a cool tool! </h2>", unsafe_allow_html=True)

@app.addapp()
def page_video():
    hy.info('Hello from Video page')
    hy.video("https://www.youtube.com/watch?v=h2P9AmGcMdM")

@app.addapp()
def page_df():
    hy.info('Hello from Dataframe page')
    N = 50
    rand = pd.DataFrame()
    rand['a'] = np.arange(N)
    rand['b'] = np.random.rand(N)
    rand['c'] = np.random.rand(N)
    hy.dataframe(rand)

#Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
app.run()