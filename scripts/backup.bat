@echo off
REM ==============================================
REM Script de sauvegarde automatique Windows
REM Planifier avec: schtasks /create /sc daily /tn "SchoolBackup" /tr "python scripts\backup.py"
REM ==============================================

cd /d "%~dp0.."
python scripts\backup.py
