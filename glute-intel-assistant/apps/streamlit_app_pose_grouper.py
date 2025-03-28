# apps/streamlit_app_pose_grouper.py (PRL+ upgraded with workout preview + intelligence selector)

import streamlit as st
import os
import tempfile
import uuid
from datetime import datetime
import sys

# Add parent folder to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.image_validator import is_valid_image, get_image_metadata
from utils.drive_uploader import authenticate_drive, create_drive_folder_if_missing, upload_image_to_drive
from utils.pose_classifier import classify_pose
from utils.clip_tagger import suggest_clip_tags
from assistants.plan_generator import generate_glute_plan, INTELLIGENCE_PROFILES

POSE_OPTIONS = ["Front", "Side", "Rear"]

st.set_page_config(page_title="Pose Grouper Assistant", layout="wide")
st.title("📸 Multi-View Pose Grouper + Glute Plan Preview")
st.markdown("Group front/side/rear images of the same subject and preview a tailored glute transformation plan.")

# Inputs
session_id = st.text_input("Enter Session ID", value="march27_session")
subject_id = st.text_input("Enter Subject ID", value=f"subject_{uuid.uuid4().hex[:6]}")

uploaded_files = st.file_uploader("Upload up to 3 images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Plan Preview Settings (sidebar)
st.sidebar.title("🧠 Plan Generator Settings")
st.sidebar.markdown("Choose your guidance source for GPT training philosophy.")
selected_expert = st.sidebar.selectbox("Select Intelligence Profile", INTELLIGENCE_PROFILES)
fitness_level = st.sidebar.selectbox("Select Fitness Level", ["Beginner", "Intermediate", "Advanced"])
goal_text = st.sidebar.text_input("Goal Focus", value="Aesthetic Shape + Strength")

# Setup
if uploaded_files:
    st.subheader("🖼️ Assign Poses + View AI Suggestions")
    pose_assignments = {}
    assigned_poses = set()
    all_tags = set()

    for i, uploaded_file in enumerate(uploaded_files):
        st.image(uploaded_file, width=300, caption=uploaded_file.name)

        predicted_pose, confidence = classify_pose(uploaded_file)
        st.markdown(f"**AI Suggests:** `{predicted_pose}` ({confidence:.1f}% confidence)")

        pose = st.selectbox(
            f"Select pose for image {i+1}", POSE_OPTIONS, index=POSE_OPTIONS.index(predicted_pose) if predicted_pose in POSE_OPTIONS else 0, key=f"pose_{i}"
        )

        if pose in assigned_poses:
            st.warning(f"⚠️ Pose '{pose}' already assigned. Each pose must be unique.")
        else:
            assigned_poses.add(pose)
            pose_assignments[pose] = uploaded_file

    if len(pose_assignments) >= 1:
        if st.button("Group, Tag & Save to Drive"):
            with st.spinner("🔐 Connecting to Google Drive..."):
                drive = authenticate_drive()
                base_folder_id = create_drive_folder_if_missing(drive, "AI_Glute_Assistant")
                session_folder_id = create_drive_folder_if_missing(drive, session_id, parent_id=base_folder_id)
                subject_folder_id = create_drive_folder_if_missing(drive, subject_id, parent_id=session_folder_id)

            for pose, file in pose_assignments.items():
                is_valid, msg = is_valid_image(file)
                if not is_valid:
                    st.error(f"❌ {file.name}: {msg}")
                    continue

                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(file.read())
                    tmp_path = tmp.name

                filename = f"{pose.lower()}.jpg"
                file_url = upload_image_to_drive(drive, open(tmp_path, "rb"), filename, subject_folder_id)
                meta = get_image_metadata(file)

                clip_tags = suggest_clip_tags(tmp_path)
                all_tags.update(clip_tags)

                st.success(f"✅ Uploaded {pose} view: [View in Drive]({file_url})")
                st.write(f"📏 Resolution: {meta['width']}x{meta['height']}, 💾 Size: {meta['size_MB']}MB")
                st.markdown(f"🧠 Suggested Tags: `{', '.join(clip_tags[:3])}`")
                os.remove(tmp_path)

            # Save log CSV locally
            log_lines = ["subject_id,pose,filename,timestamp\n"]
            for pose in pose_assignments:
                log_lines.append(f"{subject_id},{pose},{pose.lower()}.jpg,{datetime.utcnow()}\n")

            log_file = f"{subject_id}_log.csv"
            with open(log_file, "w") as f:
                f.writelines(log_lines)
            st.download_button("📥 Download Log CSV", data="".join(log_lines), file_name=log_file)

            # 🔮 Generate and preview plan
            if all_tags:
                st.markdown("---")
                st.subheader("🧠 AI-Generated Glute Plan Preview")
                st.markdown(f"**Tags used:** `{', '.join(all_tags)}`")
                with st.spinner("Generating plan based on expert philosophy and tags..."):
                    plan_md = generate_glute_plan(
                        glute_tags=list(all_tags),
                        user_fitness_level=fitness_level,
                        goals=goal_text,
                        expert_source=selected_expert
                    )
                st.markdown(plan_md, unsafe_allow_html=True)
    else:
        st.info("Please assign at least one unique pose.")
else:
    st.info("Upload up to 3 images to begin pose grouping.")

