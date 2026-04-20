chcp 65001 >nul
cd /d "%~dp0"
netstat -ano | findstr ":7860 :7861 :7862"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7860"') do (
    echo Killing process %%a on port 7860
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7861"') do (
    echo Killing process %%a on port 7861
    taskkill /F /PID %%a 2>nul
)
".\py312b10gradio610\python.exe" textstat_gradio610_webui.py
pause
