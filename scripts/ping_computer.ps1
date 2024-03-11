[CmdletBinding()]
param(
    [string]$Computer
)

Function Ping-Computer {
    try {
        Test-Connection $Computer -Count 1 -erroraction Stop | Out-Null
        exit 0
    }
    catch {
        exit 1
    }
}
Ping-Computer

if ($LASTEXITCODE -eq 0) {
    exit 0
}
else {
    exit 1
}
