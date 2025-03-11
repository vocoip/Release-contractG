@echo off 
chcp 65001 > nul 
echo Installing contract generation tool... 
if not exist "%PROGRAMFILES%\contractG" mkdir "%PROGRAMFILES%\contractG" 
xcopy /E /I /Y "contractG" "%PROGRAMFILES%\contractG" 
echo Creating desktop shortcut... 
powershell "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\ContractGenerator.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\contractG\start_contract_tool.bat'; $Shortcut.WorkingDirectory = '%PROGRAMFILES%\contractG'; $Shortcut.Save()" 
echo Creating start menu shortcut... 
powershell "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('StartMenu') + '\Programs\ContractGenerator.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\contractG\start_contract_tool.bat'; $Shortcut.WorkingDirectory = '%PROGRAMFILES%\contractG'; $Shortcut.Save()" 
echo Installation complete! 
