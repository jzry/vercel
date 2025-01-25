import OCR.okra as okra
import cv2
from termcolor import colored
from pathlib import Path


dg = okra.DigitGetter(debug=True)

# Uncomment this line to display images while OCRing
#dg.debug_images = True

# Load a test image
#
# .\neat_pen.jpg
# .\sloppy_pen.jpg
# .\dark_pen.jpg
#
# .\neat_pencil.jpg
# .\sloppy_pencil.jpg
#
img = cv2.imread(Path(__file__).parent.parent / 'Test Images' / 'neat_pen.jpg', 0) # 0 is for monochrome

numbers, confidence = dg.image_to_digits(img)

for i in range(len(numbers)):
    if confidence[i] > 90.0:
        print(numbers[i], colored(f'({confidence[i]:>.2f}%)', 'green', attrs=['bold']))
    elif confidence[i] > 80.0:
        print(numbers[i], colored(f'({confidence[i]:>.2f}%)', 'yellow', attrs=['bold']))
    else:
        print(numbers[i], colored(f'({confidence[i]:>.2f}%)', 'red', attrs=['bold']))
