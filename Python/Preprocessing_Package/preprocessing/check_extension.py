import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
from PIL.Image import DecompressionBombError
import filetype
from io import BytesIO
from .exceptions import *

try:
    from pdf2image import convert_from_bytes
    PDF_ENABLED = True

except ImportError:
    PDF_ENABLED = False

try:
    from pillow_heif import register_heif_opener
    # Register HEIF opener with Pillow
    register_heif_opener()
    HEIC_ENABLED = True

except ImportError:
    HEIC_ENABLED = False


def check_extension(raw_image):
    """
    Function Brief: Checks the file extension of an image file and loads the
                    pixel data into a numpy array. The allowed types are
                    (jpg, png, bmp, tif, heic, and pdf)

    Parameters:
        raw_image (bytes): A buffer holding the raw byte data of an image.

    Returns:
        np.ndarray : The pixel data loaded into a numpy array.

    Raises:
        PreprocessingExtensionError : Invalid or unknown file type.
        PreprocessingImageError : Image is corrupted or incompatable.
        NotImplementedError : HEIC or PDF loading not configured.
    """

    allowed_extensions = {'jpg', 'png', 'bmp', 'tif', 'pdf', 'heic'}

    extension = filetype.guess_extension(raw_image)

    # Check if the file extension was found
    if extension is None:
        raise PreprocessingExtensionError('Unable to determine file type')

    # Check if the file extension is in the allowed list
    if extension not in allowed_extensions:
        raise PreprocessingExtensionError('File type is not supported')

    # Make sure the heif package is available for heic images
    if extension == 'heic' and not HEIC_ENABLED:
        raise NotImplementedError('HEIC loading not configured')

    # PDF files are a special case
    if extension == 'pdf':

        if PDF_ENABLED:

            # Convert the PDF to image
            images = convert_from_bytes(raw_image)

            if len(images) > 1:
                print(f'Warning: Only keeping first page of pdf. Ignoring {len(images) - 1} pages')

            return np.array(images[0], dtype=np.uint8)

        else:
             raise NotImplementedError('PDF loading not configured')

    else:

        try:
            # Decode the image with Pillow and return a numpy array
            image = Image.open(BytesIO(raw_image))

        except DecompressionBombError:
            raise PreprocessingImageError('Cannot open due to Decompression Bomb security concerns')

        except UnidentifiedImageError:
            raise PreprocessingImageError('Image file is corrupt')

        except:
            raise PreprocessingImageError('An unknown error occured while opening the image')

        ImageOps.exif_transpose(image, in_place=True)
        buffer = np.array(image, dtype=np.uint8)

        if buffer.shape[2] == 4:
            return buffer[:, :, :3]

        else:
            return buffer

