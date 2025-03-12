import unittest
import numpy as np

import OCR.okra as okra


class DigitGetterTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dg = okra.DigitGetter()


    def test_column_scan(self):

        # Don't use column skipping for this test
        self.dg.column_skip = 0

        img = np.array([
            [1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0]
        ], np.uint8)

        scan_state = {}

        first_pixel = self.dg._DigitGetter__scan_columns(img, scan_state)
        self.assertEqual(first_pixel, (0, 0), 'Did not find the first pixel')

        scan_state['column'] = 1

        second_pixel = self.dg._DigitGetter__scan_columns(img, scan_state)
        self.assertEqual(second_pixel, (3, 3), 'Did not find the second pixel')

        scan_state['column'] = 4

        third_pixel = self.dg._DigitGetter__scan_columns(img, scan_state)
        self.assertIsNone(third_pixel, 'Should return None for no pixels found')


    def test_tracing(self):

        img = np.array([
            [0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0],
            [1, 0, 1, 0, 1]
        ], np.uint8)

        scan_state = {
            'upper': [0],
            'lower': [img.shape[0]]
        }

        boundary = okra.Boundary(2, 2, 2, 2)

        self.dg._DigitGetter__tracer.trace(img, boundary, (2, 2), scan_state)

        self.assertEqual(boundary.top, 1, 'Top boundary incorrect')
        self.assertEqual(boundary.bottom, 4, 'Bottom boundary incorrect')
        self.assertEqual(boundary.left, 1, 'Left boundary incorrect')
        self.assertEqual(boundary.right, 4, 'Right boundary incorrect')


    def test_trace_digit_with_lines(self):

        img = np.array([
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
        ], np.uint8)

        # Top line check

        scan_state = {
            'upper': [0],
            'lower': [img.shape[0]]
        }

        boundary = okra.Boundary(2, 2, 2, 2)

        self.dg._DigitGetter__tracer.trace(img, boundary, (2, 2), scan_state)

        self.assertEqual(boundary.top, 0, 'Top line failure; top boundary incorrect')
        self.assertEqual(boundary.bottom, 1, 'Top line failure; bottom boundary incorrect')
        self.assertEqual(boundary.left, 1, 'Top line failure; left boundary incorrect')
        self.assertEqual(boundary.right, 8, 'Top line failure; right boundary incorrect')

        # Bottom line check

        scan_state['upper'][0] = 1

        boundary = okra.Boundary(2, 2, 2, 2)

        self.dg._DigitGetter__tracer.trace(img, boundary, (2, 2), scan_state)

        self.assertEqual(boundary.top, 8, 'Bottom line failure; top boundary incorrect')
        self.assertEqual(boundary.bottom, 9, 'Bottom line failure; bottom boundary incorrect')
        self.assertEqual(boundary.left, 1, 'Bottom line failure; left boundary incorrect')
        self.assertEqual(boundary.right, 8, 'Bottom line failure; right boundary incorrect')


    def test_get_segment_type(self):

        img_shape = (46, 156)

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((40, 39)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.DIGIT, 'Digit segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((46, 35)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.DIGIT, 'Digit segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((7, 7)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.DECIMAL, 'Decimal segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((11, 8)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.DECIMAL, 'Decimal segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((10, 32)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.MINUS, 'Minus segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((9, 21)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.MINUS, 'Minus segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((1, 5)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.NOISE, 'Noise segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((0, 0)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.NOISE, 'Noise segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type(np.zeros((2, 1)), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.NOISE, 'Noise segment not indentified correctly')


    def test_blank_segment_checker(self):

        blank_img = np.array([
            [204, 206, 205, 206, 207],
            [216, 209, 206, 204, 206],
            [206, 208, 208, 207, 204],
            [205, 211, 210, 209, 209],
            [207, 204, 207, 208, 205]
        ], np.uint8)

        num, conf = self.dg.digit_from_image(blank_img)
        self.assertIsNone(num, 'Blank segment identified as non-blank')

        non_blank_img = np.array([
            [204, 206, 205, 206, 207],
            [216, 209, 25, 204, 206],
            [206, 208, 32, 207, 204],
            [205, 211, 27, 209, 209],
            [207, 204, 207, 208, 205]
        ], np.uint8)

        num, conf = self.dg.digit_from_image(non_blank_img)
        self.assertIsNotNone(num, 'Non-blank segment identified as blank')


