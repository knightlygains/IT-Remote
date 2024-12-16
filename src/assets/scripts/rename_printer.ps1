[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer,
    [string]$printerName,
    [string]$newName
)

. .\assets\scripts\functions.ps1

Function Rename-RemotePrinter {
    $dontInvoke = $false

    if($Computer -eq $env:COMPUTERNAME){
        $dontInvoke = $true
    }

    try{

        if($dontInvoke){

            try {
                Rename-Printer -Name "$printerName" -NewName "$newName" -ErrorAction Stop
                exit 0
            }
            catch {
                Set-Error "Failed to rename printer on $Computer. $_"
            }

        }else{
            $command = Invoke-Command -ComputerName $Computer -ScriptBlock -ErrorAction stop {
                param($printerName, $newName, $Computer)
    
                try {
                    Rename-Printer -Name "$printerName" -NewName "$newName" -ErrorAction Stop
                    exit 0
                }
                catch {
                    return "Failed to rename printer on $Computer. $_"
                }
                
            } -ArgumentList ($printerName, $newName, $Computer)

            if($command -like "*Failed*"){
                throw "Failed rename the printer on $Computer"
            }
        }

    }catch{
        Set-Error "$_"
        exit 1
    }
}

if (Test-Connection $Computer -Count 1) {
    Rename-RemotePrinter
}
else {
    exit 2
}