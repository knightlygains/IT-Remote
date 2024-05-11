param(
    [string]$Computer
)

try {

    if ($Computer -eq $env:COMPUTERNAME) {
        $lastboot = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime
        $CurrentDate = Get-Date
        $uptime = $CurrentDate - $lastboot
        $seconds = $uptime.Seconds
        if ($seconds -lt 10) {
            $seconds = "0$seconds"
        }
        Write-Output "$($uptime.Days) days - $($uptime.Hours):$($uptime.Minutes):$($seconds)"
    }
    else {
        Invoke-Command -ComputerName $Computer -ScriptBlock {
            $lastboot = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime
            $CurrentDate = Get-Date
            $uptime = $CurrentDate - $lastboot
            $seconds = $uptime.Seconds
            if ($seconds -lt 10) {
                $seconds = "0$seconds"
            }
            Write-Output "$($uptime.Days) days - $($uptime.Hours):$($uptime.Minutes):$($seconds)"
        } -ErrorAction Stop
    }
}
catch {
    Write-Output $_
}
