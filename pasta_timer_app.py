# pasta_timer_app.py
# Streamlit app: digital timer with static GIFs for other styles
# To run: streamlit run pasta_timer_app.py

import streamlit as st
import time
import math
import matplotlib.pyplot as plt
from io import BytesIO
import os
import numpy as np
try:
    import imageio
except ImportError:
    imageio = None

# --- Page config ---
st.set_page_config(page_title="Pasta Timer", page_icon="🍝", layout="wide")
st.title("🍝 Pasta Timer")

# --- Load default "done" assets ---
ASSETS_DIR = "assets"
DONE_IMG = os.path.join(ASSETS_DIR, "done.png")
DONE_SND = os.path.join(ASSETS_DIR, "done.mp3")
img_done = None; snd_done = None
if os.path.exists(DONE_IMG):
    with open(DONE_IMG, 'rb') as f: img_done = f.read()
if os.path.exists(DONE_SND):
    with open(DONE_SND, 'rb') as f: snd_done = f.read()

# --- GIF URLs (static animations) ---
GIF_URLS = {
    'Hourglass':    'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWFtcWlkcTlseDAxYnZybXg5NXJ5MXlremU2dXNpNmE1ZGJmbTY3ciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3QmY3Q9Zw/gLjD6hjRaLcFslzpvR/giphy.gif',
    'Running Man':  'https://media.giphy.com/media/l41lI4bYmcsPJX9Go/giphy.gif',
    'Cuckoo Clock': 'https://media.giphy.com/media/26uf6oM3B8YXxZ7GM/giphy.gif',
}

# --- Fallback draw function for Analog ---
def draw_analog(rem, total):
    frac = rem/total
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    circle = plt.Circle((0.5,0.5),0.4, fill=False, linewidth=2)
    ax.add_artist(circle)
    angle = 2*math.pi*frac - math.pi/2
    x = 0.5 + 0.35*math.cos(angle)
    y = 0.5 + 0.35*math.sin(angle)
    ax.plot([0.5,x],[0.5,y], color='black', linewidth=2)
    ax.set_aspect('equal')
    buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig); buf.seek(0)
    return buf

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
dt_txt  = col1.empty(); dt_prog  = col1.empty()
and_img = col2.empty()
hg_img  = col3.empty()
rn_img  = col4.empty()
ck_img  = col5.empty()

# --- Display static GIFs or initial fallback before loop ---
# Analog fallback uses draw at full time
and_img.image(draw_analog(total, total))
hg_img.image(GIF_URLS['Hourglass'])
rn_img.image(GIF_URLS['Running Man'])
ck_img.image(GIF_URLS['Cuckoo Clock'])

# --- Run digital timer only ---
if st.button("Start Timer"):
    for i in range(total+1):
        rem = total - i
        mins, secs = divmod(rem, 60)
        ts = f"{mins:02d}:{secs:02d}"
        # Digital updates
        dt_txt.markdown(f"**Digital**\n{ts}")
        dt_prog.progress(i / total)
        time.sleep(1)
    # Done
    st.markdown("### ⏰ Done! Enjoy your pasta! 🍝")
    if snd_done: st.audio(snd_done)
    if img_done: st.image(img_done)
    else: st.balloons()
