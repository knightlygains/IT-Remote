[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName
)

try {
    Remove-Printer -Name $printerName -ComputerName $Computer -ErrorAction Stop
    exit 0
}
catch {
    exit 1
}