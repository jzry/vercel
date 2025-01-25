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


    def test_trace_digit(self):

        img = np.array([
            [0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0],
            [1, 0, 1, 0, 1]
        ], np.uint8)

        boundary = okra.Boundary(2, 2, 2, 2)

        self.dg._DigitGetter__trace_digit(img, boundary, (2, 2))

        self.assertEqual(boundary.top, 1, 'Top boundary incorrect')
        self.assertEqual(boundary.bottom, 4, 'Bottom boundary incorrect')
        self.assertEqual(boundary.left, 1, 'Left boundary incorrect')
        self.assertEqual(boundary.right, 4, 'Right boundary incorrect')


    def test_get_segment_type(self):

        img_shape = (46, 156)

        seg_type = self.dg._DigitGetter__get_segment_type((40, 39), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.DIGIT, 'Digit segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type((46, 35), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.DIGIT, 'Digit segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type((7, 7), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.DECIMAL, 'Decimal segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type((11, 8), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.DECIMAL, 'Decimal segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type((10, 32), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.MINUS, 'Minus segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type((9, 21), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.MINUS, 'Minus segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type((1, 5), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.NOISE, 'Noise segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type((0, 0), img_shape)
        self.assertEqual(seg_type, okra.SegmentType.NOISE, 'Noise segment not indentified correctly')

        seg_type = self.dg._DigitGetter__get_segment_type((2, 1), img_shape)
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


