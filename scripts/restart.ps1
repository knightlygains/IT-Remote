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
    [int]$dateSeconds
)

Function Enable-WinRM {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computer
    )

    psexec.exe \\"$Computer" -s -nobanner -accepteula C:\Windows\System32\winrm.cmd qc -quiet

    $result = winrm id -r:$computer 2>$null
    if ($LastExitCode -eq 0) {
        psservice.exe \\"$Computer" -nobanner restart WinRM
        $result = winrm id -r:$computer 2>$null
        if ($LastExitCode -eq 0) { 
            Write-Host "WinRM Enabled on $Computer."
        }
        else {
            Write-Host "Failed to enable WinRM on $Computer."
        }
    }
    else {
        Write-Host "Failed to enable WinRM on $Computer."
    }
}

Function Restart-PCs {

    $list = Get-Content ".\lists\computers.txt"
    # If using list, set Computers = to Get-Content for list contents
    if ($Computers -eq "Use-List") {
        foreach ($Computer in $list) {
            Write-Host "Balls $Computer"
            if (Test-Connection $Computer) {
                Enable-WinRM -Computer $Computer
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

        #Store calculated date in a variable. Adding total seconds to the date = our future scheduled time
        $restartTime = (Get-Date).AddSeconds($timeAdjusted.TotalSeconds)

        #Get total seconds converted from the difference between the two dates
        $secondsToWait = [int]$timeAdjusted.TotalSeconds
    }

    foreach ($comp in $List) {

        if ($secondsToWait -lt 0) {
            $secondsToWait = 0
        }
        
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