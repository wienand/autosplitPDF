@ECHO OFF
SET SCRIPT_DIR=%~dp0

IF EXIST "%SCRIPT_DIR%\pyFlask64" (
    CALL "%SCRIPT_DIR%\pyFlask64\scripts\activate"
)

python "%SCRIPT_DIR%\autosplitPDF.py" -v %*

IF ERRORLEVEL 1 PAUSE