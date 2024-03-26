param (
    [string] $Computer,
    [string] $type
)

# Enable print service log
$enable_log_sb = {
    $logName = 'Microsoft-Windows-PrintService/Operational'

    $log = New-Object System.Diagnostics.Eventing.Reader.EventLogConfiguration $logName
    $log.IsEnabled = $true
    $log.SaveChanges()
}

try {
    Invoke-Command -ComputerName $Computer $enable_log_sb -ErrorAction Stop
}
catch {
    exit 1
}

$sb = {
    param($type)
    $logs = Get-WinEvent "Microsoft-Windows-PrintService/$type"
    return $logs
}

try{
    $result = Invoke-Command -ComputerName $Computer -ScriptBlock $sb -ArgumentList($type) -ErrorAction Stop
}catch{
    exit 1
}

foreach( $log in $result){
    Write-Host "$($log.Message)"
}