@echo off
set KMP_DUPLICATE_LIB_OK=TRUE
title Audio Transcriber (Windows)
if exist "C:\ffmpeg\bin\ffmpeg.exe" set PATH=C:\ffmpeg\bin;%PATH%
if exist "C:\ffmpeg\bin\ffprobe.exe" set PATH=C:\ffmpeg\bin;%PATH%
python "%~dp0transcribe.py" %*
pause
