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
REM FFmpeg
REM ============================

if exist "C:\ffmpeg\bin\ffmpeg.exe" set "PATH=C:\ffmpeg\bin;%PATH%"
if exist "C:\ffmpeg\bin\ffprobe.exe" set "PATH=C:\ffmpeg\bin;%PATH%"

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg not found. Installing...

  if not exist "C:\ffmpeg" mkdir "C:\ffmpeg"
  cd /d "C:\ffmpeg"

  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

  if errorlevel 1 (
    echo FFmpeg download failed.
    pause
    exit /b 1
  )

  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Expand-Archive 'ffmpeg.zip' -DestinationPath 'C:\ffmpeg' -Force"

  for /d %%i in ("C:\ffmpeg\ffmpeg-*") do (
    xcopy /E /I /Y "%%i\*" "C:\ffmpeg\" >nul
    rmdir /S /Q "%%i"
  )

  del ffmpeg.zip >nul 2>nul

  set "PATH=C:\ffmpeg\bin;%PATH%"
  setx PATH "%PATH%" >nul

  echo FFmpeg installed.
) else (
  echo FFmpeg already installed.
)

where ffprobe >nul 2>nul
if errorlevel 1 (
  echo FFprobe not found.
  pause
  exit /b 1
)

REM ============================
REM Python check (REAL)
REM ============================

echo.
echo Checking Python...

python --version >nul 2>nul
if errorlevel 1 (
  echo.
  echo Python is not properly installed.
  echo.

  choice /C YN /M "Install Python automatically?"
  if errorlevel 2 (
    echo Installation cancelled.
    pause
    exit /b 0
  )

  where winget >nul 2>nul
  if errorlevel 1 (
    echo winget not available.
    echo Please install Python manually:
    echo https://www.python.org/downloads/windows/
    echo IMPORTANT: enable "Add Python to PATH"
    pause
    exit /b 1
  )

  echo Installing Python...

  winget install -e --id Python.Python.3.13 --source winget
  if errorlevel 1 (
    echo Trying Python 3.12...
    winget install -e --id Python.Python.3.12 --source winget
  )

  if errorlevel 1 (
    echo Python installation failed.
    echo Install manually from:
    echo https://www.python.org/downloads/windows/
    pause
    exit /b 1
  )

  echo.
  echo Python installed.
  echo Close this window and run installer again.
  pause
  exit /b 0
)

echo Python OK.

REM ============================
REM pip setup
REM ============================

echo.
echo Preparing pip...

python -m ensurepip --upgrade
python -m pip install --upgrade pip

REM ============================
REM dependencies
REM ============================

echo.
echo Installing dependencies...

python -m pip install faster-whisper tqdm huggingface_hub

if errorlevel 1 (
  echo.
  echo Dependency installation FAILED.
  echo See error above.
  pause
  exit /b 1
)

echo Dependencies installed.

REM ============================
REM model selection
REM ============================

echo.
echo Choose model:
echo 1^) small
echo 2^) medium
echo 3^) large
echo 4^) all
set /p MODELCHOICE=Choice: 

if "%MODELCHOICE%"=="1" (
  python "%SCRIPT_DIR%preload_models.py" small
) else if "%MODELCHOICE%"=="2" (
  python "%SCRIPT_DIR%preload_models.py" medium
) else if "%MODELCHOICE%"=="3" (
  python "%SCRIPT_DIR%preload_models.py" large
) else if "%MODELCHOICE%"=="4" (
  python "%SCRIPT_DIR%preload_models.py" small medium large
) else (
  python "%SCRIPT_DIR%preload_models.py" medium
)

if errorlevel 1 (
  echo Model download failed.
  pause
  exit /b 1
)

REM ============================
REM init
REM ============================

echo.
echo Initializing project...
python "%SCRIPT_DIR%transcribe.py" --init

if errorlevel 1 (
  echo Init failed.
  pause
  exit /b 1
)

echo.
echo ========================================
echo Installation SUCCESSFUL
echo ========================================
echo.

pause
