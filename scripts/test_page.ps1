[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName
)
Function Send-TestPage {
    Invoke-Command -ComputerName $Computer -ScriptBlock {
        param($printerName)
        $printer = Get-WmiObject Win32_Printer | Where-Object { $_.name -eq "$printerName" }
        $printer.PrintTestPage()
    } -ArgumentList ($printerName)
}

Send-TestPage

if ($LASTEXITCODE -eq 0) {
    exit 0
}
else {
    exit 1
}