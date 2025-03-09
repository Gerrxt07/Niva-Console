@ECHO OFF
TITLE Niva

CLS

where python
IF ERRORLEVEL 1 (
    ECHO Python not found. Please install Python 3.11 or higher.
    EXIT /B 1
) ELSE (
    ECHO Python found
)

where pip
IF ERRORLEVEL 1 (
    ECHO pip not found. Please install pip.
    EXIT /B 1
) ELSE (
    ECHO pip found
)

where git
IF ERRORLEVEL 1 (
    ECHO git not found. Please install git.
    EXIT /B 1
) ELSE (
    ECHO git found
)

TIMEOUT /T 3 /NOBREAK > NUL
CLS

ECHO Installing dependencies...
TIMEOUT /T 1 /NOBREAK > NUL
pip install -r requirements.txt

TIMEOUT /T 3 /NOBREAK > NUL
CLS

python Niva.py

PAUSE