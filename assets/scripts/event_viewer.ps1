param(
    [string]$Computer
)

if (Test-Connection $Computer -Quiet) {
    eventvwr.exe $Computer
    exit 0
}
else {
    exit 1
}