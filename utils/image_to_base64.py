import base64
from io import BytesIO
from PIL import Image
import os

async def convert_image_to_base64(image_path, max_size=(75, 75)):
    if not os.path.exists(image_path):
        print(f"Image {image_path} not found.")
        return None
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return f"data:image/jpg;base64,{base64_image}"
    except Exception as e:
        print(f"Error converting image to Base64: {e}")
        return None