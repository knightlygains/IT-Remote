param(
    [string]$Computer
)

if ($env:COMPUTERNAME -eq $Computer) {
    try {
        Restart-Service -Name Spooler -ErrorAction Stop
        exit 0
    }
    catch {
        exit 1
    }
}
elseif (Test-Connection $Computer -Count 1) {
    $command = Invoke-Command -ComputerName $Computer -ScriptBlock {
        try {
            Restart-Service -Name Spooler -ErrorAction Stop
            return 0
        }
        catch {
            return 1
        }
    }
    if ($command -eq 0) {
        exit 0
    }
    elseif ($command -eq 1) {
        exit 1
    }
}
else {
    exit 2
}