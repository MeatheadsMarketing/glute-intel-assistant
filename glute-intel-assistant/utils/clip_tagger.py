# utils/clip_tagger.py

from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch

# Load model + processor globally
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Glute shape categories (from prior system strategy)
GLUTE_TAGS = [
    "Round (Bubble)", "Heart-Shaped (A-frame)", "Square", "Inverted (V-shape)", "Natural BBL Look",
    "High-Riding Glutes", "Low-Set Glutes", "Hip-Dominant", "Thigh-Dominant", "Hamstring-Dominant",
    "Wide-Set Glutes", "Close-Set Glutes", "Compact & Toned", "Soft & Natural", "Muscle-Dominant",
    "Fat-Dominant", "Shelf Glutes", "Sloped Glutes", "Upper-Glute Emphasis", "Lower-Glute Emphasis",
    "Balanced (Proportionate)", "Peach Shape", "Mini BBL Look", "Deep Hip Dips", "Smooth Silhouette"
]

@torch.no_grad()
def suggest_clip_tags(image_path_or_file, top_k: int = 5):
    """
    Suggests glute tag categories using CLIP similarity.
    Returns list of top_k predicted tags ranked by confidence.
    """
    try:
        if hasattr(image_path_or_file, 'read'):
            image = Image.open(image_path_or_file).convert("RGB")
        else:
            image = Image.open(str(image_path_or_file)).convert("RGB")

        inputs = clip_processor(text=GLUTE_TAGS, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        logits = outputs.logits_per_image.softmax(dim=1).squeeze().tolist()

        tag_conf = list(zip(GLUTE_TAGS, logits))
        ranked = sorted(tag_conf, key=lambda x: x[1], reverse=True)
        return [tag for tag, prob in ranked[:top_k]]

    except Exception as e:
        return ["Unknown"]

