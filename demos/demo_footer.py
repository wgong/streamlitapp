"""
Thank you - https://discuss.streamlit.io/t/st-footer/6447/18?u=wgong27514
"""

import streamlit as st
from streamlit.components.v1 import html
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb


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


def do_footer():

    myargs = [
        "Made with ❤️ by ",
        _image('https://image.pngaaa.com/798/5084798-middle.png',
              width=px(50), height=px(25)),
        _link("http://streamlit.io", "Streamlit"),
    ]
    _layout(*myargs)


if __name__ == "__main__":
    do_footer()
