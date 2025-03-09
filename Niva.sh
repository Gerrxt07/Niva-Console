#!/usr/bin/env bash

clear
which python
if [ $? -ne 0 ]; then
    echo "Python not found. Please install Python 3.11 or higher."
    exit 1
else
    echo "Python found"
fi

which pip
if [ $? -ne 0 ]; then
    echo "pip not found. Please install pip."
    exit 1
else
    echo "pip found"
fi

which git
if [ $? -ne 0 ]; then
    echo "git not found. Please install git."
    exit 1
else
    echo "git found"
fi

sleep 3
clear

echo "Installing dependencies..."
sleep 1
pip install -r requirements.txt

sleep 3
clear

python Niva.py

read -n 1 -s -r -p "Press any key to continue..."