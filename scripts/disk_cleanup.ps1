
# [CmdletBinding()]
param (
    [string]$Computers,
    [string]$delete_users,
    [string]$logout,
    [string]$list
)

if ($list -eq "True") {
    $Computers = Get-Content ".\lists\computers.txt"
}

foreach ($Computer in $Computers) {
    $this_comps_results = ""

    Invoke-Command -ComputerName $Computer -ScriptBlock {
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
        New-Item -Path ".\results\ClearSpace\$Computer-ClearSpace.txt" -ItemType "file" -Force
        Set-Content -Path ".\results\ClearSpace\$Computer-ClearSpace.txt" -Value $this_comps_results
    } -ArgumentList($delete_users, $this_comps_results, $Computer, $logout)
}