[CmdletBinding()]
param(
    [string]$Computer
)

$result = Test-Connection $Computer -Count 1
$result
if ($result.Status -eq "TimedOut") {
    # Couldn't ping known destination
    exit 2
}
elseif ($result.Status -eq "Success") {
    # Pinged computer successfully
    exit 0
}
else {
    # Failed
    exit 1
}
