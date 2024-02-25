#!/bin/bash

VENV_DIR="venvs/neu-mate"

# Check the platform (Windows or Linux)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # On Windows, activate using the activate.bat script
    source "$VENV_DIR/Scripts/activate"
else
    # On Linux and other Unix-like systems, activate using the activate script
    source "$VENV_DIR/bin/activate"
fi
