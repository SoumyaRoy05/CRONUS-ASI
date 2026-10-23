Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\Codes\CRONUS-ASI"
WshShell.Run """D:\Codes\CRONUS-ASI\.venv\Scripts\pythonw.exe"" ""D:\Codes\CRONUS-ASI\cronus_tray.py""", 0, False
