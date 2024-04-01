param (
    [string] $Computer
)

if ($Computer -like "localhost") {
    $Computer = $env:COMPUTERNAME
}

$result_json_path = ".\results\ClearSpace\$Computer-Space-Available.json"

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

$space_obj = ConvertFrom-Json $json_format

Function Get-Space {
    if (Test-Connection $Computer) {
        try {
            $disks = Get-CimInstance -ComputerName $Computer win32_logicaldisk -ErrorAction Stop | Select-Object -Property DeviceID, @{Label = 'FreeSpace'; expression = { ($_.FreeSpace / 1GB).ToString('F2') + " GB" } }, @{Label = 'MaxSize'; expression = { ($_.Size / 1GB).ToString('F2') + " GB" } }, SystemName
            foreach ($disk in $disks) {
                $freespace = [float]$($disk.FreeSpace.replace("GB", ""))
                $maxsize = [float]$($disk.MaxSize.replace("GB", ""))
                $percentfree = [math]::Round((($freespace / $maxsize) * 100), 2)
                $log_object = @"
                    {
                        "FreeSpace": "$($freespace)",
                        "MaxSize": "$($maxsize)",
                        "PercentFree": "$($percentfree)% left."
                    }
"@ 
                $space_obj | add-member -Name "$($disk.DeviceId)" -value (ConvertFrom-Json $log_object) -MemberType NoteProperty
            }
            try {
                Set-Content -Path $result_json_path -Value (ConvertTo-Json $space_obj) -ErrorAction Stop
            }
            catch {
                exit 1
            }
            exit 0
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
    Get-Space
    exit 0
}
catch {
    exit 1
}