
[CmdletBinding()]
param (
    [string]$Computers,
    [string]$delete_users,
    [string]$logout
)

Function Enable-WinRM {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computer
    )
    
    Write-Host "Enabling WinRM on" $Computer "..." -ForegroundColor red
    psexec.exe \\"$Computer" -s -nobanner -accepteula C:\Windows\System32\winrm.cmd qc -quiet

    $result = winrm id -r:$computer 2>$null
    if ($LastExitCode -eq 0) {
        psservice.exe \\"$Computer" -nobanner restart WinRM
        $result = winrm id -r:$computer 2>$null
        if ($LastExitCode -eq 0) { 
            Write-Host "WinRM Enabled on $Computer."
        }
        else {
            Write-Host "Failed to enable WinRM on $Computer."
        }
    }
    else {
        Write-Host "Failed to enable WinRM on $Computer."
    } #end of if
} #end of else 

$list = Get-Content ".\lists\computers.txt"
# If using list, set Computers = to Get-Content for list contents
if ($Computers -eq "Use-List") {
    foreach ($Computer in $list) {
        Write-Host "Unga $Computer"
        Enable-WinRM -Computer $Computer
    }
}
else {
    # If not using list, set list equal to computers
    # we passed in through args
    $list = $Computers
}

foreach ($Computer in $list) {
    $this_comps_results = ""

    Function Get-Space {
        try {
            $space = Get-CimInstance -ComputerName $Computer win32_logicaldisk -ErrorAction Stop | Select-Object -Property DeviceID, @{Label = 'FreeSpace'; expression = { ($_.FreeSpace / 1GB).ToString('F2') + "GB" } }, @{Label = 'MaxSize'; expression = { ($_.Size / 1GB).ToString('F2') + "kGB" } }
            return "$($space.FreeSpace) / $($space.MaxSize)"
        }
        catch {
            return "Couldn't query space on $Computer."
        }
    }

    if (Test-Connection $Computer) {
        $space_before = Get-Space

        $command = Invoke-Command -ComputerName $Computer -ScriptBlock {
            param($delete_users, $this_comps_results, $Computer, $logout)
            #Get logged in users
            $users = query user /server:$Computer;

            # We store logged in users and their IDs here so we can
            # get the IDs later for logoff.
            $arrayOfUsers = @() ;

            foreach ($user in $users) {
                if ($user -ne $users[0]) {
                    $user = ("$user").TrimStart()
                    $firstWhiteSpace = "$user".IndexOf(" ")
                    $userOnly = "$user".Substring(0, $firstWhiteSpace)
                    $arrayOfUsers += $userOnly
                }
            }

            #Remove recycle bin data
            $Path = 'C' + ':\$Recycle.Bin'
            # Get all items (files and directories) within the recycle bin path, including hidden ones
            try {
                Get-ChildItem $Path -Force -Recurse -ErrorAction Stop | Remove-Item -Recurse -Exclude "*.ini" -Force -ErrorAction Stop
                $this_comps_results += "Removed recycle bin data on $Computer.`n"
            }
            catch {
                $this_comps_results += "Couldn't remove recycle bin data on $($Computer): $_`n"
            }

            # Remove Temp files from various locations 
            $Path1 = 'C' + ':\Windows\Temp' 
            try {
                Get-ChildItem $Path1 -Force -Recurse -ErrorAction Stop | Remove-Item -Recurse -Force -ErrorAction Stop
                $this_comps_results += "Removed Windows\Temp on $Computer.`n"
            }
            catch {
                $this_comps_results += "Couldn't remove Windows\Temp on $($Computer): $_`n"
            }

            # Specify the path where temporary files are stored in the Windows Prefetch folder
            $Path2 = 'C' + ':\Windows\Prefetch' 
            try {
                Get-ChildItem $Path2 -Force -Recurse -ErrorAction Stop | Remove-Item -Recurse -Force -ErrorAction Stop
                $this_comps_results += "Removed Windows\Temp on $Computer.`n"
            }
            catch {
                $this_comps_results += "Couldn't remove Windows\Prefetch on $($Computer): $_`n"
            }

            # Get each user and their temp directory then delete everything in it

            $user_folders = Get-ChildItem -Path "C:\Users"

            foreach ($user in $user_folders) {
                if ($user -ne "Public") {
                    $Path3 = 'C' + ":\Users\$($user.name)\AppData\Local\Temp"
                    # Remove all items (files and directories) from the specified user's Temp folder
                    try {
                        Get-ChildItem $Path3 -Force -Recurse -ErrorAction Stop | Remove-Item -Recurse -Force -ErrorAction Stop
                        $this_comps_results += "Removed AppData\Local\Temp from $user on $Computer.`n"
                    }
                    catch {
                        $this_comps_results += "Couldn't remove AppData\Local\Temp from $user on $($Computer): $_`n"
                    }
                }
                
            }

            # If we want to delete user profiles
            if ($delete_users -eq "True") {
                # Get all CimInstances of user profiles
                $users_to_delete = Get-CimInstance Win32_UserProfile | Where-Object { ($_.LocalPath -notLike 
                        "Public", 
                        "admin", 
                        "localadmin")
                }
        
                if ($logout -eq "True") {
                    $IDs = @() ;
                    for ($i = 1; $i -lt $users.Count; $i++) {
                        # using regex to find the IDs
                        $temp = [string]($users[$i] | Select-String -pattern "\s\d+\s").Matches ;
                        $temp = $temp.Trim() ;
                        $IDs += $temp ;
                    }
                
                    foreach ($user_id in $IDs) {
                        Write-Host "Logging off user ID: $user_id"
                        logoff $user_id
                    }
                }

                # Make sure they are not logged in before deleting
                foreach ($u in $users_to_delete) {
                    try {
                        Remove-CimInstance -InputObject $u -ErrorAction Stop
                        $this_comps_results += "Removed user $($u.LocalPath) on $Computer.`n"
                    }
                    catch {
                        $this_comps_results += "Couldn't remove user $($u.LocalPath) on $($Computer): $_`n"
                    }
                    
                }
            }
            return $this_comps_results
        } -ArgumentList($delete_users, $this_comps_results, $Computer, $logout)

        $results = $command

        $space_after = Get-Space

        $results += "$($Computer) - Space before: $space_before | Space after: $space_after"
    }
    else {
        $results += "$($Computer) could not be contacted."
    }

    New-Item -Path ".\results\ClearSpace\$Computer-ClearSpace.txt" -ItemType "file" -Force
    Set-Content -Path ".\results\ClearSpace\$Computer-ClearSpace.txt" -Value $results
}