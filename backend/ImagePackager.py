from PIL import Image
from io import BytesIO
from base64 import b64encode


def encode_base64(img):
    """
    Encodes an image as a base64 string.

    Parameters:
        img (numpy.ndarray): The image to encode.

    Returns:
        str: The image represented as base64 characters.
    """

    # Load numpy array into Pillow image
    img = Image.fromarray(img)

    # Save raw image data using jpeg format
    binary_buffer = BytesIO()
    img.save(binary_buffer, format='jpeg')

    # Encode binary data as base64 string
    encoded = b64encode(binary_buffer.getvalue())
    human_readable = encoded.decode('utf-8')

    return human_readable

