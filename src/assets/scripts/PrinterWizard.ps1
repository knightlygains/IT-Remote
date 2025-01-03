[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer
)

. .\assets\scripts\functions.ps1

Function getPrinters {
    $dontInvoke = $false

    if($Computer -eq $env:COMPUTERNAME){
        $dontInvoke = $true
    }
    
    # Enable print service log
    $enable_log_sb = {
        $logName = 'Microsoft-Windows-PrintService/Operational'

        $log = New-Object System.Diagnostics.Eventing.Reader.EventLogConfiguration $logName
        $log.IsEnabled = $true
        $log.SaveChanges()
    }

    try {

        if($dontInvoke){
            & $enable_log_sb
        }else{
            Invoke-Command -ComputerName $Computer $enable_log_sb -ErrorAction Stop
        }
        
    }
    catch {
        Set-Error "$_"
        return "Fail"
    }
    

    try {

        if($dontInvoke){
            $printers = Get-CimInstance -Class Win32_Printer -ErrorAction Stop | Select-Object Name, PrinterStatus, Type, PortName, DriverName, Shared, Published
        }else{
            #Variable that allows us to loop through and get all printers on a remote computer.
            $printers = Get-CimInstance -Class Win32_Printer -ComputerName $Computer -ErrorAction Stop | Select-Object Name, PrinterStatus, Type, PortName, DriverName, Shared, Published
        }

    }
    catch {
        Set-Error "$_"
        return "Fail"
    }
    
    # Initialize variable number to assign to and increment with each printer
    $variableNumber = 1

    New-Item -Path ".\assets\results\Printers\$Computer-Printers.json" -ItemType "file" -Force | Out-Null
    
    $json_format = @"
    {
        
    }
"@

    $json_obj = ConvertFrom-Json $json_format

    foreach ($printer in $printers) {
        Set-Variable -Name "Printer_$($variableNumber)|:$($printer.Name)" -Value "$($printer.Name)" -Scope script #create variable of each printer with the value as the name
        
        $printerStatus = ""
        #Convert Printer Status code
        switch ($printer.PrinterStatus) {
            1 { $printerStatus = "Other" }
            2 { $printerStatus = "Unknown" }
            3 { $printerStatus = "Idle" }
            4 { $printerStatus = "Printing" }
            5 { $printerStatus = "Warmup" }
            6 { $printerStatus = "Stopped Printing" }
            7 { $printerStatus = "Offline" }
        }

        $name_to_use = $printer.name

        if ($printer.name.Contains("\")) {
            $name_to_use = $printer.name.Replace("\", "\\")
        }

        $printer_json = @"
        {
            "Name": "$name_to_use",
            "Status": "$printerStatus",
            "Port": "$($printer.PortName)",
            "Published": "$($printer.Published)",
            "Type": "$($printer.Type)",
            "Shared": "$($printer.Shared)",
            "Driver": "$($printer.DriverName)"
        }
"@
        
        $json_obj | add-member -Name "$variableNumber" -value (ConvertFrom-Json $printer_json) -MemberType NoteProperty
        
        $variableNumber += 1
    }

    Set-Content -Path ".\assets\results\printers\$Computer-Printers.json" -Value (ConvertTo-Json $json_obj)

}

if (Test-Connection $Computer) {
    $result = getPrinters
    if ($result -eq "Fail") {
        exit 1
    }
    else {
        exit 0
    }
}
else {
    exit 2
}