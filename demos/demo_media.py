import streamlit as st
from streamlit import config
from streamlit.session_data import get_url

from streamlit.elements.image import (
    _BytesIO_to_bytes,
    _normalize_to_bytes,
    MAXIMUM_CONTENT_WIDTH,
)
from streamlit.in_memory_file_manager import (
    _calculate_file_id,
    _get_extension_for_mimetype,
    STATIC_MEDIA_ENDPOINT,
)

def img_url(image):
    mimetype = image.type
    # st.write(f"mimetype: {mimetype}")
    data = _BytesIO_to_bytes(image)
    data, mimetype = _normalize_to_bytes(data, MAXIMUM_CONTENT_WIDTH, mimetype)
    extension = _get_extension_for_mimetype(mimetype)
    file_id = _calculate_file_id(data=data, mimetype=mimetype)
    URL = get_url(config.get_option("browser.serverAddress"))
    st.json({"URL": URL, "STATIC_MEDIA_ENDPOINT": STATIC_MEDIA_ENDPOINT, "file_id": file_id, "extension": extension})
    return "{}{}/{}{}".format(URL, STATIC_MEDIA_ENDPOINT, file_id, extension)

img = st.file_uploader("upload image", type=["jpg", "png", "md", "txt"])

if img:
    st.image(img)
    st.write(img_url(img))