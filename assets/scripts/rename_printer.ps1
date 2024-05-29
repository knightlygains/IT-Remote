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
            Rename-Printer -Name "$printerName" -NewName "$newName" -ErrorAction Stop
            exit 0
        }
        catch {
            exit 1
        }
        
    } -ArgumentList ($printerName, $newName)
}

if (Test-Connection $Computer -Count 1) {
    Rename-RemotePrinter
}
else {
    exit 2
}