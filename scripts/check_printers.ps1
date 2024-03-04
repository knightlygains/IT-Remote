[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]$Computer
)

$message = ""

Function EnableWinRM {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computers
    )
    #accept eula for psexec so it works
    Start-Process cmd -ArgumentList "/c psexec -accepteula" -WindowStyle hidden
    #Enable WinRM to use Get-CimInstance
    if ($Computer -like "*\.*\.*\.*") {
        Write-Host "matched"
    }
    
    #check if winrm running on computer
    $result = winrm id -r:$Computer 2>$null
    if ($LastExitCode -eq 0) {
        Write-Host "WinRM already enabled on" $Computer "..." -ForegroundColor green
    }
    else {
        Write-Host "Enabling WinRM on" $Computer "..." -ForegroundColor red
        psexec.exe \\"$Computer" -s C:\Windows\System32\winrm.cmd qc -quiet
    
        if ($LastExitCode -eq 0) {
            psservice.exe \\"$Computer" restart WinRM
            $result = winrm id -r:$Computer 2>$null
    
            if ($LastExitCode -eq 0) { Write-Host "WinRM successfully enabled!" -ForegroundColor green }
            else {
                exit 1
            }
        }
        else {
            $message += "Couldn't enable WinRM on $Computer."
        } #end of if
    } #end of else 
    
}

Function Get-PrintServerPrinters {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computer
    )

    $scriptBlock = {
        if (Test-Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Print\Connections") {
            #Get child keys in ...\Print\Connection
            $printConnectionKeys = Get-ChildItem -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Print\Connections"

            #String variable to keep track of found printer names
            $printersFound = ""

            #variable to increment for use in setting unique variable names
            $printerCount = 0

            #loop through each child key found and grab its 'Printer' subkey value
            foreach ($key in $printConnectionKeys) {
                #Increase printerCount to make a unique variable name
                $printerCount += 1

                #Get just the keyname by itself
                $actualKey = Split-Path $key -Leaf

                #Use previously defined registry path and $actualKey to access the 'Printer' subkey
                $printer = Get-ItemPropertyValue -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Print\Connections\$actualKey" -Name "Printer"

                #Create unique variable with name found in subkey
                New-Variable -Name "printer_$($printerCount)_" -Value $printer -Scope script

                #update the string to store what we found, retaining previously stored info
                $printersFound = $printersFound + "`n $printer."
            }

            $printers = Get-Variable -Name "printer_*_" -ValueOnly 

            #returns all variables we created
            return $printers
        }
        else {
            return
        }
    }

    #Finally, execute the scriptblock on remote computer
    Invoke-Command -ComputerName $Computer -ScriptBlock $scriptBlock -OutVariable output

    if (-not($null -eq $output)) {
        #Grab output from the scriptblock, display contents in formatted gridview
        $output | Select-Object @{Label = 'Printer Name'; expression = { $_ } }, @{Label = 'Computer Name'; expression = { $_.PSComputerName } } | Out-GridView -Title "$Computer's printserver printers"
    }
    else {
        $message += "No printers connected via printserver found. "
    }
}

Function Get-Printers {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computer
    )

    EnableWinRM $Computer

    Get-CimInstance -Class Win32_Printer -ComputerName $Computer | Select-Object Name, ComputerName, Type, PortName, DriverName, Shared, Published | Out-GridView -Title "$Computer Printers"

    Get-PrintServerPrinters -Computer $Computer
    $message += "$Computer's local printers generated in new window. "

}

Get-Printers -Computer $Computer

return $message