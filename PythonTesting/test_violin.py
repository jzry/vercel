import unittest

import OCR.violin as violin


class ViolinTestCase(unittest.TestCase):

    def test_validate_score(self):

        integer_cases = [
            # OCR output               max_score        expected output
            [([0], [99.0]),            [3, 5, 10, 25],  ('0', 99.0)],
            [([3], [90.0]),            [3, 5, 10, 25],  ('3', 90.0)],
            [([5], [87.6]),            [5, 10, 25],     ('5', 87.6)],
            [([9], [92.5]),            [10, 25],        ('9', 92.5)],
            [([1, 0], [100.0, 100.0]), [10, 25],        ('10', 100.0)],
            [([1, 1], [95.0, 100.0]),  [25],            ('11', 95.0)],
            [([1, 9], [95.0, 94.0]),   [25],            ('19', 94.0)],
            [([2, 0], [80.0, 94.0]),   [25],            ('20', 80.0)],
            [([2, 1], [91.0, 99.0]),   [25],            ('21', 91.0)],
            [([2, 5], [91.7, 92.0]),   [25],            ('25', 91.7)],
            [([], []),                 [5],             ('', 0.0)],
            [([], []),                 [10],            ('', 0.0)]
        ]

        float_cases = [
            # OCR output                           max_score        expected output
            [(['.', 5], [90.0, 98.0]),             [3, 5, 10, 25],  ('.5', 90.0)],
            [(['.', 4, 6], [90.0, 98.0, 71.9]),    [3, 5, 10, 25],  ('.46', 71.9)],
            [([0, '.', 5], [97.0, 90.0, 98.0]),    [3, 5, 10, 25],  ('0.5', 90.0)],
            [([1, '.', 5], [96.0, 92.0, 98.0]),    [3, 5, 10, 25],  ('1.5', 92.0)],
            [([2, '.', 4], [87.0, 91.0, 99.0]),    [3, 5, 10, 25],  ('2.4', 87.0)],
            [(['.', 2, 5], [64.0, 92.0, 94.0]),    [3, 5, 10, 25],  ('.25', 64.0)],
            [([9, '.', 5], [91.0, 99.0, 93.0]),    [10, 25],        ('9.5', 91.0)],
            [([10, '.', 6], [93.4, 95.0, 96.0]),   [25],            ('10.6', 93.4)],
            [([15, '.', 9, 5], [85.6, 93.0, 89.0]),[25],            ('15.95', 85.6)],
            [([24, '.', 5], [90.0, 93.0, 89.0]),   [25],            ('24.5', 89.0)],
        ]

        for case_num, integer_case in enumerate(integer_cases):

            for max_score in integer_case[1]:

                out = violin.validate_score(integer_case[0], max_score)
                self.assertEqual(out, integer_case[2], f'Integer case {case_num}, max_score={max_score}')

                # Skip the next test for the first case
                if case_num == 0:
                    continue

                out = violin.validate_score(integer_case[0], max_score, 1)
                self.assertEqual(out, integer_case[2],
                    f'Integer case {case_num}, max_score={max_score}, min_score=1'
                )

        for case_num, float_case in enumerate(float_cases):

            for max_score in float_case[1]:

                out = violin.validate_score(float_case[0], max_score)
                self.assertEqual(out, float_case[2], f'Float case {case_num}, max_score={max_score}')


    def test_decimal_handling(self):

        decimal_cases = [
            # OCR output                            expected number of decimals
            [([0, '.', '.'], [9.0, 9.0, 9.0]),                   0],
            [([2, 1, '.'], [9.0, 9.0, 9.0]),                     0],
            [(['.', 0, '.', '.'], [9.0, 9.0, 9.0, 9.0]),         1],
            [(['.', 5, 5, '.'], [9.0, 9.0, 9.0, 9.0]),           1],
            [([5, '.', '.', 5], [9.0, 10.0, 9.0, 9.0]),          1],
            [([5, '.', 6, '.', 5], [9.0, 9.0, 9.0, 12.0, 9.0]),  1],
            [([5, '.', '.', '.', 5], [9.0, 9.0, 8.0, 7.0, 9.0]), 1],
            [(['.', 5, '.', '.', 5], [9.0, 9.0, 7.0, 8.0, 9.0]), 1],
            [(['.', '.', 5, '.', 5], [9.0, 7.0, 9.0, 8.0, 9.0]), 1],
            [([1, 1, '.', '.', 5], [9.0, 9.0, 9.0, 8.0, 9.0]),   1],
            [([1, 1, '.', 5, '.'], [9.0, 9.0, 8.0, 9.0, 9.0]),   1]
        ]

        for case_num, decimal_case in enumerate(decimal_cases):

            out = violin.validate_score(decimal_case[0], 99)
            decimal_count = out[0].count('.')
            self.assertEqual(decimal_count, decimal_case[1], f'Decimal case {case_num}')


    def test_validate_rider_number(self):

        test_cases = [
            # OCR output                            Expected output
            [([7, 2, 3], [50.0, 99.0, 99.0]),            'L23'],
            [([1, 1, 8], [60.0, 99.0, 99.0]),            'L18'],
            [([1, 9], [45.5, 99.0]),                     'L9'],
            [([1, 9], [97.0, 99.0]),                     '19'],
            [([8, 6, 2, 4], [37.0, 68.0, 92.0, 93.0]),   'L24'],
            [([], []),                                   '']
        ]

        for case_num, test_case in enumerate(test_cases):

            number, confidence = violin.validate_rider_number(test_case[0])
            self.assertEqual(number, test_case[1], f'Case {case_num}')


    def test_validate_time(self):

        test_cases = [
            # OCR output                            Expected output
            [([4, 3], [99.0, 99.0]),                     '43'],
            [([5, 9], [94.0, 97.0]),                     '59'],
            [([1, 0, 0], [99.0, 94.0, 97.0]),            '100'],
            [([1, 2, 3], [92.0, 98.0, 95.0]),            '123'],
            [([1, 5, 9], [94.0, 90.0, 93.0]),            '159'],
            [([3, 4, 7], [98.0, 95.0, 96.0]),            '347'],
            [([4, 0, 9], [98.0, 95.0, 96.0]),            '409'],
            [([], []),                                   '']
        ]

        for case_num, test_case in enumerate(test_cases):

            number, confidence = violin.validate_time(test_case[0])
            self.assertEqual(number, test_case[1], f'Case {case_num}')


    def test_validate_weight(self):

        test_cases = [
            # OCR output                            Expected output
            [([8, 5], [98.0, 98.0]),                     '85'],
            [([9, 9], [99.0, 97.0]),                     '99'],
            [([1, 0, 0], [92.0, 99.0, 97.0]),            '100'],
            [([1, 2, 5], [97.0, 97.0, 96.0]),            '125'],
            [([1, 9, 9], [99.0, 89.0, 91.0]),            '199'],
            [([2, 0, 0], [95.0, 92.0, 98.0]),            '200'],
            [([2, 3, 7], [96.0, 94.0, 91.0]),            '237'],
            [([], []),                                   '']
        ]

        for case_num, test_case in enumerate(test_cases):

            number, confidence = violin.validate_weight(test_case[0])
            self.assertEqual(number, test_case[1], f'Case {case_num}')

