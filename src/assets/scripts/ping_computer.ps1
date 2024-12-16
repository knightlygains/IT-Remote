[CmdletBinding()]
param(
    [string]$Computer
)

$result = Test-Connection $Computer -ResolveDestination -Count 1
if ($result.Status -eq "TimedOut") {
    # Couldn't ping known destination
    Write-Output "Connection to $Computer timed out."
    exit 2
}
elseif ($result.Status -eq "Success") {
    # Pinged computer successfully
    Write-Output "$($result.Destination) is online."
    exit 0
}
else {
    # Failed
    Write-Output "$Computer is offline or doesn't exist."
    exit 1
}
