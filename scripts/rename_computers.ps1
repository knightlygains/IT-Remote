param(
    [string]$Computer,
    [string]$username,
    [string]$id,
    [string]$winRM = "True"
)

if ($winRM -eq "True") {
    $winRM = $true
}
else {
    $winRM = $false
}

$results = ""
$results_file = "./results/$id-rename_computers.txt"

# Create json file
try {
    if (-not(Test-Path $results_file)) {
        New-Item -Path $results_file -ItemType "file" -Force -ErrorAction Stop
    }
}
catch {
    exit 1
}

if ($Computer -eq "list of computers") {
    $old_names = Get-Content "./lists/computers.txt"
}
else {
    $old_names = $Computer
}

$new_names = Get-Content "./lists/new_names.txt"

$new_new_names = @()

foreach ($name in $new_names) {
    $new_new_names += $name
}

$i = 0

foreach ($pc in $old_names) {
    
    try {
        Rename-Computer -ComputerName $pc -NewName $new_new_names[$i] -Credential $username -Force -Verbose -ErrorAction Stop
        $results += "Renamed $pc to $($new_new_names[$i]).`n"
    }
    catch {
        Write-Host "Couldn't rename, adding to failed list" -ForegroundColor Red
        $results += "Couldn't rename $pc. $_`n"
    }

    Write-Host "Renaming $pc to $($new_new_names[$i])"
    $i ++
}

# Set-Content -Path $results_file -Value $results

exit 0