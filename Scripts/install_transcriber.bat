@echo off
setlocal

set KMP_DUPLICATE_LIB_OK=TRUE
set "SCRIPT_DIR=%~dp0"

color 0B
title Audio Transcriber Setup (Windows)

echo.
echo ==================================================
echo        Audio Transcriber Setup for Windows
echo ==================================================
echo.
echo This installer will prepare:
echo   - FFmpeg
echo   - Python
echo   - Python dependencies
echo   - Transcription model files
echo.
echo Please keep this window open until setup finishes.
echo.

echo [1/5] Checking FFmpeg...

if exist "C:\ffmpeg\bin\ffmpeg.exe" set "PATH=C:\ffmpeg\bin;%PATH%"
if exist "C:\ffmpeg\bin\ffprobe.exe" set "PATH=C:\ffmpeg\bin;%PATH%"

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo      FFmpeg not found. Installing FFmpeg...

  if not exist "C:\ffmpeg" mkdir "C:\ffmpeg"
  cd /d "C:\ffmpeg"

  echo      Downloading FFmpeg. Please wait...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'" >nul 2>nul

  if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: FFmpeg download failed.
    pause
    exit /b 1
  )

  echo      Extracting FFmpeg. Please wait...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive 'ffmpeg.zip' -DestinationPath 'C:\ffmpeg' -Force" >nul 2>nul

  for /d %%i in ("C:\ffmpeg\ffmpeg-*") do (
    xcopy /E /I /Y "%%i\*" "C:\ffmpeg\" >nul
    rmdir /S /Q "%%i"
  )

  del "C:\ffmpeg\ffmpeg.zip" >nul 2>nul

  set "PATH=C:\ffmpeg\bin;%PATH%"
  setx PATH "%PATH%" >nul 2>nul

  echo      FFmpeg installed successfully.
) else (
  echo      FFmpeg already installed.
)

where ffprobe >nul 2>nul
if errorlevel 1 (
  color 0C
  echo.
  echo ERROR: FFprobe was not found.
  pause
  exit /b 1
)

echo.
echo [2/5] Checking Python...

python --version >nul 2>nul
if errorlevel 1 (
  echo      Python is not properly installed.
  echo.

  choice /C YN /M "Install Python automatically?"
  if errorlevel 2 (
    echo.
    echo Setup cancelled.
    pause
    exit /b 0
  )

  where winget >nul 2>nul
  if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: winget is not available.
    echo Please install Python manually from:
    echo https://www.python.org/downloads/windows/
    echo.
    pause
    exit /b 1
  )

  echo      Installing Python. Please wait...
  winget install -e --id Python.Python.3.13 --source winget --accept-package-agreements --accept-source-agreements >nul 2>nul
  if errorlevel 1 (
    echo      Python 3.13 failed. Trying Python 3.12...
    winget install -e --id Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements >nul 2>nul
  )

  if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: Python installation failed.
    echo Please install Python manually from:
    echo https://www.python.org/downloads/windows/
    pause
    exit /b 1
  )

  echo.
  echo Python installed successfully.
  echo Please close this window and run the installer again.
  pause
  exit /b 0
)

echo      Python OK.

echo.
echo [3/5] Installing Python dependencies...
echo      Please wait...

python -m ensurepip --upgrade >nul 2>nul
python -m pip install --upgrade pip >nul 2>nul
python -m pip install --upgrade faster-whisper tqdm huggingface_hub >nul 2>nul

if errorlevel 1 (
  color 0C
  echo.
  echo ERROR: Python dependency installation failed.
  echo Please check your internet connection and try again.
  pause
  exit /b 1
)

echo      Dependencies installed successfully.

echo.
echo [4/5] Choose transcription model:
echo.
echo   1^) Fast      - small
echo   2^) Balanced  - medium
echo   3^) Accurate  - large
echo   4^) All Models
echo.
set /p MODELCHOICE=Enter choice [1-4]: 

echo.
echo      Downloading selected model(s).
echo      This may take several minutes. Please wait...

if "%MODELCHOICE%"=="1" (
  python "%SCRIPT_DIR%preload_models.py" small >nul 2>nul
) else if "%MODELCHOICE%"=="2" (
  python "%SCRIPT_DIR%preload_models.py" medium >nul 2>nul
) else if "%MODELCHOICE%"=="3" (
  python "%SCRIPT_DIR%preload_models.py" large >nul 2>nul
) else if "%MODELCHOICE%"=="4" (
  python "%SCRIPT_DIR%preload_models.py" small medium large >nul 2>nul
) else (
  echo      Invalid choice. Using medium model.
  python "%SCRIPT_DIR%preload_models.py" medium >nul 2>nul
)

if errorlevel 1 (
  color 0C
  echo.
  echo ERROR: Model download failed.
  echo Please check your internet connection and run this installer again.
  pause
  exit /b 1
)

echo      Model setup completed.

echo.
echo [5/5] Initializing project folders...

python "%SCRIPT_DIR%transcribe.py" --init >nul 2>nul

if errorlevel 1 (
  color 0C
  echo.
  echo ERROR: Project initialization failed.
  pause
  exit /b 1
)

echo.
color 09
echo ==================================================
echo        Installation completed
color 0F
echo        Setup is ready to use
color 0C
echo        Enjoy transcribing!
color 0B
echo ==================================================
echo.
echo You can now place audio files in the Input folder
echo and run:
echo.
echo   transcribe.bat
echo.
pause
