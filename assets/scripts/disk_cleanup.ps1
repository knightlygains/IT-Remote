
param (
    [string]$Computers,
    [string]$delete_users,
    [string]$logout,
    [string]$winRM = "True"
)

if ($winRM -eq "True") {
    $winRM = $true
}
else {
    $winRM = $false
}

Write-Output "winRM is $winRM"

. .\assets\scripts\functions.ps1

$list = Get-Content ".\settings\lists\computers.txt"
# If using list, set Computers = to Get-Content for list contents
if ($Computers -eq "list of computers") {
    foreach ($Computer in $list) {
        Enable-WinRM -Computer $Computer -winRM $winRM
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
        param(
            [bool]$free_space_only = $false
        )
        try {
            $space = Get-CimInstance -ComputerName $Computer win32_logicaldisk -ErrorAction Stop | Select-Object -Property DeviceID, @{Label = 'FreeSpace'; expression = { ($_.FreeSpace / 1GB).ToString('F2') } }, @{Label = 'MaxSize'; expression = { ($_.Size / 1GB).ToString('F2') } }
            if ($free_space_only) {
                return $space.FreeSpace
            }
            return "$($space.FreeSpace) / $($space.MaxSize)"
        }
        catch {
            return "Couldn't query space on $Computer."
        }
    }

    if (Test-Connection $Computer) {
        $space_before = Get-Space $true

        $command = Invoke-Command -ComputerName $Computer -ScriptBlock {
            param($delete_users, $this_comps_results, $Computer, $logout)
            #Get logged in users
            $users = query user /server:$Computer;

            # Log out users if True
            if ($logout -eq "True") {
                $IDs = @() ;
                for ($i = 1; $i -lt $users.Count; $i++) {
                    # using regex to find the IDs
                    $temp = [string]($users[$i] | Select-String -pattern "\s\d+\s").Matches ;
                    $temp = $temp.Trim() ;
                    $IDs += $temp ;
                }
            
                foreach ($user_id in $IDs) {
                    logoff $user_id
                    $this_comps_results += "Logged off user ID: $user_id`n"
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
                $this_comps_results += "`nRemoved Windows\Temp on $Computer.`n"
            }
            catch {
                $this_comps_results += "`nCouldn't remove Windows\Temp on $($Computer): $_`n"
            }

            # Specify the path where temporary files are stored in the Windows Prefetch folder
            $Path2 = 'C' + ':\Windows\Prefetch' 
            try {
                Get-ChildItem $Path2 -Force -Recurse -ErrorAction Stop | Remove-Item -Recurse -Force -ErrorAction Stop
                $this_comps_results += "`nRemoved Windows\Temp on $Computer.`n"
            }
            catch {
                $this_comps_results += "`nCouldn't remove Windows\Prefetch on $($Computer): $_`n"
            }

            # Get each user and their temp directory then delete everything in it

            $user_folders = Get-ChildItem -Path "C:\Users"

            foreach ($user in $user_folders) {
                if ($user -ne "Public") {
                    $Path3 = 'C' + ":\Users\$($user.name)\AppData\Local\Temp"
                    # Remove all items (files and directories) from the specified user's Temp folder
                    try {
                        Get-ChildItem $Path3 -Force -Recurse -ErrorAction Stop | Remove-Item -Recurse -Force -ErrorAction Stop
                        $this_comps_results += "`nRemoved AppData\Local\Temp from $user on $Computer.`n"
                    }
                    catch {
                        $this_comps_results += "`nCouldn't remove AppData\Local\Temp from $user on $($Computer): $_`n"
                    }
                }
                
            }

            # If we want to delete user profiles
            if ($delete_users -eq "True") {
                # Get all CimInstances of user profiles
                $users_to_delete = Get-CimInstance Win32_UserProfile | 
                Where-Object {
                    $_.LocalPath -notLike "*Public" -and $_.LocalPath -notLike "*admin" -and $_.LocalPath -notLike "*localadmin" -and $_.LocalPath -notLike "*systemprofile" -and $_.LocalPath -notLike "*LocalService" -and $_.LocalPath -notLike "*NetworkService"
                }

                # Make sure they are not logged in before deleting
                foreach ($u in $users_to_delete) {
                    try {
                        Remove-CimInstance -InputObject $u -ErrorAction Stop
                        $this_comps_results += "`nRemoved user $($u.LocalPath) on $Computer.`n"
                    }
                    catch {
                        $this_comps_results += "`nCouldn't remove user $($u.LocalPath) on $($Computer): $_`n"
                    }
                    
                }
            }
            return $this_comps_results
        } -ArgumentList($delete_users, $this_comps_results, $Computer, $logout)

        $results = $command

        $space_after = Get-Space $true

        $space_cleared = $space_after - $space_before
        $space_cleared = [math]::Round($space_cleared, 2)

        $results += "`n$($Computer) - Space before: $($space_before)GB | Space after: $($space_after)GB."
        $results += "`nCleared space: $($space_cleared)GB."
    }
    else {
        $results += "$($Computer) could not be contacted."
    }

    New-Item -Path ".\assets\results\ClearSpace\$Computer-ClearSpace.txt" -ItemType "file" -Force
    Set-Content -Path ".\assets\results\ClearSpace\$Computer-ClearSpace.txt" -Value $results
}