import streamlit as st

from datetime import datetime
import time

def do_work(time_spent=5):
    time.sleep(time_spent)

time_spent = st.number_input("time", disabled=True)
t1 = datetime.now()
# t1 = time.time()
do_work(int(time_spent))
t2 = datetime.now()
# t2 = time.time()
st.write(f"{t2-t1}")