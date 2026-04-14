@echo off
set KMP_DUPLICATE_LIB_OK=TRUE
title Audio Transcriber Setup (Windows)
echo ========================================
echo Audio Transcriber Setup
echo ========================================
echo.

if exist "C:\ffmpeg\bin\ffmpeg.exe" set PATH=C:\ffmpeg\bin;%PATH%
if exist "C:\ffmpeg\bin\ffprobe.exe" set PATH=C:\ffmpeg\bin;%PATH%

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found in PATH.
  echo Please install Python 3 and run this installer again.
  pause
  exit /b 1
)

python -m pip install --upgrade pip >nul 2>nul
python -m pip install --upgrade faster-whisper tqdm huggingface_hub >nul 2>nul

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg not found in PATH.
  echo Please install FFmpeg and run this installer again.
  pause
  exit /b 1
)

where ffprobe >nul 2>nul
if errorlevel 1 (
  echo FFprobe not found in PATH.
  echo Please install FFmpeg with ffprobe and run this installer again.
  pause
  exit /b 1
)

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
pause
