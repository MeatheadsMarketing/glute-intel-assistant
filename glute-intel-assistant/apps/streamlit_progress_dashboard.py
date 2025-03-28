# apps/streamlit_progress_dashboard.py (PRL+ Manual Full Rebuild for Deployment Clarity)

import streamlit as st
import os
import pandas as pd
import datetime
from PIL import Image
import matplotlib.pyplot as plt

from assistants.assistant_chain_engine import auto_chain_for_session

# ───────────────────────────────────────────────
# CONFIGURATION
st.set_page_config(page_title="📈 Glute Progress Tracker", layout="wide")
st.title("📈 Client Progress Tracker Dashboard")
st.markdown("Track all sessions, tag evolution, and assistant-generated plans.")

# ───────────────────────────────────────────────
# PATHS
LOGS_DIR = "data/logs"
UPLOADS_DIR = "uploads"
TAG_LOG_PATH = "data/tag_logs.csv"
PLAN_LOG_PATH = "data/plan_logs.csv"

# ───────────────────────────────────────────────
# HELPERS

def list_logs():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    return sorted([f for f in os.listdir(LOGS_DIR) if f.endswith("_log.txt")], reverse=True)

def load_image_thumbnail(path, size=(200, 280)):
    return Image.open(path).resize(size)

def load_tag_data():
    if os.path.exists(TAG_LOG_PATH):
        return pd.read_csv(TAG_LOG_PATH)
    return pd.DataFrame(columns=["session_id", "tag", "timestamp"])

def load_plan_archive():
    if os.path.exists(PLAN_LOG_PATH):
        return pd.read_csv(PLAN_LOG_PATH)
    return pd.DataFrame(columns=["session_id", "plan_text", "timestamp"])

# ───────────────────────────────────────────────
# UI: Sidebar Session Selector
log_files = list_logs()
st.sidebar.title("📂 Session Logs")
selected_log = st.sidebar.selectbox("Select Session", log_files)

if selected_log:
    session_id = selected_log.replace("_log.txt", "")
    log_path = os.path.join(LOGS_DIR, selected_log)
    with open(log_path, "r") as f:
        meta_lines = [line.strip() for line in f if line.strip()]

    st.subheader(f"📝 {selected_log}")
    for line in meta_lines:
        st.markdown(f"- {line}")

    # ───────────────────────────────────────────────
    # IMAGE HISTORY DISPLAY
    subject_dir = os.path.join(UPLOADS_DIR, session_id)
    if os.path.exists(subject_dir):
        imgs = sorted([f for f in os.listdir(subject_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
        st.markdown("### 📸 Uploaded Images")
        cols = st.columns(min(len(imgs), 3))
        for i, img in enumerate(imgs):
            with cols[i % len(cols)]:
                img_path = os.path.join(subject_dir, img)
                st.image(load_image_thumbnail(img_path), caption=img)
    else:
        st.warning("No image folder found. Check uploads directory.")

    # ───────────────────────────────────────────────
    # TAG EVOLUTION TIMELINE
    with st.expander("📊 Tag Evolution Timeline"):
        tag_df = load_tag_data()
        tag_df = tag_df[tag_df.session_id == session_id]
        if not tag_df.empty:
            tag_chart = tag_df.groupby("tag").size().sort_values(ascending=False)
            st.bar_chart(tag_chart)
        else:
            st.info("No tags logged yet.")

    # ───────────────────────────────────────────────
    # PLAN HISTORY VIEWER
    with st.expander("🧠 GPT Plan Archive"):
        plan_df = load_plan_archive()
        plan_df = plan_df[plan_df.session_id == session_id]
        if not plan_df.empty:
            for _, row in plan_df.iterrows():
                st.markdown(f"**🗓️ {row['timestamp']}**")
                st.markdown(row['plan_text'], unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No plans archived for this session.")

        st.markdown("### 🔁 Run Assistant Chain for This Session")
        if st.button("⚡ Auto-generate tags and plan"):
            tags, plan = auto_chain_for_session(session_id)
            st.success(f"✅ Tags: {', '.join(tags)}")
            st.markdown("**Generated Plan:**")
            st.markdown(plan, unsafe_allow_html=True)

    # ───────────────────────────────────────────────
    # LOG EXPORT
    with st.expander("📥 Download Logs"):
        st.download_button("📥 Download Session Log", "\n".join(meta_lines), file_name=selected_log)

else:
    st.info("Please select a session log from the sidebar to begin.")

