"""
Streamlit Concept and Hello Demo based on 
    - https://docs.streamlit.io/library/get-started/main-concepts
    - streamlit hello

Source code: 
    https://github.com/wgong/streamlitapp/blob/main/demos/demo_concept.py

Deployed at:
    https://share.streamlit.io/wgong/streamlitapp/main/demos/demo_concept.py

"""

import streamlit as st

import os
import time
from pathlib import Path
from io import StringIO 
import base64
import urllib
import inspect
from urllib.error import URLError

import pandas as pd
import numpy as np
import altair as alt
# import matplotlib.pyplot as plt
# import plotly.figure_factory as ff
# from bokeh.plotting import figure
import pydeck as pdk

from streamlit.components.v1 import html
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

# Initial page config
st.set_page_config(
     page_title='Streamlit Concept Demo',
     layout="wide",
     initial_sidebar_state="expanded",
)

# app-data
data_st_tutorials = {
    "shail_deliwala" : {
        "title" : "Streamlit 101",
        "blog"  : {
            "url" : "https://towardsdatascience.com/streamlit-101-an-in-depth-introduction-fc8aad9492f2",
            "desc" : "Streamlit 101: An in-depth introduction - Airbnb NYC data"
        }
    },
    "marc_madsen" : {
        "title" : "Awesome-streamlit resources and gallery by Marc",
        "app" : {
            "url" : "https://awesome-streamlit.azurewebsites.net/",
            "desc" : "Awesome-streamlit"
        },
        "src" : {
            "url" : "https://github.com/MarcSkovMadsen/awesome-streamlit",
            "desc" :"github/MarcSkovMadsen/awesome-streamlit"
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
            "url" : "https://github.com/Jcharis/Streamlit_DataScience_Apps",
            "desc" :"github/JCharis/Streamlit_DataScience_Apps"
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
    },
    "1littlecoder" : {
        "title" : "Streamlit Tutorials by 1littlecoder",
        "vid" : {
            "url" : "https://www.youtube.com/watch?v=Iv2vt-7AYNQ&list=PLpdmBGJ6ELUI6Tws8BqVVNadsYOQlWGtw",
            "desc" : "Streamlit Tutorials by 1littlecoder"
        },
        "src" : {
            "url" : "https://github.com/amrrs/youtube-r-snippets/blob/master/streamlit_code_editor.py",
            "desc" :"github/amrrs/youtube-r-snippets"
        }
    },
}

##########################
###  define helper functions with prefix "_"
##########################

# cache functions for performance
@st.experimental_memo(ttl=3600)
def _read_code_from_url(url):
    return [line.decode("utf-8") for line in urllib.request.urlopen(url)]

@st.cache
def _convert_df2csv(df, index=True):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=index).encode('utf-8')

@st.cache
def _get_UN_data():
    AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")

@st.cache
def _df_from_data_file(filename):
    url = (
        "http://raw.githubusercontent.com/streamlit/"
        "example-data/master/hello/v1/%s" % filename)
    return pd.read_json(url)

@st.cache # 👈 below function will be cached
def _img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

@st.cache # 👈 below function will be cached
def _fibonacci(n):
    # Function for nth fibonacci number

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
        return _fibonacci(n-1) + _fibonacci(n-2)

def _set_bg_img_url(url=None):
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.

    How to use:
        >>> img_url = "https://images.unsplash.com/photo-1444044205806-38f3ed106c10?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"
        >>> _set_bg_img_url(url=img_url)
        
    Soruce - https://discuss.streamlit.io/t/how-do-i-use-a-background-image-on-streamlit/5067/19?u=wgong27514
    '''
    if url:
        st.markdown(f"""
            <style>
            .stApp {{
                background: url({url});
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        
def _set_bg_img():
    menu_item = st.session_state.menu_item
    if menu_item in menu_dict["concepts"].keys() and "img" in menu_dict["concepts"][menu_item]:
        img_url = menu_dict["concepts"][menu_item]["img"]
        _set_bg_img_url(url=img_url)


##########################
###  define event handlers with prefix "do_"
##########################


def do_data():

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
    st.json({'foo':'bar','ya':'hoo'})

    st.subheader('st.metric')
    st.metric(label="T", value="273 K", delta="1.2 K")

    st.subheader('st.latex')
    st.write("Beautiful equations: ")
    st.latex(r''' e^{i\pi} + 1 = 0 ''')
    st.latex(r""" F = ma """)
    st.latex(r""" E = mc^2 """)
    st.latex(r""" E = h\nu """)
    st.latex(r"""
    i\hbar \frac{{\partial \psi (x,t)}}{{\partial t}} = - \frac{{\hbar ^2 }}{{2m}}\frac{{\partial ^2 \psi (x,t)}}{{\partial x^2 }} + U(x)\psi (x,t) 
    """)

    st.markdown("""
    More equations can be found at [http://www.equationsheet.com/](http://www.equationsheet.com/)
    """)


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
    st.subheader('st.line_chart')
    st.line_chart(chart_data)

    st.subheader('st.download_button')
    st.download_button(
        label="Download dataframe as CSV",
        data=_convert_df2csv(chart_data, index=False),
        file_name='df.csv',
        mime='text/csv',
    )

    st.subheader('st.uploaded_file')
    csv_file = st.file_uploader("Choose a csv file", key="upload_csv")
    if csv_file is not None:
        df_csv = pd.read_csv(csv_file)
        st.write("Your uploaded CSV file:")
        st.dataframe(df_csv)

    txt_file = st.file_uploader("Choose a text file", key="upload_txt")
    if txt_file is not None:
        # To convert to a string based IO:
        stringio = StringIO(txt_file.getvalue().decode("utf-8"))
        # st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write("Your uploaded text file:")
        st.write(string_data)

    img_file = st.file_uploader("Choose an image file", key="upload_img")
    if img_file is not None:
        img_bytes = img_file.getvalue()
        st.write("Your uploaded image file:")
        st.image(img_bytes)

    with st.expander("Show code"):
        st.code(inspect.getsource(do_data))



def do_code(url="https://raw.githubusercontent.com/wgong/streamlitapp/main/demos/demo_concept.py"):
    with st.expander("Show code"):
        st.code(inspect.getsource(do_code))

    filename = url.split("/")[-1]
    st.markdown(f"""
    ### How to display github source code
    [{filename}]({url})
    """,unsafe_allow_html=True)
    st.code("".join(_read_code_from_url(url)))



def do_chart():
    with st.echo():
        df = pd.DataFrame(
            [[np.sin(i), np.cos(i), 1.5*np.sin(3*i)] 
                for i in np.arange(0,4*np.pi,0.1)],
            columns=['sin(x)', 'cos(x)', '1.5sin(3x)'])


    st.subheader('st.line_chart')
    st.line_chart(df)    

    st.subheader('st.area_chart')
    st.area_chart(df)    

    with st.echo():
        df2 = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['a', 'b', 'c'])    

    st.subheader('st.bar_chart')  # not easy for unstack bar
    st.bar_chart(df2)   

    if False:  # disable - error in streamlit cloud
        st.subheader('st.pyplot') 
        arr = np.random.normal(1, 1, size=100)
        fig, ax = plt.subplots()
        ax.hist(arr, bins=20)
        st.pyplot(fig)

    st.subheader('st.altair_chart') 
    c = alt.Chart(df2).mark_circle().encode(
        x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
    st.altair_chart(c, use_container_width=True)

    if False:  # disable - error in streamlit cloud
        st.subheader('st.plotly_chart') 
        # Add histogram data
        x1 = np.random.randn(200) - 2
        x2 = np.random.randn(200)
        x3 = np.random.randn(200) + 2

        # Group data together
        hist_data = [x1, x2, x3]

        group_labels = ['Group 1', 'Group 2', 'Group 3']

        # Create distplot with custom bin_size
        fig = ff.create_distplot(
                hist_data, group_labels, bin_size=[.1, .25, .5])

        st.plotly_chart(fig, use_container_width=True)

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

    if False:  # disable - error in streamlit cloud
        st.subheader('st.bokeh_chart') 
        x = [1, 2, 3, 4, 5]
        y = [i*i for i in x]

        p = figure(
            title='simple line example',
            x_axis_label='x',
            y_axis_label='y')

        p.line(x, y, legend_label='Squared', line_width=2)
        st.bokeh_chart(p, use_container_width=True)

    with st.expander("Show code"):
        st.code(inspect.getsource(do_chart))

def do_media():
    st.title('Media ')

    st.header('Image ')
    st.subheader("glipse of [Huangshan](https://www.google.com/search?rlz=1C1CHBF_enUS949US953&sxsrf=AOaemvKjSzJqu-a89inA5ddCLPwN6yTS5A:1642809970191&source=univ&tbm=isch&q=huangshan+image&fir=c5JbjbKRqMYzSM%252CprEGJfbX4gK1QM%252C_%253BKDGXUGwkG9HJlM%252CprEGJfbX4gK1QM%252C_%253BsAJIYULVc8LIdM%252CjlUYtsu-BMNYnM%252C_%253BT3diVkmbJwRCvM%252CuULWDkXX6y_AtM%252C_%253BNM8dklixiMn4JM%252CY4uyDKPk0t-hvM%252C_%253Bzif9QvqQ0usaHM%252Cr3dKhkFPF8GyfM%252C_%253Bh9TJ9g_37Sit_M%252C7PkIwO15CHEAMM%252C_%253BIesJFYFRE_C7XM%252CezzzG1WCERTNsM%252C_%253BU4XoFhMNdyHevM%252CprEGJfbX4gK1QM%252C_%253BTQOabpFHQuMFyM%252ClNJBXwZLn85NCM%252C_%253BWu0q9fYRBcmCwM%252CmkDBcTJMjszmsM%252C_%253BF0lwAmH5NowxPM%252CTzSKpaqZ1Dq6MM%252C_%253BWykWSfyVqd4ZKM%252C-vYDZcuHEz0gKM%252C_&usg=AI4_-kRSL2DKzRpR64M2F5njm_m_qp3LGg&sa=X&ved=2ahUKEwi6_dKFiMT1AhWhlGoFHdYZBLEQ7Al6BAgGEDw&biw=1389&bih=826&dpr=1)")
    st.image("https://images.chinahighlights.com/allpicture/2019/12/b50add17df9d489a967108d5_cut_800x500_66.jpg",
        caption="The Yellow Mountain in Anhui, China")


    st.header('Video ')
    st.video("https://www.youtube.com/watch?v=rOjHhS5MtvA")
    st.video("https://www.youtube.com/watch?v=q2KBWmiL71o")
    st.video("https://www.youtube.com/watch?v=_T8LGqJtuGc")
    st.subheader("Smart Squirrels")
    st.video("https://www.youtube.com/watch?v=hFZFjoX2cGg")
    st.video("https://www.youtube.com/watch?v=DTvS9lvRxZ8")

    st.header('Audio ')
    st.subheader("classical music from [http://www.lisztonian.com/](http://www.lisztonian.com/titles/index.php?s=title)")
    st.write("Bagatelle in A Minor - WoO 59 (Fur Elise or For Elise) - Ludwig Van Beethoven")
    st.audio("http://download.lisztonian.com/music/download/Bagatelle+in+A+Minor++WoO+59-81.mp3")

    st.subheader("clips from [SoundHelix](https://www.soundhelix.com/audio-examples)")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

    st.subheader("Internet radio")
    st.markdown("""
    - [AccuRadio](https://www.accuradio.com/) is a good source, but don't know how to get the URL
    for st.audio() call. 
    """)

    st.markdown("""
    - [mutiny-studio](http://nthmost.net:8000/mutiny-studio)
    """)
    st.audio("http://nthmost.net:8000/mutiny-studio")
    st.markdown("""
    - [440hz-radio](https://stream.440hz-radio.de/440hz-main.mp3?start=1597517799)
    """)
    st.audio("https://stream.440hz-radio.de/440hz-main.mp3?start=1597517799")

    with st.expander("Show code"):
        st.code(inspect.getsource(do_media))



def do_widget():

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

    st.subheader('st.text_area ')
    st.text_area("Your name", key="text")
    # You can access the value at any point with:
    st.write(f"You entered: {st.session_state.text}")

    col_date, col_time = st.columns(2)
    with col_date:
        st.subheader('st.date_input ')
        birthday = st.date_input('Your birthday')
        st.write(f"Birthday = {birthday}")

    with col_time:
        st.subheader('st.time_input ')
        meet_time = st.time_input('Meeting time')
        st.write(f"Meet at {meet_time}")

    st.subheader('st.color_picker ')
    fav_color = st.color_picker('Favorite color')
    st.write(f"Favorite color = {fav_color}")

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
    if st.checkbox('Show dataframe', key="show_df"):
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['a', 'b', 'c'])
        chart_data

    st.subheader('st.progress')
    'Starting a long computation...'
    # Add a placeholder
    latest_iteration = st.empty()
    bar = st.progress(0)
    for i in range(10):
        # Update the progress bar with each iteration.
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
        time.sleep(0.1)
    '...and now we\'re done!'

    st.subheader('st.form, st.expander')

    col1,col2 = st.columns(2)

    with col1:
        with st.form(key='login_form'):
            username = st.text_input('Username')
            password = st.text_input('Password', type="password")
            click_login = st.form_submit_button('Login')
    with col2:
        if click_login:
            st.text("Form data: ")
            st.json({'Username':username, 'Password': password})


    st.markdown("""
    Another example: [SQL Playground by JCharis](https://github.com/Jcharis/Streamlit_DataScience_Apps/tree/master/sqlplayground_app)
    """, unsafe_allow_html=True)



    with st.expander("Show code"):
        st.code(inspect.getsource(do_widget))


def do_layout():
    _set_bg_img()

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

    with st.expander("Show code"):
        st.code(inspect.getsource(do_layout))


def do_theme():
    _set_bg_img()

    ## Theme
    st.header('Theme')
    with st.expander("Show code"):
        st.code(inspect.getsource(do_theme))



def do_cache():
    _set_bg_img()

    ## Caching
    st.header('Caching')
    max_num = st.number_input("Set max number of the slider", value=100)
    if max_num:
        if int(max_num) > 300:
            st.warning(f"Your number {int(max_num)} is too big, let us keep it to 300")
            MAX_NUM = 300
        else:
            MAX_NUM = int(max_num)
        num = st.slider("num", 1, MAX_NUM, 5)
        ts_start = time.time()
        with st.spinner("Calculating ..."):
            fib_num = _fibonacci(num)
        st.balloons()

        ts_duration = time.time() - ts_start
        st.write(f"Fib({num}) = {fib_num} \n calculated in {ts_duration:.3f} sec")
        st.button("Re-Run")

    st.markdown("""##### Note:
    - calculating Fib of the same number takes much smaller constant time
    - sub-function within recursive calls are also cached
    """)

    with st.expander("Show code"):
        st.code(inspect.getsource(do_cache))

def do_learn():

    st.header("Learn Streamlit")

    for k in data_st_tutorials.keys():
        st.subheader(data_st_tutorials[k]["title"])
        st_data = data_st_tutorials[k]
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
        if "app" in st_data:
            # display app
            st.markdown(f"""
            - [{st_data["app"]["desc"]}]({st_data["app"]["url"]})
            """)
    
    with st.expander("Show code"):
        st.code(inspect.getsource(do_learn))

def _lbs2kgs():
    st.session_state.kgs = st.session_state.lbs / 2.2046

def _kgs2lbs():
    st.session_state.lbs  = st.session_state.kgs * 2.2046

def do_misc():
    _set_bg_img()

    st.header('Misc')

    st.subheader("set background image")
    with st.expander("Show code"):
        st.code(inspect.getsource(_set_bg_img_url))    

    
    st.subheader("st.session_state")
    st.write("Below is a lb / kg convertor:")
    col1, buff, col2 = st.columns([2,1,2])
    with col1:
        pounds = st.number_input("Pounds:", key="lbs",
            on_change=_lbs2kgs)

    with col2:
        kgs = st.number_input("Kgs:", key="kgs",
            on_change=_kgs2lbs)

    st.write("st.session_state is a global dictionary storing widget state")
    st.write("watch a YouTube video to learn more:")
    st.video("https://youtu.be/92jUAXBmZyU")

    st.subheader("st.echo")
    with st.echo():
        st.write('This code will be printed')

        a = 10
        b = 20
        print(f"{a} + {b} = {a+b}")

    st.subheader("st.help")
    st.write("st.help(pd.DataFrame)")
    st.help(pd.DataFrame)


    st.write(f"os.getcwd() = {os.getcwd()}" )

    with st.expander("Show code"):
        st.code(inspect.getsource(do_misc))


def do_animation():

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

    with st.expander("Show code"):
        st.code(inspect.getsource(do_animation))

def do_plotting():

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

    with st.expander("Show code"):
        st.code(inspect.getsource(do_plotting))    
 
def do_mapping():

    st.title("Mapping Demo")
    st.markdown('''
    This demo shows how to use [st.pydeck_chart](https://docs.streamlit.io/library/api-reference/charts/st.pydeck_chart) to display geospatial data.
    ''', unsafe_allow_html=True)

    try:
        ALL_LAYERS = {
            "Bike Rentals": pdk.Layer(
                "HexagonLayer",
                data=_df_from_data_file("bike_rental_stats.json"),
                get_position=["lon", "lat"],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                extruded=True,
            ),
            "Bart Stop Exits": pdk.Layer(
                "ScatterplotLayer",
                data=_df_from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius="[exits]",
                radius_scale=0.05,
            ),
            "Bart Stop Names": pdk.Layer(
                "TextLayer",
                data=_df_from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_text="name",
                get_color=[0, 0, 0, 200],
                get_size=15,
                get_alignment_baseline="'bottom'",
            ),
            "Outbound Flow": pdk.Layer(
                "ArcLayer",
                data=_df_from_data_file("bart_path_stats.json"),
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

    with st.expander("Show code"):
        st.code(inspect.getsource(do_mapping)) 

def do_dataframe():

    st.title("DataFrame Demo")
    st.markdown("""
    This demo shows how to use st.write to visualize Pandas DataFrames.
    (Data courtesy of the [UN Data Explorer](http://data.un.org/Explorer.aspx).)
    """, unsafe_allow_html=True)

    try:
        df = _get_UN_data()
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

    with st.expander("Show code"):
        st.code(inspect.getsource(do_dataframe))         

def do_nothing():
    pass




def do_tabs():
    """
    Thank you - https://discuss.streamlit.io/t/st-footer/6447/18
    """

    def _tabs(tabs_data = {}, default_tab=0):
            tab_titles = list(tabs_data.keys())
            if not tab_titles:
                return None
            active_tab = st.radio("", tab_titles, index=default_tab)
            tab_idx = tab_titles.index(active_tab)+1
            st.markdown("""  
                <style type="text/css">
                div[role=radiogroup] > label > div:first-of-type {
                display: none
                }
                div[role=radiogroup] {
                    flex-direction: unset
                }
                div[role=radiogroup] label {             
                    border: 1px solid #999;
                    background: #FFF;
                    padding: 6px 12px;
                    border-radius: 12px 12px 0 0;
                    position: relative;
                    top: 1px;
                    }
                div[role=radiogroup] label:nth-child(""" + str(tab_idx) + """) {    
                    background:  #CCFF00 !important;
                    border-bottom: 1px solid transparent;
                }            
                </style>
            """,unsafe_allow_html=True)        
            return tabs_data[active_tab]

    def _tab__show_video():
        st.title("Russia – Ukraine conflict / crisis Explained")
        st.video("https://www.youtube.com/watch?v=h2P9AmGcMdM")

    def _tab__fake_df():
        N = 50
        rand = pd.DataFrame()
        rand['a'] = np.arange(N)
        rand['b'] = np.random.rand(N)
        rand['c'] = np.random.rand(N)    
        return rand

    st.markdown("""
    ## Multi-page app using [hydralit](https://github.com/TangleSpace/hydralit)

    [example](https://share.streamlit.io/wgong/streamlitapp/main/demos/demo_hydralit.py)
    """, unsafe_allow_html=True)

    with st.expander("Show code"):
        st.code(inspect.getsource(do_tabs))

    st.markdown("""
    ## Another lightweight __Tab__ example 
     
    found at [Multiple tabs in streamlit](https://discuss.streamlit.io/t/multiple-tabs-in-streamlit/1100/19?u=wgong27514)
    """, unsafe_allow_html=True)

    tab_content = _tabs({
            "Tab html": "<h2> Hello Streamlit, <br/> what a cool tool! </h2>",
            "Tab video": _tab__show_video, 
            "Tab df": _tab__fake_df()
        })
    if tab_content is None:
        return

    if callable(tab_content):
        tab_content()
    elif isinstance(tab_content, str):
        st.markdown(tab_content, unsafe_allow_html=True)
    else:
        st.write(tab_content) 

    with st.expander("Show code"):
        st.code(inspect.getsource(do_tabs))






def do_footer():
    """
    Thank you - https://discuss.streamlit.io/t/st-footer/6447/18?u=wgong27514
    """

    def _image(src_as_string, **style):
        return img(src=src_as_string, style=styles(**style))


    def _link(link, text, **style):
        return a(_href=link, _target="_blank", style=styles(**style))(text)


    def _layout(*args):
        style = """
        <style>
        # MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp { bottom: 80px; }
        </style>
        """

        style_div = styles(
            position="fixed",
            left=0,
            bottom=0,
            margin=px(0, 0, 0, 0),
            width=percent(100),
            color="black",
            text_align="center",
            height="auto",
            opacity=1
        )

        # 分割线
        style_hr = styles(
            display="block",
            margin=px(0, 0, 0, 0),
            border_style="inset",
            border_width=px(2)
        )

        # 修改p标签内文字的style
        body = p(
            id='myFooter',
            style=styles(
                margin=px(0, 0, 0, 0),
                # 通过调整padding自行调整上下边距以达到满意效果
                padding=px(5),
                # 调整字体大小
                font_size="0.8rem",
                color="rgb(51,51,51)"
            )
        )
        foot = div(
            style=style_div
        )(
            hr(
                style=style_hr
            ),
            body
        )

        st.markdown(style, unsafe_allow_html=True)

        for arg in args:
            if isinstance(arg, str):
                body(arg)

            elif isinstance(arg, HtmlElement):
                body(arg)

        st.markdown(str(foot), unsafe_allow_html=True)

        # js获取背景色 由于st.markdown的html实际上存在于iframe, 所以js检索的时候需要window.parent跳出到父页面
        # 使用getComputedStyle获取所有stApp的所有样式，从中选择bgcolor
        js_code = '''
        <script>
        function rgbReverse(rgb){
            var r = rgb[0]*0.299;
            var g = rgb[1]*0.587;
            var b = rgb[2]*0.114;
            
            if ((r + g + b)/255 > 0.5){
                return "rgb(49, 51, 63)"
            }else{
                return "rgb(250, 250, 250)"
            }
            
        };
        var stApp_css = window.parent.document.querySelector("#root > div:nth-child(1) > div > div > div");
        window.onload = function () {
            var mutationObserver = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        /************************当DOM元素发送改变时执行的函数体***********************/
                        var bgColor = window.getComputedStyle(stApp_css).backgroundColor.replace("rgb(", "").replace(")", "").split(", ");
                        var fontColor = rgbReverse(bgColor);
                        var pTag = window.parent.document.getElementById("myFooter");
                        pTag.style.color = fontColor;
                        /*********************函数体结束*****************************/
                    });
                });
                
                /**Element**/
                mutationObserver.observe(stApp_css, {
                    attributes: true,
                    characterData: true,
                    childList: true,
                    subtree: true,
                    attributeOldValue: true,
                    characterDataOldValue: true
                });
        }
        

        </script>
        '''
        html(js_code)

    myargs = [
        "Made with ❤️ by ",
        _image('https://image.pngaaa.com/798/5084798-middle.png',
              width=px(50), height=px(25)),
        _link("http://streamlit.io", "Streamlit"),
    ]
    _layout(*myargs)

    st.markdown("This __Footer__ example was found at [st.footer](https://discuss.streamlit.io/t/st-footer/6447/18)")

    st.write("Do you see footer at the bottom? ")
    st.image("https://hotemoji.com/images/emoji/l/17zcrtb11cx2zl.png")

    with st.expander("Show code"):
        st.code(inspect.getsource(do_footer))

# menu_item to handler mapping
menu_dict = {
    "demos" : {
        "Animation": {"fn": do_animation, },
        "Dataframe":  {"fn": do_dataframe},
        "Mapping": {"fn": do_mapping, },
        "Plotting": {"fn": do_plotting},
        "Tab":  {"fn": do_tabs},
        "Footer":  {"fn": do_footer},
    },
    "concepts" : {
            "Data": {"fn": do_data, },
            "Code": {"fn": do_code, },
            "Cache": {"fn": do_cache, "img": "https://www.blueskyamusements.com/images/site/template/bkg-sky.jpg"},
            "Chart": {"fn": do_chart, },
            "Media": {"fn": do_media, },
            "Widget": {"fn": do_widget, },
            "Layout": {"fn": do_layout, "img": "https://i.pinimg.com/originals/62/54/49/6254491a98878eaa3a3c5dd6f38d3788.jpg"},
            "Theme": {"fn": do_theme, "img": "https://cdn.pixabay.com/photo/2020/06/19/22/33/wormhole-5319067_960_720.jpg"},
            "Learn":{"fn": do_learn},
            "Misc": {"fn": do_misc, "img": "https://images.unsplash.com/photo-1512273222628-4daea6e55abb?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"},
    }
}

# img_url = "https://images.unsplash.com/photo-1444044205806-38f3ed106c10?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"


# body
def do_body():
    menu_item = st.session_state.menu_item
    demo_item = st.session_state.demo_item

    if demo_item in menu_dict["demos"].keys():
        menu_dict["demos"][demo_item]["fn"]()
    else:
        if menu_item in menu_dict["concepts"].keys():
            menu_dict["concepts"][menu_item]["fn"]()

    # if st.sidebar.checkbox('Complete code'):
    #     with open(__file__) as f:
    #         st.sidebar.code(f.read())

    

## sidebar Menu
def do_sidebar():
    st.sidebar.markdown('''
    [<img src='https://streamlit.io/images/brand/streamlit-mark-color.svg' class='img-fluid' width=128 height=64>](https://streamlit.io/)
    ''', unsafe_allow_html=True)

    st.sidebar.markdown("""
    <span style="color:red">__Streamlit__ </span>: Why-What-How
    """, unsafe_allow_html=True)
    st.sidebar.video("https://www.youtube.com/watch?v=R2nr1uZ8ffc")

    st.sidebar.markdown("[__Concepts__](https://docs.streamlit.io/library/get-started/main-concepts)")
    menu_options = sorted(list(menu_dict["concepts"].keys()))
    default_ix = menu_options.index("Chart")
    menu_item = st.sidebar.selectbox("Explore:", menu_options, index=default_ix, key="menu_item")
    st.sidebar.markdown("""
    <small>Since Streamlit runs script from top to bottom, we use menu-item to split
    the whole script into sections, so only a selected section is rerun
    </small>""", unsafe_allow_html=True)

    # st.sidebar.markdown("__Demos__")
    demo_options = ["_____"] + list(menu_dict["demos"].keys())
    demo_ix = demo_options.index("_____")
    demo_item = st.sidebar.selectbox("Play demo: ", demo_options, index=demo_ix, key="demo_item")
    st.sidebar.markdown("""
    <small>Streamlit built-in demos (unpick to explore concept)
    </small>""", unsafe_allow_html=True)
    st.sidebar.code('$ streamlit hello')


    st.sidebar.write("""
    __Resources__
    - [Cheatsheet](https://docs.streamlit.io/library/cheatsheet)
    - [API Reference](https://docs.streamlit.io/library/api-reference)
    - [Components](https://docs.streamlit.io/library/components)
    - [Gallery](https://streamlit.io/gallery)
    - [Community](https://discuss.streamlit.io/)
    - [Awesome-streamlit](https://awesome-streamlit.azurewebsites.net/)
    """)


    if st.sidebar.checkbox('Code for sidebar', key="do_sidebar"):
        st.sidebar.code(inspect.getsource(do_sidebar))


def main():
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
