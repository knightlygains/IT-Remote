# whosLoggedIn

[cmdletBinding()]
param (
    [string] $computer
)

Function Get-LoggedInUser {
    $loggedInUsers = "No one"

    $users = query user /server:$computer;

    $arrayOfUsers = @() ;

    foreach ($user in $users) {
        if ($user -ne $users[0]) {
            $user = ("$user").TrimStart()
            $firstWhiteSpace = "$user".IndexOf(" ")
            $userOnly = "$user".Substring(0, $firstWhiteSpace)
            $arrayOfUsers += $userOnly
        }
    }

    #Check if we found any users logged in
    if ($arrayOfUsers.Length -ne 0) {
        #Reset loggedInUsers text
        $loggedInUsers = ""
        forEach ($user in $arrayOfUsers) {
            #Check if we are at the last user in the array and strcuture grammar accordingly
            if ($user -eq $arrayOfUsers[$arrayOfUsers.Length - 1] -AND $arrayOfUsers.Length -ne 1) {
                $loggedInUsers += "and $user "
                #check if there is only 1 user
            }
            elseif ($arrayOfUsers.Length -eq 1) {
                $loggedInUsers += "$user "
                #Else add comma to prepare for more users grammatically
            }
            else {
                $loggedInUsers += "$user, "
            }
        }
    }

    $message = "No one is logged in to computer: $Computer."

    #IF we have more than 1 user logged in:
    if ($arrayOfUsers.Length -ne 0 -AND $arrayOfUsers.Length -ne 1) {
        $message = $loggedInUsers + "are currently logged in to computer: $Computer."
        #IF we have just 1 user logged in:
    }
    elseif ($arrayOfUsers.Length -eq 1) {
        $message = $loggedInUsers + "is currently logged in to computer: $Computer."
    }

    return $message
}

Get-LoggedInUser