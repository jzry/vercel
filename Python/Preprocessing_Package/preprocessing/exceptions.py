#
# Custom Exceptions for the preprocessing code
#


class PreprocessingExtensionError(Exception):
    """Something is wrong with file type of the uploaded file"""

class PreprocessingImageError(Exception):
    """An image could not be opened for some reason"""

class PreprocessingAlignmentError(Exception):
    """An image could not be aligned for some reason"""
