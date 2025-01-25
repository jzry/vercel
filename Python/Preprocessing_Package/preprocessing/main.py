'''
Running "python3 main.py" will generate a folder of images that is structured in the same format
as the dictionary below for 5 rider columns. Each key holds the scorefield category and each value
holds the (X,Y,width,height) of the box cutout from the original image.

This is the main program to preprocess an image for the OCR.
This program should return a dictionary that is structured in the following way:

"Rider1": {
        "Rider#": (456, 399, 149, 43),
        "recovery": (448, 642, 149, 43),  # (x, y, width, height)
        "hydration": (448, 690, 149, 43),
        "lesions": (448, 736, 149, 43),
        "soundness": (448, 828, 149, 43),
        "qual_movement": (448, 882, 149, 43),
        "rider_time": (403, 1204, 149, 43),
        "rider_weight": (403, 1622, 149, 43)
    },

To access an image, you would do:

# Save a cutout of the scorefield in the same directory.
cv2.imwrite("example.jpg", extracted_fields["Rider1"]["recovery"])

# Remove the horizontal lines of the cutout.
img = horizontal_remover.remove_horizontal_lines("example.jpg")

The end of the program should have a dictionary that is identical to the
intermediary, but it is cleaned of horizontal lines.
'''

# import cv2
# from scoresheet import Paper_Extraction # used to extract paper from original.
# from preprocessing import absolute_scorefields
from preprocessing import scorefields
# import horizontal_remover
from pathlib import Path
# from check_extension import checkExtension

filePath = 'bc'
fileName = "BC-black-1.jpg"
full_path = Path(filePath) / fileName

# Check and convert image extension if necessary
# image_path = checkExtension(str(full_path))

###################################################################
# FUNCTION TO EXTRACT AND WARP PAPER USED ONLY FOR TESTING BECAUSE
# BCSegments and CTRSegments already calls this function inside it.
###################################################################

# with open(Path(filePath) / fileName, 'rb') as image_file:

#     buffer = image_file.read()
#     extracted_paper = Paper_Extraction(buffer)

####################################
# CREATE THE DICTIONARY FOR THE BCE.
####################################

with open(full_path, 'rb') as image_file:

    buffer = image_file.read()
    # absolute
    # extracted_fields = absolute_scorefields.BCSegments(buffer)

    # aligned and relative
    extracted_fields = scorefields.BCSegments(buffer)


####################################
# CREATE THE DICTIONARY FOR THE CTR.
####################################

# with open(Path(filePath) / fileName, 'rb') as image_file:

#     buffer = image_file.read()
#     extracted_fields = scorefields.CTRSegments(buffer)


######################################################################################
# EXTRACT IMAGES FROM DICTIONARY AND REMOVE HORIZONTAL NOISE TEST ON A SINGLE SEGMENT.
# THIS IS JUST USED FOR TESTING. IGNORE THIS.
######################################################################################

# # Create an example file name to output to.
# fileSegmentName = "example_segment.jpg"

# # Extract a single segment from the dictionary and write it to the example file.
# cv2.imwrite(fileSegmentName, extracted_fields["Rider4"]["lesions"])

# # Remove the horizontal lines from the single field segment.
# segment_image = horizontal_remover.remove_horizontal_lines(fileSegmentName)

# cv2.imwrite("segment_output.jpg", segment_image)
