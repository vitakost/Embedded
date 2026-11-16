@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if "%DEVICE_PORT%"=="" set DEVICE_PORT=rfc2217://127.0.0.1:4000
set RUNS=%1
if "%RUNS%"=="" set RUNS=5
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found in %CD% - create it first, see VSCODE_SETUP.md
  exit /b 1
)
if not exist evidence mkdir evidence
.venv\Scripts\python.exe --version > evidence\env.txt
.venv\Scripts\python.exe -m pip show pytest pyserial >> evidence\env.txt
echo DEVICE_PORT=%DEVICE_PORT% >> evidence\env.txt
echo --- cmd AutoRun (HKCU / HKLM) >> evidence\env.txt
reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun >> evidence\env.txt 2>&1
reg query "HKLM\Software\Microsoft\Command Processor" /v AutoRun >> evidence\env.txt 2>&1
.venv\Scripts\python.exe probe_raw.py evidence\raw_probe.log
echo PING latency check ...
.venv\Scripts\python.exe ping_latency.py evidence\ping_latency.log
echo Baseline run, client timeout 1.0 s ...
set DEVICE_TIMEOUT=1.0
set SERIAL_LOG=evidence\serial_baseline_t1.log
.venv\Scripts\python.exe -m pytest -v > evidence\pytest_baseline_t1.txt 2>&1
call :check evidence\pytest_baseline_t1.txt
set DEVICE_TIMEOUT=3.0
for /L %%i in (1,1,%RUNS%) do call :run %%i
echo DONE
goto :eof
:run
echo Regression run %1 of %RUNS%, client timeout 3.0 s ...
set SERIAL_LOG=evidence\serial_run%1.log
.venv\Scripts\python.exe -m pytest -v > evidence\pytest_run%1.txt 2>&1
call :check evidence\pytest_run%1.txt
goto :eof
:check
findstr /r /c:"=* [0-9]* passed" /c:"=* [0-9]* failed" %1 >nul
if errorlevel 1 (echo WARNING: no pytest summary in %1) else (echo %1 complete)
goto :eof
