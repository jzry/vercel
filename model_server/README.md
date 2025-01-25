# TorchServe Setup Guide

TorchServe will manage the image classifer on the deployment server.
This README will go through the steps of setting it up.

> [!NOTE]
> TorchServe only runs on Linux, so don't bother trying to set this
> up if your OS is Windows or MacOS.

## Java Dependency

Install Java 21:

`sudo apt install jdk-21`

## Install Packages

Install Python dependencies:

`pip install torchserve torch-model-archiver torch-workflow-archiver pyyaml captum`

## Build Model Archive

Navigate to the directory `seniordesign/model_server/` and run the following command:

```
torch-model-archiver --model-name OkraClassifier \
                     --version 1.0 \
                     --model-file ../Python/OCR_Package/OCR/OkraClassifier.py \
                     --serialized-file ../Python/OCR_Package/OCR/weights/okra.resnet.weights \
                     --handler ../Python/OCR_Package/OCR/OkraHandler.py \
                     --export-path model_store/ --force
```

## Start TorchServe

```
torchserve --start --ncs \
           --model-store model_store/ \
           --models OkraClassifier=OkraClassifier.mar \
           --ts-config config.properties
```

## Stop TorchServe

`torchserve --stop`
