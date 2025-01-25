#
# Custom Exceptions for the OCR Package
#


class OkraBlankSegmentException(Exception):
    """
        Raised when an image segment is blank.

        This exception is used internally by okra.py and
        does not need to be handled elsewhere.
    """


class OkraModelError(Exception):
    """Raised when the image classifier fails"""

    def __init__(self, message, body):

        super().__init__(message)
        self.body = body

