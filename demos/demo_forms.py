import streamlit as st 

st.title("Demo Streamlit Forms & Submit")

with st.form(key = "form1"):
    name =  st.text_input(label = "Enter the model name")
    number =  st.slider("Enter your age", min_value=10, max_value = 100 )
    submit =  st.form_submit_button(label = "Submit this form")
    if submit:
        st.json({"name":name, "number":number})

col1, col2 = st.columns(2)

with col1:
    with st.form('Form1'):
        flavor = st.selectbox('Select flavor', ['Vanilla', 'Chocolate'], key=1)
        intensity = st.slider(label='Select intensity', min_value=0, max_value=100, key=4)
        submitted1 = st.form_submit_button('Submit 1')
        if submitted1:
            st.json({"flavor":flavor, "intensity":intensity})

with col2:
    with st.form('Form2'):
        topping = st.selectbox('Select Topping', ['Almonds', 'Sprinkles'], key=2)
        intensity = st.slider(label='Select Intensity', min_value=0, max_value=100, key=3)
        submitted2 = st.form_submit_button('Submit 2')
        if submitted2:
            st.json({"topping":topping, "intensity":intensity})


st.markdown("Columns inside form")

with st.form(key='columns_in_form'):
    cols = st.columns(5)
    val_dict = {}
    for i, col in enumerate(cols):
        val_dict[f"Col_{i}"] = col.selectbox(f'Col_{i}', [f"col_{i}_val_{j}" for j in range(6)], key=i)
    submitted = st.form_submit_button('Submit')
    if submitted:
        st.json(val_dict)

