# pasta_timer_app.py
# Streamlit app: synchronized timers with optional GIF animations aligned to countdown
# Uses placeholders to update each timer in place rather than stacking
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
img_done = None
snd_done = None
if os.path.exists(DONE_IMG):
    with open(DONE_IMG, 'rb') as f:
        img_done = f.read()
if os.path.exists(DONE_SND):
    with open(DONE_SND, 'rb') as f:
        snd_done = f.read()

# --- GIF URLs (publicly accessible) ---
GIF_URLS = {
    'Hourglass':    'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWFtcWlkcTlseDAxYnZybXg5NXJ5MXlremU2dXNpNmE1ZGJmbTY3ciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3QmY3Q9Zw/gLjD6hjRaLcFslzpvR/giphy.gif',
    'Running Man':  'https://media.giphy.com/media/l41lI4bYmcsPJX9Go/giphy.gif',
    'Cuckoo Clock': 'https://media.giphy.com/media/26uf6oM3B8YXxZ7GM/giphy.gif',
    'Analog':       None,   # fallback to Matplotlib draw
    'Digital':      None,   # fallback to text + progress bar
}

@st.cache_resource
def load_gif_frames(url):
    """Download a GIF and split it into frames."""
    if not imageio:
        return None
    try:
        reader = imageio.get_reader(url)
        return [frame for frame in reader]
    except:
        return None

# --- Fallback draw functions ---
def draw_analog(rem, total):
    frac = rem/total
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    circ = plt.Circle((0.5,0.5),0.4,fill=False,linewidth=2)
    ax.add_artist(circ)
    ang = 2*math.pi*frac - math.pi/2
    x = 0.5 + 0.35*math.cos(ang)
    y = 0.5 + 0.35*math.sin(ang)
    ax.plot([0.5,x],[0.5,y],color='black',linewidth=2)
    ax.set_aspect('equal')
    buf = BytesIO()
    plt.savefig(buf,format='png',bbox_inches='tight',pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf

def draw_hourglass(rem, total):
    frac = rem/total
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    up = plt.Polygon([[0.2,0.8],[0.8,0.8],[0.5,0.5]],fill=None,edgecolor='black',linewidth=2)
    dn = plt.Polygon([[0.2,0.2],[0.8,0.2],[0.5,0.5]],fill=None,edgecolor='black',linewidth=2)
    ax.add_patch(up); ax.add_patch(dn)
    ytop = 0.5 + 0.3*frac
    sand_up = plt.Polygon([[0.2,0.8],[0.8,0.8],[0.8,ytop],[0.2,ytop]],color='black')
    ax.add_patch(sand_up)
    ybot = 0.2 + 0.3*(1-frac)
    sand_dn = plt.Polygon([[0.2,0.2],[0.8,0.2],[0.8,ybot],[0.2,ybot]],color='black')
    ax.add_patch(sand_dn)
    ax.scatter([0.5],[0.5],s=5,c='black')  # fixed drop
    ax.set_aspect('equal')
    buf = BytesIO()
    plt.savefig(buf,format='png',bbox_inches='tight',pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf

def draw_running(rem, total):
    frac = (total-rem)/total
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    ax.hlines(0.5,0.1,0.9,color='gray',linewidth=2)
    x = 0.1 + 0.8*frac
    ax.text(x,0.5,'🏃',fontsize=16,ha='center',va='center')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    buf = BytesIO()
    plt.savefig(buf,format='png',bbox_inches='tight',pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf

def draw_cuckoo(rem, total):
    passed = int((total-rem)//60)
    fig, ax = plt.subplots(figsize=(2,2))
    ax.axis('off')
    ax.text(0.5,0.7,'🕰️',fontsize=20,ha='center')
    ax.text(0.5,0.3,'🕊'*passed,fontsize=12,ha='center')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    buf = BytesIO()
    plt.savefig(buf,format='png',bbox_inches='tight',pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf

# --- Pasta selection ---
times = {
    "Spaghetti": 8*60,
    "Penne":    11*60,
    "Fusilli":  10*60,
    "Ravioli":   5*60,
    "Custom":   None
}
sel = st.selectbox("Pick your pasta:", list(times.keys()))
if sel == "Custom":
    total = int(st.number_input("Cook time (min):",1,60,10)*60)
else:
    total = times[sel]
st.write(f"{sel} cooks for {total//60} min.")

# --- Prepare placeholders in five columns ---
col1,col2,col3,col4,col5 = st.columns(5)
dt_txt  = col1.empty(); dt_prog  = col1.empty()
ana_pl  = col2.empty()
hg_pl   = col3.empty()
run_pl  = col4.empty()
cuc_pl  = col5.empty()

# --- Preload GIF frames ---
frames  = {}
lengths = {}
for k, url in GIF_URLS.items():
    if url and imageio:
        f = load_gif_frames(url)
        if f:
            frames[k]  = f
            lengths[k] = len(f)

# --- Run the synchronized countdown ---
if st.button("Start Timer"):
    for i in range(total+1):
        rem = total - i
        m, s = divmod(rem, 60)
        ts = f"{m:02d}:{s:02d}"

        # Digital
        dt_txt.markdown(f"**Digital**\n{ts}")
        dt_prog.progress(i/total)

        # Analog
        if "Analog" in frames:
            idx = min(int(i/total * lengths["Analog"]), lengths["Analog"]-1)
            ana_pl.image(frames["Analog"][idx])
        else:
            ana_pl.image(draw_analog(rem, total))

        # Hourglass
        if "Hourglass" in frames:
            idx = min(int(i/total * lengths["Hourglass"]), lengths["Hourglass"]-1)
            hg_pl.image(frames["Hourglass"][idx])
        else:
            hg_pl.image(draw_hourglass(rem, total))

        # Running Man
        if "Running Man" in frames:
            idx = min(int(i/total * lengths["Running Man"]), lengths["Running Man"]-1)
            run_pl.image(frames["Running Man"][idx])
        else:
            run_pl.image(draw_running(rem, total))

        # Cuckoo Clock
        if "Cuckoo Clock" in frames:
            idx = min(int(i/total * lengths["Cuckoo Clock"]), lengths["Cuckoo Clock"]-1)
            cuc_pl.image(frames["Cuckoo Clock"][idx])
        else:
            cuc_pl.image(draw_cuckoo(rem, total))

        time.sleep(1)

    # Done
    st.markdown("### ⏰ Done! Enjoy your pasta! 🍝")
    if snd_done:
        st.audio(snd_done)
    if img_done:
        st.image(img_done)
    else:
        st.balloons()
