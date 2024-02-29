Write-Host " _____     _     _              _ _ _ _     
|  _  |___|_|___| |_ ___ ___   | | | |_|___ 
|   __|  _| |   |  _| -_|  _|  | | | | |- _|
|__|  |_| |_|_|_|_| |___|_|    |_____|_|___|
"
#Check for PsTools
if(-not(Test-Path "c:\windows\system32\psexec.exe" -PathType leaf) -OR -not(Test-Path "c:\windows\system32\psservice.exe" -PathType leaf)){
    Write-Host "PsExec or PsService was not detected in your system32 folder. These tools will be necessary to invoke commands on the remote computer."
    Write-Host "These tools can be downloaded from https://learn.microsoft.com/en-us/sysinternals/downloads/psexec"
    $openLink = Read-Host "Would you like to go there now? (Y/N)"
    if($openLink -eq "y"){
        Start-Process "https://learn.microsoft.com/en-us/sysinternals/downloads/psexec"
        exit
    } else {
        exit
    }
}

Function EnableWinRM {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computers
    )
    #accept eula for psexec so it works
    Start-Process cmd -ArgumentList "/c psexec -accepteula" -WindowStyle hidden
    #Enable WinRM to use Get-CimInstance and Invoke-Command
    foreach ($computer in $Computers) {
        #check if winrm running on computer
        $result = winrm id -r:$Computers 2>$null
        if ($LastExitCode -eq 0) {
            Write-Host "WinRM already enabled on" $computer "..." -ForegroundColor green
        }
        else {
            Write-Host "Enabling WinRM on" $computer "..." -ForegroundColor red
            psexec.exe \\$computer -s C:\Windows\System32\winrm.cmd qc -quiet
        
            if ($LastExitCode -eq 0) {
                psservice.exe \\$computer restart WinRM
                $result = winrm id -r:$computer 2>$null
        
                if ($LastExitCode -eq 0) { Write-Host "WinRM successfully enabled!" -ForegroundColor green }
                else {
                    exit 1
                }
            }
            else {
                Write-Host "Couldn't enable WinRM on $computer."
            }
        }
    }
}

Function getPrinters {
    #Variable that allows us to loop through and get all printers on a remote computer.
    $printers = Get-CimInstance -Class Win32_Printer -ComputerName $Computer | Select-Object Name, PrinterStatus

    $variableNumber = 1
    #Loop through adapters and create/update variables for each one.
    foreach ($printer in $printers) {
        Set-Variable -Name "Printer_$($variableNumber)|:$($printer.Name)" -Value "$($printer.Name)" -Scope script #create variable of each printer with the value as the name
        
        $printerStatus = ""
        #Convert Printer Status code
        switch ($printer.PrinterStatus){
            1{$printerStatus = "Other"}
            2{$printerStatus = "Unknown"}
            3{$printerStatus = "Idle"}
            4{$printerStatus = "Printing"}
            5{$printerStatus = "Warmup"}
            6{$printerStatus = "Stopped Printing"}
            7{$printerStatus = "Offline"}
        }

        Write-Host "Printer$($variableNumber) $($printer.Name) Status: $printerStatus."
        $variableNumber += 1
    }
}

$Computer = Read-Host "What's the computer hostname or IP?"

if(Test-Connection $Computer -Count 1){
    EnableWinRM -Computers $Computer
    Do{ #Start of printer modification
        getPrinters #Call function to create variables of the printers

        $answer = Read-Host "Which printer do you want to change? (Type the number seen after 'Printer')"
        $printerSelection = Get-Variable -Name "Printer_$answer|*"

        Write-Host "Printer selected: $($printerSelection.Value)."

        Do{#Get answer for what we will do with the printer
            $answer2 = Read-Host "What will we do? U(Uninstall), R(Rename), T(Print test page)"
            if(-not($answer2 -eq "u" -OR $answer2 -eq "r" -OR $answer2 -eq "t")){
                Write-Host "Invalid answer."
            }
        }Until($answer2 -eq "u" -OR $answer2 -eq "r" -OR $answer2 -eq "t")

        $printerToChange = $printerSelection.Value

        if($answer2 -eq "r"){ #Rename printer
            $newName = Read-Host "What will the new name be?" #Get new name

            Invoke-Command -ComputerName $Computer -ScriptBlock {
                param($printerToChange, $newName)
                Start-Process powershell -Wait -ArgumentList "Rename-Printer", "-Name", "'$printerToChange'", "-NewName", "'$newName'"
            } -ArgumentList ($printerToChange, $newName)

            Write-Host "Changed printer $printerToChange name to: $newName."
        }
        if($answer2 -eq "t"){ #Print a test page
            Invoke-Command -ComputerName $Computer -ScriptBlock {
                param($printerToChange)
                $printer = Get-WmiObject Win32_Printer | where {$_.name -eq "$printerToChange"}
                $printer.PrintTestPage()
            } -ArgumentList ($printerToChange)
            Write-Host "Test page sent from printer $printerToChange on computer $Computer."
        } if($answer2 -eq "u"){ #Uninstall printer
            $areYouSure = Read-Host "Are you sure you want to uninstall $($printerSelection.Value) from $Computer? (Y/N)"
            if($areYouSure -eq "y"){
                Write-Host "Variables: $printerToChange, $Computer"
                Invoke-Command -ComputerName $Computer -ScriptBlock {
                    param($printerToChange)
                    Start-Process powershell -Wait -ArgumentList "Remove-Printer", "-Name", "'$printerToChange'"
                } -ArgumentList ($printerToChange)
                Write-Host "Removed printer: $printerToChange."
            } else {
                Write-Host "Cancelled removal."
            }
        }

        Do{ #Get answer for if we will modify another printer
            $continue = Read-Host "Would you like to modify another printer? (Y/N)"
            if(-not($continue -eq "y" -OR $continue -eq "n")){
                Write-Host "Invalid answer."
            }
        }Until($continue -eq "y" -OR $continue -eq "n")

    Write-Host ""
        
    }Until($continue -eq "n") #End of printer modification and script
} else {
    Write-Host "Couldn't contact $Computer."
}