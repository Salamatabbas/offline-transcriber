@echo off
title Model Upgrade Tool (Windows)
echo ========================================
echo Model Upgrade Tool (Windows)
echo ========================================
echo.

set KMP_DUPLICATE_LIB_OK=TRUE
cd /d %~dp0

if "%1"=="" goto menu

:args
if "%1"=="" goto doneargs
if "%1"=="-small" (
    echo Downloading model: small
    python preload_models.py small
) else if "%1"=="-medium" (
    echo Downloading model: medium
    python preload_models.py medium
) else if "%1"=="-large" (
    echo Downloading model: large
    python preload_models.py large
) else (
    echo Unknown option: %1
)
shift
goto args

:doneargs
echo.
echo Upgrade finished.
pause
exit /b 0

:menu
echo Choose model to install:
echo 1^) Fast      ^(small^)
echo 2^) Balanced  ^(medium^)
echo 3^) Accurate  ^(large^)
echo 4^) All Models
set /p choice=Enter choice [1-4]:

if "%choice%"=="1" (
    python preload_models.py small
) else if "%choice%"=="2" (
    python preload_models.py medium
) else if "%choice%"=="3" (
    python preload_models.py large
) else if "%choice%"=="4" (
    python preload_models.py small medium large
) else (
    echo Invalid choice
)

echo.
echo Upgrade finished.
pause
