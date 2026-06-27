import os
import uuid
from io import BytesIO
# pyrefly: ignore [missing-import]
from PIL import Image
# pyrefly: ignore [missing-import]
from decorators import time_logger

# We will create an 'uploads' folder safely inside our project
UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@time_logger
def process_and_save_image(file_bytes: bytes, filename: str) -> dict:
    """Compresses the image and saves it securely to disk"""
    
    # 1. Security: Generate a random string (uuid) for the filename 
    # This prevents hackers from using malicious filenames to break our server
    secure_name = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_DIR, secure_name)
    
    # 2. Open the image in computer memory using Pillow
    image = Image.open(BytesIO(file_bytes))
    
    # 3. Strip transparency so we can compress it as a small JPEG
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        
    # 4. Compression: If it's a massive 4K image, shrink it to 1000px wide max
    if image.width > 1000:
        ratio = 1000 / image.width
        new_size = (1000, int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        
    # 5. Compression: Save it at 85% quality!
    image.save(filepath, format="JPEG", quality=85)
    
    # Return the new path and metadata to save in the database
    return {
        "path": filepath,
        "metadata": {
            "original_name": filename,
            "format": "JPEG",
            "size": os.path.getsize(filepath) # Returns size in bytes
        }
    }
