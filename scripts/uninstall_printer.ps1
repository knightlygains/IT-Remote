[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName
)

if (Test-Connection $Computer) {
    try {
        if ($Computer -like "localhost") {
            Remove-Printer -Name "$printerName" -ErrorAction Stop
        }
        else {
            Remove-Printer -Name "$printerName" -ComputerName $Computer -ErrorAction Stop
        }
        
        exit 0
    }
    catch {
        exit 1
    }
}
else {
    exit 1
}
