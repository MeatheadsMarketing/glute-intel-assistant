# utils/image_validator.py

import io
from PIL import Image

# Supported formats and size limit (8MB)
SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'webp']
MAX_SIZE_MB = 8
MIN_WIDTH = 256
MIN_HEIGHT = 256

def is_valid_image(file):
    """Checks format, file size, and resolution."""
    file_size_mb = len(file.getbuffer()) / (1024 * 1024)
    file_type = file.type.split('/')[-1].lower()
    
    if file_type not in SUPPORTED_FORMATS:
        return False, f"Unsupported format: {file_type}"
    if file_size_mb > MAX_SIZE_MB:
        return False, f"File too large: {file_size_mb:.2f}MB"
    
    try:
        img = Image.open(file)
        width, height = img.size
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            return False, f"Image resolution too low: {width}x{height}"
    except Exception as e:
        return False, f"Corrupted image or cannot open: {e}"

    return True, "Image is valid"

def get_image_metadata(file):
    """Returns dictionary of image metadata."""
    img = Image.open(file)
    width, height = img.size
    file.seek(0, io.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    return {
        "width": width,
        "height": height,
        "format": img.format,
        "size_MB": round(size_mb, 2)
    }

def get_image_dimensions(file):
    """Returns (width, height) tuple."""
    img = Image.open(file)
    return img.size
