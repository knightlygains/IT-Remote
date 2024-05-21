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
            if ($seconds -lt 10) {
                $seconds = "0$seconds"
            }
            return "$($uptime.Days) days - $($uptime.Hours):$($uptime.Minutes):$($seconds)"
        } -ErrorAction Stop

        Set-Content -Path "$result_path/$Computer-uptime.txt" -Value $result
    }
}
catch {
    Write-Output $_
}
