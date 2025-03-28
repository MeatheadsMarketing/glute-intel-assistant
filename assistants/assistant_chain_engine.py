# apps/streamlit_progress_dashboard.py (PRL+ Step 4: Integrated Assistant Chaining Engine)

import streamlit as st
import os
import pandas as pd
import datetime
from PIL import Image
import matplotlib.pyplot as plt
from collections import defaultdict
from assistants.assistant_chain_engine import auto_chain_for_session

st.set_page_config(page_title="📈 Glute Progress Tracker", layout="wide")
st.title("📈 Client Progress Tracker Dashboard")
st.markdown("Browse, review, and track all before/after sessions, shape tag deltas, and plan summaries.")

LOGS_DIR = "data/logs"
UPLOADS_DIR = "uploads"
TAG_LOG_PATH = "data/tag_logs.csv"
PLAN_LOG_PATH = "data/plan_logs.csv"

@st.cache_data
def list_logs():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    files = [f for f in os.listdir(LOGS_DIR) if f.endswith("_log.txt")]
    return sorted(files, reverse=True)

@st.cache_data
def load_image_thumbnail(path, size=(200, 280)):
    return Image.open(path).resize(size)

@st.cache_data
def load_tag_data():
    if os.path.exists(TAG_LOG_PATH):
        return pd.read_csv(TAG_LOG_PATH)
    return pd.DataFrame(columns=["session_id", "tag", "timestamp"])

@st.cache_data
def load_plan_archive():
    if os.path.exists(PLAN_LOG_PATH):
        return pd.read_csv(PLAN_LOG_PATH)
    return pd.DataFrame(columns=["session_id", "plan_text", "timestamp"])

log_files = list_logs()
st.sidebar.title("📂 Session Log Viewer")
selected_log = st.sidebar.selectbox("Choose a Session Log", log_files)

if selected_log:
    log_path = os.path.join(LOGS_DIR, selected_log)
    with open(log_path, "r") as f:
        lines = f.readlines()
    meta_lines = [line.strip() for line in lines if line.strip()]
    st.subheader(f"📝 Summary: {selected_log}")
    for line in meta_lines:
        st.markdown(f"- {line}")

    session_id = selected_log.replace("_log.txt", "")
    subject_dir = os.path.join(UPLOADS_DIR, session_id)
    if os.path.exists(subject_dir):
        st.markdown("### 📸 Image History")
        imgs = sorted([f for f in os.listdir(subject_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
        cols = st.columns(min(len(imgs), 3))
        for i, img_name in enumerate(imgs):
            with cols[i % len(cols)]:
                img_path = os.path.join(subject_dir, img_name)
                st.image(load_image_thumbnail(img_path), caption=img_name)
    else:
        st.warning("No matching image folder found. Please ensure 'uploads/session_id/' is synced.")

    with st.expander("📊 Tag Change History (Evolution Timeline)"):
        tag_df = load_tag_data()
        tag_df = tag_df[tag_df["session_id"] == session_id]
        if not tag_df.empty:
            grouped = tag_df.groupby("tag").size().sort_values(ascending=False)
            st.bar_chart(grouped)
            st.markdown("This graph shows the distribution of dominant glute shape tags over time.")
        else:
            st.info("No tag history found for this session.")

    with st.expander("🧠 GPT Plan Archive"):
        plan_df = load_plan_archive()
        plan_df = plan_df[plan_df["session_id"] == session_id]
        if not plan_df.empty:
            for idx, row in plan_df.iterrows():
                st.markdown(f"**🗓️ {row['timestamp']}**")
                st.markdown(row['plan_text'], unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No archived plans found for this session.")

        st.markdown("---")
        st.markdown("### 🔁 Run Assistant Chaining for This Session")
        if st.button("⚡ Auto-Generate Tags + Plan for this Session"):
            tags, plan = auto_chain_for_session(session_id)
            st.success(f"✅ Assistant chaining complete! Tags: {', '.join(tags)}")
            st.markdown("**New Plan Preview:**")
            st.markdown(plan, unsafe_allow_html=True)

    with st.expander("📤 Export Options"):
        st.download_button("📥 Download Session Log", "".join(meta_lines), file_name=selected_log)
else:
    st.info("Select a session log from the sidebar to view full tracking history.")

