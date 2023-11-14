import streamlit as st
from pathlib import Path

import shutil
# Create a title
st.title("Image Browser")

if "selected_imgs" not in st.session_state:
    st.session_state["selected_imgs"] = {}

# Get a list of images from the folder
def glob_img_files(folder=".", types=["jpg", "png", "jpeg"]):
    files = []
    for f in Path(folder).glob("*"):
        for _type in types:
            if f.name.lower().endswith(_type):
                files.append(f"{folder}\\\\{f.name}")
    return files
    
def add_img(file_img):
    selected_imgs = st.session_state["selected_imgs"]
    selected_imgs[file_img] = 1
    st.session_state["selected_imgs"] = selected_imgs

def remove_img(file_img):
    selected_imgs = st.session_state["selected_imgs"]
    if file_img in selected_imgs:
        selected_imgs.pop(file_img)
    st.session_state["selected_imgs"] = selected_imgs


c1,_, c2 = st.columns(3)
with c2:
    dest_folder=st.text_input("Image target folder:", value="c:\\tmp\\images")
with c1:
    source_folder = st.text_input("Image source folder:", value=".\Samsung-20210911")
if not Path(dest_folder).exists():
    Path(dest_folder).mkdir(parents=True,exist_ok=True)

image_list = list(st.session_state["selected_imgs"].keys())
if image_list:
    c_list, c_copy = st.columns([4,2])
    with c_list:
        st.write(image_list)
    with c_copy:
        if st.button("Copy selected images from source to target folder"):
            for img in image_list:
                # Get the source and destination paths
                source_path = Path(img)
                destination_path = Path(dest_folder) / source_path.name

                # Copy the file
                shutil.copy(source_path, destination_path)

#########################
data = glob_img_files(folder=source_folder)
num_imgs = len(data)



c1, c2, c3, c4, _, c5 = st.columns([2,2,2,2,1,2])
# Create an input field for page size
with c5:
    page_size = st.number_input('Page Size', min_value=1, value=4, step=2)

# Create a session state to store the current page number
if "page" not in st.session_state:
    st.session_state['page'] = 0

# Get the current page number
page_number = st.session_state['page']
at_begin = (page_number<=0)
at_end = (page_number + 1 >= len(data) // page_size + 1)

# Create buttons for navigating to previous, next, first, and last pages
with c1:
    if st.button('First <<', disabled=at_begin):
        st.session_state['page'] = 0
with c2:
    if st.button('Prev <', disabled=at_begin):
        st.session_state['page'] -= 1
with c3:
    if st.button('Next >', disabled=at_end):
        st.session_state['page'] += 1
with c4:
    if st.button('Last >>', disabled=at_end):
        st.session_state['page'] = len(data) // page_size


# Calculate the starting and ending indices for the current page
start_index = page_number * page_size
end_index = start_index + page_size

# Get the data for the current page
page_data = data[start_index:end_index]

for image in page_data:
    hash_val = hash(image)
    c_label, c_add, c_remove = st.columns([3, 1,1])
    with c_add:
        if st.button("Add", key=f"ADD{hash_val}"):
            add_img(image)
    with c_remove:
        if st.button("Remove", key=f"REMOVE{hash_val}"):
            remove_img(image)
        
    with c_label:
        st.write(f"Filename: '{image}'")
        
    st.image(image)
