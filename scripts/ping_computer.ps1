[CmdletBinding()]
param(
    [string]$Computer
)

try {
    Test-Connection $Computer -Count 1 -erroraction Stop | Out-Null
    $result = "$Computer is online."
}
catch {
    $result = "$Computer is offline."
}

return $result
