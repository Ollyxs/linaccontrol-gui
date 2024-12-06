@echo off
call python -m venv venv
call venv\Scripts\activate
call python -m pip install --upgrade pip
call python -m pip install -r requirements.txt
