param(
    [string]$Computer
)

Function Open-CShare {
    param (
        [string]$Computer
    )
    if (Test-Connection $Computer -Count 1) {
        Invoke-Item -Path \\$Computer\C$
        exit 0
    }
    else {
        exit 1
    }
}

Open-CShare $Computer