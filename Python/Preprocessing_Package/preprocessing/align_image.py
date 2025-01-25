import cv2 as cv
import numpy as np
from pathlib import Path

BCFilePath = 'bc/'
BCFileName = "BCE-TEMPLATE.jpg"

CTRFilePath = 'ctr/'
CTRFileName = "CTR-TEMPLATE.jpg"

'''
Function Brief: Aligns an input BCE image to a predefined BCE template image based on feature matching. 
                It detects keypoints in both images, matches them, and computes a homography matrix 
                to transform the input image, making it align with the template. The aligned image 
                is then returned.

Parameters:
    image (numpy.ndarray): The source image to be aligned to the template.

Returns:
    aligned_image (numpy.ndarray): The aligned version of the input image, transformed to match the layout of the template image.
'''
def BCAlignImage(image):
    # Load the image
    template = cv.imread(Path(__file__).parent / BCFilePath / BCFileName)

    # Detect ORB features and compute descriptors.
    orb = cv.ORB_create()

    template_gray = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Find keypoints and descriptors with ORB for both images
    keypoints1, descriptors1 = orb.detectAndCompute(template_gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(image_gray, None)

    # Match descriptors using BFMatcher
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    # Select only the top matches
    num_matches = 50
    matches = matches[:num_matches]

    # Draw matches for visualization (optional)
    matched_image = cv.drawMatches(template, keypoints1, image, keypoints2, matches, None, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    # Get matched keypoints for homography
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Compute Homography matrix
    M, mask = cv.findHomography(dst_pts, src_pts, cv.RANSAC, 5.0)

    # Warp output_image to align with template_image
    h, w = template.shape[:2]
    aligned_image = cv.warpPerspective(image, M, (w, h))

    return aligned_image

'''
Function Brief: Aligns an input CTR image to a predefined CTR template image based on feature matching. 
                It detects keypoints in both images, matches them, and computes a homography matrix 
                to transform the input image, making it align with the template. The aligned image 
                is then returned.

Parameters:
    image (numpy.ndarray): The source image to be aligned to the template.

Returns:
    aligned_image (numpy.ndarray): The aligned version of the input image, transformed to match the layout of the template image.
'''
def CTRAlignImage(image):
    # Load the image
    template = cv.imread(Path(__file__).parent / CTRFilePath / CTRFileName)

    # Detect ORB features and compute descriptors.
    orb = cv.ORB_create()

    template_gray = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Find keypoints and descriptors with ORB for both images
    keypoints1, descriptors1 = orb.detectAndCompute(template_gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(image_gray, None)

    # Match descriptors using BFMatcher
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    # Select only the top matches
    num_matches = 50
    matches = matches[:num_matches]

    # Draw matches for visualization (optional)
    matched_image = cv.drawMatches(template, keypoints1, image, keypoints2, matches, None, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    # Get matched keypoints for homography
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Compute Homography matrix
    M, mask = cv.findHomography(dst_pts, src_pts, cv.RANSAC, 5.0)

    # Warp output_image to align with template_image
    h, w = image.shape[:2]
    aligned_image = cv.warpPerspective(image, M, (w, h))

    return aligned_image
