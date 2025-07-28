# pasta_timer_app.py
# Streamlit app for selecting pasta by image, timing it with various clock styles, and showing a custom photo + sound when done
# To run: streamlit run pasta_timer_app.py

import streamlit as st
import time

st.set_page_config(page_title="Pasta Timer", page_icon="🍝", layout="centered")
st.title("🍝 Pasta Timer")

# --- Upload custom "done" image and sound ---
done_image = st.file_uploader(
    "Upload an image to display when time's up", 
    type=["png", "jpg", "jpeg"], key="done_img"
)
done_sound = st.file_uploader(
    "Upload a sound to play when time's up", 
    type=["mp3", "wav", "ogg"], key="done_sound"
)

# --- Define pasta types with cook times and images ---
pasta_types = {
    "Spaghetti": {"time": 8 * 60, "img_path": "images/spaghetti.jpg"},
    "Penne": {"time": 11 * 60, "img_path": "images/penne.jpg"},
    "Fusilli": {"time": 10 * 60, "img_path": "images/fusilli.jpg"},
    "Ravioli": {"time": 5 * 60, "img_path": "images/ravioli.jpg"},
    "Custom": {"time": None, "img_path": None}
}

# --- Choose pasta ---
st.markdown("## Choose your pasta by clicking the image below:")
cols = st.columns(len(pasta_types))
selected_pasta = None
for idx, (name, opts) in enumerate(pasta_types.items()):
    with cols[idx]:
        if opts["img_path"]:
            st.image(opts["img_path"], caption=name, use_column_width=True)
        else:
            st.write(name)
        if st.button(name, key=f"select_{name}"):
            selected_pasta = name

# --- Once pasta is selected ---
if selected_pasta:
    if selected_pasta == "Custom":
        minutes = st.number_input(
            "Enter cooking time in minutes:", 
            min_value=1, max_value=60, value=10
        )
        total_seconds = int(minutes * 60)
        st.write(f"Custom time set: {minutes} minutes")
    else:
        total_seconds = pasta_types[selected_pasta]["time"]
        st.write(f"You chose {selected_pasta}. Cook time: {total_seconds//60} minutes.")
    if pasta_types[selected_pasta]["img_path"]:
        st.image(pasta_types[selected_pasta]["img_path"], width=200)

    # --- Clock style options ---
    clock_styles = [
        "Digital", "Hourglass", "Analog", 
        "Running Man", "Cuckoo Clock"
    ]
    style = st.selectbox(
        "Choose a timer style:", clock_styles
    )

    # placeholders
    image_placeholder = st.empty()
    time_placeholder = st.empty()
    progress = None
    if style == "Digital":
        progress = st.progress(0)

    # --- Start timer ---
    if st.button("Start Timer", key="start_timer"):
        # show animation once for non-digital
        if style != "Digital":
            img_path = f"clocks/{style.lower().replace(' ', '_')}.gif"
            image_placeholder.image(
                img_path, caption=f"{style} Timer",
                use_column_width=False, width=200
            )

        for elapsed in range(total_seconds + 1):
            remaining = total_seconds - elapsed
            mins, secs = divmod(remaining, 60)
            time_str = f"{mins:02d}:{secs:02d}"

            if style == "Digital":
                image_placeholder.markdown(f"### ⏱ Time remaining: **{time_str}**")
                progress.progress(elapsed / total_seconds)
            else:
                time_placeholder.markdown(f"**{time_str}**")

            time.sleep(1)

        # time's up
        time_placeholder.markdown("### ⏰ Time's up! Enjoy your pasta! 🍝")
        if done_sound:
            st.audio(done_sound.read(), format=None)
        if done_image:
            st.image(done_image, use_column_width=True)
        else:
            st.balloons()
