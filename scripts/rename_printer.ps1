[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName,
    [string]$newName
)

Invoke-Command -ComputerName $Computer -ScriptBlock {
    param($printerName, $newName)
    Rename-Printer -Name "$printerName" -NewName "$newName"
} -ArgumentList ($printerName, $newName)