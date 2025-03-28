# apps/streamlit_glute_comparator.py (PRL+ final expansion)

import streamlit as st
from PIL import Image, ImageDraw
import os
import io
import datetime
import torch
from utils.clip_tagger import suggest_clip_tags
from assistants.plan_generator import generate_glute_plan

st.set_page_config(page_title="Before/After Glute Comparison", layout="wide")
st.title("📊 Before/After Glute Visual Tracker + AI Transformation Feedback")
st.markdown("Upload and compare two glute images to visually and semantically track transformation.")

# Sidebar metadata entry
st.sidebar.header("🗂️ Comparison Metadata")
comparison_id = st.sidebar.text_input("Session or Client ID", value=f"glute_progress_{datetime.date.today()}")
description = st.sidebar.text_area("Notes (e.g., Program used, key dates)", placeholder="e.g., Week 1 vs Week 8 after Glute Power Plan")

col1, col2 = st.columns(2)
with col1:
    before_file = st.file_uploader("⬅️ Upload BEFORE Image", type=["jpg", "jpeg", "png"], key="before")
with col2:
    after_file = st.file_uploader("➡️ Upload AFTER Image", type=["jpg", "jpeg", "png"], key="after")

@st.cache_data
def load_image(file):
    img = Image.open(file).convert("RGB")
    return img.resize((500, 700))

def add_guidelines(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    width, height = image.size
    center_x = width // 2
    draw.line([(center_x, 0), (center_x, height)], fill="red", width=3)
    return image

if before_file and after_file:
    before_img = load_image(before_file)
    after_img = load_image(after_file)

    st.markdown("### 🔍 Visual Alignment Preview")
    col1, col2 = st.columns(2)
    with col1:
        st.image(add_guidelines(before_img.copy()), caption="Before (w/ alignment)", use_column_width=True)
    with col2:
        st.image(add_guidelines(after_img.copy()), caption="After (w/ alignment)", use_column_width=True)

    st.markdown("---")
    st.subheader("📌 Comparison Summary")
    st.markdown(f"**ID:** `{comparison_id}`  ")
    st.markdown(f"**Notes:** {description if description else 'None provided'}`")

    layout = st.radio("View mode", ["Side-by-Side", "Stacked"])
    if layout == "Stacked":
        st.image([before_img, after_img], caption=["Before", "After"], width=500)

    timestamp = datetime.datetime.now().isoformat()
    log_data = f"ID: {comparison_id}\nTimestamp: {timestamp}\nNotes: {description}"
    st.download_button("📥 Download Log", log_data, file_name=f"{comparison_id}_log.txt")

    st.markdown("---")
    st.subheader("🧠 AI Tag Delta & Transformation Feedback")

    before_tags = suggest_clip_tags(before_file, top_k=5)
    after_tags = suggest_clip_tags(after_file, top_k=5)

    st.markdown(f"**Before Tags:** `{', '.join(before_tags)}`")
    st.markdown(f"**After Tags:** `{', '.join(after_tags)}`")

    delta_tags = list(set(after_tags) - set(before_tags))
    lost_tags = list(set(before_tags) - set(after_tags))

    st.markdown("#### 🧪 Tag Delta Analysis")
    if delta_tags:
        st.success(f"Gains/Improvements: `{', '.join(delta_tags)}`")
    else:
        st.info("No new dominant shape changes detected.")
    if lost_tags:
        st.warning(f"Reduced Traits: `{', '.join(lost_tags)}`")

    st.markdown("#### 🧠 GPT Summary Plan Suggestion (Optional)")
    with st.expander("Generate Updated Plan Based on Change"):
        expert = st.selectbox("Expert Filter", ["Bret Contreras", "Jeff Nippard", "NASM"])
        updated_plan = generate_glute_plan(glute_tags=after_tags, expert_source=expert)
        st.markdown(updated_plan, unsafe_allow_html=True)
else:
    st.info("Upload both a BEFORE and AFTER image to begin comparison.")
