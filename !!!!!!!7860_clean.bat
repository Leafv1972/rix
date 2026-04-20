netstat -ano | findstr ":7860 :7861 :7862"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7860"') do (
    echo Killing process %%a on port 7860
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7861"') do (
    echo Killing process %%a on port 7861
    taskkill /F /PID %%a 2>nul
)