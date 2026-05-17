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

REM ============================
REM FFmpeg
REM ============================

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

  if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: FFmpeg extraction failed.
    pause
    exit /b 1
  )

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

REM ============================
REM Python
REM ============================

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

REM ============================
REM Python Dependencies
REM ============================

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

REM ============================
REM Model Selection
REM ============================

echo.
echo [4/5] Choose transcription model:
echo.
echo   1^) Fast      - small
echo   2^) Balanced  - medium
echo   3^) Accurate  - large
echo   4^) All Models
echo   5^) I already have the models - skip model download
echo.
set /p MODELCHOICE=Enter choice [1-5]: 

echo.

if "%MODELCHOICE%"=="1" (
  echo      Downloading small model. Please wait...
  python "%SCRIPT_DIR%preload_models.py" small >nul 2>nul
) else if "%MODELCHOICE%"=="2" (
  echo      Downloading medium model. Please wait...
  python "%SCRIPT_DIR%preload_models.py" medium >nul 2>nul
) else if "%MODELCHOICE%"=="3" (
  echo      Downloading large model. Please wait...
  python "%SCRIPT_DIR%preload_models.py" large >nul 2>nul
) else if "%MODELCHOICE%"=="4" (
  echo      Downloading all models. Please wait...
  python "%SCRIPT_DIR%preload_models.py" small medium large >nul 2>nul
) else if "%MODELCHOICE%"=="5" (
  echo      Model download skipped.
  goto after_model_download
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

:after_model_download
echo      Model setup completed.

REM ============================
REM Initialize Project
REM ============================

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

REM ============================
REM Launcher Creation
REM ============================

echo.
echo Creating Windows launcher...

set "PROJECT_DIR=%SCRIPT_DIR%.."
set "LOCAL_LAUNCHER=%PROJECT_DIR%\Transcribe.bat"
set "ICON_PATH=%PROJECT_DIR%\Assets\transcribe.ico"

REM Create reliable launcher inside the main project folder.
(
  echo @echo off
  echo title Offline Transcriber
  echo color 0B
  echo cd /d "%SCRIPT_DIR%"
  echo echo.
  echo echo ==================================================
  echo echo        Offline Transcriber
  echo echo ==================================================
  echo echo.
  echo echo Put your audio files in:
  echo echo   "%PROJECT_DIR%\Input"
  echo echo.
  echo echo Common commands:
  echo echo.
  echo echo   transcribe.bat
  echo echo   transcribe.bat -single audio.mp3
  echo echo   transcribe.bat -single audio.mp3 -translate
  echo echo   transcribe.bat -single audio.mp3 -srt
  echo echo   transcribe.bat -large
  echo echo.
  echo echo You are now in the Scripts folder.
  echo echo Type a command above and press Enter.
  echo echo.
  echo cmd /k
) > "%LOCAL_LAUNCHER%"

REM Create desktop shortcut pointing to the reliable local launcher.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop=[Environment]::GetFolderPath('Desktop'); $target='%LOCAL_LAUNCHER%'; $shortcut=Join-Path $desktop 'Transcribe.lnk'; $ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut($shortcut); $s.TargetPath=$target; $s.WorkingDirectory='%PROJECT_DIR%'; $ico='%ICON_PATH%'; if (Test-Path $ico) { $s.IconLocation=$ico }; $s.Save();" >nul 2>nul

echo Launcher created inside project:
echo   %LOCAL_LAUNCHER%

echo Desktop shortcut attempted:
echo   Transcribe.lnk

REM ============================
REM Finish
REM ============================

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
echo Or double-click the Transcribe launcher.
echo.

pause
