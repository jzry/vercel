-------------------------
# Image Processing Test #
-------------------------

---------------------
# About and Purpose #
---------------------

This directory contains code for detecting the corners of scoresheets in images, processing them to ensure each is transformed into a standardized, flat rectangle. This correction prevents the images from appearing distorted, angled, or skewed and results in a clear presentation with black backgrounds.

The purpose of this image preprocessor is to support Optical Character Recognition (OCR), which works by reading characters individually. In this project, the primary focus is on extracting numerical values from designated score boxes on the scoresheet for automated score calculations. The preprocessor enables the segmentor to focus on specific coordinates to extract fields with handwritten numbers. Once segmented, these fields are primed for OCR, allowing for seamless score computation based on extracted values.

---------------------
# Code Descriptions #
---------------------

# scoresheet.py
The scripts are designed to extract and standardize a specific type of scoresheet from an image by detecting its corners and applying a perspective transformation to ensure the sheet appears flat and rectangular. It processes the image by converting it to grayscale, applying Gaussian blur, and adaptive thresholding, followed by detecting the largest quadrilateral contour. The script then sorts the corner points in clockwise order to resize and warp the image for a clear, sharp output. This prepares the image for further processing, such as segmentation or OCR.

# absolute_scorefields.py
absolute_scorefields.py provides two main functions, BCSegments() and CTRSegments(), which enable targeted extraction of score fields from specific regions of a scoresheet image. These functions support OCR processing by allowing the identification of fields for different score categories: BC and CTR. Each segment is visually marked, saved, and stored in a dictionary, preparing them for further processing and score calculation.

- BCSegments(): Extracts predefined fields for BC score sections from the scoresheet image.
Detects and marks each field in the BC section, displays each segment with green rectangles, and saves each marked segment in a dictionary.

- CTRSegments(): Similar to BCSegments(), this function targets CTR score sections.
It extracts each predefined CTR score field, displays, marks, and saves the fields for efficient OCR integration.
Both functions are designed to handle images with consistent scoresheet layouts, ensuring that extracted fields align correctly with OCR requirements

# scorefields.py
scorefield.py provides two main functions, BCSegments() and CTRSpecSegments(), which enable targeted extraction of score fields from specific regions of a scoresheet image. This script first aligns the input scoresheet image to a template image, ensuring consistent layout and positioning. Once aligned, it extracts and marks fields for different score categories: BC and CTR, scaling the coordinates relative to the dimensions of the extracted image.

- BCSegments(): Extracts predefined fields for BC score sections from the aligned scoresheet image. After aligning the input image to the template, it calculates relative coordinates based on the scaled dimensions, ensuring that each field is accurately located. Each field in the BC section is marked with green rectangles, displayed, and saved in a dictionary, making it ready for OCR processing.

- CTRSpecSegments(): Similar to BCSegments(), this function targets CTR score sections. It aligns the image, calculates relative coordinates for each CTR field, marks the fields with rectangles, and saves them for efficient OCR integration.

Both functions are designed to work with consistently structured scoresheet layouts, using relative coordinates to improve adaptability to varying image sizes. This approach ensures that the extracted fields are correctly aligned and ready for OCR requirements, even if the image dimensions vary.

# align_image.py
align_image.py provides functions to align input images of specific score categories (BCE and CTR) to their respective template images, ensuring consistency in layout for further processing. The alignment is achieved through feature matching, enabling accurate placement of fields for OCR and other analyses.

- BCAlignImage(image): Aligns an input BCE scoresheet image with a predefined BCE template. The function utilizes ORB (Oriented FAST and Rotated BRIEF) to detect and match key features between the input and template images. Based on the matched features, it calculates a homography matrix, transforming the input image to match the template layout. The aligned image is returned for further processing.

- CTRSpecAlignImage(image): Similarly aligns an input CTR scoresheet image with a CTR template. Using the same feature-matching technique, it finds corresponding points between the input and template images, applies a homography transformation, and produces an aligned image consistent with the CTR template structure.

Each function is designed to handle images with consistent layouts, making them suitable for precise field extraction and OCR operations in a controlled environment. The template-based alignment ensures that the resulting images are uniform, improving the accuracy of subsequent data extraction tasks.

# check_extension.py
check_extension.py provides a utility function that checks an image file's extension and converts unsupported formats to .jpg to maintain compatibility.

--------------
# How to use #
--------------

- Ensure that all dependencies (OpenCV, Numpy, Python3, etc.) are installed, it is useful to make a virtual environment (venv) in the directory of the code that you're testing so that you can delete these installations once you're done using them. Refer to: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments for instructions on setting up a virtual environment to test out. Make sure to delete the .venv before pushing code again because we don't want to upload .venv to the repo.

- main.py is the file that you will use to extract the scoresheet from an image and to simultaneously extract the segments from the warped image. In main.py, "fileName" is the file that you want to extract the information out of, "filePath" is the path of the file location.

- To extract the file and segment out the scorecards, do: ```python3 main.py```.