# TorchServe Setup Guide

TorchServe will manage the image classifer on the deployment server.
This README will go through the steps of setting it up.

> [!NOTE]
> These instructions assume you are running TorchServe on a Debian-based Linux distro.
> If for some reason you want to run TorchServe on Windows see
> [this guide](https://pytorch.org/serve/torchserve_on_win_native.html).

## Install Dependencies

### Java

Install Java 21:

`sudo apt install jdk-21`

### Python

The required Python packages should have been installed during the
[Python setup](../Python#server-installation).

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

This will store the model in the file 
`seniordesign/model_server/model_store/OkraClassifier.mar`.
In this format, the model is ready to be served by TorchServe.

## Run TorchServe

> [!NOTE]
> This will run TorchServe in the current terminal.
> See below to run TorchServe as a background process.

To start TorchServe:

```
torchserve --start --ncs \
           --model-store model_store/ \
           --models OkraClassifier=OkraClassifier.mar \
           --ts-config config.properties
```

To stop TorchServe:

`torchserve --stop`

## Daemonize TorchServe

To daemonize TorchServe, a background process must be created
that runs on startup. This can be accomplished by creating a
systemd service. Using a text editor such as `nano` or `vim`,
create a file: `/etc/systemd/system/start-torchserve.service`.
Copy and paste the following lines into the newly created file and
replace `%USER%` with the name of the user that should run
torchserve:

```
[Unit]
Description=TorchServe Service

[Service]
Type=simple
PIDFile=/run/torchserve.pid
WorkingDirectory=/home/%USER%/seniordesign/model_server
User=%USER%
Group=%USER%
ExecStart=/home/%USER%/seniordesign/python_env/bin/torchserve --start --ncs --model-store model_store/ --models OkraClassifier=OkraClassifier.mar --ts-config config.properties
ExecStop=/home/%USER%/seniordesign/python_env/bin/torchserve --stop
RemainAfterExit=true
TimeoutStartSec=infinity
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

The TorchServe service can now be managed using `systemctl`.

- Get the status of the service:

    `systemctl status start-torchserve`

- Enable the service to run on startup:

    `systemctl enable start-torchserve`

- Disable the service:

    `systemctl disable start-torchserve`

- Start the service:

    `systemctl start start-torchserve`

- Stop the service:

    `systemctl stop start-torchserve`
