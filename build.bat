@echo off
echo ========================================
echo   Markdown Editor - Build Script
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Build with PyInstaller
echo Building standalone executable...
pyinstaller --clean MarkdownEditor.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Build successful!
    echo   Output: dist\MarkdownEditor.exe
    echo ========================================
) else (
    echo.
    echo Build failed. Please check the errors above.
)

pause
