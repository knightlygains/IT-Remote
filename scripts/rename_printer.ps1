[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName,
    [string]$newName
)

Invoke-Command -ComputerName $Computer -ScriptBlock {
    param($printerName, $newName)
    try {
        Rename-Printer -Name "$printerName" -NewName "$newName"
    }
    catch {
        exit 1
    }
    
} -ArgumentList ($printerName, $newName)

if ($LASTEXITCODE -eq 0) {
    exit 0
}
else {
    exit 1
}