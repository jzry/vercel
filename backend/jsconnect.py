import sys
import json
from contextlib import redirect_stdout, redirect_stderr
from os import devnull
import importlib.util
from pathlib import Path

from preprocessing.exceptions import *
from OCR.exceptions import *


def main():

    # Receive from parent process
    script_name, args, image_buffer = receive()

    # Temporarily redirect stdout and stderr so random
    # messages aren't sent to the parent process
    #
    with open(devnull, 'w') as null_device:
        with redirect_stdout(null_device):
            with redirect_stderr(null_device):

                print('ERROR if you see this message')

                result = run_code(script_name, args, image_buffer)

    # Send to parent process
    send(result)


def run_code(script_name, args, image_buffer):
    """
    Runs the image processing code based on the scorecard type.

    Parameters:
        script_name (str): A string with the name of the Python script to run.
        args (dict): A dictionary containing arguments for the target Python
                     script.
        image_buffer (bytes): A byte array storing an image.

    Returns:
        dict: A dictionary with result, data, and message fields
    """

    try:
        target = load_module(script_name)

    except FileNotFoundError:
        return { 'status': -1, 'data': {}, 'message': f'"{script_name}" not found' }

    try:
        if callable(target.run):
            data = target.run(args, image_buffer)

        else:
            return { 'status': -2, 'data': {}, 'message': f'"{script_name}" does not contain "run" function' }

    except PreprocessingExtensionError as e:
        return error_response(1, e)

    except NotImplementedError as e:
        return error_response(2, e)

    except PreprocessingImageError as e:
        return error_response(3, e)

    except OkraModelError as e:
        return error_response(4, e)

    return { 'status': 0, 'data': data, 'message': 'Success' }


def error_response(status, err):
    """
    Packages error information into a response dictionary.

    Arguments:
        status (int): A number that indentifies the type of error.
        err (Exception): The exception that was caught.

    Returns:
        dict: A response dictionary.
    """

    return {
        'status': status,
        'data': {},
        'message': str(err)
    }


def receive():
    """
    Receives image data and parameters from the parent JavaScript process.

    Returns:
        str: The name of the Python script to run
        dict: A dictionary with arguments to pass to the Python script
        bytes: A byte array storing an image.

    Raises:
        ValueError: Invalid command line arguments.
    """

    if len(sys.argv) == 4:

        # The first argument specifies the script name
        script_name = sys.argv[1]

        if script_name[-3:].lower() != '.py':
            raise ValueError('Script name should have file extension of ".py"')

        try:
            # The second argument is the number of bytes to read from stdin
            input_length_bytes = int(sys.argv[2])

        except ValueError:
            raise ValueError('Expected first argument to be an integer')

        if input_length_bytes < 0:
            raise ValueError('Expected first argument to be positive')

        args = json.loads(sys.argv[3])

        if input_length_bytes > 0:
            # Read the image data from standard input
            image_buffer = sys.stdin.buffer.read(input_length_bytes)

        else:
            image_buffer = None

        return script_name, args, image_buffer

    else:
        raise ValueError(f'Expected 3 command line arguments; Received {len(sys.argv) - 1}')


def send(data):
    """
    Sends JSON data to the parent JavaScript process.

    Parameters:
        data (dict): The response data stored in a dictionary object.
    """

    # Convert the dictionary to a JSON string
    # and return through standard output
    print(json.dumps(data))


def load_module(module_name):
    """Dynamically loads a Python module"""

    path = Path(__file__).parent / module_name

    spec = importlib.util.spec_from_file_location(module_name[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# Run It
if __name__ == '__main__':
    main()

