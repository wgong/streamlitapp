import streamlit as st
from pytube import YouTube, Playlist

itag_mp4_video_720p = 22

with st.form(key='downloader_form'):
    URL = st.text_input("URL", value="https://www.youtube.com/watch?v=92jUAXBmZyU&t=15", key="url")
    yt = YouTube(URL)
    SAVE_PATH = st.text_input("Save path", value="C:/Users/w_gon/Videos", key="save_path")
    if st.form_submit_button("Download video"):
        st.write(yt.streams.get_by_itag(itag_mp4_video_720p).download(output_path=SAVE_PATH))
# dic = {
#     "title" : yt.title, 
#     "thumbnail_url" : yt.thumbnail_url
# }
# st.write(dic)



# st.video(URL)