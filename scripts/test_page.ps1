[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName
)

Invoke-Command -ComputerName $Computer -ScriptBlock {
                param($printerName)
                $printer = Get-WmiObject Win32_Printer | where {$_.name -eq "$printerName"}
                $printer.PrintTestPage()
            } -ArgumentList ($printerName)