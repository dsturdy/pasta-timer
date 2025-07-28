# pasta_timer_app.py
# Streamlit app for selecting a pasta by image, timing it, and showing a custom photo + sound when done
# To run: streamlit run pasta_timer_app.py

import streamlit as st
import time
from io import BytesIO

st.set_page_config(page_title="Pasta Timer", page_icon="🍝", layout="centered")
st.title("🍝 Pasta Timer")

# --- Upload custom "done" image and sound ---
done_image = st.file_uploader("Upload an image to display when time's up", type=["png", "jpg", "jpeg"], key="done_img")
done_sound = st.file_uploader("Upload a sound to play when time's up", type=["mp3", "wav", "ogg"], key="done_sound")

# --- Define pasta types with cook times and images ---
pasta_types = {
    "Spaghetti": {"time": 8 * 60, "img_path": "images/spaghetti.jpg"},
    "Penne": {"time": 11 * 60, "img_path": "images/penne.jpg"},
    "Fusilli": {"time": 10 * 60, "img_path": "images/fusilli.jpg"},
    "Ravioli": {"time": 5 * 60, "img_path": "images/ravioli.jpg"},
    "Custom": {"time": None, "img_path": None}
}

st.markdown("## Choose your pasta by clicking the image below:")
cols = st.columns(len(pasta_types))
selected = None

for idx, (name, opts) in enumerate(pasta_types.items()):
    with cols[idx]:
        if opts["img_path"]:
            st.image(opts["img_path"], caption=name, use_column_width=True)
        else:
            st.write("Custom")
        if st.button(name, key=f"select_{name}"):
            selected = name

# --- Handle selection ---
if selected:
    if selected == "Custom":
        minutes = st.number_input("Enter cooking time in minutes:", min_value=1, max_value=60, value=10)
        total_seconds = int(minutes * 60)
        st.write(f"Custom time set: {minutes} minutes")
    else:
        total_seconds = pasta_types[selected]["time"]
        st.write(f"You chose {selected}. Cook time: {total_seconds//60} minutes.")
    st.image(pasta_types[selected]["img_path"], use_column_width=False, width=200)
    if st.button("Start Timer", key="start_timer"):
        placeholder = st.empty()
        progress = st.progress(0)
        for elapsed in range(total_seconds + 1):
            remaining = total_seconds - elapsed
            mins, secs = divmod(remaining, 60)
            placeholder.markdown(f"### Time remaining: **{mins:02d}:{secs:02d}**")
            progress.progress(elapsed / total_seconds)
            time.sleep(1)
        placeholder.markdown("### ⏰ Time's up! Enjoy your pasta! 🍝")
        # play sound if provided
        if done_sound:
            sound_bytes = done_sound.read()
            st.audio(sound_bytes, format=None)
        # show image if provided
        if done_image:
            st.image(done_image, use_column_width=True)
        else:
            st.balloons()
