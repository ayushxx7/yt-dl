set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )
echo "Installing Chocolatey Package Manager"
Powershell.exe -executionpolicy bypass -File choco_install_powershell.ps1
echo "Install ffmpeg using Chocolatey. Required for merging audio and video files."
start cmd /k "choco install ffmpeg -y"
py -m pip install -r requirements.txt
py download_all.py
