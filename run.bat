@echo off
cd /d E:\0000ew V2Claude
python -m uvicorn backend.main:app --reload --port 8000
pause
