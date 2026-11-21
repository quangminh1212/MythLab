@echo off
rem MythLab Truyen - chay server doc truyen (Go) o http://127.0.0.1:8765 va mo trinh duyet.
rem   run_reader.bat            cong 8765
rem   run_reader.bat 9000       cong khac
rem   run_reader.bat 8765 --lan   them tham so cho server (vd. --lan, --prefetch-covers)
rem Chua co mythlab-server.exe thi tu build bang apps\desktop\build.ps1 (can Go va Node.js).
rem Dat MYTHLAB_NO_BROWSER=1 de khong mo trinh duyet.
setlocal
cd /d "%~dp0"
set "EXE=%~dp0..\apps\desktop\dist\mythlab-server.exe"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8765"
if not exist "%EXE%" (
  echo Chua co mythlab-server.exe - dang build ^(lan dau mat vai phut^)...
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\apps\desktop\build.ps1"
  if errorlevel 1 ( echo Build loi. & pause & exit /b 1 )
)
if not exist "%EXE%" ( echo Khong thay %EXE% & pause & exit /b 1 )
shift
set "EXTRA="
:collect
if "%~1"=="" goto run
set "EXTRA=%EXTRA% %~1"
shift
goto collect
:run
if not defined MYTHLAB_NO_BROWSER start "" "http://127.0.0.1:%PORT%"
"%EXE%" --port %PORT% --config "%~dp0config.json" %EXTRA%
