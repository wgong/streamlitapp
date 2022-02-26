import streamlit as st

from datetime import datetime
import time

def do_work(time_spent=5):
    time.sleep(time_spent)

t1 = datetime.now()
do_work()
t2 = datetime.now()

st.write(f"{t2-t1}")