# Configuring Python

Before running this project, you must have the correct version of Python
and all [PyPI](https://pypi.org/) dependencies installed.

## Install Python

Python version 3.12 should be installed on your device.
Python can be downloaded from the
[official Python download page](https://www.python.org/downloads/).

> [!IMPORTANT]
> As of January 2025, PyTorch [does not support Python 3.13](https://pytorch.org/get-started/locally/#windows-python)
> on all systems. If you install version 3.13, PyTorch may not work correctly!

To check your Python version, run the following command:

`python -V`

> [!NOTE]
> Depending on your system configuration and how you installed Python, the command
> to run Python could be `python`, `python3`, or even `py`. To keep things simple,
> the command `python` will be used in the following instructions.

## Configuring A Python Virtual Environment

Open a terminal and navigate to the project's root directory `seniordesign/`.
Create a new [virtual environment](https://docs.python.org/3.12/library/venv.html)
with the command:

`python -m venv python_env`

To start using the virtual environment,
you must first source it in your terminal:

- **Linux and MacOS**
    - `source python_env/bin/activate`
- **Windows**
    - In cmd.exe: `python_env\Scripts\activate.bat`
    - In Powershell: `python_env\Scripts\Activate.ps1`

If successful, you will see the text `(python_env)` appear at the beginning
of the prompt line in your terminal.

> [!IMPORTANT]
> You may have to source the virtual environment every time you
> start your terminal. Make sure `(python_env)` appears in your terminal
> before running python or pip!

To show the packages installed in your Python virtual environment run:

`pip list -l`

## Installing Packages

Navigate in your terminal to the directory `seniordesign/Python/`.
Packages will be installed using [pip](https://pip.pypa.io/en/stable/).

### Developer Installation

`pip install -r dev-requirements.txt`

Also, install PyTorch using the command provided by
[their website](https://pytorch.org/get-started/locally/).
From the options on the linked page, select the following:

| PyTorch Build  | Your OS | Package | Language | Platform         |
| -------------- | ------- | ------- | -------- | ---------------- |
| `Stable (2.x)` | Your OS | `Pip`   | `Python` | `CPU` (see note) |

> [!NOTE]
> To run this project, only a CPU is needed, but if you would like to train a model, a
> GPU is recommended. If you would like to use your GPU you can install a version of
> PyTorch with the latest
> [CUDA version that your GPU supports](https://en.wikipedia.org/wiki/CUDA#GPUs_supported).

### Server Installation

> [!NOTE]
> This method is for installation on a server running a Linux distro.
> The correct version of PyTorch will automatically be installed.

`pip install -r server-requirements.txt`
