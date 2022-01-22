"""
Streamlit Concept and Hello Demo
based on 
1) https://docs.streamlit.io/library/get-started/main-concepts
2) 

The source code: 
    https://github.com/wgong/streamlitapp/blob/main/demos/demo_concept.py

"""

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
import pydeck as pdk
from urllib.error import URLError


st_tutorials_data = {
    "shail_deliwala" : {
        "title" : "Streamlit 101",
        "blog"  : {
            "url" : "https://towardsdatascience.com/streamlit-101-an-in-depth-introduction-fc8aad9492f2",
            "desc" : "Streamlit 101: An in-depth introduction - Airbnb NYC data"
        }
    },
    "data_professor" : {
        "title" : "Streamlit Web App in Python by Data Professor",
        "vid" : {
            "url" : "https://www.youtube.com/watch?v=ZZ4B0QUHuNc&list=PLtqF5YXg7GLmCvTswG32NqQypOuYkPRUE",
            "desc" : "How to Build Your First Data Science Web App in Python - Streamlit Tutorial"
        },
        "src" : {
            "url" : "https://github.com/dataprofessor/code.git",
            "desc" :"github/dataprofessor/code"
        }
    },
    "jcharis" : {
        "title" : "Streamlit Python Tutorials Crash Course",
        "vid" : {
            "url" : "https://www.youtube.com/watch?v=6acv9LL6gHg&list=PLJ39kWiJXSixyRMcn3lrbv8xI8ZZoYNZU&index=2",
            "desc" :"Building a NLP App with Streamlit,Spacy and Python"
        },
        "src" : {
            "url" : "https://github.com/Jcharis/DataScienceTools.git",
            "desc" :"github/JCharis/DataScienceTools"
        }
    },
    "part_time_larry" : {
        "title" : "Streamlit Tutorials by Part Time Larry",
        "vid" : {
            "url" : "https://www.youtube.com/watch?v=0ESc1bh3eIg",
            "desc" :"Streamlit - Building Financial Dashboards with Python"
        },
        "src" : {
            "url" : "https://github.com/hackingthemarkets/streamlit-dashboards.git",
            "desc" :"github/hackingthemarkets/streamlit-dashboards"
        }
    }
}

# Initial page config


st.set_page_config(
     page_title='Streamlit Concept Demo',
     layout="wide",
     initial_sidebar_state="expanded",
)

@st.cache
def get_UN_data():
    AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")

@st.cache
def from_data_file(filename):
    url = (
        "http://raw.githubusercontent.com/streamlit/"
        "example-data/master/hello/v1/%s" % filename)
    return pd.read_json(url)

@st.cache # 👈 below function will be cached
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

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

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_data))



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

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_chart))

def demo_media():
    st.title('Media ')

    st.header('Image ')
    st.subheader("glipse of [Huangshan](https://www.google.com/search?rlz=1C1CHBF_enUS949US953&sxsrf=AOaemvKjSzJqu-a89inA5ddCLPwN6yTS5A:1642809970191&source=univ&tbm=isch&q=huangshan+image&fir=c5JbjbKRqMYzSM%252CprEGJfbX4gK1QM%252C_%253BKDGXUGwkG9HJlM%252CprEGJfbX4gK1QM%252C_%253BsAJIYULVc8LIdM%252CjlUYtsu-BMNYnM%252C_%253BT3diVkmbJwRCvM%252CuULWDkXX6y_AtM%252C_%253BNM8dklixiMn4JM%252CY4uyDKPk0t-hvM%252C_%253Bzif9QvqQ0usaHM%252Cr3dKhkFPF8GyfM%252C_%253Bh9TJ9g_37Sit_M%252C7PkIwO15CHEAMM%252C_%253BIesJFYFRE_C7XM%252CezzzG1WCERTNsM%252C_%253BU4XoFhMNdyHevM%252CprEGJfbX4gK1QM%252C_%253BTQOabpFHQuMFyM%252ClNJBXwZLn85NCM%252C_%253BWu0q9fYRBcmCwM%252CmkDBcTJMjszmsM%252C_%253BF0lwAmH5NowxPM%252CTzSKpaqZ1Dq6MM%252C_%253BWykWSfyVqd4ZKM%252C-vYDZcuHEz0gKM%252C_&usg=AI4_-kRSL2DKzRpR64M2F5njm_m_qp3LGg&sa=X&ved=2ahUKEwi6_dKFiMT1AhWhlGoFHdYZBLEQ7Al6BAgGEDw&biw=1389&bih=826&dpr=1)")
    st.image("https://images.chinahighlights.com/allpicture/2019/12/b50add17df9d489a967108d5_cut_800x500_66.jpg",
        caption="The Yellow Mountain in Anhui, China")


    st.header('Video ')
    st.video("https://www.youtube.com/watch?v=rOjHhS5MtvA")
    st.video("https://www.youtube.com/watch?v=q2KBWmiL71o")

    st.header('Audio ')
    st.subheader("classical music from [http://www.lisztonian.com/](http://www.lisztonian.com/titles/index.php?s=title)")
    st.write("Bagatelle in A Minor - WoO 59 (Fur Elise or For Elise) - Ludwig Van Beethoven")
    st.audio("http://download.lisztonian.com/music/download/Bagatelle+in+A+Minor++WoO+59-81.mp3")

    st.subheader("clips from [SoundHelix](https://www.soundhelix.com/audio-examples)")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_media))



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

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_widget))


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

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_layout))


def demo_theme():

    ## Theme
    st.header('Theme')
    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_theme))

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

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_cache))

def demo_learn():

    st.header("Learn Streamlit")

    for k in st_tutorials_data.keys():
        st.subheader(st_tutorials_data[k]["title"])
        st_data = st_tutorials_data[k]
        if "vid" in st_data:
            # display video
            st.video(st_data["vid"]["url"])
            st.markdown(f"""
            - [{st_data["vid"]["desc"]}]({st_data["vid"]["url"]})
            """)
        if "src" in st_data:
            # display src
            st.markdown(f"""
            - [{st_data["src"]["desc"]}]({st_data["src"]["url"]})
            """)
        if "blog" in st_data:
            # display blog
            st.markdown(f"""
            - [{st_data["blog"]["desc"]}]({st_data["blog"]["url"]})
            """)
    
    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_learn))

def demo_misc():

    st.header('Misc')
    st.write(f"os.getcwd() = {os.getcwd()}" )

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_misc))

## sidebar Menu
def demo_sidebar():
    st.sidebar.markdown('''
    [<img src='https://streamlit.io/images/brand/streamlit-mark-color.svg' class='img-fluid' width=32 height=32>](https://streamlit.io/)
    ''', unsafe_allow_html=True)

    st.sidebar.markdown("""
    <span style="color:red">__Streamlit__ </span>: Why-What-How
    """, unsafe_allow_html=True)
    st.sidebar.video("https://www.youtube.com/watch?v=R2nr1uZ8ffc")

    st.sidebar.markdown("[__Concepts__](https://docs.streamlit.io/library/get-started/main-concepts)")
    menu_options = ("Data", "Chart", "Media", "Widget", "Layout", "Theme", "Cache", "Learn", "Misc")
    default_ix = menu_options.index("Chart")
    menu_item = st.sidebar.selectbox("Explore: ", menu_options, index=default_ix, key="menu_item")
    st.sidebar.markdown("""
    <small>Since Streamlit runs script from top to bottom, we use menu-item to split
    the whole script into sections, so only a selected section is rerun
    </small>""", unsafe_allow_html=True)

    st.sidebar.markdown("__Demos__")
    demo_options = ["_____", "Animation", "Plotting", "Mapping", "Dataframe"]
    demo_ix = demo_options.index("_____")
    demo_item = st.sidebar.selectbox("Pick a demo: ", demo_options, index=demo_ix, key="demo_item")
    st.sidebar.markdown("""
    <small>Streamlit builtin demos (unpick to explore concept)
    </small>""", unsafe_allow_html=True)
    st.sidebar.code('$ streamlit hello')


    st.sidebar.write("""
    __Resources__
    - [Cheatsheet](https://docs.streamlit.io/library/cheatsheet)
    - [API Reference](https://docs.streamlit.io/library/api-reference)
    - [Components](https://docs.streamlit.io/library/components)
    - [Gallery](https://streamlit.io/gallery)
    - [Community](https://discuss.streamlit.io/)
    """)

    if st.sidebar.checkbox('Show code ...', key="sidebar_src"):
        st.sidebar.code(inspect.getsource(demo_sidebar))

# body
def demo_body():
    menu_item = st.session_state.menu_item
    demo_item = st.session_state.demo_item

    # if st.session_state.sidebar_src:
    #     st.session_state.sidebar_src = False  # cannot be reset

    # demo hello
    if demo_item == "Animation":
        demo_animation()
    elif demo_item == "Plotting":
        demo_plotting()
    elif demo_item == "Mapping":
        demo_mapping()
    elif demo_item == "Dataframe":
        demo_dataframe()
    else:
        # demo concepts
        if menu_item == "Data":
            demo_data()
        elif menu_item == "Cache":
            demo_cache()  
        elif menu_item == "Chart":  # default
            demo_chart()
        elif menu_item == "Media":
            demo_media()
        elif menu_item == "Widget":
            demo_widget()
        elif menu_item == "Layout":
            demo_layout()
        elif menu_item == "Theme":
            demo_theme()
        elif menu_item == "Learn":
            demo_learn()
        elif menu_item == "Misc":
            demo_misc()


def demo_animation():

    st.title("Animation  Demo")
    st.markdown('''
    This demo displays an animated fractal based on the the Julia Set. Use the slider to tune different parameters.
    ''', unsafe_allow_html=True)


    # Interactive Streamlit elements, like these sliders, return their value.
    # This gives you an extremely simple interaction model.
    left_column, right_column = st.columns(2)
    with left_column:
        iterations = st.slider("Level of detail", 2, 20, 10, 1)
    with right_column:
        separation = st.slider("Separation", 0.7, 2.0, 0.7885)

    # Non-interactive elements return a placeholder to their location
    # in the app. Here we're storing progress_bar to update it later.
    progress_bar = st.progress(0)

    # These two elements will be filled in later, so we create a placeholder
    # for them using st.empty()
    frame_text = st.empty()
    image = st.empty()
    n_frames = 50
    m, n, s = 960, 640, 400
    x = np.linspace(-m / s, m / s, num=m).reshape((1, m))
    y = np.linspace(-n / s, n / s, num=n).reshape((n, 1))

    for frame_num, a in enumerate(np.linspace(0.0, 4 * np.pi, n_frames)):
        # Here were setting value for these two elements.
        progress_bar.progress(frame_num)
        frame_text.text("Frame %i/%i" % (frame_num + 1, n_frames))

        # Performing some fractal wizardry.
        c = separation * np.exp(1j * a)
        Z = np.tile(x, (n, 1)) + 1j * np.tile(y, (1, m))
        C = np.full((n, m), c)
        M = np.full((n, m), True, dtype=bool)
        N = np.zeros((n, m))

        for i in range(iterations):
            Z[M] = Z[M] * Z[M] + C[M]
            M[np.abs(Z) > 2] = False
            N[M] = i

        # Update the image placeholder by calling the image() function on it.
        image.image(1.0 - (N / N.max()), use_column_width=True)

    # We clear elements by calling empty on them.
    progress_bar.empty()
    frame_text.empty()

    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
    st.button("Re-run")

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_animation))

def demo_plotting():

    st.title("Plotting  Demo")
    st.markdown('''
    This demo illustrates a combination of plotting and animation with Streamlit. We're generating a bunch of random numbers in a loop for around 5 seconds. Enjoy!    
    ''', unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status_text = st.empty()
    last_rows = np.random.randn(1, 1)
    chart = st.line_chart(last_rows)

    for i in range(1, 101):
        new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
        status_text.text("%i%% Complete" % i)
        chart.add_rows(new_rows)
        progress_bar.progress(i)
        last_rows = new_rows
        time.sleep(0.05)

    progress_bar.empty()

    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
    st.button("Re-run")

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_plotting))    
 
def demo_mapping():

    st.title("Mapping Demo")
    st.markdown('''
    This demo shows how to use [st.pydeck_chart](https://docs.streamlit.io/library/api-reference/charts/st.pydeck_chart) to display geospatial data.
    ''', unsafe_allow_html=True)

    try:
        ALL_LAYERS = {
            "Bike Rentals": pdk.Layer(
                "HexagonLayer",
                data=from_data_file("bike_rental_stats.json"),
                get_position=["lon", "lat"],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                extruded=True,
            ),
            "Bart Stop Exits": pdk.Layer(
                "ScatterplotLayer",
                data=from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius="[exits]",
                radius_scale=0.05,
            ),
            "Bart Stop Names": pdk.Layer(
                "TextLayer",
                data=from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_text="name",
                get_color=[0, 0, 0, 200],
                get_size=15,
                get_alignment_baseline="'bottom'",
            ),
            "Outbound Flow": pdk.Layer(
                "ArcLayer",
                data=from_data_file("bart_path_stats.json"),
                get_source_position=["lon", "lat"],
                get_target_position=["lon2", "lat2"],
                get_source_color=[200, 30, 0, 160],
                get_target_color=[200, 30, 0, 160],
                auto_highlight=True,
                width_scale=0.0001,
                get_width="outbound",
                width_min_pixels=3,
                width_max_pixels=30,
            ),
        }
        st.markdown('### Map Layers')
        selected_layers = [
            layer for layer_name, layer in ALL_LAYERS.items()
            if st.checkbox(layer_name, True)]
        if selected_layers:
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state={"latitude": 37.76,
                                    "longitude": -122.4, "zoom": 11, "pitch": 50},
                layers=selected_layers,
            ))
        else:
            st.error("Please choose at least one layer above.")
    except URLError as e:
        st.error("""
            **This demo requires internet access.**

            Connection error: %s
        """ % e.reason)

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_mapping)) 

def demo_dataframe():

    st.title("DataFrame Demo")
    st.markdown("""
This demo shows how to use st.write to visualize Pandas DataFrames.
(Data courtesy of the [UN Data Explorer](http://data.un.org/Explorer.aspx).)
    """, unsafe_allow_html=True)

    try:
        df = get_UN_data()
        countries = st.multiselect(
            "Choose countries", list(df.index), ["China", "United States of America"]
        )
        if not countries:
            st.error("Please select at least one country.")
        else:
            data = df.loc[countries]
            data /= 1000000.0
            st.write("### Gross Agricultural Production ($B)", data.sort_index())

            data = data.T.reset_index()
            data = pd.melt(data, id_vars=["index"]).rename(
                columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
            )
            chart = (
                alt.Chart(data)
                .mark_area(opacity=0.3)
                .encode(
                    x="year:T",
                    y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                    color="Region:N",
                )
            )
            st.altair_chart(chart, use_container_width=True)
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**

            Connection error: %s
        """
            % e.reason
        )

    if st.checkbox('Show code ...'):
        st.code(inspect.getsource(demo_dataframe))         

def main():
    demo_sidebar()
    demo_body()

# Run main()
if __name__ == '__main__':
    main()