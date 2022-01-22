import os
import time
from pathlib import Path
import base64
import inspect

import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
import altair as alt
# import plotly.figure_factory as ff
# from bokeh.plotting import figure

import streamlit as st

# Initial page config

st.set_page_config(
     page_title='Streamlit Concept Demo',
     layout="wide",
     initial_sidebar_state="expanded",
)

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def demo_data():

    ## Display Data
    st.header('Data')

    st.subheader('st.write anything')
    st.write(pd.DataFrame({
        'first column': list(range(5)),
        'second column': [100*i for i in range(5)]
    }))

    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    })
    df # same as : st.write(df)

    st.subheader('st.json')
    st.json({'foo':'bar','fu':'ba'})

    st.subheader('st.metric')
    st.metric(label="T", value="273 K", delta="1.2 K")


    st.subheader('st.dataframe makes interactive table')
    df = np.random.randn(10, 20)
    st.dataframe(df)

    dataframe = pd.DataFrame(
        np.random.randn(10, 20),
        columns=('col %d' % i for i in range(20)))
    st.dataframe(dataframe.style.highlight_max(axis=0))

    st.subheader('st.table makes static table')
    st.table(dataframe)

    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])
    st.line_chart(chart_data)



def demo_chart():
    df = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])

    st.subheader('st.line_chart')
    st.line_chart(df)    

    st.subheader('st.area_chart')
    st.area_chart(df)    

    st.subheader('st.bar_chart')  # not easy for unstack bar
    st.bar_chart(df)   

    # st.subheader('st.pyplot') 
    # arr = np.random.normal(1, 1, size=100)
    # fig, ax = plt.subplots()
    # ax.hist(arr, bins=20)
    # st.pyplot(fig)

    st.subheader('st.altair_chart') 
    c = alt.Chart(df).mark_circle().encode(
        x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
    st.altair_chart(c, use_container_width=True)

    # st.subheader('st.plotly_chart') 
    # # Add histogram data
    # x1 = np.random.randn(200) - 2
    # x2 = np.random.randn(200)
    # x3 = np.random.randn(200) + 2

    # # Group data together
    # hist_data = [x1, x2, x3]

    # group_labels = ['Group 1', 'Group 2', 'Group 3']

    # # Create distplot with custom bin_size
    # fig = ff.create_distplot(
    #         hist_data, group_labels, bin_size=[.1, .25, .5])

    # st.plotly_chart(fig, use_container_width=True)

    st.subheader('st.graphviz_chart') 
    st.graphviz_chart('''
        digraph {
            run -> intr
            intr -> runbl
            runbl -> run
            run -> kernel
            kernel -> zombie
            kernel -> sleep
            kernel -> runmem
            sleep -> swap
            swap -> runswap
            runswap -> new
            runswap -> runmem
            new -> runmem
            sleep -> runmem
        }
    ''')

    st.subheader('st.map')
    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
        columns=['lat', 'lon'])
    st.map(map_data)    

    # st.subheader('st.bokeh_chart') 
    # x = [1, 2, 3, 4, 5]
    # y = [i*i for i in x]

    # p = figure(
    #     title='simple line example',
    #     x_axis_label='x',
    #     y_axis_label='y')

    # p.line(x, y, legend_label='Squared', line_width=2)
    # st.bokeh_chart(p, use_container_width=True)

def demo_media():
    st.title('Media ')

    st.header('Image ')
    st.subheader("glipse of [Huangshan](https://www.google.com/search?rlz=1C1CHBF_enUS949US953&sxsrf=AOaemvKjSzJqu-a89inA5ddCLPwN6yTS5A:1642809970191&source=univ&tbm=isch&q=huangshan+image&fir=c5JbjbKRqMYzSM%252CprEGJfbX4gK1QM%252C_%253BKDGXUGwkG9HJlM%252CprEGJfbX4gK1QM%252C_%253BsAJIYULVc8LIdM%252CjlUYtsu-BMNYnM%252C_%253BT3diVkmbJwRCvM%252CuULWDkXX6y_AtM%252C_%253BNM8dklixiMn4JM%252CY4uyDKPk0t-hvM%252C_%253Bzif9QvqQ0usaHM%252Cr3dKhkFPF8GyfM%252C_%253Bh9TJ9g_37Sit_M%252C7PkIwO15CHEAMM%252C_%253BIesJFYFRE_C7XM%252CezzzG1WCERTNsM%252C_%253BU4XoFhMNdyHevM%252CprEGJfbX4gK1QM%252C_%253BTQOabpFHQuMFyM%252ClNJBXwZLn85NCM%252C_%253BWu0q9fYRBcmCwM%252CmkDBcTJMjszmsM%252C_%253BF0lwAmH5NowxPM%252CTzSKpaqZ1Dq6MM%252C_%253BWykWSfyVqd4ZKM%252C-vYDZcuHEz0gKM%252C_&usg=AI4_-kRSL2DKzRpR64M2F5njm_m_qp3LGg&sa=X&ved=2ahUKEwi6_dKFiMT1AhWhlGoFHdYZBLEQ7Al6BAgGEDw&biw=1389&bih=826&dpr=1)")
    st.image("https://images.chinahighlights.com/allpicture/2019/12/b50add17df9d489a967108d5_cut_800x500_66.jpg",
        caption="The Yellow Mountain in Anhui, China")
    st.header('Audio ')
    st.subheader("clips from [SoundHelix](https://www.soundhelix.com/audio-examples)")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    st.header('Video ')

    st.video("https://www.youtube.com/watch?v=q2KBWmiL71o")

def demo_widget():

    ## UI control
    st.header('Widgets ')

    st.subheader('st.slider')  
    # Add a slider to the sidebar:
    slider_range = st.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )
    st.write(f"Range: {slider_range}")

    slider_value = st.slider(
        'Select a values',
        0.0, 100.0, 50.0
    )
    st.write(f"Value: {slider_value}")

    x = st.slider('x') # 👈 this is a widget
    st.write(x, 'squared is', x * x)

    st.subheader('st.text_input ')
    st.text_input("Your name", key="name")
    # You can access the value at any point with:
    st.write(f"You entered: {st.session_state.name}")

    st.subheader('st.selectbox ')
    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    })
    option = st.selectbox(
        'Which number do you like best?',
        df['first column'])
    'You selected: ', option

    # Add a selectbox to the sidebar:
    selectbox_contact = st.selectbox(
        'How would you like to be contacted?',   # label
        ('Email', 'Home phone', 'Mobile phone')
    )
    st.write(f"You prefer to be contacted by : {selectbox_contact}")

    st.subheader('st.checkbox ')
    if st.checkbox('Show dataframe'):
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['a', 'b', 'c'])
        chart_data

    st.subheader('st.progress')
    'Starting a long computation...'
    # Add a placeholder
    latest_iteration = st.empty()
    bar = st.progress(0)
    for i in range(30):
        # Update the progress bar with each iteration.
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
        time.sleep(0.1)
    '...and now we\'re done!'



def demo_layout():

    ## UI Layout
    st.header('Layout')

    st.subheader('st.columns')  
    left_column, right_column = st.columns(2)

    # You can use a column just like st.sidebar:
    with left_column:
        st.subheader('st.button')    
        st.button('Press me!')
    # Or even better, call Streamlit functions inside a "with" block:
    with right_column:
        st.subheader('st.radio')    
        chosen = st.radio(
            'Sorting hat',
            ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
        st.write(f"You are in {chosen} house!")

def demo_theme():

    ## Theme
    st.header('Theme')

@st.cache # 👈 below function will be cached
def Fibonacci(n):
    # Function for nth Fibonacci number

    # Check if input is 0 then it will
    # print incorrect input
    if n < 0:
        print(f"Incorrect input: {n}, must be an int >=0")
        return None

    # Check if n is 0
    # then it will return 0
    elif n == 0:
        return 0

    # Check if n is 1,2
    # it will return 1
    elif n == 1 or n == 2:
        return 1
    else:
        return Fibonacci(n-1) + Fibonacci(n-2)

def demo_cache():
    
    ## Caching
    st.header('Caching')
    num = st.slider("num", 1, 100, 5)
    ts_start = time.time()
    fib_num = Fibonacci(num)
    ts_duration = time.time() - ts_start
    st.write(f"Fib({num}) = {fib_num} \n calculated in {ts_duration:.3f} sec")
    st.button("Re-Run")

    st.markdown("""##### Note:
    - calculating Fib of the same number takes much smaller constant time
    - sub-function within recursive calls are also cached
    """)

def demo_misc():

    st.header('Misc')
    st.write(f"os.getcwd() = {os.getcwd()}" )

## sidebar Menu
def demo_sidebar():
    global menu_item

    st.sidebar.markdown('''
    [<img src='data:image/png;base64,{}' class='img-fluid' width=32 height=32>](https://streamlit.io/)
    '''.format(img_to_bytes("streamlit_logo.png")), unsafe_allow_html=True)

    st.sidebar.markdown("""
    <span style="color:red">__Streamlit__ </span>: Why-What-How
    """, unsafe_allow_html=True)
    st.sidebar.video("https://www.youtube.com/watch?v=R2nr1uZ8ffc")
    menu_options = ("Data", "Chart", "Media", "Widget", "Layout", "Theme", "Cache", "Misc")
    default_ix = menu_options.index("Chart")
    st.sidebar.markdown("[Concepts](https://docs.streamlit.io/library/get-started/main-concepts)")
    menu_item = st.sidebar.selectbox("Explore: ", menu_options, index=default_ix)
    st.sidebar.markdown("""
    <small>Since Streamlit runs script from top to bottom, we use menu-item to split
    the whole script into sections, so only a selected section is rerun
    </small>""", unsafe_allow_html=True)

    st.sidebar.write("""
    Resources
    - [Cheatsheet](https://docs.streamlit.io/library/cheatsheet)
    - [API Reference](https://docs.streamlit.io/library/api-reference)
    - [Components](https://docs.streamlit.io/library/components)
    - [Gallery](https://streamlit.io/gallery)
    - [Community](https://discuss.streamlit.io/)
    """)


# body
def demo_body():
    global menu_item

    if menu_item == "Data":
        demo_data()
        if st.checkbox('Show code ...'):
            st.code(inspect.getsource(demo_data))
    elif menu_item == "Chart":
        demo_chart()
        if st.checkbox('Show code ...'):
            st.code(inspect.getsource(demo_chart))

    elif menu_item == "Media":
        demo_media()
        if st.checkbox('Show code ...'):
            st.code(inspect.getsource(demo_media))

    elif menu_item == "Widget":
        demo_widget()
        if st.checkbox('Show code ...'):
            st.code(inspect.getsource(demo_widget))
    elif menu_item == "Layout":
        demo_layout()
        if st.checkbox('Show code ...'):
            st.code(inspect.getsource(demo_layout))
    elif menu_item == "Theme":
        demo_theme()
        if st.checkbox('Show code ...'):
            st.code(inspect.getsource(demo_theme))
    elif menu_item == "Misc":
        demo_misc()
        if st.checkbox('Show code ...'):
            st.code(inspect.getsource(demo_misc))
    else:
        demo_cache()  # default
        if st.checkbox('Show code ...'):
            st.code(inspect.getsource(demo_cache))


def main():
    demo_sidebar()
    demo_body()

# Run main()
if __name__ == '__main__':
    main()