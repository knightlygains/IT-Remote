[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName
)

. .\assets\scripts\functions.ps1

if (Test-Connection $Computer) {

    try {
        if ($Computer -eq $env:COMPUTERNAME) {
            Remove-Printer -Name "$printerName" -ErrorAction Stop
        }
        else {
            Remove-Printer -Name "$printerName" -ComputerName $Computer -ErrorAction Stop
        }
        exit 0
    }
    catch {
        Set-Error "$_"
        exit 1
    }
}
else {
    exit 1
}