# pasta_timer_app.py
# Streamlit app generating timer visuals in Python on the fly
# To run: streamlit run pasta_timer_app.py

import streamlit as st
import time
import math
import matplotlib.pyplot as plt
from io import BytesIO
import os

st.set_page_config(page_title="Pasta Timer", page_icon="🍝", layout="centered")
st.title("🍝 Pasta Timer")

# --- Static defaults (place your files in assets/) ---
ASSETS_DIR = "assets"
DEFAULT_DONE_IMAGE = os.path.join(ASSETS_DIR, "done.png")
DEFAULT_DONE_SOUND = os.path.join(ASSETS_DIR, "done.mp3")

# upload overrides
uploaded_image = st.file_uploader(
    "Optional: upload an image to display when time's up", 
    type=["png","jpg","jpeg"], key="done_img"
)
uploaded_sound = st.file_uploader(
    "Optional: upload a sound to play when time's up", 
    type=["mp3","wav","ogg"], key="done_sound"
)

# Determine which image and sound to use
if uploaded_image:
    done_image_bytes = uploaded_image.read()
    done_image_to_show = done_image_bytes
else:
    # load static default file
    if os.path.exists(DEFAULT_DONE_IMAGE):
        with open(DEFAULT_DONE_IMAGE, "rb") as f:
            done_image_to_show = f.read()
    else:
        done_image_to_show = None

if uploaded_sound:
    done_sound_bytes = uploaded_sound.read()
    done_sound_to_play = done_sound_bytes
else:
    if os.path.exists(DEFAULT_DONE_SOUND):
        with open(DEFAULT_DONE_SOUND, "rb") as f:
            done_sound_to_play = f.read()
    else:
        done_sound_to_play = None

# pasta types
types = {"Spaghetti":480, "Penne":660, "Fusilli":600, "Ravioli":300, "Custom":None}
sel = st.selectbox("Pick your pasta:", list(types.keys()))

if sel == "Custom":
    mins = st.number_input("Cook time (minutes):", 1, 60, 10)
    total = int(mins*60)
else:
    total = types[sel]
    st.write(f"{sel} cooks for {total//60} minutes.")

style = st.selectbox("Timer style:", ["Digital","Analog","Hourglass","Running Man","Cuckoo Clock"])

# drawing functions
def gen_analog(rem, tot):
    fig,ax = plt.subplots()
    ax.axis('off')
    circle = plt.Circle((0.5,0.5),0.4, fill=False, linewidth=2)
    ax.add_artist(circle)
    frac = rem/tot
    angle = 2*math.pi*frac - math.pi/2
    x = 0.5 + 0.35*math.cos(angle)
    y = 0.5 + 0.35*math.sin(angle)
    ax.plot([0.5,x],[0.5,y],color='black',linewidth=3)
    ax.set_aspect('equal')
    buf=BytesIO(); plt.savefig(buf,format='png'); plt.close(fig); buf.seek(0)
    return buf

def gen_hourglass(rem, tot):
    fig,ax=plt.subplots(); ax.axis('off')
    top=plt.Polygon([[0.2,0.8],[0.8,0.8],[0.5,0.5]],fill=None,edgecolor='black'); ax.add_patch(top)
    bot=plt.Polygon([[0.2,0.2],[0.8,0.2],[0.5,0.5]],fill=None,edgecolor='black'); ax.add_patch(bot)
    frac=rem/tot
    y_top=0.5+0.3*frac
    fill_top=plt.Polygon([[0.2,0.8],[0.8,0.8],[0.8,y_top],[0.2,y_top]],color='black'); ax.add_patch(fill_top)
    frac2=1-frac
    y_bot=0.2+0.3*frac2
    fill_bot=plt.Polygon([[0.2,0.2],[0.8,0.2],[0.8,y_bot],[0.2,y_bot]],color='black'); ax.add_patch(fill_bot)
    ax.set_aspect('equal')
    buf=BytesIO(); plt.savefig(buf,format='png'); plt.close(fig); buf.seek(0)
    return buf

def gen_running(rem, tot):
    bar_len=30
    pos=int((tot-rem)/tot*bar_len)
    return '-'*pos + '🏃' + '-'*(bar_len-pos)

def gen_cuckoo(rem, tot):
    mins_passed=int((tot-rem)//60)
    return '🕰️ ' + '🕊'*mins_passed

# placeholders
img_pl=st.empty(); txt_pl=st.empty(); prog=None
if style=="Digital": prog=st.progress(0)

if st.button("Start Timer"):
    for elapsed in range(total+1):
        rem=total-elapsed
        m,s=divmod(rem,60); ts=f"{m:02d}:{s:02d}"
        if style=="Digital":
            txt_pl.markdown(f"### ⏱ {ts}")
            prog.progress(elapsed/total)
        elif style=="Analog":
            img_pl.image(gen_analog(rem,total))
            txt_pl.markdown(ts)
        elif style=="Hourglass":
            img_pl.image(gen_hourglass(rem,total))
            txt_pl.markdown(ts)
        elif style=="Running Man":
            txt_pl.text(gen_running(rem,total))
        else:
            txt_pl.markdown(gen_cuckoo(rem,total)+" **"+ts+"**")
        time.sleep(1)
    txt_pl.markdown("### ⏰ Done! 🍝")
    if done_sound_to_play:
        st.audio(done_sound_to_play, format=None)
    if done_image_to_show:
        st.image(done_image_to_show)
    else:
        st.balloons()
