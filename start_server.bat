@echo off
REM Start the NAS Django backend using Waitress (Windows-compatible WSGI server).
REM Run this file to launch the backend in production mode.
REM Requires .env to be configured (copy .env.example and fill in values).

cd /d E:\NAS
call venv\Scripts\activate
cd nas_server
waitress-serve --port=8000 --threads=4 nas_server.wsgi:application
