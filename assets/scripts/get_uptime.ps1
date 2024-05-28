param(
    [string]$Computer
)

$result_path = "./assets/results/Uptime"

if (-not(Test-Path $result_path)) {
    New-Item "$result_path/$Computer-uptime.txt" -ItemType File
}

try {

    if ($Computer -eq $env:COMPUTERNAME) {
        $lastboot = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime
        $CurrentDate = Get-Date
        $uptime = $CurrentDate - $lastboot
        $seconds = $uptime.Seconds
        if ($seconds -lt 10) {
            $seconds = "0$seconds"
        }
        Set-Content -Path "$result_path/$Computer-uptime.txt" -Value "$($uptime.Days) days - $($uptime.Hours):$($uptime.Minutes):$($seconds)"
    }
    else {
        
        $result = Invoke-Command -ComputerName $Computer -ScriptBlock {
            $lastboot = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime
            $CurrentDate = Get-Date
            $uptime = $CurrentDate - $lastboot
            $seconds = $uptime.Seconds
            $hours = $uptime.Hours
            $mins = $uptime.Minutes
            if ($seconds -lt 10) {
                $seconds = "0$seconds"
            }
            if ($hours -lt 0) {
                $hours = "0$hours"
            }
            if ($mins -lt 10) {
                $mins = "0$mins"
            }
            return "$($uptime.Days) days - $($hours):$($mins):$($seconds)"
        } -ErrorAction Stop

        Set-Content -Path "$result_path/$Computer-uptime.txt" -Value $result
    }
}
catch {
    Write-Output $_
}
