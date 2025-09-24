@echo off
echo ======================================
echo    RASA CHATBOT STARTUP SCRIPT
echo ======================================
echo.

REM Change to project directory
cd /d "C:\Users\sagar shresti\Desktop\CHATBOTPRO"

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation worked
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    echo Make sure you're in the correct directory and venv folder exists
    pause
    exit /b 1
)

echo Virtual environment activated successfully!
echo.

REM Start Rasa server in new window
echo Starting Rasa server...
start "Rasa Server" cmd /k "rasa run --enable-api --cors '*' --port 5005"

REM Wait for Rasa server to start
echo Waiting 15 seconds for Rasa server to initialize...
timeout /t 15 /nobreak > nul

REM Start Rasa Actions server in new window
echo Starting Rasa Actions server...
start "Rasa Actions" cmd /k "rasa run actions"

REM Wait for Actions server to start
echo Waiting 5 seconds for Actions server to initialize...
timeout /t 5 /nobreak > nul

REM Start FastAPI server in new window
echo Starting FastAPI web server...
start "FastAPI Server" cmd /k "python main.py"

REM Wait a bit for FastAPI to start
timeout /t 3 /nobreak > nul

echo.
echo ======================================
echo       ALL SERVERS STARTED!
echo ======================================
echo.
echo Your chatbot is now running at:
echo http://localhost:8000
echo.
echo Servers running in separate windows:
echo - Rasa Server: localhost:5005
echo - Rasa Actions: localhost:5055  
echo - FastAPI Web: localhost:8000
echo.
echo Press any key to open the chatbot in your browser...
pause > nul

REM Open browser
start http://localhost:8000

echo.
echo To stop all servers, close the terminal windows.
echo Press any key to exit this launcher...
pause > nul