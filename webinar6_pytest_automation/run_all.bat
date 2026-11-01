@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if "%DEVICE_PORT%"=="" set DEVICE_PORT=rfc2217://127.0.0.1:4000
set RUNS=%1
if "%RUNS%"=="" set RUNS=5
if not exist evidence mkdir evidence
.venv\Scripts\python.exe --version > evidence\env.txt
.venv\Scripts\python.exe -m pip show pytest pyserial >> evidence\env.txt
echo DEVICE_PORT=%DEVICE_PORT% >> evidence\env.txt
.venv\Scripts\python.exe probe_raw.py evidence\raw_probe.log
echo Baseline run, client timeout 1.0 s ...
set DEVICE_TIMEOUT=1.0
set SERIAL_LOG=evidence\serial_baseline_t1.log
.venv\Scripts\python.exe -m pytest -v > evidence\pytest_baseline_t1.txt 2>&1
set DEVICE_TIMEOUT=3.0
for /L %%i in (1,1,%RUNS%) do call :run %%i
echo DONE
goto :eof
:run
echo Regression run %1 of %RUNS%, client timeout 3.0 s ...
set SERIAL_LOG=evidence\serial_run%1.log
.venv\Scripts\python.exe -m pytest -v > evidence\pytest_run%1.txt 2>&1
goto :eof
