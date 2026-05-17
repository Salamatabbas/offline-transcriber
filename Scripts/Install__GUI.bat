@echo off
setlocal

:: مسیر اسکریپت
set "SCRIPT_DIR=%~dp0"

:: حل مشکل OpenMP
set KMP_DUPLICATE_LIB_OK=TRUE

color 0B
title Audio Transcriber GUI Installer (Windows)

echo.
echo ==================================================
echo        Audio Transcriber GUI Installer
echo ==================================================
echo.

:: ============================
:: FFmpeg
:: ============================
echo [1/5] Checking FFmpeg...

if exist "C:\ffmpeg\bin\ffmpeg.exe" set "PATH=C:\ffmpeg\bin;%PATH%"
if exist "C:\ffmpeg\bin\ffprobe.exe" set "PATH=C:\ffmpeg\bin;%PATH%"

where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo FFmpeg not found. Installing...
    if not exist "C:\ffmpeg" mkdir "C:\ffmpeg"
    cd /d "C:\ffmpeg"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'" >nul 2>nul
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive 'ffmpeg.zip' -DestinationPath 'C:\ffmpeg' -Force" >nul 2>nul
    for /d %%i in ("C:\ffmpeg\ffmpeg-*") do (
        xcopy /E /I /Y "%%i\*" "C:\ffmpeg\" >nul
        rmdir /S /Q "%%i"
    )
    del "C:\ffmpeg\ffmpeg.zip" >nul 2>nul
    set "PATH=C:\ffmpeg\bin;%PATH%"
    setx PATH "%PATH%" >nul 2>nul
    echo FFmpeg installed successfully.
) else (
    echo FFmpeg already installed.
)

where ffprobe >nul 2>nul
if errorlevel 1 (
    color 0C
    echo ERROR: FFprobe not found.
    pause
    exit /b 1
)

:: ============================
:: Python
:: ============================
echo.
echo [2/5] Checking Python...

python --version >nul 2>nul
if errorlevel 1 (
    echo Python not found. Installing automatically...
    where winget >nul 2>nul
    if errorlevel 1 (
        color 0C
        echo ERROR: winget is not available. Install Python manually.
        pause
        exit /b 1
    )
    winget install -e --id Python.Python.3.13 --source winget --accept-package-agreements --accept-source-agreements >nul 2>nul
    if errorlevel 1 (
        winget install -e --id Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements >nul 2>nul
    )
    if errorlevel 1 (
        color 0C
        echo ERROR: Python installation failed.
        pause
        exit /b 1
    )
    echo Python installed successfully. Restart installer.
    pause
    exit /b 0
)
echo Python OK.

:: ============================
:: Python Dependencies
:: ============================
echo.
echo [3/5] Installing Python dependencies...
python -m ensurepip --upgrade >nul 2>nul
python -m pip install --upgrade pip >nul 2>nul
python -m pip install --upgrade faster-whisper tqdm huggingface_hub >nul 2>nul
echo Dependencies installed successfully.

:: ============================
:: Install All Models (GUI)
:: ============================
echo.
echo [4/5] Installing transcription models...
python "%SCRIPT_DIR%preload_models.py" small medium large >nul 2>nul
echo All models installed successfully.

:: ============================
:: Initialize Project
:: ============================
echo.
echo [5/5] Initializing project folders...
python "%SCRIPT_DIR%transcribe.py" --init >nul 2>nul
echo Project folders initialized.

:: ============================
:: GUI Launcher
:: ============================
echo.
echo Creating GUI launcher...
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "LOCAL_LAUNCHER=%PROJECT_DIR%\Transcribe_GUI.bat"
set "ICON_PATH=%PROJECT_DIR%\Assets\transcribe.ico"

(
    echo @echo off
    echo set KMP_DUPLICATE_LIB_OK=TRUE
    echo if exist "C:\ffmpeg\bin\ffmpeg.exe" set PATH=C:\ffmpeg\bin;%%PATH%%
    echo if exist "C:\ffmpeg\bin\ffprobe.exe" set PATH=C:\ffmpeg\bin;%%PATH%%
    echo python "%%~dp0scripts\transcribe_gui.py" %%*
) > "%LOCAL_LAUNCHER%"

:: Create desktop shortcut for GUI
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$desktop=[Environment]::GetFolderPath('Desktop'); ^
$target='%LOCAL_LAUNCHER%'; ^
$shortcut=Join-Path $desktop 'Transcribe_GUI.lnk'; ^
$ws=New-Object -ComObject WScript.Shell; ^
$s=$ws.CreateShortcut($shortcut); ^
$s.TargetPath=$target; ^
$s.WorkingDirectory='%PROJECT_DIR%'; ^
$ico='%ICON_PATH%'; ^
if (Test-Path $ico) { $s.IconLocation=$ico }; ^
$s.Save();" >nul 2>nul

echo GUI launcher created:
echo   %LOCAL_LAUNCHER%
echo Desktop shortcut: Transcribe_GUI.lnk

pause
exit /b 0