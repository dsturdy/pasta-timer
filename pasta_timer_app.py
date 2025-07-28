# pasta_timer_app.py
# Streamlit app: synchronized timers with optional GIF animations aligned to countdown
# To run: streamlit run pasta_timer_app.py

import streamlit as st
import time
import math
import matplotlib.pyplot as plt
from io import BytesIO
import os
import numpy as np
import imageio

# --- Page config ---
st.set_page_config(page_title="Pasta Timer", page_icon="🍝", layout="wide")
st.title("🍝 Pasta Timer")

# --- Load default "done" assets ---
ASSETS_DIR = "assets"
DONE_IMG_PATH = os.path.join(ASSETS_DIR, "done.png")
DONE_SOUND_PATH = os.path.join(ASSETS_DIR, "done.mp3")

done_img = None
if os.path.exists(DONE_IMG_PATH):
    with open(DONE_IMG_PATH, "rb") as f:
        done_img = f.read()

done_sound = None
if os.path.exists(DONE_SOUND_PATH):
    with open(DONE_SOUND_PATH, "rb") as f:
        done_sound = f.read()

# --- GIF URLs (publicly accessible) ---
GIF_URLS = {
    "Hourglass":     "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWFtcWlkcTlseDAxYnZybXg5NXJ5MXlremU2dXNpNmE1ZGJmbTY3ciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3QmY3Q9Zw/gLjD6hjRaLcFslzpvR/giphy.gif",
    "Running Man":   "https://media.giphy.com/media/l41lI4bYmcsPJX9Go/giphy.gif",
    "Cuckoo Clock":  "https://media.giphy.com/media/26uf6oM3B8YXxZ7GM/giphy.gif",
    "Analog":        None,
    "Digital":       None,
}

@st.cache_resource
# Load GIF frames once per URL
def load_gif_frames(url):
    try:
        reader = imageio.get_reader(url)
        return [frame for frame in reader]
    except Exception:
        return None

# --- Fallback draw functions ---
def draw_analog(rem, total):
    frac = rem / total
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    circle = plt.Circle((0.5,0.5), 0.4, fill=False, linewidth=2)
    ax.add_artist(circle)
    angle = 2 * math.pi * frac - math.pi/2
    x = 0.5 + 0.35 * math.cos(angle)
    y = 0.5 + 0.35 * math.sin(angle)
    ax.plot([0.5, x], [0.5, y], color='black', linewidth=2)
    ax.set_aspect('equal')
    buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0); plt.close(fig); buf.seek(0)
    return buf


def draw_hourglass(rem, total):
    frac = rem / total
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    # outline triangles
    up = plt.Polygon([[0.2,0.8],[0.8,0.8],[0.5,0.5]], fill=None, edgecolor='black', linewidth=2)
    dn = plt.Polygon([[0.2,0.2],[0.8,0.2],[0.5,0.5]], fill=None, edgecolor='black', linewidth=2)
    ax.add_patch(up); ax.add_patch(dn)
    # sand levels
    y_top = 0.5 + 0.3 * frac
    sand_top = plt.Polygon([[0.2,0.8],[0.8,0.8],[0.8,y_top],[0.2,y_top]], color='black')
    ax.add_patch(sand_top)
    y_bot = 0.2 + 0.3 * (1-frac)
    sand_bot = plt.Polygon([[0.2,0.2],[0.8,0.2],[0.8,y_bot],[0.2,y_bot]], color='black')
    ax.add_patch(sand_bot)
    # fixed drop in neck
    ax.scatter([0.5], [0.5], s=5, c='black')
    ax.set_aspect('equal')
    buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0); plt.close(fig); buf.seek(0)
    return buf


def draw_running(rem, total):
    frac = (total - rem) / total
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    ax.hlines(0.5, 0.1, 0.9, color='gray', linewidth=2)
    x = 0.1 + 0.8 * frac
    ax.text(x, 0.5, '🏃', fontsize=16, ha='center', va='center')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0); plt.close(fig); buf.seek(0)
    return buf


def draw_cuckoo(rem, total):
    passed = int((total - rem) // 60)
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    ax.text(0.5, 0.7, '🕰️', fontsize=20, ha='center')
    ax.text(0.5, 0.3, '🕊' * passed, fontsize=12, ha='center')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    buf = BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0); plt.close(fig); buf.seek(0)
    return buf

# --- Pasta selection ---
pasta_times = {"Spaghetti":8*60, "Penne":11*60, "Fusilli":10*60, "Ravioli":5*60, "Custom":None}
sel = st.selectbox("Pick your pasta:", list(pasta_times.keys()))
if sel == "Custom":
    mins = st.number_input("Cook time (minutes):",1,60,10)
    total = int(mins*60)
else:
    total = pasta_times[sel]
    st.write(f"{sel} cooks for {total//60} minutes.")

# --- Preload GIF frames ---
gif_frames = {}
gif_lengths = {}
for name, url in GIF_URLS.items():
    if url:
        frames = load_gif_frames(url)
        if frames:
            gif_frames[name] = frames
            gif_lengths[name] = len(frames)

# --- Run timers in two rows ---
if st.button('Start Timer'):
    for i in range(total + 1):
        rem = total - i
        mins, secs = divmod(rem, 60)
        ts = f"{mins:02d}:{secs:02d}"

        # First row: Digital, Analog, Hourglass
        r1 = st.columns(3)
        with r1[0]:
            st.markdown("**Digital**")
            st.text(ts)
        with r1[1]:
            st.markdown("**Analog**")
            frames = gif_frames.get("Analog")
            if frames:
                idx = min(int(i/total * gif_lengths["Analog"]), gif_lengths["Analog"]-1)
                st.image(frames[idx])
            else:
                st.image(draw_analog(rem, total))
        with r1[2]:
            st.markdown("**Hourglass**")
            frames = gif_frames.get("Hourglass")
            if frames:
                idx = min(int(i/total * gif_lengths["Hourglass"]), gif_lengths["Hourglass"]-1)
                st.image(frames[idx])
            else:
                st.image(draw_hourglass(rem, total))

        # Second row: Running Man, Cuckoo Clock
        r2 = st.columns(2)
        with r2[0]:
            st.markdown("**Running Man**")
            frames = gif_frames.get("Running Man")
            if frames:
                idx = min(int(i/total * gif_lengths["Running Man"]), gif_lengths["Running Man"]-1)
                st.image(frames[idx])
            else:
                st.image(draw_running(rem, total))
        with r2[1]:
            st.markdown("**Cuckoo Clock**")
            frames = gif_frames.get("Cuckoo Clock")
            if frames:
                idx = min(int(i/total * gif_lengths["Cuckoo Clock"]), gif_lengths["Cuckoo Clock"]-1)
                st.image(frames[idx])
            else:
                st.image(draw_cuckoo(rem, total))

        time.sleep(1)

    # Done
    st.markdown("### ⏰ Done! Enjoy your pasta! 🍝")
    if done_sound:
        st.audio(done_sound)
    if done_img:
        st.image(done_img)
    else:
        st.balloons()
