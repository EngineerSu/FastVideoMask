@echo off
chcp 65001 >nul 2>&1

echo ========================================
echo   FastVideoMask Build Script
echo ========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

echo [1/3] Checking PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [INSTALL] Installing PyInstaller...
    python -m pip install pyinstaller
)

echo.
echo [2/3] Building...
echo.

python -m PyInstaller --onefile --windowed --name "FastVideoMask" --clean --noconfirm main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

if exist "%USERPROFILE%\dist\FastVideoMask.exe" (
    if not exist "dist" mkdir dist
    move "%USERPROFILE%\dist\FastVideoMask.exe" "dist\FastVideoMask.exe" >nul 2>&1
)

echo.
echo [3/3] Build complete!
echo.
echo Output: %~dp0dist\FastVideoMask.exe
echo.
echo ========================================
pause
