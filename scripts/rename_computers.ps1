param(
    [string]$id,
    [string]$winRM = "True"
)

if ($winRM -eq "True") {
    $winRM = $true
}
else {
    $winRM = $false
}

$old_names = Get-Content "./lists/computers.txt"
$new_names = Get-Content "./lists/new_names.txt"

$i = 0

foreach ($pc in $old_names) {
    Write-Host "Renaming $pc to $($new_names[$i])"
    $i ++
}