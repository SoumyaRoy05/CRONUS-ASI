@echo off
title CRONUS ASI - Sovereign Terminal
color 0B
echo ============================================================
echo               CRONUS ASI - SOVEREIGN TERMINAL               
echo ============================================================
cd /d "D:\Codes\CRONUS-ASI"
call .venv\Scripts\activate.bat
python cronus.py
pause
