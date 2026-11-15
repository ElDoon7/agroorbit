@echo off
title AgroOrbit - NASA Mission Control Launch Console
cd /d "%~dp0"
echo =========================================================================
echo    🛰️ AgroOrbit (Team: Nova Squad NASA)
echo    NASA Space Apps Challenge 2026 - Field Shift System
echo =========================================================================
echo.
echo Launching AgroOrbit on Streamlit...
echo Opening in Google Chrome / Default Browser at http://localhost:8501
echo.
"C:\Users\Mo7md\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m streamlit run app.py
pause
