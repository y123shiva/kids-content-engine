import streamlit as st
import requests
import os
from pathlib import Path

# --- Config ---
API_URL = "http://localhost:8000"
VIDEO_DIR = Path("outputs/video")

st.set_page_config(page_title="Bibo Lab | AI Animation Studio", page_icon="🤖")

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Bibo Lab Studio")
st.subheader("Transform ideas into children's animation")

# --- Sidebar: System Health ---
with st.sidebar:
    st.header("System Status")
    try:
        health = requests.get(f"{API_URL}/").json()
        st.success(f"🟢 {health['status']}")
    except:
        st.error("🔴 Backend Offline")
    
    st.divider()
    st.info("Bibo Lab v1.0 - Powered by RAG + TTS + Motion Engine")

# --- Main Interface: Control Panel ---
with st.expander("🚀 Create New Adventure", expanded=True):
    topic = st.text_input("What should Bibo learn about today?", placeholder="e.g. Brushing teeth, Gravity, Sharing")
    col1, col2 = st.columns(2)
    with col1:
        age_group = st.selectbox("Age Group", ["3-4 years", "5-6 years"])
    with col2:
        render_quality = st.select_slider("Quality", options=["Draft", "HD"])

    if st.button("Generate Animation"):
        if topic:
            with st.status("🎬 Bibo is working...", expanded=True) as status:
                st.write("📝 Brainstorming script (RAG)...")
                # Call your Master Workflow logic here
                res = requests.post(f"{API_URL}/script/generate-from-rag", json={"query": topic, "k": 3})
                
                if res.status_code == 200:
                    script_data = res.json()
                    st.write("🔊 Generating Bibo's voice...")
                    # Trigger Animation (Stage 3)
                    requests.post(f"{API_URL}/animation/generate", json=script_data['script'])
                    status.update(label="✅ Production Complete!", state="complete")
                    st.balloons()
                else:
                    st.error("Something went wrong in the lab.")
        else:
            st.warning("Please enter a topic first!")

# --- Video Gallery ---
st.divider()
st.header("📺 Recent Productions")

if VIDEO_DIR.exists():
    video_files = list(VIDEO_DIR.glob("*.mp4"))
    if video_files:
        # Display in a grid
        cols = st.columns(2)
        for idx, v_file in enumerate(reversed(video_files)): # Show newest first
            with cols[idx % 2]:
                st.video(str(v_file))
                st.caption(f"🎥 {v_file.name}")
    else:
        st.write("No videos found yet. Start generating!")
else:
    st.info("The production gallery is empty.")