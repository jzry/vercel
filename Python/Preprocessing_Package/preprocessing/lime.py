import cv2 as cv
import numpy as np

from . import template
from .exceptions import PreprocessingAlignmentError


def BCAlignImage(image):
    """
    Aligns an extracted BC page with the template page.

    Parameters:
        image (numpy.ndarray): The image to align.

    Returns:
        numpy.ndarray: The aligned image.
    """

    try:

        # Locate the template corners
        scanned_corners = __find_corners(image)

    except PreprocessingAlignmentError as e:

        print('Warning: preprocessing.lime failed to align the image;', e)

        # If we can't find the corners, return the original image
        return image

    # Compute the scale between this image and the template image
    x_scale = image.shape[1] / template.BC_WIDTH
    y_scale = image.shape[0] / template.BC_HEIGHT

    # Calculate the the locations of the template corners at the scale of this
    # image
    template_corners = np.float32([
        [486  * x_scale, 263  * y_scale],
        [1716 * x_scale, 263  * y_scale],
        [486  * x_scale, 1587 * y_scale],
        [1716 * x_scale, 1587 * y_scale]
    ])

    # __demo_image(
    #     image,
    #     [scanned_corners, template_corners],
    #     ['r', 'g'],
    #     'Before'
    # )

    # Apply a perspective transformation to align the image
    M = cv.getPerspectiveTransform(scanned_corners, template_corners)
    image = cv.warpPerspective(image, M, (image.shape[1], image.shape[0]))

    # __demo_image(
    #     image,
    #     [scanned_corners, template_corners],
    #     ['r', 'g'],
    #     'After'
    # )
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    return image


def CTRAlignImage(image):
    """
    Aligns an extracted CTR page with the template page.

    Parameters:
        image (numpy.ndarray): The image to align.

    Returns:
        numpy.ndarray: The aligned image.
    """

    try:

        # Locate the template corners
        scanned_corners = __find_corners(image, ctr_mode=True)

    except PreprocessingAlignmentError as e:

        print('Warning: preprocessing.lime failed to align the image;', e)

        # If we can't find the corners, return the original image
        return image

    # Compute the scale between this image and the template image
    x_scale = image.shape[1] / template.CTR_WIDTH
    y_scale = image.shape[0] / template.CTR_HEIGHT

    # Calculate the the locations of the template corners at the scale of this
    # image
    template_corners = np.float32([
        [118  * x_scale, 615  * y_scale],
        [1580 * x_scale, 614  * y_scale],
        [118  * x_scale, 2080 * y_scale],
        [1581 * x_scale, 2080 * y_scale]
    ])

    # __demo_image(
    #     image,
    #     [scanned_corners, template_corners],
    #     ['r', 'g'],
    #     'Before'
    # )

    # Apply a perspective transformation to align the image
    M = cv.getPerspectiveTransform(scanned_corners, template_corners)
    image = cv.warpPerspective(image, M, (image.shape[1], image.shape[0]))

    # __demo_image(
    #     image,
    #     [scanned_corners, template_corners],
    #     ['r', 'g'],
    #     'After'
    # )
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    return image


def __find_corners(image, ctr_mode=False):
    """
    Locates the template corners of a scoresheet. These are the four points
    that lie on the ends of the outer two vertical lines that are in the page.

    Parameters:
        image (numpy.ndarray): The image of the page.
        ctr_mode (bool): Enables special behaviours specific to the CTR page.

    Returns:
        numpy.ndarray: An array with shape (4, 2) containing the (x, y)
                       coordinates of the four corners.

    Raises:
        PreprocessingAlignmentError: Unable to locate the corners.
   """

    # Prepare image
    processed_image = __preprocess(image)

    # Find the four lines
    line_points = __find_vertical_lines(processed_image, ctr_mode)

    # Trace up and down the outer two lines
    TL = __follow_line(processed_image, line_points[0], step=-1)
    BL = __follow_line(processed_image, line_points[0], step= 1)
    TR = __follow_line(processed_image, line_points[3], step=-1)
    BR = __follow_line(processed_image, line_points[3], step= 1)

    # Place the corner coordinates in a numpy array
    scanned_corners = np.float32([TL, TR, BL, BR])

    return scanned_corners


def __preprocess(image):
    """
    Performs operations on the input image to prepare it for template corner
    detection.

    Parameters:
        image (numpy.ndarray): The color input image.

    Returns:
        numpy.ndarray: A black and white, thresholded version of the input
                       image.
    """

    # Create grayscale version of the image
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Apply a threshold. It's not important if handwriting and text quality is
    # reduced. Just as long as the four vertical line are clearly visible.
    thresh_image = cv.adaptiveThreshold(
        gray_image,
        255,
        cv.ADAPTIVE_THRESH_MEAN_C,
        cv.THRESH_BINARY,
        15,
        10
    )

    # __demo_image(
    #     thresh_image,
    #     [],
    #     [],
    #     'gray'
    # )
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    return thresh_image



def __find_vertical_lines(image, ctr_mode=False):
    """
    Finds the coordinates of four vertical lines in a scoresheet image.

    Parameters:
        image (numpy.ndarray): The thresholded image of the page.
        ctr_mode (bool): Enables special behaviours specific to the CTR page.

    Returns:
        numpy.ndarray: An array with shape (4, 2) containing four (x, y)
                       coordinates that lie on the four lines.

    Raises:
        PreprocessingAlignmentError: The line points could not be found.
    """

    # The index of the middle row
    middle = image.shape[0] * 5 // 9

    # Use margins on the left and right edges to avoid noise
    if ctr_mode:
        percent_margin = 0.03

    else:
        percent_margin = 0.10

    margin = int(image.shape[1] * percent_margin)
    columns = slice(margin, -margin)

    # The starting row
    row = image[middle, columns]

    for next_row_i in range(middle + 1, image.shape[0]):

        row = np.logical_or(row, image[next_row_i, columns])
        x_points = __get_points_from_row_slice(row)

        if len(x_points) == 4:
            # Found them!
            break

        elif len(x_points) < 4:
            raise PreprocessingAlignmentError('Fewer than 4 points detected')

    if len(x_points) > 4:
        raise PreprocessingAlignmentError('More than 4 points detected')

    if not ctr_mode:
        # If these points lie on the four lines, they will be spaced equally
        __validate_point_spacing(x_points, tolerance=0.05)

    line_points = np.array([
        [margin + x_points[0], middle],
        [margin + x_points[1], middle],
        [margin + x_points[2], middle],
        [margin + x_points[3], middle]
    ])

    return line_points


def __get_points_from_row_slice(img_row):
    """
    Returns the x-coordinates of lines passing through an image row slice.

    Parameters:
        img_row (numpy.ndarray): A row slice from the image being processed.

    Returns:
        list: The x-coordinates of the lines.
    """

    x_points = []
    line_flag = False

    for i in range(len(img_row)):

        if line_flag:

            # A value of True indicates a background pixel
            if img_row[i]:
                line_flag = False

        else:

            # A value of False indicates a line pixel
            if not img_row[i]:
                x_points.append(i)
                line_flag = True

    return x_points


def __validate_point_spacing(x_points, tolerance):
    """
    Checks if four points really lie on the four vertical lines of a BCE
    scoresheet. If they are on the lines, they will be equally spaced apart.

    Parameters:
        x_points (list(int)): The x-coordinates being validated.
        tolerance (float): The max percent difference in spacing that will
                           still be considered equal.

    Raises:
        PreprocessingAlignmentError: The points are not valid.
    """

    gaps = []

    for i in range(1, len(x_points)):
        gaps.append(x_points[i] - x_points[i - 1])

    for i in range(1, len(gaps)):

        allowed_difference = gaps[i] * tolerance

        if gaps[i - 1] > gaps[i] + allowed_difference:
            raise PreprocessingAlignmentError('Point spacing is inconsistent')

        if gaps[i - 1] < gaps[i] - allowed_difference:
            raise PreprocessingAlignmentError('Point spacing is inconsistent')


def __follow_line(image, start_pixel, step):
    """
    Finds the (x, y) coordinate of the end of a line.

    Parameters:
        image (numpy.ndarray): The thresholded image.
        start_pixel ((int, int)): The location in the image to start. The pixel
                                  at this location should lie on a line.
        step (int): The change in the y-coordinate after every iteration. This
                    should be either +1 or -1.

    Returns:
        list: The (x, y) coordinate of the line's end point.
    """

    x, y = start_pixel

    while True:

        next_y = y + step

        if next_y < 0 or next_y >= image.shape[0]:
            return [x, y]

        slant_left = __is_line(image, x - 1, next_y)
        straight = __is_line(image, x, next_y)
        slant_right = __is_line(image, x + 1, next_y)

        if not slant_left and not slant_right and not straight:
            # This is the end of the line
            return [x, y]

        if not slant_left and slant_right:
            x += 1

        if not slant_right and slant_left:
            x -= 1

        if not straight and slant_right:
            x += 1

        if not straight and slant_left:
            x -= 1

        y = next_y


def __is_line(image, x, y):
    """
    Checks if a pixel in an image is part of a line or not.

    Parameters:
        image (numpy.ndarray): The thresholded image.
        x (int): The x-coordinate of the pixel to check.
        y (int): The y-coordinate of the pixel to check.

    Returns:
        bool: True if the pixel lies on a line and False otherwise.
    """

    if x < 0 or x >= image.shape[1]:
        return False

    return image[y, x] == 0


def __demo_image(image, points, colors, name):
    """
    Shows the image alignment for debugging or demonstration.

    Parameters:
        image (numpy.ndarray): The image to display.
        points (list(numpy.ndarry)): A list of coordinate sets.
        colors (list(str)): The color to use for each coordinate set.
        name (str): The window name to use.
    """

    #
    # If the image displayed is too large or too small, change this scale
    # factor to the percentage that best works for your screen.
    #
    scale_factor = 0.3

    if len(points) != len(colors):
        raise Exception("There should be exactly one color per set of points")

    demo_img = image.copy()

    for i, point_set in enumerate(points):

        if colors[i] == 'r':
            color = (0, 0, 255)

        elif colors[i] == 'g':
            color = (0, 255, 0)

        elif colors[i] == 'b':
            color = (255, 0, 0)

        else:
            color = (0, 0, 0)

        for point in point_set:
            cv.circle(
                demo_img,
                (int(point[0]), int(point[1])),
                radius=10,
                color=color,
                thickness=-1
            )

    resized = cv.resize(
        demo_img,
        (0, 0),
        fx=scale_factor,
        fy=scale_factor,
        interpolation=cv.INTER_AREA
    )
    cv.imshow(name, resized)

