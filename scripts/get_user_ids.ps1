param(
    [string]$computer
)

Function Get-UserIDs {

    New-Item -Path ".\results\Users\$computer-Users.json" -ItemType "file" -Force | Out-Null
    
    $json_format = @"
    {
        
    }
"@

    $json_obj = ConvertFrom-Json $json_format

    # Get logged in users
    $users = query user /server:$computer;
    $found_users = @() ;

    # Filter out ID numbers from each user and store in list
    for ($i = 1; $i -lt $users.Count; $i++) {

        # using regex to find the IDs
        $temp = [string]($users[$i] | Select-String -pattern "\s\d+\s").Matches ;
        $temp = $temp.Trim() ;

        # Using split to grab username
        $username = -Split [string]($users[$i])
        $username = $username[0]

        $user_object = [PSCustomObject]@{
            Name = $username
            ID = $temp
        }

        $found_users += $user_object

        $user_json = @"
        {
            "ID": "$($temp)"
        }
"@

        $json_obj | add-member -Name "$username" -value (ConvertFrom-Json $user_json) -MemberType NoteProperty
    }

    # foreach ($user in $found_users) {
    #     logoff $user.ID /server:$computer
    #     Write-Host "Logged off $($user.Name), $($user.ID)"
    # }

    # Write-Host "Logged off $($found_users.length) users on $computer."

    Set-Content -Path ".\results\Users\$computer-Users.json" -Value (ConvertTo-Json $json_obj)
}

Get-UserIDs