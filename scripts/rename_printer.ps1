[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName,
    [string]$newName
)

Function Rename-RemotePrinter {
    Invoke-Command -ComputerName $Computer -ScriptBlock {
        param($printerName, $newName)
        try {
            Rename-Printer -Name "$printerName" -NewName "$newName"
        }
        catch {
            exit 1
        }
        
    } -ArgumentList ($printerName, $newName)
}

if (Test-Connection $Computer) {
    Rename-RemotePrinter
    if ($LASTEXITCODE -eq 0) {
        exit 0
    }
    else {
        exit 1
    }
}
else {
    exit 1
}
