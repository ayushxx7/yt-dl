:: echo "Installing Chocolatey Package Manager"
:: Powershell.exe -executionpolicy bypass -File choco_install_powershell.ps1
:: echo "Install ffmpeg using Chocolatey. Required for merging audio and video files."
:: call cmd /k choco install ffmpeg -y
py -m pip install -r requirements.txt
py download_all.py
