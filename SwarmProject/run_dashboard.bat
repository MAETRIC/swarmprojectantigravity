@echo off
echo Starting SWED-A Dashboard Ecosystem...
echo.
echo Launching Python Backend...
start cmd /k "title SWED-A Backend API && color 0C && echo Starting Swarm Edge Defence Backend... && python api_server.py"
echo.
echo Launching React Frontend...
start cmd /k "title SWED-A Frontend UI && color 0B && cd dashboard && echo Starting Web UI Server... && npm run dev"
echo.
echo Successfully launched both servers! 
echo Please check your terminal windows and open the browser URL shown in the Frontend window (usually http://localhost:5173).
pause
