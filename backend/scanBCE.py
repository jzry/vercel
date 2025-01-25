import sys
import json
from contextlib import redirect_stdout, redirect_stderr
from os import devnull


def main():

    ret_val = {}

    if len(sys.argv) == 3:

        # The number of bytes to read from stdin
        input_length_bytes = int(sys.argv[1])

        # Read the image data from stdin
        image_buffer = sys.stdin.buffer.read(input_length_bytes)

        # Temporarily redirect stdout and stderr so
        # random messages aren't sent to Express
        with open(devnull, 'w') as null_device:
            with redirect_stdout(null_device):
                with redirect_stderr(null_device):

                    print('ERROR if you see this message')

                    ret_val = process_BCE(image_buffer, sys.argv[2] == 'torchserve')

    else:

        ret_val['error'] = 'Incorrect number of arguments'


    # Return the results as JSON through stdout
    print(json.dumps(ret_val))



#
# Run all the code to process the BCE scoresheet
#
def process_BCE(image_buffer, torchserve):

    from preprocessing.scorefields import BCSegments
    from OCR import okra
    from OCR import violin as v

    extracted_fields = BCSegments(image_buffer)

    # Prepare the OCR
    dg = okra.DigitGetter(ts=torchserve)

    rider_keys = extracted_fields.keys()
    output_dict = {}

    for rider_key in rider_keys:

        output_dict[rider_key] = {}

        #
        # Dictionary   <--   OCR validation   <--   OCR   <--   Image Segments
        #

        insert_into_dict(output_dict, rider_key, 'Rider number',        v.validate_rider_number(dg.image_to_digits(extracted_fields[rider_key]['Rider#'])))

        insert_into_dict(output_dict, rider_key, 'Recovery',      v.validate_score(dg.image_to_digits(extracted_fields[rider_key]['recovery']),      10, 1))
        insert_into_dict(output_dict, rider_key, 'Hydration',     v.validate_score(dg.image_to_digits(extracted_fields[rider_key]['hydration']),     10, 1))
        insert_into_dict(output_dict, rider_key, 'Lesions',       v.validate_score(dg.image_to_digits(extracted_fields[rider_key]['lesions']),       10, 1))
        insert_into_dict(output_dict, rider_key, 'Soundness',     v.validate_score(dg.image_to_digits(extracted_fields[rider_key]['soundness']),     10, 1))
        insert_into_dict(output_dict, rider_key, 'Qual Mvmt', v.validate_score(dg.image_to_digits(extracted_fields[rider_key]['qual_movement']), 10, 1))

        insert_into_dict(output_dict, rider_key, 'Ride time, this rider',    v.validate_time(dg.image_to_digits(extracted_fields[rider_key]['rider_time'])))
        insert_into_dict(output_dict, rider_key, 'Weight of this rider',  v.validate_weight(dg.image_to_digits(extracted_fields[rider_key]['rider_weight'])))

    return output_dict

#
# Helper function to insert outputs into the dictionary
#
def insert_into_dict(dictionary, rider, field, output):

    num, conf = output

    dictionary[rider][field] = {'value': num, 'confidence': conf}


def debug_main():

    from termcolor import colored
    from pathlib import Path

    filename = 'BC-1.jpg'

    full_path = Path(__file__).parent.parent / 'Python' / 'Preprocessing_Package' / 'preprocessing' / 'bc' / filename

    with open(full_path, 'rb') as file:
        image_buffer = file.read()

    ret_val = process_BCE(image_buffer)

    for rider_key in ret_val.keys():

        print(colored(f'----------- {rider_key}', color='blue', attrs=['bold']))

        for key in ret_val[rider_key].keys():

            if ret_val[rider_key][key]['confidence'] >= 90.0:
                print(key, colored(ret_val[rider_key][key]['value'], color='green', attrs=['bold']))
            elif ret_val[rider_key][key]['confidence'] >= 80.0:
                print(key, colored(ret_val[rider_key][key]['value'], color='yellow', attrs=['bold']))
            elif ret_val[rider_key][key]['value'] == '':
                print(colored(key, color='red', attrs=['bold']))
            else:
                print(key, colored(ret_val[rider_key][key]['value'], color='red', attrs=['bold']))


# Do It
main()

# For debugging only
# debug_main()
