param(
    [string]$Computer
)

try {
    Invoke-Command -ComputerName $Computer -ScriptBlock {
        $lastboot = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime
        $CurrentDate = Get-Date
        $uptime = $CurrentDate - $lastboot
        Write-Output "$($uptime.Days):$($uptime.Hours):$($uptime.Minutes):$($uptime.Seconds)"
    } -ErrorAction Stop
}
catch {
    Write-Output $_
}
