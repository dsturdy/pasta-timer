# pasta_timer_app.py
# Streamlit app: synchronized timers (Digital, Analog, Hourglass, Running Man, Cuckoo Clock) with Python-generated frames and static done assets
# To run: streamlit run pasta_timer_app.py

import streamlit as st
import time
import math
import matplotlib.pyplot as plt
from io import BytesIO
import os
import numpy as np

st.set_page_config(page_title="Pasta Timer", page_icon="🍝", layout="centered")
st.title("🍝 Pasta Timer")

# --- Static defaults (place your done assets in assets/) ---
ASSETS_DIR = "assets"
DEFAULT_DONE_IMAGE = os.path.join(ASSETS_DIR, "done.png")
DEFAULT_DONE_SOUND = os.path.join(ASSETS_DIR, "done.mp3")

# load done assets
if os.path.exists(DEFAULT_DONE_IMAGE):
    with open(DEFAULT_DONE_IMAGE, "rb") as f:
        done_image_to_show = f.read()
else:
    done_image_to_show = None

if os.path.exists(DEFAULT_DONE_SOUND):
    with open(DEFAULT_DONE_SOUND, "rb") as f:
        done_sound_to_play = f.read()
else:
    done_sound_to_play = None

# --- Pasta selection ---
pasta_times = {
    "Spaghetti": 8 * 60,
    "Penne":    11 * 60,
    "Fusilli":  10 * 60,
    "Ravioli":   5 * 60,
    "Custom":   None
}
sel = st.selectbox("Pick your pasta:", list(pasta_times.keys()))
if sel == "Custom":
    mins = st.number_input("Cook time (minutes):", 1, 60, 10)
    total = int(mins * 60)
else:
    total = pasta_times[sel]
    st.write(f"{sel} cooks for {total//60} minutes.")

# placeholders
dig_pl = st.empty()
prog   = st.progress(0)
ana_pl = st.empty()
hg_pl  = st.empty()
rn_pl  = st.empty()
ck_pl  = st.empty()

# --- Drawing functions ---
def gen_analog(rem, tot):
    fig, ax = plt.subplots()
    ax.axis('off')
    circle = plt.Circle((0.5, 0.5), 0.4, fill=False, linewidth=2)
    ax.add_artist(circle)
    frac = rem / tot
    angle = 2 * math.pi * frac - math.pi/2
    x = 0.5 + 0.35 * math.cos(angle)
    y = 0.5 + 0.35 * math.sin(angle)
    ax.plot([0.5, x], [0.5, y], color='black', linewidth=3)
    ax.set_aspect('equal')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf


def gen_hourglass(rem, tot):
    fig, ax = plt.subplots()
    ax.axis('off')
    tri_up = plt.Polygon([[0.2,0.8],[0.8,0.8],[0.5,0.5]], fill=None, edgecolor='black', linewidth=2)
    tri_dn = plt.Polygon([[0.2,0.2],[0.8,0.2],[0.5,0.5]], fill=None, edgecolor='black', linewidth=2)
    ax.add_patch(tri_up)
    ax.add_patch(tri_dn)
    frac = rem / tot
    # sand
    y_top = 0.5 + 0.3 * frac
    sand_top = plt.Polygon([[0.2,0.8],[0.8,0.8],[0.8,y_top],[0.2,y_top]], color='black')
    ax.add_patch(sand_top)
    frac2 = 1 - frac
    y_bot = 0.2 + 0.3 * frac2
    sand_bot = plt.Polygon([[0.2,0.2],[0.8,0.2],[0.8,y_bot],[0.2,y_bot]], color='black')
    ax.add_patch(sand_bot)
    # falling grains
    n = min(int(100 * frac2), 50)
    xs = np.random.uniform(0.45, 0.55, n)
    ys = np.random.uniform(0.48, 0.52, n)
    ax.scatter(xs, ys, s=5, c='black')
    ax.set_aspect('equal')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf


def gen_running(rem, tot):
    # moving runner icon along a track
    fig, ax = plt.subplots(figsize=(4,1))
    ax.axis('off')
    frac = (tot - rem) / tot
    x = 0.1 + 0.8 * frac
    ax.plot([0.1, 0.9], [0.5, 0.5], color='gray', linewidth=2)
    ax.text(x, 0.5, '🏃', fontsize=20, ha='center', va='center')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf


def gen_cuckoo(rem, tot):
    # cuckoo pops one bird per minute passed
    mins_passed = int((tot - rem) // 60)
    fig, ax = plt.subplots(figsize=(3,1))
    ax.axis('off')
    for i in range(mins_passed):
        ax.text(0.05 + 0.1*i, 0.5, '🕊', fontsize=20)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf

# --- Run timers ---
if st.button("Start Timer"):
    for elapsed in range(total + 1):
        rem = total - elapsed
        m, s = divmod(rem, 60)
        ts = f"{m:02d}:{s:02d}"
        # digital
        dig_pl.markdown(f"**Digital:** {ts}")
        prog.progress(elapsed / total)
        # analog
        ana_pl = ana_pl or st.empty()
        buf_a = gen_analog(rem, total)
        ana_pl.image(buf_a, caption="Analog")
        # hourglass
        hg_pl = hg_pl or st.empty()
        buf_h = gen_hourglass(rem, total)
        hg_pl.image(buf_h, caption="Hourglass")
        # running man
        rn_pl = rn_pl or st.empty()
        buf_r = gen_running(rem, total)
        rn_pl.image(buf_r, caption="Running Man")
        # cuckoo clock
        ck_pl = ck_pl or st.empty()
        buf_c = gen_cuckoo(rem, total)
        ck_pl.image(buf_c, caption="Cuckoo Clock")
        time.sleep(1)
    st.markdown("### ⏰ Done! 🍝")
    if done_sound_to_play:
        st.audio(done_sound_to_play, format=None)
    if done_image_to_show:
        st.image(done_image_to_show)
    else:
        st.balloons()
