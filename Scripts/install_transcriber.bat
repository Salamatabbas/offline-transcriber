@echo off
setlocal

set KMP_DUPLICATE_LIB_OK=TRUE
set "SCRIPT_DIR=%~dp0"

title Audio Transcriber Setup (Windows)

echo ========================================
echo Audio Transcriber Setup
echo ========================================
echo.

REM ============================
REM FFmpeg Check & Local Install
REM ============================

if exist "C:\ffmpeg\bin\ffmpeg.exe" set "PATH=C:\ffmpeg\bin;%PATH%"
if exist "C:\ffmpeg\bin\ffprobe.exe" set "PATH=C:\ffmpeg\bin;%PATH%"

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg not found. Installing FFmpeg locally in C:\ffmpeg...

  if not exist "C:\ffmpeg" (
    mkdir "C:\ffmpeg"
  )

  cd /d "C:\ffmpeg"

  echo Downloading FFmpeg...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

  if errorlevel 1 (
    echo.
    echo FFmpeg download failed. Please check your internet connection and try again.
    pause
    exit /b 1
  )

  echo Extracting FFmpeg...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive 'ffmpeg.zip' -DestinationPath 'C:\ffmpeg' -Force"

  if errorlevel 1 (
    echo.
    echo FFmpeg extraction failed.
    pause
    exit /b 1
  )

  for /d %%i in ("C:\ffmpeg\ffmpeg-*") do (
    xcopy /E /I /Y "%%i\*" "C:\ffmpeg\" >nul
    rmdir /S /Q "%%i"
  )

  del "C:\ffmpeg\ffmpeg.zip" >nul 2>nul

  set "PATH=C:\ffmpeg\bin;%PATH%"
  setx PATH "%PATH%" >nul

  echo FFmpeg installed in C:\ffmpeg\bin
) else (
  echo FFmpeg already installed.
)

where ffprobe >nul 2>nul
if errorlevel 1 (
  echo.
  echo FFprobe not found after FFmpeg installation.
  echo Please check whether C:\ffmpeg\bin\ffprobe.exe exists.
  pause
  exit /b 1
)

REM ============================
REM Python Check & Optional Install
REM ============================

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo Python was not found.
  echo This program requires Python 3.
  echo.

  choice /C YN /M "Do you want to install Python automatically now?"
  if errorlevel 2 (
    echo.
    echo Installation cancelled.
    echo Thank you. Please install Python later from:
    echo https://www.python.org/downloads/windows/
    echo.
    echo IMPORTANT: During installation, enable:
    echo   Add python.exe to PATH
    echo.
    pause
    exit /b 0
  )

  echo.
  echo Installing Python using winget...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo.
    echo winget was not found on this system.
    echo Please install Python manually from:
    echo https://www.python.org/downloads/windows/
    echo.
    echo IMPORTANT: During installation, enable:
    echo   Add python.exe to PATH
    echo.
    pause
    exit /b 1
  )

  winget install -e --id Python.Python.3

  echo.
  echo Checking Python installation...

  where python >nul 2>nul
  if errorlevel 1 (
    echo.
    echo Python was installed, but it is not available in this Command Prompt yet.
    echo Please close this window, open a new Command Prompt, and run this installer again.
    echo.
    pause
    exit /b 0
  )
)

echo Python found.

REM ============================
REM Python Dependencies
REM ============================

echo Installing Python dependencies...
python -m pip install --upgrade pip >nul 2>nul
python -m pip install --upgrade faster-whisper tqdm huggingface_hub >nul 2>nul

if errorlevel 1 (
  echo.
  echo Python dependency installation failed.
  echo Please check your internet connection and try again.
  pause
  exit /b 1
)

REM ============================
REM Model Selection
REM ============================

echo.
echo Choose model download option:
echo 1^) Fast      ^(small^)
echo 2^) Balanced  ^(medium^)
echo 3^) Accurate  ^(large^)
echo 4^) All Models ^(larger download^)
set /p MODELCHOICE=Enter choice [1-4]: 

if "%MODELCHOICE%"=="1" (
  python "%SCRIPT_DIR%preload_models.py" small
) else if "%MODELCHOICE%"=="2" (
  python "%SCRIPT_DIR%preload_models.py" medium
) else if "%MODELCHOICE%"=="3" (
  python "%SCRIPT_DIR%preload_models.py" large
) else if "%MODELCHOICE%"=="4" (
  python "%SCRIPT_DIR%preload_models.py" small medium large
) else (
  echo Invalid choice. Using medium.
  python "%SCRIPT_DIR%preload_models.py" medium
)

if errorlevel 1 (
  echo.
  echo Model download failed.
  echo Please check your internet connection and run this installer again.
  pause
  exit /b 1
)

REM ============================
REM Initialize Project
REM ============================

echo.
echo Initializing project folders...
python "%SCRIPT_DIR%transcribe.py" --init

if errorlevel 1 (
  echo.
  echo Project initialization failed.
  pause
  exit /b 1
)

echo.
echo Installation finished successfully.
echo.
echo If FFmpeg or Python is not recognized later, close and reopen Command Prompt.
pause
