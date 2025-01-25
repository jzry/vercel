# Imports
import cv2 as cv
import numpy as np
from .check_extension import check_extension

"""
Function Brief: Extract and warp a score sheet from an input image by detecting
the largest quadrilateral contour and applying a perspective transformation.
Parameters:
    BC_scoresheet (str): The file path of the input image containing the score sheet.
Returns:
    warped_img (numpy.ndarray): The resulting image of the extracted and
    warped score sheet with sharp borders.
"""
def Paper_Extraction(BC_scoresheet):

    fileOutPath = "output/"
    output_filename = "output_extraction.jpg"

    original_img = check_extension(BC_scoresheet)
    if original_img is None:
        print(f"Cannot read image file: {BC_scoresheet}")
        return -1

    # Resize image for faster processing, maintaining aspect ratio
    max_dimension = 1000
    scale = min(max_dimension / original_img.shape[1], max_dimension / original_img.shape[0])
    resized_image = cv.resize(original_img, (0, 0), fx=scale, fy=scale)

    # Convert to grayscale and blur
    gray = cv.cvtColor(resized_image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)

    # Edge detection using Canny
    edged = cv.Canny(blurred, 75, 200)

    # Morphological operations to close gaps
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
    closed = cv.morphologyEx(edged, cv.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv.findContours(closed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Sort contours by area, largest first
    contours = sorted(contours, key=cv.contourArea, reverse=True)

    # Find the largest quadrilateral contour
    document_contour = None
    for contour in contours:
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.02 * peri, True)

        if len(approx) == 4 and cv.isContourConvex(approx):
            area = cv.contourArea(approx)
            if area > 10000:  # Adjust the minimum area threshold as needed
                document_contour = approx
                break

    if document_contour is None:
        print("Error: Document contour not found")
        return -1

    # Map the points to the original image size
    inverse_scale = 1.0 / scale
    document_contour = np.array([np.array([int(pt[0][0] * inverse_scale), int(pt[0][1] * inverse_scale)]) for pt in document_contour])

    # Reorder points: [top-left, top-right, bottom-right, bottom-left]
    def reorder_points(points):
        rect = np.zeros((4, 2), dtype="float32")
        s = points.sum(axis=1)
        diff = np.diff(points, axis=1)

        rect[0] = points[np.argmin(s)]
        rect[2] = points[np.argmax(s)]
        rect[1] = points[np.argmin(diff)]
        rect[3] = points[np.argmax(diff)]

        return rect

    document_contour = reorder_points(document_contour)

    # Compute the width and height of the new image
    width_a = np.linalg.norm(document_contour[2] - document_contour[3])
    width_b = np.linalg.norm(document_contour[1] - document_contour[0])
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(document_contour[1] - document_contour[2])
    height_b = np.linalg.norm(document_contour[0] - document_contour[3])
    max_height = max(int(height_a), int(height_b))

    # Destination points
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    # Perspective transform
    M = cv.getPerspectiveTransform(document_contour, dst)
    warped = cv.warpPerspective(original_img, M, (max_width, max_height))

    # Convert to grayscale and apply adaptive threshold for mask
    # warped_gray = cv.cvtColor(warped, cv.COLOR_BGR2GRAY)
    # mask = cv.adaptiveThreshold(warped_gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                # cv.THRESH_BINARY, 15, 15)

    # Apply mask to each channel of the original warped image to retain color
    # scanned = cv.bitwise_and(warped, warped, mask=mask)

    # Save the output image
    if not cv.imwrite(output_filename, warped):
        print(f"Error: Could not save output image: {fileOutPath + output_filename}")
        return -1

    print(f"Success: Processing complete. Output saved to {fileOutPath + output_filename}!")

    return warped
