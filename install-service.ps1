# Create scheduled task to run server at startup
$TaskName = "HaystackServer"
$Action = New-ScheduledTaskAction -Execute "python" -Argument '-m uvicorn main:app --host 127.0.0.1 --port 8000' -WorkingDirectory "e:\haystack\backend"
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force

Write-Host "✓ Task '$TaskName' created successfully" -ForegroundColor Green
Write-Host "Server will start automatically on boot" -ForegroundColor Cyan
