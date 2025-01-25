import OCR.okra as okra
import cv2
from termcolor import colored
import matplotlib.pyplot as plt
from pathlib import Path



def display_results(nums, confs):

    for i in range(len(nums)):

        print(colored(nums[i], confidence2color(confs[i]), attrs=['bold']), end='')

    min_conf = min(confs)
    max_conf = max(confs)

    print('\t(', end='')
    print(colored(f'{min_conf:.2f}%', confidence2color(min_conf), attrs=['bold']), end='')
    print(', ', end='')
    print(colored(f'{max_conf:.2f}%', confidence2color(max_conf), attrs=['bold']), end='')
    print(')')


def confidence2color(confidence):

    if confidence > 90.0:
        return 'green'
    elif confidence > 80.0:
        return 'yellow'
    else:
        return 'red'




############################################################

dg = okra.DigitGetter(debug=True)

############################################################

print('DigitGetter is ready')
input('>')



### Demonstrate digit finding

wide_image = cv2.imread(Path(__file__).parent.parent / 'Test Images' / 'neat_pen.jpg')
wide_image = cv2.cvtColor(wide_image, cv2.COLOR_BGR2RGB)

plt.imshow(wide_image)
plt.show()
input('>')

dg.debug_images = True

##########################################################

numbers, confidence = dg.image_to_digits(wide_image)

##########################################################

display_results(numbers, confidence)
input('>')

### Demonstrate with actual scoresheet values

dg.debug_images = False

for img_name in ['S1.jpg', 'S7.jpg', 'T9.jpg', 'T2.jpg', 'T5.jpg', 'T10.jpg']:

    img = cv2.imread(Path(__file__).parent.parent / 'Test Images' / f'{img_name}')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.imshow(img)
    plt.show()

    numbers, confidence = dg.image_to_digits(img)

    display_results(numbers, confidence)
    input('>')


print('Done')
