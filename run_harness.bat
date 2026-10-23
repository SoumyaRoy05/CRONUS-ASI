@echo off
title CRONUS-ASI Automated Evaluation & Test Harness
color 0B
echo ==============================================================================
echo                CRONUS-ASI AUTOMATED HARNESS & EVALUATION RIG
echo ==============================================================================
echo.
cd /d "D:\Codes\CRONUS-ASI"
".venv\Scripts\python.exe" test_harness.py
echo.
echo Press any key to close this harness diagnostic window...
pause >nul
