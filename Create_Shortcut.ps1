# CPL Desktop Shortcut Creator
# Run this script as Administrator to create desktop shortcut

$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = "$Desktop\CPL.lnk"
$IconPath = "$PSScriptRoot\cpl.ico"

# Create WScript Shell
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)

$Shortcut.TargetPath = "$PSScriptRoot\Start_CPL.bat"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "CPL - Cognitive Processing Language"
$Shortcut.IconLocation = "$PSScriptRoot\cpl.ico"

$Shortcut.Save()

Write-Host "Shortcut created at: $ShortcutPath"
