# Imports
import os
import cv2 as cv
import numpy as np
from . import template
from . import scoresheet
from .lime import BCAlignImage, CTRAlignImage
from .check_extension import check_extension

"""
Function Brief: Extracts and marks predefined segments (fields) for each rider section on an image.
                It draws rectangles on each defined field, displaying them and saving each segment in a dictionary.
Parameters:
    image (str): Path to the source image from which segments need to be extracted.

Returns:
    extracted_fields (dict): A dictionary containing the score fields from each rider from the BCE scoresheet.
"""
def BCSegments(image, corner_dict):

    fileOutPath = "output/"
    output_filename = "output_extraction.jpg"

    corner_points = np.array([[pt['x'], pt['y']] for pt in corner_dict], dtype=np.float32)

    # Compute the width and height of the new image
    width_a = np.linalg.norm(corner_points[2] - corner_points[3])
    width_b = np.linalg.norm(corner_points[1] - corner_points[0])
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(corner_points[1] - corner_points[2])
    height_b = np.linalg.norm(corner_points[0] - corner_points[3])
    max_height = max(int(height_a), int(height_b))

    # Destination points
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    # Decode image
    decoded_img = check_extension(image)

    # Perspective transform
    M = cv.getPerspectiveTransform(corner_points, dst)
    warped_img = cv.warpPerspective(decoded_img, M, (max_width, max_height))

    # Save the output image
    if not cv.imwrite(output_filename, warped_img):
        print(f"Error: Could not save output image: {fileOutPath + output_filename}")

    '''Just for the sake of verifing the output
    -------------------------------------------'''
    output_folder='intermediary_fields'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    '''-------------------------------------------'''

    extracted_fields = {}

    # imread() when image is file path
    # extracted_image = cv.imread(image)
    # Gives the extracted image that is warped to fit a rectangle.
    # extracted_image = scoresheet.Paper_Extraction(warped_img)

    # Gives aligned image to the template
    extracted_image = BCAlignImage(warped_img)

    horizontal_scalefactor = 1
    vertical_scalefactor = 1

    # Check if the result is an integer indicating failure
    if isinstance(extracted_image, int) and extracted_image == -1:
        print("Error: Cannot read image file after extraction.")
        return -1
    else:
        # Get, Check and Resize(if needed) dimensions of extracted_image
        height, width = extracted_image.shape[:2]
        horizontal_scalefactor = width / template.BC_WIDTH
        vertical_scalefactor = height / template.BC_HEIGHT

    '''This code is just to verify the output.
    ------------------------------------------------------------------'''
    marked_image = extracted_image.copy()
    '''------------------------------------------------------------------'''

    for rider, fields in template.BC_TEMPLATE_FIELDS.items():
        extracted_fields[rider] = {}

        '''This code is just to verify the output.
        ------------------------------------------------------------------'''
        # Create a subfolder for each rider to organize output
        rider_folder = os.path.join(output_folder, rider)
        if not os.path.exists(rider_folder):
            os.makedirs(rider_folder)
        '''------------------------------------------------------------------'''

        for field_name, (x, y, w, h) in fields.items():

            x = int(np.round(x * horizontal_scalefactor))
            w = int(np.round(w * horizontal_scalefactor))
            y = int(np.round(y * vertical_scalefactor))
            h = int(np.round(h * vertical_scalefactor))

            # We are cropping out field from the extracted image here.
            field_image = extracted_image[y:y + h, x:x + w]

            # We need to pass the field image to the horizontal remover function here
            # so we can set the key to the cleaned up segment field image.
            # field_image is a cropped version of extracted_image, and extracted_image is
            # a cv2 matrix returned from scoresheet.py
            # so we could pass field_image into the horizontal_removal function as a cv2 object.
            # field_image_no_horizontals = horizontal_remover.remove_horizontal_lines(field_image)

            # Compare example.jpg against Rider5 rider_weight since it is the last field in the loop
            # to see if the function is working.
            # cv.imwrite("example.jpg", field_image_no_horizontals)

            '''This code is just to verify the output.
            ------------------------------------------------------------------'''
            # Save each cropped image to the specified folder
            field_path = os.path.join(rider_folder, f"{field_name}.jpg")

            # IF YOU CHANGE field_image_no_horizontals to field_image, you can get all the segments of
            # the original image without the horizontal_remover function edits. I commented it out in case
            # you want to test it out.
            # cv.imwrite(field_path, field_image_no_horizontals)
            cv.imwrite(field_path, field_image)

            # mark the fields on the image
            marked_image = cv.rectangle(marked_image, (x, y), (x + w, y + h), (255, 0, 0), 1)
            '''------------------------------------------------------------------'''

            # Setting the dictionary key to the segmented image.
            extracted_fields[rider][field_name] = field_image

    if cv.imwrite('outfield.jpg', marked_image):
        print("Extraction complete.")

    return extracted_fields

"""
Function Brief: Extracts and marks predefined segments (fields) for a judge scoresheet.
                It draws rectangles on each defined field, displaying them and saving each segment in a dictionary.
Parameters:
    image (str): Path to the source image from which segments need to be extracted.

Returns:
    extracted_fields (dict): A dictionary containing the score fields from the judge scoresheet.
"""
def CTRSegments(image, corner_dict):

    fileOutPath = "output/"
    output_filename = "output_extraction.jpg"

    corner_points = np.array([[pt['x'], pt['y']] for pt in corner_dict], dtype=np.float32)

    # Compute the width and height of the new image
    width_a = np.linalg.norm(corner_points[2] - corner_points[3])
    width_b = np.linalg.norm(corner_points[1] - corner_points[0])
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(corner_points[1] - corner_points[2])
    height_b = np.linalg.norm(corner_points[0] - corner_points[3])
    max_height = max(int(height_a), int(height_b))

    # Destination points
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    # Decode image
    decoded_img = check_extension(image)

    # Perspective transform
    M = cv.getPerspectiveTransform(corner_points, dst)
    warped_img = cv.warpPerspective(decoded_img, M, (max_width, max_height))

    # Save the output image
    if not cv.imwrite(output_filename, warped_img):
        print(f"Error: Could not save output image: {fileOutPath + output_filename}")

    '''Just for the sake of verifying the output
    -------------------------------------------'''
    output_folder='extracted_fields'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    '''-------------------------------------------'''

    extracted_fields = {}

    # imread() when image is file path
    # extracted_image = cv.imread(image)
    # extracted_image = scoresheet.Paper_Extraction(image)

    # Gives aligned image to the template
    extracted_image = CTRAlignImage(warped_img)


    horizontal_scalefactor = 1
    vertical_scalefactor = 1

    # # Check if the result is an integer indicating failure
    if isinstance(extracted_image, int) and extracted_image == -1:
        print("Error: Cannot read image file after extraction.")
        return -1
    else:
        # Get, Check and Resize(if needed) dimensions of extracted_image
        height, width = extracted_image.shape[:2]
        horizontal_scalefactor = width / template.CTR_WIDTH
        vertical_scalefactor = height / template.CTR_HEIGHT

    '''Just for the sake of verfiy the output
    ------------------------------------------------------------------'''
    marked_image = extracted_image.copy()
    '''------------------------------------------------------------------'''

    for field_name, (x, y, w, h) in template.CTR_TEMPLATE_FIELDS.items():

        x = int(np.round(x * horizontal_scalefactor))
        w = int(np.round(w * horizontal_scalefactor))
        y = int(np.round(y * vertical_scalefactor))
        h = int(np.round(h * vertical_scalefactor))

        # Extract each field from the image
        field_image = extracted_image[y:y + h, x:x + w]

        '''Just for the sake of verfiy the output
        ------------------------------------------------------------------'''
        # Save each cropped image to the specified folder
        field_path = os.path.join(output_folder, f"{field_name}.jpg")
        cv.imwrite(field_path, field_image)
        '''------------------------------------------------------------------'''

        # Mark the fields on the copy of the image for verification
        marked_image = cv.rectangle(marked_image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Store the extracted field image in the dictionary
        extracted_fields[field_name] = field_image


    if cv.imwrite('outfield.jpg', marked_image):
        print("Extraction complete. Output saved.")

    return extracted_fields

# BC_score_fields = BCSegments("bc/BC-1.jpg")
