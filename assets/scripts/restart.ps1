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

. .\assets\scripts\functions.ps1


Function Restart-PCs {

    $action = "Restarted"
    $list = Get-Content ".\settings\lists\computers.txt"
    # If using list, set Computers = to Get-Content for list contents
    if ($Computers -eq "list of computers") {
        foreach ($Computer in $list) {
            if ((Test-Connection $Computer) -AND ($winRM -eq $true)) {
                Enable-WinRM -Computer $Computer -winRM $winRM
            }
        }
    }
    else {
        # If not using list, set list equal to computers
        # we passed in through args
        $list = $Computers
    }

    New-Item ".\assets\results\Restart\$id-Restart.txt" -type file -force | Out-Null

    #Grab date and time values from the schedule text boxes
    $currentDate = Get-Date

    if ($scheduled -eq "True") {
        #Store date and time values in a variable to use with restart command
        $restartDate = Get-Date -Month $dateMonth -Day $dateDay -Year $dateYear -Hour $dateHour -Minute $dateMinute -Second $dateSeconds

        #Find difference between current date/time and our scheduled date/time
        $timeAdjusted = New-TimeSpan -Start $currentDate -End $restartDate

        #Get total seconds converted from the difference between the two dates
        $secondsToWait = [int]$timeAdjusted.TotalSeconds

        $action = "Restarting"
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

        if ($shutdown -eq "True") {
            shutdown /s /m \\$comp /t $secondsToWait 2>&1 | out-string
            $action = "Shutdown"
        }
        else {
            shutdown /r /m \\$comp /t $secondsToWait 2>&1 | out-string
        }
        
        if (-not($LastExitCode -eq 0)) {
            Add-Content -Path ".\assets\results\Restart\$id-Restart.txt" -Value "$action failed on $comp. A restart may already be pending, WinRM couldn't be neabled, or it is offline."
        }
        else {
            Add-Content -Path ".\assets\results\Restart\$id-Restart.txt" -Value "$((Get-Culture).TextInfo.ToTitleCase($action)) $comp at $restartTime."
        }
    }
}

Restart-PCs