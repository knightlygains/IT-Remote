Function Enable-WinRM {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computer
    )
    
    Write-Host "Enabling WinRM on" $Computer "..." -ForegroundColor red
    psexec.exe \\"$Computer" -s -nobanner -accepteula C:\Windows\System32\winrm.cmd qc -quiet

    $result = winrm id -r:$Computer 2>$null
    if ($LastExitCode -eq 0) {
        psservice.exe \\"$Computer" -nobanner restart WinRM
        # $result = winrm id -r:$Computer 2>$null
        if ($LastExitCode -eq 0) { 
            return $true
        }
        else {
            return $false
        }
        while ($true) {
            continue
        }
    }
    else {
        return $false
    }
}