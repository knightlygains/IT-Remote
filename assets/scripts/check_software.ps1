param (
    [string]$Computer,
    [string]$SoftwareName,
    [string]$id,
    [string]$all,
    [string]$winRM
)

if ($winRM -eq "True") {
    $winRM = $true
}
else {
    $winRM = $false
}

. .\assets\scripts\functions.ps1

Function Enable-RemoteRegistry {
    [CmdletBinding()]
    param(
        [string]$Computer
    )

    Foreach ($Comp in $Computer) {
        try {
            $RemoteRegistry = Get-CimInstance -Class Win32_Service -ComputerName $Comp -Filter 'Name = "RemoteRegistry"' -ErrorAction Stop
            if ($RemoteRegistry.State -eq 'Running') {
                Write-Output "$Comp's Remote Registry is already Enabled"
            }

            if ($RemoteRegistry.StartMode -eq 'Disabled') {
                Invoke-Command -ComputerName $comp -ScriptBlock {
                    Set-Service -Name "RemoteRegistry" -StartupType Manual -ErrorAction Stop
                }
                Write-Output "$Comp : Remote Registry has been Enabled"
            }

            if ($RemoteRegistry.State -eq 'Stopped') {
                Invoke-Command -ComputerName $comp -ScriptBlock {
                    Start-Service "RemoteRegistry" -ErrorAction Stop
                }
                Write-Output "$Comp : Remote Registry has been Started"
            }
        }
        catch {
            $ErrorMessage = $Comp + " Error: " + $_.Exception.Message
        }
    }
}

Function Get-InstalledSoftware {
    Param(
        [string]$Computer,
        [string]$SoftwareName
    )

    Begin {
        Enable-RemoteRegistry $Computer
        $lmKeys = "Software\Microsoft\Windows\CurrentVersion\Uninstall", "SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        $lmReg = [Microsoft.Win32.RegistryHive]::LocalMachine
        $cuKeys = "Software\Microsoft\Windows\CurrentVersion\Uninstall"
        $cuReg = [Microsoft.Win32.RegistryHive]::CurrentUser
    }
    Process {
        if (Test-Connection -ComputerName $Computer -count 1 -quiet) {
            $masterKeys = @()
            $remoteCURegKey = [Microsoft.Win32.RegistryKey]::OpenRemoteBaseKey($cuReg, $Computer)
            $remoteLMRegKey = [Microsoft.Win32.RegistryKey]::OpenRemoteBaseKey($lmReg, $Computer)
            foreach ($key in $lmKeys) {
                $regKey = $remoteLMRegKey.OpenSubkey($key)
                if ($null -ne $regKey) {
                    foreach ($subName in $regKey.GetSubkeyNames()) {
                        foreach ($sub in $regKey.OpenSubkey($subName)) {
                            if (-not($null -eq $sub.GetValue("displayname"))) {
                                $masterKeys += (New-Object PSObject -Property @{
                                        "ComputerName"     = "$Computer"
                                        "Name"             = $sub.GetValue("displayname")
                                        "SystemComponent"  = $sub.GetValue("systemcomponent")
                                        "ParentKeyName"    = $sub.GetValue("parentkeyname")
                                        "Version"          = $sub.GetValue("DisplayVersion")
                                        "UninstallCommand" = $sub.GetValue("UninstallString")
                                        "InstallDate"      = $sub.GetValue("InstallDate")
                                        "RegPath"          = $sub.ToString()
                                    })
                            }
                        }
                    }
                }
            }
            foreach ($key in $cuKeys) {
                $regKey = $remoteCURegKey.OpenSubkey($key)
                if ($null -ne $regKey) {


                    foreach ($subName in $regKey.getsubkeynames()) {
                        foreach ($sub in $regKey.opensubkey($subName)) {
                            if (-not($null -eq $sub.GetValue("displayname"))) {
                                $masterKeys += (New-Object PSObject -Property @{
                                        "ComputerName"     = "$Computer"
                                        "Name"             = $sub.GetValue("displayname")
                                        "SystemComponent"  = $sub.GetValue("systemcomponent")
                                        "ParentKeyName"    = $sub.GetValue("parentkeyname")
                                        "Version"          = $sub.GetValue("DisplayVersion")
                                        "UninstallCommand" = $sub.GetValue("UninstallString")
                                        "InstallDate"      = $sub.GetValue("InstallDate")
                                        "RegPath"          = $sub.ToString()
                                    })
                            }
                            
                        }
                    }
                }
            }

            $woFilter = { $null -ne $_.name -AND $_.SystemComponent -ne "1" -AND $null -eq $_.ParentKeyName -AND $_.name -match "$SoftwareName" }
            $props = 'Name', 'Version', 'ComputerName', 'Installdate', 'RegPath'
            
            if ($all -eq "True") {
                $masterKeys = ($masterKeys | Select-Object $props | Sort-Object Name)
            }
            else {
                $masterKeys = ($masterKeys | Where-Object $woFilter | Select-Object $props | Sort-Object Name)
            }
           
            #$masterKeys
            if ($null -eq $masterKeys) {
                $notFoundObject = [PSCustomObject]@{
                    ComputerName = $Computer
                    Name         = "'$SoftwareName' NOT found"
                    Version      = 'N/A'
                }
                New-Variable -Name "softwareObject_$($Computer)_" -Value $notFoundObject -Scope script
                Write-Host "'$SoftwareName' not found on $Computer."
            }
            else {
                #Create a new variable with a unique name and assign the object as the value
                New-Variable -Name "softwareObject_$($Computer)_" -Value $masterKeys -Scope script   
                Write-Host "$Computer's software matching '$SoftwareName' collected in a variable."
            }

        }
        else {
            $offlineObject = [PSCustomObject]@{
                ComputerName = $Computer
                Name         = "N/A - Offline"
                Version      = 'N/A - Offline'
            }
            Write-Host "Couldn't contact $Computer."
            $script:ErrorMsg2 = "Couldn't contact $Computer."
            New-Variable -Name "softwareObject_$($Computer)_" -Value $offlineObject -Scope script 
        }
    }
    End {}
}

$list = Get-Content ".\settings\lists\computers.txt"
# If using list, set Computers = to Get-Content for list contents
if ($Computer -eq "list of computers") {
    Write-Host $list
    foreach ($Comp in $list) {
        if (Test-Connection -ComputerName $Comp) {
            Enable-WinRM $Comp $winRM
        }
    }
}
else {
    # If not using list, set list equal to Computer
    # we passed in through args
    $list = $Computer
}

foreach ($pc in $list) {
    if (Test-Connection -ComputerName $pc) {
        Get-InstalledSoftware -Computer $pc -Softwarename $SoftwareName
    }
    else {
        $offlineObject = [PSCustomObject]@{
            ComputerName = $pc
            Name         = "N/A - Offline"
            Version      = 'N/A - Offline'
        }
        New-Variable -Name "softwareObject_$($pc)_" -Value $offlineObject -Scope script 
    }
}

$found_software = Get-Variable -Name "softwareObject_*_" -ValueOnly

if ($Computer -eq "list of computers") {
    $filename = "Programs-$id.json"
    New-Item -Path ".\assets\results\Programs\$filename" -ItemType "file" -Force | Out-Null

    $computers = @()

    foreach ($result in $found_software) {
        if (-not($computers -contains $result.ComputerName)) {
            $computers += $result.ComputerName
        }
    }
}
else {
    $filename = "$Computer-Programs.json"
    New-Item -Path ".\assets\results\Programs\$filename" -ItemType "file" -Force | Out-Null
}

if ($Computer -eq "list of computers") {

    # Object to store all results and convert to json
    $results = [PSCustomObject]@{

    }

    foreach ($pc in $list) {

        $this_PCs_software = $found_software | Where-Object { $_.ComputerName -like "*$pc*" }

        $programs = @()

        foreach ($program in $this_PCs_software) {

            try {
                $regPath = $($program.RegPath).Replace("\", "\\")
            }
            catch {
                Write-Host $_
                $regPath = "None"
            }
                
    
            $software_obj = @{
                ComputerName = $program.ComputerName
                Name         = $program.Name
                Version      = $program.Version
                InstallDate  = $program.InstallDate
                RegPath      = $regPath
            }
    
            $programs += $software_obj
            
        }

        $computer_results = @{
            Programs = $programs
        }
        $results | Add-Member -MemberType NoteProperty -Name "$pc" -Value $computer_results

    }

    Set-Content -Path ".\assets\results\Programs\$filename" -Value (ConvertTo-Json $results -Depth 4)
}
else {
    # Log each software found to json
    $results = [PSCustomObject]@{

    }

    $this_PCs_software = $found_software | Where-Object { $_.ComputerName -like "*$pc*" }

    $programs = @()

    foreach ($program in $this_PCs_software) {

        try {
            $regPath = $($program.RegPath).Replace("\", "\\")
        }
        catch {
            Write-Host $_
            $regPath = "None"
        }

        $software_obj = @{
            ComputerName = $program.ComputerName
            Name         = $program.Name
            Version      = $program.Version
            InstallDate  = $program.InstallDate
            RegPath      = $regPath
        }

        $programs += $software_obj
        
    }

    $computer_results = @{
        Programs = $programs
    }
    $results | Add-Member -MemberType NoteProperty -Name "$pc" -Value $computer_results

    Set-Content -Path ".\assets\results\Programs\$filename" -Value (ConvertTo-Json $results -Depth 4)
}
return $filename