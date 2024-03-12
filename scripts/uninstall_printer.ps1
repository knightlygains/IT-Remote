[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName
)
Function Uninstall-Printer {
    Invoke-Command -ComputerName $Computer -ScriptBlock {
        param($printerName)
        Remove-Printer -Name "$printerName"
    } -ArgumentList ($printerName)
}

Uninstall-Printer

if ($LASTEXITCODE -eq 0) {
    Write-Host "Exiting 0"
    exit 0
}
else {
    Write-Host "Exiting 1"
    exit 1
}