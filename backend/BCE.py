from preprocessing.scorefields import BCSegments
from OCR import okra
from OCR import violin as v
import ImagePackager


# A key map to convert the score-field key
# names to the ones used by the frontend.
key_map = {
    'Rider#':        'Rider number',
    'recovery':      'Recovery',
    'hydration':     'Hydration',
    'lesions':       'Lesions',
    'soundness':     'Soundness',
    'qual_movement': 'Qual Mvmt',
    'rider_time':    'Ride time, this rider',
    'rider_weight':  'Weight of this rider'
}


def run(args, image_buffer):
    """
    Runs all the image processing code for the BCE type scorecard.

    Parameters:
        args (dict): A dictionary containing the arguments:
                     'torchserve' (bool): A flag to specify whether TorchServe
                                          should be used or not.
                     'corner_points' (dict): A dictionary containing the
                                             coordinates of the page corners
                                             (optional).
        image_buffer (bytes): The raw image data.

    Returns:
        dict: An array of dictionary objects containing score-field values and
              confidences for each rider.
    """

    if 'corner_points' not in args.keys():
        import corners
        expected_corners = corners.run(None, image_buffer)
        args['corner_points'] = expected_corners['corner_points']

    # Get the score field segments
    extracted_fields = BCSegments(image_buffer, args['corner_points'])

    # Prepare the OCR
    dg = okra.DigitGetter(ts=args['torchserve'])

    rider_keys = extracted_fields.keys()

    rider_data = []

    for rider_key in rider_keys:

        scanned_vals = process_rider_fields(extracted_fields[rider_key], dg)

        if (are_blank(scanned_vals)):
            continue

        rider_data.append(scanned_vals)

    return { 'riderData': rider_data, 'riderCount': len(rider_data) }


def process_rider_fields(rider_segments, dg):
    """
    Processes all the score-fields for a single rider.

    Parameters:
        rider_segments (dict): A dictionary containing the image segments
                        for a single rider's score fields.
        dg (okra.DigitGetter): An instance of the OCR class.

    Returns:
        dict: A dictionary containing values and confidences for each
              score-field associated with the rider.
    """

    rider_output = {}

    field_keys = rider_segments.keys()

    for key_num, field_key in enumerate(field_keys):

        # Run the OCR
        raw_out = dg.image_to_digits(rider_segments[field_key])

        # Use the appropriate validation
        #
        if key_num == 0:
            num, conf = v.validate_rider_number(raw_out)

        elif key_num == 6:
            num, conf = v.validate_time(raw_out)

        elif key_num == 7:
            num, conf = v.validate_weight(raw_out)

        else:
            num, conf = v.validate_score(raw_out, 10, 1)

        encoded_image = ImagePackager.encode_base64(rider_segments[field_key])

        # Save results
        rider_output[key_map[field_key]] = {
            'value': num,
            'confidence': conf,
            'image': encoded_image
        }

    return rider_output


def are_blank(fields):
    """ Returns True if the fields are empty and False otherwise"""

    blank_field_count = 0
    blank_count_threshold = 5

    for key in fields.keys():

        if fields[key]['value'] == '':
            blank_field_count += 1

        if blank_field_count >= blank_count_threshold:
            return True

    return False


def _debug_main():

    import sys
    from termcolor import colored

    if len(sys.argv) != 2:
        print('\n  Usage: python BCE.py <Path to image>\n')
        return

    try:
        with open(sys.argv[1], 'rb') as file:
            image_buffer = file.read()

    except FileNotFoundError:
        print(f'\n  Cannot open "{sys.argv[1]}"\n')
        return

    ret_val = run({'torchserve': False}, image_buffer)

    for riderNumber in range(ret_val['riderCount']):

        print(colored(f'----------- Rider {riderNumber + 1}', color='blue', attrs=['bold']))

        rider_dict = ret_val['riderData'][riderNumber]

        for key in rider_dict.keys():

            if rider_dict[key]['confidence'] >= 95.0:
                print(key, colored(rider_dict[key]['value'], color='green', attrs=['bold']))

            elif rider_dict[key]['confidence'] >= 85.0:
                print(key, colored(rider_dict[key]['value'], color='yellow', attrs=['bold']))

            elif rider_dict[key]['value'] == '':
                print(colored(key, color='red', attrs=['bold']))

            else:
                print(key, colored(rider_dict[key]['value'], color='red', attrs=['bold']))


if __name__ == '__main__':
    _debug_main()

