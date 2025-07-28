# pasta_timer_app.py
# Streamlit app: digital timer with static GIFs for other styles (Goat, Hourglass, Running Man, Penguin)
# To run: streamlit run pasta_timer_app.py

import streamlit as st
import time
import os

# --- Page config ---
st.set_page_config(page_title="Pasta Timer", page_icon="🍝", layout="wide")
st.title("🍝 Pasta Timer")

# --- Load default "done" assets ---
ASSETS_DIR = "assets"
DONE_IMG = os.path.join(ASSETS_DIR, "gnome.png")
DONE_SND = os.path.join(ASSETS_DIR, "done.wav")
img_done = None
snd_done = None
if os.path.exists(DONE_IMG):
    with open(DONE_IMG, "rb") as f:
        img_done = f.read()
if os.path.exists(DONE_SND):
    with open(DONE_SND, "rb") as f:
        snd_done = f.read()

# --- GIF URLs (static animations) ---
GIF_URLS = {
    'Hourglass':    'https://media.giphy.com/media/QdVmkR04rz7vbT3cx9/giphy.gif',
    'Penguin':      'https://media.giphy.com/media/xvc8R0LCww4Ar4EWH9/giphy.gif',
    'Goat':         'https://media.giphy.com/media/Lqmp9tVPIvtyyKQneQ/giphy.gif',
    'Running Man':  'https://media.giphy.com/media/c43fAlwzxxOVch2OTK/giphy.gif',
}

# --- Pasta selection ---
pasta_times = {
    "Spaghetti": 8*60,
    "Penne":    11*60,
    "Fusilli":  10*60,
    "Ravioli":   5*60,
    "Custom":   None
}
sel = st.selectbox("Pick your pasta:", list(pasta_times.keys()))
if sel == "Custom":
    minutes = st.number_input("Cook time (minutes):", 1, 60, 10)
    total = int(minutes * 60)
else:
    total = pasta_times[sel]
    st.write(f"{sel} cooks for {total//60} minutes.")

# --- Prepare placeholders in columns ---
col1, col2, col3, col4, col5 = st.columns(5)
dt_txt   = col1.empty()
dt_prog  = col1.empty()
goat_img = col2.empty()
hg_img   = col3.empty()
rm_img   = col4.empty()
pn_img   = col5.empty()

# --- Display static GIFs before loop ---
goat_img.image(GIF_URLS['Goat'])
hg_img.image(GIF_URLS['Hourglass'])
rm_img.image(GIF_URLS['Running Man'])
pn_img.image(GIF_URLS['Penguin'])

# --- Run digital timer only ---
if st.button("Start Timer"):
    for i in range(total+1):
        rem = total - i
        mins, secs = divmod(rem, 60)
        ts = f"{mins:02d}:{secs:02d}"
        dt_txt.markdown(ts)
        dt_prog.progress(i / total)
        time.sleep(1)
    st.markdown("### ⏰ Done! Enjoy your pasta! 🍝")
    if snd_done:
        st.audio(snd_done)
    if img_done:
        st.image(img_done)
    else:
        st.balloons()
