@echo off
cd c:\Users\manji\OneDrive\Desktop\swarmprojectantigravity\SwarmProject
echo Initializing Vite React Dashboard...
call npx -y create-vite@latest dashboard --template react
cd dashboard
echo Installing Dependencies...
call npm install
call npm install tailwindcss postcss autoprefixer recharts lucide-react socket.io-client
call npx -y tailwindcss init -p
echo Build Setup Complete!
