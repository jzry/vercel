# Web-based Automated Scorecard Reading and Calculation

This is a UCF senior design project completed by a team
of six from September 2024 - May 2025 and is a practical
application of the knowledge gained from our undergraduate
computer science education.

## Background

The [South Eastern Distance Rider's Association](https://www.distanceriding.org/)
is a non-profit organization that holds equestrian distance riding events.
Distance riding events are competitions where horses and their riders
must complete courses between 25 and 100 miles long. Participants
are scored based on their time and the soundness of the horse. For
safety, horses are evaluated by veterinarians at regular intervals
during the event and are only allowed to continue if they pass the
checkup. Two scorecards are typically used: the Competitive Trail
Ride (CTR) form and the Best Condition Evaluation (BCE) form.

## Goal

Develop a mobile-first website, tailored to the iPhone, that
automates the reading and calculation of score cards for
the South Eastern Distance Riders Association.

At minimum, a user should be able to use their phone to take a photo of
a score card, review and correct the scanned values, and view the scoring
results. This will require the use of computer vision/machine learning
techniques to read the written values from the scorecards.

## Overview

The UI was developed with [ReactJS](https://react.dev/), and the
server/API was developed using [ExpressJS](https://expressjs.com/).
The image processing was done in Python and relies heavily on
[OpenCV](https://opencv.org/) and [PyTorch](https://pytorch.org/).
See the documentation below for more information.

## Documentation

[React Frontend](./frontend#getting-started-with-create-react-app)

[Express Backend](./backend#expressjs-server)

[Image Processing and Segmentation](./Python/Preprocessing_Package/preprocessing#image-processing-test)

[Optical Character Recognition](./Python/OCR_Package/OCR#ocr-package)

[API Reference](./backend/API.md)

[Environment Variables Reference](./ENV.md)

[Python Setup](./Python#configuring-python)

[TorchServe Setup](./model_server#torchserve-setup-guide)

[Rick's Video](https://www.youtube.com/watch?v=E4WlUXrJgy4)

## Getting Started

1. The first step is to clone this repository onto your device using [git](https://git-scm.com/).
1. If you have not done so already, install [Node.js](https://nodejs.org/en).
1. Follow the directions in the [Python Setup](./Python#configuring-python) guide.
1. Define the environment variables in the appropriate files as described in the
[Environment Variables Reference](./ENV.md).
1. Install dependencies and run the [Express Backend](./backend#expressjs-server).
1. Install dependencies and run the [React Frontend](./frontend#getting-started-with-create-react-app).

