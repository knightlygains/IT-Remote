

[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer
)
Function getPrinters {
    
    # Enable print service log
    Invoke-Command -ComputerName $Computer -ScriptBlock {
        $logName = 'Microsoft-Windows-PrintService/Operational'

        $log = New-Object System.Diagnostics.Eventing.Reader.EventLogConfiguration $logName
        $log.IsEnabled = $true
        $log.SaveChanges()
    }

    try {
        #Variable that allows us to loop through and get all printers on a remote computer.
        $printers = Get-CimInstance -Class Win32_Printer -ComputerName $Computer | Select-Object Name, PrinterStatus, Type, PortName, DriverName, Shared, Published
    }
    catch {
        exit 1
    }
    
    # Initialize variable number to assign to and increment with each printer
    $variableNumber = 1

    New-Item -Path ".\results\Printers\$Computer-Printers.json" -ItemType "file" -Force | Out-Null
    
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
            "Type": $($printer.Type),
            "Shared": "$($printer.Shared)",
            "Driver": "$($printer.DriverName)"
        }
"@
        
        $json_obj | add-member -Name "$variableNumber" -value (ConvertFrom-Json $printer_json) -MemberType NoteProperty
        
        $variableNumber += 1
    }

    Set-Content -Path ".\results\$Computer-Printers.json" -Value (ConvertTo-Json $json_obj)

    exit 0
}

if (Test-Connection $Computer) {
    getPrinters
}
else {
    exit 1
}



# Do{ #Start of printer modification
#     getPrinters #Call function to create variables of the printers

#     $answer = Read-Host "Which printer do you want to change? (Type the number seen after 'Printer')"
#     $printerSelection = Get-Variable -Name "Printer_$answer|*"

#     Write-Host "Printer selected: $($printerSelection.Value)."

#     Do{#Get answer for what we will do with the printer
#         $answer2 = Read-Host "What will we do? U(Uninstall), R(Rename), T(Print test page)"
#         if(-not($answer2 -eq "u" -OR $answer2 -eq "r" -OR $answer2 -eq "t")){
#             Write-Host "Invalid answer."
#         }
#     }Until($answer2 -eq "u" -OR $answer2 -eq "r" -OR $answer2 -eq "t")

#     $printerToChange = $printerSelection.Value

#     if($answer2 -eq "r"){ #Rename printer
#         $newName = Read-Host "What will the new name be?" #Get new name

#         Invoke-Command -ComputerName $Computer -ScriptBlock {
#             param($printerToChange, $newName)
#             Start-Process powershell -Wait -ArgumentList "Rename-Printer", "-Name", "'$printerToChange'", "-NewName", "'$newName'"
#         } -ArgumentList ($printerToChange, $newName)

#         Write-Host "Changed printer $printerToChange name to: $newName."
#     }
#     if($answer2 -eq "t"){ #Print a test page
#         Invoke-Command -ComputerName $Computer -ScriptBlock {
#             param($printerToChange)
#             $printer = Get-WmiObject Win32_Printer | where {$_.name -eq "$printerToChange"}
#             $printer.PrintTestPage()
#         } -ArgumentList ($printerToChange)
#         Write-Host "Test page sent from printer $printerToChange on computer $Computer."
#     } if($answer2 -eq "u"){ #Uninstall printer
#         $areYouSure = Read-Host "Are you sure you want to uninstall $($printerSelection.Value) from $Computer? (Y/N)"
#         if($areYouSure -eq "y"){
#             Write-Host "Variables: $printerToChange, $Computer"
#             Invoke-Command -ComputerName $Computer -ScriptBlock {
#                 param($printerToChange)
#                 Start-Process powershell -Wait -ArgumentList "Remove-Printer", "-Name", "'$printerToChange'"
#             } -ArgumentList ($printerToChange)
#             Write-Host "Removed printer: $printerToChange."
#         } else {
#             Write-Host "Cancelled removal."
#         }
#     }

#     Do{ #Get answer for if we will modify another printer
#         $continue = Read-Host "Would you like to modify another printer? (Y/N)"
#         if(-not($continue -eq "y" -OR $continue -eq "n")){
#             Write-Host "Invalid answer."
#         }
#     }Until($continue -eq "y" -OR $continue -eq "n")

# Write-Host ""
    
# }Until($continue -eq "n") #End of printer modification and script