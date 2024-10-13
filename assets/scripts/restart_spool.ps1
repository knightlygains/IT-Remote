param(
    [string]$Computer
)

. .\assets\scripts\functions.ps1

if ($env:COMPUTERNAME -eq $Computer) {
    try {
        Restart-Service -Name Spooler -ErrorAction Stop
        exit 0
    }
    catch {
        Set-Error "$_"
        exit 1
    }
}
elseif (Test-Connection $Computer -Count 1) {
    $command = Invoke-Command -ComputerName $Computer -ScriptBlock {
        param($Computer)

        try {
            Restart-Service -Name Spooler -ErrorAction Stop
            return 0
        }
        catch {
            return "Failed to restart print spooler on $Computer. $_"
        }
    } -ArgumentList ($Computer)

    if ($command -eq 0) {
        exit 0
    }
    elseif ($command -like "*Failed*") {
        Set-Error "$command"
        exit 1
    }
    
}
else {
    exit 2
}