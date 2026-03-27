@echo off
echo ==========================================
echo FIXING MISSING DEPENDENCIES AUTOMATICALLY
echo ==========================================
echo.
echo Please make sure you closed the previous red/blue terminal windows!
echo If you haven't, please close them now before continuing.
pause
echo.
echo Installing Python Backend Packages...
call pip install fastapi uvicorn websockets python-socketio
echo.
echo Installing Node.js Frontend Packages...
cd c:\Users\manji\OneDrive\Desktop\swarmprojectantigravity\SwarmProject\dashboard
call npm install lucide-react recharts socket.io-client tailwindcss postcss autoprefixer
echo.
echo ==========================================
echo DONE! YOU CAN NOW RUN run_dashboard.bat AGAIN!
echo ==========================================
pause
