param(
    [string]$id,
    [string]$shutdown,
    [string]$scheduled,
    [string]$Computers,
    [int]$dateMonth,
    [int]$dateDay,
    [int]$dateYear,
    [int]$dateHour,
    [int]$dateMinute,
    [int]$dateSeconds,
    [string]$timeFormat,
    [string]$winRM
)

if ($winRM -eq "True") {
    $winRM = $true
}
else {
    $winRM = $false
}

. .\scripts\functions.ps1


Function Restart-PCs {

    $list = Get-Content ".\lists\computers.txt"
    # If using list, set Computers = to Get-Content for list contents
    if ($Computers -eq "Use-List") {
        foreach ($Computer in $list) {
            Write-Host "Balls $Computer"
            if (Test-Connection $Computer) {
                Enable-WinRM -Computer $Computer -winRM $winRM
            }
        }
    }
    else {
        # If not using list, set list equal to computers
        # we passed in through args
        $list = $Computers
    }

    New-Item ".\results\Restart\$id-Restart.txt" -type file | Out-Null

    #Grab date and time values from the schedule text boxes
    $currentDate = Get-Date

    if ($scheduled -eq "True") {
        #Store date and time values in a variable to use with restart command
        $restartDate = Get-Date -Month $dateMonth -Day $dateDay -Year $dateYear -Hour $dateHour -Minute $dateMinute -Second $dateSeconds

        #Find difference between current date/time and our scheduled date/time
        $timeAdjusted = New-TimeSpan -Start $currentDate -End $restartDate

        #Get total seconds converted from the difference between the two dates
        $secondsToWait = [int]$timeAdjusted.TotalSeconds
    }

    foreach ($comp in $List) {

        if ($secondsToWait -lt 0) {
            $secondsToWait = 0
        }

        Function Format-Time {
            if ($scheduled -eq "True") {
                $hour = $dateHour
                $minute = $dateMinute
                $seconds = $dateSeconds
            }
            else {
                $hour = $currentDate.Hour
                $minute = $currentDate.Minute
                $seconds = $currentDate.Second
            }
            if ($minute -lt 10) {
                $minute = "0$minute"
            }
            if ($seconds -lt 10) {
                $seconds = "0$seconds"
            }
            
            $am_pm = "am"
            if ($timeFormat -eq "12" -AND [int]$hour -gt 12) {
                $hour = [int]$hour - 12
                $am_pm = "pm"
            }
            return  "$($hour):$($minute):$($seconds)$am_pm"
        }

        $formatted_time = Format-Time

        $restartTime = "$dateMonth/$dateDay/$dateYear, $formatted_time"

        Write-Host "Seconds to wait $secondsToWait"
        
        $action = "restart"

        if ($shutdown -eq "True") {
            shutdown /s /m \\$comp /t $secondsToWait
            $action = "shutdown"
        }
        else {
            shutdown /r /m \\$comp /t $secondsToWait
        }
        
        if (-not($LastExitCode -eq 0)) {
            Add-Content -Path ".\results\Restart\$id-Restart.txt" -Value "Could not $action $comp."
        }
        else {
            Add-Content -Path ".\results\Restart\$id-Restart.txt" -Value "$($action): $comp at $restartTime."
        }
    }
}

Restart-PCs