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

                    ret_val = process_CTR(image_buffer, sys.argv[2] == 'torchserve')

    else:

        ret_val['error'] = 'Incorrect number of arguments'


    # Return the results as JSON through stdout
    print(json.dumps(ret_val))



#
# Run all the code to process the CTR scoresheet
#
def process_CTR(image_buffer, torchserve):

    from preprocessing.scorefields import CTRSegments
    from OCR import okra
    from OCR import violin as v

    extracted_fields = CTRSegments(image_buffer)

    # Prepare the OCR
    dg = okra.DigitGetter(ts=torchserve)

    field_keys = extracted_fields.keys()

    output_dict = {}

    max_score_per_field = [5, 5, 5, 5, 5, 3, 0, 2, 5, 5, 20, 5, 10, 25, 5, 5, None, None]
    out_field_keys = [
        'Pulse Before Trot Out',
        'Pulse After Trot Out',
        'Mucous Membrane',
        'Capillary Refill',
        'Skin Pinch',
        'Jugular Vein Refill',
        'Gut Sounds',
        'Anal Tone',
        'Muscle Tone',
        'Unwillingness to trot',
        'Tendons, Ligaments, Joints, Filings',
        'Interferences',
        'Grade 1',
        'Grade 2',
        'Back Tenderness',
        'Tack Area',
        'Hold on Trail',
        'Time Penalty'
    ]

    for i, key in enumerate(field_keys):

        if key == 'gut_sounds':
            continue

        #
        # Dictionary   <--   OCR validation   <--   OCR   <--   Image Segments
        #

        raw_ouput = dg.image_to_digits(extracted_fields[key])

        num, conf = v.validate_score(raw_ouput, max_score_per_field[i])

        output_dict[out_field_keys[i]] = {'value': num, 'confidence': conf}



    return output_dict


def debug_main():

    from termcolor import colored
    from pathlib import Path

    filename = 'CTR-1.jpg'

    full_path = Path(__file__).parent.parent / 'Python' / 'Preprocessing_Package' / 'preprocessing' / 'ctr' / filename

    with open(full_path, 'rb') as file:
        image_buffer = file.read()

    ret_val = process_CTR(image_buffer)

    for key in ret_val.keys():

        if key == 'gut_sounds':
            continue

        if ret_val[key]['confidence'] >= 90.0:
            print(key, colored(ret_val[key]['value'], color='green', attrs=['bold']))
        elif ret_val[key]['confidence'] >= 80.0:
            print(key, colored(ret_val[key]['value'], color='yellow', attrs=['bold']))
        elif ret_val[key]['value'] == '':
            print(colored(key, color='red', attrs=['bold']))
        else:
            print(key, colored(ret_val[key]['value'], color='red', attrs=['bold']))



# Do It
main()

# For debugging only
# debug_main()
