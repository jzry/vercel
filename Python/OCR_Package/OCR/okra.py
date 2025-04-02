import numpy as np
import cv2
from enum import IntEnum
import requests
import json

from .exceptions import *

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_ENABLED = True
except ImportError:
    MATPLOTLIB_ENABLED = False


class DigitGetter:
    """
    A basic OCR class that only recognizes numbers.

    Attributes:
        debug_images (bool): Output the input image after the preprocessing
                             stage (default=False).
        column_skip (int): The number of image columns to be skipped each loop
                           of the scan (default=2).
        fraction_padding (float): The minimum fractional percentage of the
                                  segmented image's height or width that
                                  should be padding (default=0.2).
        find_decimal_points (bool): Determines whether or not decimal points
                                    will appear in the output (default=True).
        find_minus_signs (bool): Determines whether or not minus signs will
                                 appear in the output (default=False).
        blank_threshold (int): The max difference between the lightest and
                               darkest pixels in an image for it to be
                               considered a blank segment (default=120).
        use_width_as_reference (bool): Use the image width instead of height
                                       as a reference when identifying
                                       handwriting segments (default=False).
        scribble_threshold (float): The percentage of pixels in a segment that
                                    have to be filled-in to be considered a
                                    scribbled out number that should be ignored
                                    (default=80.0).
    """

    def __init__(self, ts=False):
        """Creates a new instance of DigitGetter"""

        self.__debug = not ts

        if self.__debug:

            from .OkraHandler import OkraHandler

            self.__classifier_handle = OkraHandler()
            self.__classifier_handle.initialize()

        self.__tracer = OkraTracer()

        # Set default attributes

        self.debug_images = False
        self.column_skip = 2
        self.fraction_padding = 0.2
        self.find_decimal_points = True
        self.find_minus_signs = False
        self.blank_threshold = 120
        self.use_width_as_reference = False
        self.scribble_threshold = 80.0


    def __preprocess_image(self, img):
        """
        Prepares an image for OCRing.

        Parameters:
            img (numpy.ndarray): The image to process.

        Returns:
            numpy.ndarray: The processed image.
        """

        # Convert to grayscale
        if img.ndim == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # If there is a number in the image, there
        # will be a large difference between the
        # brightest pixel and the darkest pixel
        if (img.max() - img.min() <= self.blank_threshold):
            raise OkraBlankSegmentException

        # Apply a slight blur
        img = cv2.bilateralFilter(img, 5, self.blank_threshold, 20)

        # Apply threshold
        _, img = cv2.threshold(
            img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        # Perform dilation to make digits stand out better
        img = cv2.dilate(img, (3, 3), iterations=1)

        self.__show_debug_image(img, 'Pre-processed Image')

        return img


    def digit_from_image(self, img):
        """
        Extracts a single digit from an image.

        Parameters:
            img (numpy.ndarray): An image containing a single digit.

        Returns:
            (int, float): A tuple with the digit's value and the confidence as
                          a percentage.

        Raises:
            OkraModelError: Failed to run a model.
        """

        try:
            img = self.__preprocess_image(img)

        except OkraBlankSegmentException:
            return (None, None)

        return self.__digit_from_image(img)


    def __digit_from_image(self, img):
        """
        Extracts a single digit from an image (no pre-processing).

        Parameters:
            img (numpy.ndarray): An image containing a single digit.

        Returns:
            (int, float): A tuple with the digit's value and the confidence as
                          a percentage.
        """

        self.__show_debug_image(img, 'Digit')

        body = self.__send_to_model('OkraClassifier', img)

        return (body['Digit'], body['Confidence'])


    def image_to_digits(self, img, expected_digit_count=None):
        """
        Extracts a line of digits from an image.

        Parameters:
            img (numpy.ndarray): An image containing some digits.
            expected_digit_count (int): The number of digits that are expected
                                        to be in the image. This is to help
                                        detect overlapping digits. By default,
                                        this is disabled (Default=None).

        Returns:
            (list(int), list(float)): A tuple with a list of digit values and
                                      a list of confidences as percentages.

        Raises:
            OkraModelError: Failed to run a model.
            TypeError: The expected digit count cannot be zero or negative.
        """

        try:
            img = self.__preprocess_image(img)

        except OkraBlankSegmentException:
            return ([], [])

        # A dictionary to save the state of the scan
        scan_state = {}

        # A list to store all the segments extracted from the image
        segments = []

        # Loop until the scan returns 'None'
        while True:

            digit_pixel = self.__scan_columns(img, scan_state)

            if digit_pixel == None:
                break

            # Get the slice of the image containing the handwriting
            segment = self.__get_segment(
                img,
                digit_pixel,
                scan_state
            )

            # Add this segment to the list
            segments.append(segment)


        # Check for overlapped digits
        if expected_digit_count is not None:
            if expected_digit_count <= 0:
                raise TypeError(
                    f'The expected digit count must be a postive integer. \
                    Received: {expected_digit_count}'
                )

            is_digit = lambda x: x['type'] == SegmentType.DIGIT

            number_of_digits = len(list(filter(is_digit, segments)))

            while number_of_digits < expected_digit_count:

                if not self.__split_digit(segments):
                    break

                number_of_digits += 1


        # The return values
        numbers = []
        confidence = []

        # Process all the segments found earlier
        for segment in segments:

            if segment['type'] == SegmentType.DIGIT:

                self.__process_digit_segment(
                    segment['img'],
                    numbers,
                    confidence
                )

            elif segment['type'] == SegmentType.DECIMAL:

                if self.find_decimal_points:
                    conf = self.__get_decimal_confidence(segment['img'].shape)
                    numbers.append('.')
                    confidence.append(conf)

                self.__show_debug_image(segment['img'], 'Decimal Point')

            elif segment['type'] == SegmentType.MINUS:

                if self.find_minus_signs:
                    conf = self.__get_decimal_confidence(segment['img'].shape)
                    numbers.append('-')
                    confidence.append(100.0 - conf)

                self.__show_debug_image(segment['img'], 'Minus Symbol')

            else:
                self.__show_debug_image(segment['img'], 'Ignored')

        return (numbers, confidence)


    def __scan_columns(self, img, scan_state):
        """
        Scans the columns of an image to find digits.

        Parameters:
            img (numpy.ndarray): An image containing some digits.
            scan_state (dict): A dictionary object to save the state of the
                               scan between calls. This should be {} on the
                               first call.

        Returns:
            (int, int): The coordinates of the first digit pixel encountered.
            None: No digits found.
        """

        if scan_state == {}:

            scan_state['column'] = 0

            scan_state['upper'] = [0]
            scan_state['lower'] = [img.shape[0]]
            scan_state['upper_stop'] = [img.shape[1]]
            scan_state['lower_stop'] = [img.shape[1]]


        # x is the current column
        # y is the current row

        x = scan_state['column']

        while x < img.shape[1]:

            while scan_state['upper_stop'][-1] < x:

                del scan_state['upper'][-1]
                del scan_state['upper_stop'][-1]

            while scan_state['lower_stop'][-1] < x:

                del scan_state['lower'][-1]
                del scan_state['lower_stop'][-1]

            upper = scan_state['upper'][-1]
            lower = scan_state['lower'][-1]

            for y in range(upper, lower):

                # Handwriting will have a non-zero value.
                # The background has a value of 0.
                if img[y, x] != 0:

                    scan_state['column'] = x
                    return (x, y)

            # Move to the next column
            x = x + self.column_skip + 1

        return None


    def __get_segment(self, img, start_pixel, scan_state):
        """
        Segments out a piece of handwriting from an image.

        Parameters:
            img (numpy.ndarray): An image.
            start_pixel (int, int): The coordinate of the starting pixel.
            scan_state (dict): A dictionary object to save the state of the
                               scan between function calls.

        Returns:
            dict: The segment and its type stored in a dictionary:
                  'img' (numpy.ndarray): A slice of img containing handwriting.
                  'type' (SegmentType): The type of handwriting in the segment.
        """

        bounds = Boundary(
            start_pixel[1],
            start_pixel[0],
            start_pixel[1],
            start_pixel[0]
        )

        # Find the actual boundary of the digit.
        # 'bounds' will be updated with the correct values.
        self.__tracer.trace(img, bounds, start_pixel, scan_state)

        # Update the scan state
        if bounds.bottom < img.shape[0] // 2:

            scan_state['upper'].append(bounds.bottom + 1)
            scan_state['upper_stop'].append(bounds.right)

        elif bounds.top > img.shape[0] // 2:

            scan_state['lower'].append(bounds.top)
            scan_state['lower_stop'].append(bounds.right)
            scan_state['column'] += self.column_skip + 1

        else:
            scan_state['column'] = bounds.right + 1


        # Copy the box containing the digit from the image
        segment = bounds.get_slice(img)

        # Determine what we just segmented out of the image
        segment_type = self.__get_segment_type(segment, img.shape)

        return {'img': segment, 'type': segment_type}


    def __get_segment_type(self, segment, img_shape):
        """
        Determines the contents of a segment based on its size and shape.

        Parameters:
            segment (numpy.ndarray): The image segment.
            img_shape (int, int): The shape of the original image.

        Returns:
            SegmentType: The type of the segment.
        """

        height = segment.shape[0]
        width = segment.shape[1]

        if self.use_width_as_reference:

            digit_min_height = img_shape[1] // 5.5
            noise_max_size = img_shape[1] // 21

        else:

            digit_min_height = img_shape[0] // 3
            noise_max_size = img_shape[0] // 7

        # Is this tall enough to be a digit?
        if height >= digit_min_height:

            # This might be a scribbled out digit
            if height < width * 3:

                # Find the percentage of "filled-in" pixels
                fill = 100 * np.count_nonzero(segment) / (width * height)

                if fill > self.scribble_threshold:
                    return SegmentType.NOISE

            # Otherwise, this is just a regular digit
            return SegmentType.DIGIT

        # Is this really small?
        if height < noise_max_size and \
           width < noise_max_size:

            return SegmentType.NOISE

        # Is this flat and long?
        if width >= height * 2:

            return SegmentType.MINUS

        # It's probably a decimal if we reach here
        return SegmentType.DECIMAL


    def __split_digit(self, segments):
        """
        Splits the widest digit segment into halves. Assuming that overlapping-
        digit segments will be wider than normal single digit segments, this
        will seperate the overlapping digits into their own segments.

        Parameters:
            segments (list(dict)): All the segments extracted from the image.

        Returns:
            bool: True if a segment was split and False if no splittable
                  segments are available.
        """

        index_of_widest = None

        for i, segment in enumerate(segments):

            if segment['type'] == SegmentType.DIGIT:

                height, width = segment['img'].shape

                if width >= height:

                    if index_of_widest is not None:

                        widest = segments[index_of_widest]['img'].shape[1]

                        if width > widest:
                            index_of_widest = i

                    else:
                        index_of_widest = i


        if index_of_widest is not None:

            print('OCR Digit-overlap Issue Detected! - Splitting segment')

            segment = segments.pop(index_of_widest)['img']

            half = segment.shape[1] // 2

            left_half = segment[:, :half]
            right_half = segment[:, half:]

            segments.insert(
                index_of_widest,
                {'img': right_half, 'type': SegmentType.DIGIT}
            )

            segments.insert(
                index_of_widest,
                {'img': left_half, 'type': SegmentType.DIGIT}
            )

            return True

        return False


    def __apply_padding(self, img):
        """
        Adds padding around an image. The resulting image will be very close
        to being square in shape.

        Parameters:
            img (numpy.ndarray): The image to pad.

        Returns:
            numpy.ndarray: The padded image.
        """

        fixed_padding = int(max(img.shape) * self.fraction_padding)

        # This will be the size of the image after padding
        largest_dim = max(img.shape) + 2 * fixed_padding

        # This is how much padding will be needed to make the image a square
        dynamic_padding = int((largest_dim - min(img.shape)) / 2)

        dynamic_pad = (dynamic_padding, dynamic_padding)
        fixed_pad = (fixed_padding, fixed_padding)

        # If the y dimension is smaller the x dimension, then use the dynamic
        # pad on the y dimension (add more rows than columns).
        #
        # If the x dimension is smaller the y dimension, then use the dynamic
        # pad on the x dimension (add more columns than rows).
        #
        if (img.shape[0] <= img.shape[1]):
            img = np.pad(img, (dynamic_pad, fixed_pad))
        else:
            img = np.pad(img, (fixed_pad, dynamic_pad))

        return img


    def __process_digit_segment(self, digit_segment, numbers, confidence):
        """
        Applies padding to a digit segment and sends it to the image
        classifier.

        Parameters:
            digit_segment (numpy.ndarray): An image segment containing a digit.
            numbers (list(int)): The list where the image classifier's result
                                 will be placed.
            confidence (list(float)): The list where the image classifier's
                                      confidence will be placed.
        """

        # Prepare the segment
        digit_segment = self.__apply_padding(digit_segment)

        # Classify the digit
        num, conf = self.__digit_from_image(digit_segment)
        numbers.append(num)
        confidence.append(conf)


    def __get_decimal_confidence(self, segment_shape):
        """
        Computes a confidence value for a decimal based on how round it is.

        Parameters:
            segment_shape (int, int): The shape of the image segment
                                      containing the decimal point.

        Returns:
            float: The confidence as a percentage.
        """

        # Divide the smaller dimension by the larger dimension
        ratio = min(segment_shape) / max(segment_shape)

        # The higher the ratio, the higher the confidence.
        # You may want to graph this to see what's going on
        confidence = 1 - (ratio - 1)**2

        return confidence * 100.0


    def __send_to_model(self, model_name, img):
        """
        Sends an image to a machine learning model to be processed.

        Parameters:
            model_name (str): The name of the target model.
            img (numpy.ndarray): The image to send to the model.

        Returns:
            dict: The model's results.

        Raises:
            OkraModelError: Failed to run a model.
        """

        payload = {"data": img.tobytes(), "x": img.shape[1], "y": img.shape[0]}

        if self.__debug:

            if model_name == 'OkraClassifier':

                response = self.__classifier_handle.handle(payload)

            else:
                raise OkraModelError(f'Unkown model: "{model_name}"')

            body = json.loads(response[0])

        else:

            try:
                response = requests.post(
                    f'http://localhost:6060/predictions/{model_name}',
                    data=payload
                )
                body = response.json()

                if response.status_code != 200:
                    raise OkraModelError(
                        f'TorchServe could not process the request: {body}'
                    )

            except requests.exceptions.ConnectionError as e:
                raise OkraModelError(f'Unable to connect to TorchServe: {e}')

        return body


    def __show_debug_image(self, img, title):
        """Helper function to display a matplotlib plot of an image"""

        if self.__debug:
            if self.debug_images:
                if MATPLOTLIB_ENABLED:

                    plt.imshow(img)
                    plt.title(title)
                    plt.show()

                else:
                    print('Warning: matplotlib is not configured')



class OkraTracer:
    """A class that contains the code for tracing handwriting"""

    def __init__(self):

        self.__directions = [
            (0, -1),            # 0 - NORTH
            (1, -1),            # 1 - NORTHEAST
            (1, 0),             # 2 - EAST
            (1, 1),             # 3 - SOUTHEAST
            (0, 1),             # 4 - SOUTH
            (-1, 1),            # 5 - SOUTHWEST
            (-1, 0),            # 6 - WEST
            (-1, -1)            # 7 - NORTHWEST
        ]

        self.__num_directions = len(self.__directions)


    def trace(self, img, bounds, pixel, scan_state):
        """
        An edge tracing algorithm that finds the smallest box that fits a
        piece of handwriting.

        Parameters:
            img (numpy.ndarray): An image.
            bounds (Boundary): An object to store the bounds of the
                               handwriting.
            pixel (int, int): The coordinate of the starting pixel.
            scan_state (dict): A dictionary object to save the state of the
                               scan between function calls.
        """

        # The traversable area within the image
        img_bounds = Boundary(
            scan_state['upper'][-1],
            img.shape[1] - 1,
            scan_state['lower'][-1] - 1,
            0
        )

        # A list to track horizontal movement during the trace
        layers = [0] * img.shape[0]

        start_direction = Direction.NORTH
        current_pixel = pixel

        while True:

            rotation = range(
                start_direction,
                start_direction + self.__num_directions
            )

            for next_direction in rotation:

                next_pixel = self.__move(next_direction, current_pixel)

                if img_bounds.contains(next_pixel):
                    if self.__is_white(next_pixel, img):

                        self.__update_bounds(bounds, next_pixel)
                        self.__update_layers(
                            layers,
                            next_direction,
                            next_pixel
                        )
                        start_direction = self.__get_start_direction(
                            next_direction
                        )
                        current_pixel = next_pixel
                        break

            # Check for complete loop
            if current_pixel == pixel:
                break

        # Before returning, check for the digit-touching-line issue.
        self.__check_for_line_issue(bounds, layers, img.shape)


    def __move(self, direction, current_pixel):
        """
        Determines the pixel coordinate after moving.

        Parameters:
            direction (Direction): The direction relative to the current pixel
                                   to move.
            current_pixel (int, int): The pixel from which to move from.

        Returns:
            (int, int): The coordinate of the pixel moved to.
        """

        move_val = self.__directions[direction % self.__num_directions]
        return (current_pixel[0] + move_val[0], current_pixel[1] + move_val[1])


    def __is_white(self, location, img):
        """
        Returns False if the pixel at the location is black (background).
        Returns True if the pixel at the location is white (handwriting).
        """

        return img[location[1], location[0]] != 0


    def __update_bounds(self, bounds, location):
        """Expands the boundary to contain the latest tracing location"""

        if location[0] > bounds.right:
            bounds.right = location[0]
        elif location[0] < bounds.left:
            bounds.left = location[0]

        if location[1] > bounds.bottom:
            bounds.bottom = location[1]
        elif location[1] < bounds.top:
            bounds.top = location[1]


    def __update_layers(self, layers, direction, pixel):
        """Tracks horizontal movement in each row of the image"""

        direction %= self.__num_directions

        if direction == Direction.EAST or direction == Direction.WEST:
            layers[pixel[1]] += 1


    def __get_start_direction(self, direction):
        """
        After each iteration of the tracing algorithm, the start direction for
        the next iteration must be determined. This direction is chosen based
        on the direction taken to reach the current pixel.

        Parameters:
            direction (Direction): The direction taken to reach the current
                                   pixel.

        Returns:
            Direction: The starting direction for the next iteration of
                       tracing.
        """

        direction %= self.__num_directions

        if direction < Direction.EAST:
            return Direction.WEST

        elif direction < Direction.SOUTH:
            return Direction.NORTH

        elif direction < Direction.WEST:
            return Direction.EAST

        else:
            return Direction.SOUTH


    def __check_for_line_issue(self, bounds, layers, img_shape):
        """
        Checks for the number-touching-line issue and compensates for it. There
        are two indicators of this issue:
            1. The boundary extending from the top half into the bottom half.
            2. A lot of horizontal movement (as indicated by the layers).

        Parameters:
            bounds (Boundary): The boundary that resulted from tracing. This
                               boundary will be adjusted if the issue is found.
            layers (list): The amount of horizontal movement per row that
                           occured during tracing.
            img_shape (int, int): The shape of the image segment.
        """

        half = img_shape[0] // 2
        line_threshold = img_shape[1] // 3

        # Check first condition
        if bounds.top < half and bounds.bottom > half:

            # Check second condition (top half)
            if max(layers[:half]) >= line_threshold:

                print('OCR Line Issue Detected! - Removing line from above')
                self.__adjust_bounds_to_line(
                    bounds,
                    layers,
                    bounds.top,
                    half
                )


            # Check second condition (bottom half)
            elif max(layers[half:]) >= line_threshold:

                print('OCR Line Issue Detected! - Removing line from below')
                self.__adjust_bounds_to_line(
                    bounds,
                    layers,
                    half,
                    bounds.bottom
                )


    def __adjust_bounds_to_line(self, bounds, layers, search_top, search_bottom):
        """
        Adjusts the boundary to cover only the line so the digits attached to
        it can be traced in future iterations.

        Parameters:
            bounds (Boundary): The boundary of the traced line and digits. This
                               boundary will be adjusted to fit the line.
            layers (list): The amount of horizontal movement per row that
                           occured during tracing.
            search_top (int): The top index to use for the line search. Indices
                              above this in the segment will be ingnored.
            search_bottom (int): The bottom index to use for the line search.
                                 Indices below this in the segment will be
                                 ingnored.
        """

        search_range = slice(search_top, search_bottom + 1)

        # The max layer is either the top or bottom of the line.
        # This will be the center index during the search for the other
        # side of the line.
        center_i = np.argmax(layers[search_range]) + search_top

        # If the center index is at the bottom of the boundary, it is
        # obviously the bottom of the line.
        if center_i == search_bottom:

            search_range = slice(search_top, search_bottom)

            high_i = search_top + np.argmax(layers[search_range])

            if layers[high_i] < 15 or center_i - high_i > 4:
                bounds.top = search_bottom - 1

            else:
                bounds.top = high_i

        # Likewise, if the center index is at the boundary top, it is the
        # top of the line.
        elif center_i == search_top:

            search_range = slice(search_top + 1, search_bottom + 1)

            low_i = search_top + 1 + np.argmax(layers[search_range])

            if layers[low_i] < 15 or low_i - center_i > 4:
                bounds.bottom = search_top + 1

            else:
                bounds.bottom = low_i

        # The center index is in the middle of the segment. We don't know
        # if its the top or bottom of the line yet.
        else:

            above_search_range = slice(search_top, center_i)
            below_search_range = slice(center_i + 1, search_bottom + 1)

            high_i = search_top + np.argmax(layers[above_search_range])
            low_i = center_i + 1 + np.argmax(layers[below_search_range])

            # The larger layer is the other side of the line
            if layers[high_i] > layers[low_i]:
                bounds.top = high_i
                bounds.bottom = center_i

            else:
                bounds.top = center_i
                bounds.bottom = low_i



class Boundary:
    """
    A class for storing the location of an image slice.

    Attributes:
        top (int): The index of the top edge.
        right (int): The index of the right edge.
        bottom (int): The index of the bottom edge.
        left (int): The index of the left edge.
    """

    def __init__(self, top, right, bottom, left):
        """Creates a new instance of Boundary"""

        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


    def shape(self):
        return (self.bottom - self.top + 1, self.right - self.left + 1)


    def get_slice(self, img):
        """
        Returns a slice of an image within the boundary.

        Parameters:
            img (numpy.ndarray): An image.

        Returns:
            numpy.ndarray: A slice of img.
        """

        # Adjust the edges if necessary
        self.fit_image(img)

        # Return a slice
        return img[self.top:(self.bottom + 1), self.left:(self.right + 1)]


    def fit_image(self, img):
        """
        Adjusts the boundary to fit within an image.

        Parameters:
            img (numpy.ndarray): An image.
        """

        # Make sure there are no negative edges

        if self.top < 0:
            self.top = 0

        if self.right < 0:
            self.right = 0

        if self.bottom < 0:
            self.bottom = 0

        if self.left < 0:
            self.left = 0

        # Make sure the edges are within the image

        if self.top >= img.shape[0]:
            self.top = img.shape[0] - 1

        if self.right >= img.shape[1]:
            self.right = img.shape[1] - 1

        if self.bottom >= img.shape[0]:
            self.bottom = img.shape[0] - 1

        if self.left >= img.shape[1]:
            self.left = img.shape[1] - 1


    def contains(self, point):
        """
        Checks if a point lies within the boundary.

        Parameters:
            point (int, int): An (x, y) coordinate.

        Returns:
            bool: True if the point is within the boundary and False otherwise.
        """

        x, y = point

        if self.left <= x and x <= self.right:
            if self.top <= y and y <= self.bottom:
                return True

        return False



class SegmentType(IntEnum):
    """
    An enumerated type to differentiate between digits, minus symbols,
    decimals, and noise.

    Values:
        NOISE   = 0 : A few disconnected pixels that should be ignored.
        MINUS   = 1 : A minus symbol that will likely be ignored.
        DECIMAL = 2 : A decimal point.
        DIGIT   = 3 : A digit that needs to be classified.
    """

    NOISE   = 0
    MINUS   = 1
    DECIMAL = 2
    DIGIT   = 3



class Direction(IntEnum):
    """An enumerated type to differentiate between different directions"""

    NORTH     = 0
    NORTHEAST = 1
    EAST      = 2
    SOUTHEAST = 3
    SOUTH     = 4
    SOUTHWEST = 5
    WEST      = 6
    NORTHWEST = 7

