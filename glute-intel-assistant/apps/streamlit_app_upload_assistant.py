import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from utils.image_validator import is_valid_image, get_image_metadata
from utils.drive_uploader import authenticate_drive, create_drive_folder_if_missing, upload_image_to_drive


# ───────────────────────────────────────────────
# UI CONFIG
st.set_page_config(page_title="Upload Assistant", layout="centered")
st.title("📤 Glute Image Upload Assistant")
st.markdown("Upload your BBL dataset images, validate quality, and auto-send to your Google Drive.")

# ───────────────────────────────────────────────
# SESSION & UPLOAD
session_id = st.text_input("Enter Session ID", value="test_session_march27")
uploaded_files = st.file_uploader(
    "Upload Images (JPG, PNG, WEBP)", 
    type=["jpg", "jpeg", "png", "webp"], 
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("Drag in one or more image files to get started.")
    st.stop()

# ───────────────────────────────────────────────
# Google Drive Connection
with st.spinner("🔐 Connecting to Google Drive..."):
    drive = authenticate_drive()
    base_folder_id = create_drive_folder_if_missing(drive, "AI_Glute_Assistant")
    session_folder_id = create_drive_folder_if_missing(drive, session_id, parent_id=base_folder_id)

# ───────────────────────────────────────────────
# Image Processing & Display
st.subheader("📸 Uploaded Image Previews")
for uploaded_file in uploaded_files:
    # Validate
    is_valid, message = is_valid_image(uploaded_file)
    if not is_valid:
        st.warning(f"⚠️ {uploaded_file.name}: {message}")
        continue

    # Display image + metadata
    st.image(uploaded_file, width=300, caption=uploaded_file.name)
    meta = get_image_metadata(uploaded_file)
    st.write(f"🧬 Resolution: {meta['width']}x{meta['height']}, Size: {meta['size_MB']}MB")

    # Save to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Upload to Google Drive
    uploaded_file.name = f"{uuid.uuid4()}.jpg"  # rename for uniqueness
    drive_link = upload_image_to_drive(drive, open(tmp_path, "rb"), uploaded_file.name, session_folder_id)
    st.success(f"✅ Uploaded to Drive: [View File]({drive_link})")

    # Clean up temp
    os.remove(tmp_path)
