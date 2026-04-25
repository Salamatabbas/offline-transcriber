@echo off

set KMP_DUPLICATE_LIB_OK=TRUE
title Audio Transcriber Setup (Windows)
echo ========================================
echo Audio Transcriber Setup
echo ========================================
echo.

REM ============================
REM FFmpeg Check & Local Install
REM ============================

if exist "C:\ffmpeg\bin\ffmpeg.exe" set PATH=C:\ffmpeg\bin;%PATH%
if exist "C:\ffmpeg\bin\ffprobe.exe" set PATH=C:\ffmpeg\bin;%PATH%

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg not found. Installing FFmpeg locally in C:\ffmpeg...

  if not exist "C:\ffmpeg" (
    mkdir "C:\ffmpeg"
  )

  cd /d "C:\ffmpeg"

  echo Downloading FFmpeg...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

  echo Extracting FFmpeg...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive 'ffmpeg.zip' -DestinationPath 'C:\ffmpeg' -Force"

  for /d %%i in ("C:\ffmpeg\ffmpeg-*") do (
    xcopy /E /I /Y "%%i\*" "C:\ffmpeg\" >nul
    rmdir /S /Q "%%i"
  )

  del "C:\ffmpeg\ffmpeg.zip" >nul 2>nul

  set PATH=C:\ffmpeg\bin;%PATH%
  setx PATH "%PATH%" >nul

  echo FFmpeg installed in C:\ffmpeg\bin
) else (
  echo FFmpeg already installed.
)

where ffprobe >nul 2>nul
if errorlevel 1 (
  echo FFprobe not found after FFmpeg installation.
  echo Please check whether C:\ffmpeg\bin\ffprobe.exe exists.
  pause
  exit /b 1
)

REM ============================
REM Python Check
REM ============================

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found in PATH.
  echo Please install Python 3 and run this installer again.
  pause
  exit /b 1
)

echo Installing Python dependencies...
python -m pip install --upgrade pip >nul 2>nul
python -m pip install --upgrade faster-whisper tqdm huggingface_hub >nul 2>nul

echo.
echo Choose model download option:
echo 1^) Fast      ^(small^)
echo 2^) Balanced  ^(medium^)
echo 3^) Accurate  ^(large^)
echo 4^) All Models ^(larger download^)
set /p MODELCHOICE=Enter choice [1-4]: 

if "%MODELCHOICE%"=="1" (
  python "%~dp0preload_models.py" small
) else if "%MODELCHOICE%"=="2" (
  python "%~dp0preload_models.py" medium
) else if "%MODELCHOICE%"=="3" (
  python "%~dp0preload_models.py" large
) else if "%MODELCHOICE%"=="4" (
  python "%~dp0preload_models.py" small medium large
) else (
  echo Invalid choice. Using medium.
  python "%~dp0preload_models.py" medium
)

echo.
echo Initializing project folders...
python "%~dp0transcribe.py" --init

echo.
echo Installation finished.
echo If FFmpeg is not recognized later, please close and reopen Command Prompt.
pause
