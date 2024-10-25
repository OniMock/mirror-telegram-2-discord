import base64
from io import BytesIO
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)


async def convert_image_to_base64(image_path, max_size=(75, 75)):
    """
    Convert an image to a Base64-encoded string.

    This function takes an image file located at `image_path`,
    resizes it to fit within the specified `max_size` (width, height)
    while maintaining the aspect ratio, and encodes it in Base64.

    Args:
        image_path (str): The path to the image file to be converted.
        max_size (tuple): A tuple representing the maximum width and
                          height for the thumbnail (default is (75, 75)).

    Returns:
        str: A Base64-encoded string representing the image,
              prefixed with a data URI scheme, or None if the image
              could not be processed.
    """
    if not os.path.exists(image_path):
        logging.info(f"Image {image_path} not found.")
        return None
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return f"data:image/jpg;base64,{base64_image}"
    except Exception as e:
        logging.error(f"Error converting image to Base64: {e}")
        return None
