import streamlit as st
from mycomponent import mycomponent
value = mycomponent(my_input_value="")
st.write("Received: ", value)