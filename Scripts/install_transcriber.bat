@echo off
setlocal EnableDelayedExpansion

set KMP_DUPLICATE_LIB_OK=TRUE
set "SCRIPT_DIR=%~dp0"

color 0B
title Audio Transcriber Setup (Windows)

echo.
echo ==================================================
echo        Audio Transcriber Setup for Windows
echo ==================================================
echo.

REM ============================
REM Spinner Function
REM ============================

set spinner=|/-\

:spin
set /a idx=(idx+1) %% 4
<nul set /p= !spinner:~%idx%,1!
timeout /t 1 >nul
<nul set /p=
goto :eof

REM ============================
REM FFmpeg
REM ============================

echo [1/5] Checking FFmpeg...

if exist "C:\ffmpeg\bin\ffmpeg.exe" set "PATH=C:\ffmpeg\bin;%PATH%"
if exist "C:\ffmpeg\bin\ffprobe.exe" set "PATH=C:\ffmpeg\bin;%PATH%"

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo Installing FFmpeg... Please wait.

  if not exist "C:\ffmpeg" mkdir "C:\ffmpeg"
  cd /d "C:\ffmpeg"

  start "" /b cmd /c powershell -Command ^
  "Invoke-WebRequest 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'" >nul 2>nul

  for /l %%i in (1,1,8) do call :spin

  powershell -Command "Expand-Archive 'ffmpeg.zip' -DestinationPath 'C:\ffmpeg' -Force" >nul 2>nul

  for /d %%i in ("C:\ffmpeg\ffmpeg-*") do (
    xcopy /E /I /Y "%%i\*" "C:\ffmpeg\" >nul
    rmdir /S /Q "%%i"
  )

  del ffmpeg.zip >nul 2>nul
  set PATH=C:\ffmpeg\bin;%PATH%
  setx PATH "%PATH%" >nul

  echo.
  echo FFmpeg installed.
) else (
  echo FFmpeg already installed.
)

REM ============================
REM Python
REM ============================

echo.
echo [2/5] Checking Python...

python --version >nul 2>nul
if errorlevel 1 (
  echo Python not found.

  choice /C YN /M "Install Python automatically?"
  if errorlevel 2 exit /b

  echo Installing Python...

  start "" /b cmd /c winget install -e --id Python.Python.3.13 --source winget --accept-package-agreements --accept-source-agreements >nul 2>nul

  for /l %%i in (1,1,10) do call :spin

  echo.
  echo Restart installer after Python install.
  pause
  exit /b
)

echo Python OK.

REM ============================
REM Dependencies
REM ============================

echo.
echo [3/5] Installing dependencies...

start "" /b cmd /c python -m pip install faster-whisper tqdm huggingface_hub >nul 2>nul

for /l %%i in (1,1,10) do call :spin

echo.
echo Dependencies installed.

REM ============================
REM Model
REM ============================

echo.
echo [4/5] Select model:
echo 1) small
echo 2) medium
echo 3) large
echo 4) all

set /p MODELCHOICE=Choice: 

echo Downloading model... please wait.

start "" /b cmd /c python "%SCRIPT_DIR%preload_models.py" >nul 2>nul

for /l %%i in (1,1,15) do call :spin

echo.
echo Model ready.

REM ============================
REM Init
REM ============================

echo.
echo [5/5] Finalizing setup...

start "" /b cmd /c python "%SCRIPT_DIR%transcribe.py" --init >nul 2>nul

for /l %%i in (1,1,5) do call :spin

color 0A
echo.
echo ========================================
echo        Installation COMPLETE
echo ========================================
echo.

pause
