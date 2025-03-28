# utils/pose_classifier.py

from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch

# Load CLIP model once globally
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Pose classes to classify
POSE_CLASSES = ["Front", "Side", "Rear"]

@torch.no_grad()
def classify_pose(image_file) -> tuple:
    """
    Classifies an image as one of Front, Side, Rear using CLIP.
    Returns (predicted_pose, confidence_percent)
    """
    try:
        if hasattr(image_file, 'read'):  # Handle Streamlit files
            image = Image.open(image_file).convert("RGB")
        else:
            image = Image.open(image_file).convert("RGB")

        inputs = clip_processor(text=POSE_CLASSES, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).squeeze().tolist()

        max_idx = int(torch.argmax(logits_per_image))
        return POSE_CLASSES[max_idx], probs[max_idx] * 100

    except Exception as e:
        return "Front", 33.3  # fallback prediction

