param (
    [string] $Computer,
    [string] $id,
    [string] $winRM = "True"
)

. .\scripts\functions.ps1

if ($winRM -eq "True") {
    $winRM = $true
}
else {
    $winRM = $false
}

if ($Computer -like "localhost") {
    $Computer = $env:COMPUTERNAME
}

$result_json_path = ".\results\ClearSpace\$id-Space-Available.json"

try {
    if (-not(Test-Path $result_json_path)) {
        New-Item -Path $result_json_path -ItemType "file" -Force -ErrorAction Stop
    }
}
catch {
    exit 1
}

$json_format = @"
    {

    }
"@

$all_results = ConvertFrom-Json $json_format

Function Get-Space {
    if ($Computer -eq "list of computers") {
        $Computer = Get-Content ".\lists\computers.txt"
        Write-Host "Computer is list"
    }
    foreach ($pc in $Computer) {
        $space_obj = ConvertFrom-Json $json_format
        if (Test-Connection $pc) {

            Enable-WinRM $pc $winRM

            try {
                $disks = Get-CimInstance -ComputerName $pc win32_logicaldisk -ErrorAction Stop | Select-Object -Property DeviceID, @{Label = 'FreeSpace'; expression = { ($_.FreeSpace / 1GB).ToString('F2') + " GB" } }, @{Label = 'MaxSize'; expression = { ($_.Size / 1GB).ToString('F2') + " GB" } }, SystemName
                foreach ($disk in $disks) {
                    $freespace = [float]$($disk.FreeSpace.replace("GB", ""))
                    $maxsize = [float]$($disk.MaxSize.replace("GB", ""))
                    $disk_id = $($disk.DeviceId)
                    $percentfree = [math]::Round((($freespace / $maxsize) * 100), 2)
                    $log_object = @"
                        {
                            "DiskId": "$($disk_id)",
                            "FreeSpace": "$($freespace)",
                            "MaxSize": "$($maxsize)",
                            "PercentFree": "$($percentfree)% left."
                        }
"@ 
                    $space_obj | add-member -Name "$disk_id" -value (ConvertFrom-Json $log_object) -MemberType NoteProperty
                    
                }

                $space_obj = ConvertTo-Json $space_obj

                $all_results | add-member -Name "$pc" -value (ConvertFrom-Json $space_obj) -MemberType NoteProperty
                
            }
            catch {
                Write-Host "Error checking space. $_"
                exit 1
            }
        }
        else {
            exit 1
        }
    }
    try {
        Set-Content -Path $result_json_path -Value (ConvertTo-Json $all_results) -ErrorAction Stop
    }
    catch {
        Write-Host "Couldnt make json $_"
        exit 1
    }
    exit 0
    
}

try {

    Get-Space

    exit 0
}
catch {
    exit 1
}