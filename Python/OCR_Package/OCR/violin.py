#
# Validation functions for OCR output
#

import random


# The confidence percentages used for inserted values
GOOD_CONFIDENCE    = 95.0
DEFAULT_CONFIDENCE = 90.0
POOR_CONFIDENCE    = 85.0

# Confidence penalties for deleting values
SMALL_PENALTY   = 1.0
DEFAULT_PENALTY = 2.5
LARGE_PENALTY   = 5.0


commonly_confused_digits = [
    [8],           # 0
    [7],           # 1
    [],            # 2
    [9, 8, 5],     # 3
    [9],           # 4
    [8, 3],        # 5
    [8],           # 6
    [1],           # 7
    [6, 5, 3, 0],  # 8
    [4, 3],        # 9
]



def validate_score(raw, max_score=None, min_score=0):
    """
    Validates and auto-corrects a score field.

    Parameters:
        raw (list, list): The raw output of the OCR.
        max_score (int): The upper-bound of the score (Defaults to None).
        min_score (int, optional): The lower-bound of the score
                                   (Defaults to 0).

    Returns:
        str: The corrected and stringified OCR output.
        float: The overall confidence percentage.
    """

    nums, confs = raw

    penalty = __remove_decimal_points(nums, confs, remove_all=False)

    if not a_valid_score(nums, max_score, min_score):

        __insert_decimal_point(nums, confs, max_score, min_score)

        if not a_valid_score(nums, max_score, min_score):

            penalty += __trim_score_digits(nums, confs, max_score, min_score)
            __insert_decimal_point(nums, confs, max_score, min_score)

            if not a_valid_score(nums, max_score, min_score):

                penalty += __force_valid_score(
                    nums, confs, max_score, min_score
                )

    penalty += __trim_leading_zeros(nums, confs)

    return __stringify(nums), __overall_confidence(confs, penalty)


def validate_rider_number(raw):
    """
    Validates and auto-corrects a rider number field.

    Parameters:
        raw (list, list): The raw output of the OCR.

    Returns:
        str: The corrected and stringified OCR output.
        float: The overall confidence percentage.
    """

    nums, confs = raw

    penalty = 0.0

    __insert_L(nums, confs)
    penalty += __remove_decimal_points(nums, confs, remove_all=True)

    if not a_valid_rider_number(nums):

        penalty += __force_valid_rider_number(nums, confs)


    return __stringify(nums), __overall_confidence(confs, penalty)


def validate_time(raw):
    """
    Validates and auto-corrects a time field.

    Parameters:
        raw (list, list): The raw output of the OCR.

    Returns:
        str: The corrected and stringified OCR output.
        float: The overall confidence percentage.
    """

    nums, confs = raw

    penalty = __remove_decimal_points(nums, confs, remove_all=True)

    if not a_valid_time(nums):

        penalty += __trim_to_length(nums, confs, length=4)

        if not a_valid_time(nums):

            penalty += __force_valid_time(nums, confs)


    return __stringify(nums), __overall_confidence(confs, penalty)


def validate_weight(raw):
    """
    Validates and auto-corrects a weight field.

    Parameters:
        raw (list, list): The raw output of the OCR.

    Returns:
        str: The corrected and stringified OCR output.
        float: The overall confidence percentage.
    """

    nums, confs = raw

    penalty = __remove_decimal_points(nums, confs, remove_all=True)

    if not a_valid_weight(nums):

        penalty += __trim_to_length(nums, confs, length=3)

        if not a_valid_weight(nums):

            penalty += __force_valid_weight(nums, confs)

    penalty += __trim_leading_zeros(nums, confs)

    return __stringify(nums), __overall_confidence(confs, penalty)


#
# First level of helper functions
#


def a_valid_score(nums, max_score, min_score):

    if not nums:
        return True

    whole, fractional = __split(nums)

    whole_num = __list_to_integer(whole)

    if fractional:

        fract_num = __list_to_integer(fractional)

        if max_score is not None:
            if not whole_num < max_score:
                return False

        if fract_num != 25 and \
           fract_num != 75 and \
           fract_num != 5:
            return False

    else:
        if max_score is not None:
            if not whole_num <= max_score:
                return False

    if not whole_num >= min_score:
        return False

    return True



def a_valid_rider_number(nums):

    if not nums:
        return True

    if len(nums) > 3:
        return False

    return True


def a_valid_time(nums):

    if not nums:
        return True

    if len(nums) > 4:
        return False

    hours = __list_to_integer(nums[:-2])
    minutes = __list_to_integer(nums[-2:])

    if hours > 24:
        return False

    if minutes >= 60:
        return False

    return True


def a_valid_weight(nums):

    if not nums:
        return True

    if len(nums) > 3:
        return False

    if len(nums) == 3:

        # It is assumed here that no rider will weight more than 399 pounds!
        #
        if nums[0] > 3:
            return False

    return True



def __remove_decimal_points(nums, confs, remove_all):

    penalty = 0.0

    if remove_all:

        i = 0

        while i < len(nums):

            if nums[i] == '.':

                del nums[i]
                del confs[i]
                penalty += SMALL_PENALTY

            else:

                i += 1
    else:

        while len(nums) > 0:

            if nums[-1] != '.':
                break

            del nums[-1]
            del confs[-1]
            penalty += SMALL_PENALTY

        if nums.count('.') > 1:

            best_decimal = -1
            i = 0

            while i < len(nums):

                if nums[i] == '.':

                    if best_decimal == -1:
                        best_decimal = i
                        i += 1

                    elif confs[i] > confs[best_decimal]:

                        del nums[best_decimal]
                        del confs[best_decimal]
                        best_decimal = i - 1
                        penalty += DEFAULT_PENALTY

                    else:

                        del nums[i]
                        del confs[i]
                        penalty += DEFAULT_PENALTY

                else:

                    i += 1

    return penalty



def __insert_decimal_point(nums, confs, max_score, min_score):

    if '.' not in nums:
        if max_score is not None:

            if max_score < 10:

                if len(nums) == 2:

                    if nums[0] < max_score and nums[1] == 5:

                        nums.insert(1, '.')
                        confs.insert(1, GOOD_CONFIDENCE)

                elif len(nums) == 3:

                    if nums[0] < max_score and \
                       (nums[1] == 2 or nums[1] == 7) and \
                       nums[2] == 5:

                        nums.insert(1, '.')
                        confs.insert(1, GOOD_CONFIDENCE)

            else:

                if len(nums) == 2:

                    if __gt(nums, max_score) and \
                       nums[1] == 5:

                        nums.insert(1, '.')
                        confs.insert(1, GOOD_CONFIDENCE)

                elif len(nums) == 3:

                    if __lt(nums[:2], max_score) and \
                       nums[2] == 5:

                        nums.insert(2, '.')
                        confs.insert(2, GOOD_CONFIDENCE)

                    elif nums[0] < max_score and \
                         (nums[1] == 2 or nums[1] == 7) and \
                         nums[2] == 5:

                        nums.insert(1, '.')
                        confs.insert(1, GOOD_CONFIDENCE)

                elif len(nums) == 4:

                    if __lt(nums[:2], max_score) and \
                       (nums[2] == 2 or nums[2] == 7) and \
                       nums[3] == 5:

                        nums.insert(2, '.')
                        confs.insert(2, GOOD_CONFIDENCE)


def __trim_score_digits(nums, confs, max_score, min_score):

    penalty = 0.0

    end = len(nums)

    if '.' in nums:

        dp_index = end = nums.index('.')

        while len(nums) - dp_index - 1 > 2:

            worst_i = dp_index + 1

            for i in range(dp_index + 2, len(nums)):

                if confs[i] < confs[worst_i]:

                    worst_i = i

            del nums[worst_i]
            del confs[worst_i]
            penalty += LARGE_PENALTY

    if max_score is not None:

        max_whole_digits = 1 if max_score < 10 else 2

        while end > max_whole_digits:

            del nums[0]
            del confs[0]
            penalty += DEFAULT_PENALTY
            end -= 1

        if end == 2:
            if nums[0] == 0:

                del nums[0]
                del confs[0]
                penalty += SMALL_PENALTY

    return penalty


def __trim_to_length(nums, confs, length):

    penalty = 0.0

    while len(nums) > length:

        del nums[0]
        del confs[0]
        penalty += DEFAULT_PENALTY

    penalty += __trim_leading_zeros(nums, confs)

    return penalty


def __trim_leading_zeros(nums, confs):

    penalty = 0.0

    while len(nums) > 1:

        if nums[0] != 0:
            break

        if nums[1] == '.':
            break

        del nums[0]
        del confs[0]
        penalty += SMALL_PENALTY

    return penalty



def __insert_L(nums, confs):

    if len(nums) > 1:

        nums[0] = 'L'
        confs[0] = GOOD_CONFIDENCE

    elif len(nums) == 1:

        nums.insert(0, 'L')
        confs.insert(0, GOOD_CONFIDENCE)



def __force_valid_score(nums, confs, max_score, min_score):

    penalty = 0.0

    whole, fractional = __split(nums)

    if fractional:

        if max_score is not None and \
           __gt(whole, max_score, or_equal=True):

            if len(whole) == 2 and max_score <= 10:

                del nums[0]
                del confs[0]
                penalty += DEFAULT_PENALTY

                if nums[0] >= max_score:

                    nums[0] = __get_replacement_digit(
                        nums[0],
                        max_score - 1,
                        min_score
                    )
                    penalty += LARGE_PENALTY

            elif max_score <= 10:

                nums[0] = __get_replacement_digit(
                    nums[0],
                    max_score - 1,
                    min_score
                )
                penalty += LARGE_PENALTY

            else:

                max_tens = max_score // 10
                max_ones = max_score % 10

                if nums[0] > max_tens:

                    del nums[0]
                    del confs[0]
                    penalty += DEFAULT_PENALTY

                elif nums[0] == max_tens and \
                     nums[1] >= max_ones:

                    nums[1] = __get_replacement_digit(nums[1], max_ones - 1, 0)
                    penalty += LARGE_PENALTY

        elif __lt(whole, min_score):

            if nums[0] == '.':

                nums.insert(0, min_score)
                confs.insert(0, DEFAULT_CONFIDENCE)

            else:

                max_digit = 9 if max_score > 10 else max_score - 1

                nums[0] = __get_replacement_digit(
                    nums[0],
                    max_digit,
                    min_score
                )

            penalty += LARGE_PENALTY

        if not __eq(fractional, [5, 25, 75]):

            if len(fractional) == 2:

                if nums[-2] != 2 and \
                   nums[-2] != 7:

                    nums[-2] = random.choice([2, 7])
                    penalty += LARGE_PENALTY

            if nums[-1] != 5:

                nums[-1] = 5
                penalty += LARGE_PENALTY

    else:

        if max_score is not None and \
           __gt(whole, max_score):

            if len(whole) == 2 and max_score < 10:

                del nums[0]
                del confs[0]
                penalty += DEFAULT_PENALTY

                if nums[0] > max_score:

                    nums[0] = __get_replacement_digit(nums[0], max_score, min_score)
                    penalty += LARGE_PENALTY

            elif max_score < 10:

                nums[0] = __get_replacement_digit(nums[0], max_score, min_score)
                penalty += LARGE_PENALTY

            else:

                max_tens = max_score // 10
                max_ones = max_score % 10

                if nums[0] > max_tens:

                    del nums[0]
                    del confs[0]
                    penalty += DEFAULT_PENALTY

                elif nums[0] == max_tens and \
                     nums[1] > max_ones:

                    nums[1] = __get_replacement_digit(nums[1], max_ones, 0)
                    penalty += LARGE_PENALTY

        elif __lt(whole, min_score):

            max_digit = 9 if max_score >= 10 else max_score

            nums[0] = __get_replacement_digit(
                nums[0],
                max_digit,
                min_score
            )

            penalty += LARGE_PENALTY

    return penalty


def __force_valid_rider_number(nums, confs):

    penalty = 0.0

    while len(nums) > 3:

        worst_i = 1

        for i in range(2, len(nums)):

            if confs[i] < confs[worst_i]:

                worst_i = i

        del nums[worst_i]
        del confs[worst_i]
        penalty += LARGE_PENALTY

    return penalty


def __force_valid_time(nums, confs):

    penalty = 0.0

    if nums[-2] > 5:

        nums[-2] = __get_replacement_digit(nums[-2], 5, 0)
        penalty += LARGE_PENALTY

    if len(nums) == 4:

        if nums[0] > 2:

            del nums[0]
            del confs[0]
            penalty += LARGE_PENALTY

    return penalty


def __force_valid_weight(nums, confs):

    nums[0] = __get_replacement_digit(nums[0], 2, 1)

    return LARGE_PENALTY



def __stringify(nums):
    """Converts the input list into a string"""

    return ''.join(str(e) for e in nums)


def __overall_confidence(confs, penalty):
    """Returns the lowest confidence value"""

    if len(confs) == 0:
        return 0.0

    return min(confs) - penalty



#
# Second level of helper functions
#


def __lt(number_list, number, or_equal=False):

    list_as_integer = __list_to_integer(number_list)

    if or_equal:

        return list_as_integer <= number

    else:

        return list_as_integer < number


def __gt(number_list, number, or_equal=False):

    list_as_integer = __list_to_integer(number_list)

    if or_equal:

        return list_as_integer >= number

    else:

        return list_as_integer > number


def __eq(number_list, numbers):

    list_as_integer = __list_to_integer(number_list)

    if isinstance(numbers, list):

        for number in numbers:

            if list_as_integer == number:

                return True

        return False

    else:

        return list_as_integer == numbers



def __list_to_integer(number_list):

    number = 0

    for next_number in number_list:

        number *= 10
        number += next_number

    return number



def __split(number_list):

    if '.' in number_list:

        decimal_point_index = number_list.index('.')

        whole = number_list[:decimal_point_index]
        fractional = number_list[decimal_point_index + 1:]

        return whole, fractional

    else:

        return number_list, None



def __get_replacement_digit(original, high, low):

    potential_replacements = commonly_confused_digits[original]

    random.shuffle(potential_replacements)

    for digit in potential_replacements:

        if digit <= high and digit >= low:

            return digit

    digit = int((random.random() * (high - low + 1)) + low)

    return digit

