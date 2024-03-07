[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer
    # [string]$list
)

# if ($list -eq "True") {
#     $Computer = Get-Content ".\lists\computers.txt"
# }

$script:end_result = ""

Function Enable-WinRM {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computer
    )
    #accept eula for psexec so it works
    Start-Process cmd -ArgumentList "/c psexec -accepteula" -WindowStyle hidden
    #Enable WinRM to use Get-CimInstance
    

    Write-Host "Enabling WinRM on" $Computer "..." -ForegroundColor red
    psexec.exe \\"$computer" -s C:\Windows\System32\winrm.cmd qc -quiet | Out-Null

    if ($LastExitCode -eq 0) {
        psservice.exe \\"$computer" restart WinRM | Out-Null

        if ($LastExitCode -eq 0) { 
            $script:end_result = "WinRM successfully enabled!"
        }
        else {
            exit 1
        }
    }
    else {
        $script:end_result = "Couldn't enable WinRM on $computer."
    } #end of if
} #end of else


try {
    Enable-WinRM $Computer -ErrorAction Stop | Out-Null
}
catch {
    $script:end_result = "WinRM could not be enabled."
}

return $script:end_result
