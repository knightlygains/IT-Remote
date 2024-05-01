param(
    [string]$Computer,
    [string]$id,
    [string]$winRM = "True"
)

. .\scripts\functions.ps1

if ($winrRM -eq "True") {
    $winRM = $true
}
else {
    $winRM = $false
}

$result_json_path = ".\results\Battery\$id-BatteryStatus.json"

# Create json file
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

Function CheckBattery {

    if ($Computer -eq "list of computers") {
        $Computer = Get-Content ".\lists\computers.txt"
        Write-Host "List of computers"
        Write-Host $Computer
    
        if ($winRM) {
            foreach ($pc in $Computer) {
                Enable-WinRM $pc
            }
        }
    }

    $results = ConvertFrom-Json $json_format

    foreach ($pc in $Computer) {
        if (Test-Connection $pc) {
            $battery = Get-CimInstance -Class CIM_Battery -ComputerName $Computer | Select-Object EstimatedChargeRemaining, BatteryStatus, DesignCapacity, FullChargeCapacity

            $script:batteryStatus = ""

            $designCapacity = "$($battery.DesignCapacity)"

            $fullChargeCapacity = "$($battery.FullChargeCapacity)"

            #Get and convert the batterystatus code to its definition
            switch ($battery.BatteryStatus) {
                1 { $batteryStatus = "Other" }
                2 { $batteryStatus = "Unknown" }
                3 { $batteryStatus = "Fully Charged" }
                4 { $batteryStatus = "Low" }
                5 { $batteryStatus = "Critical" }
                6 { $batteryStatus = "Charging" }
                7 { $batteryStatus = "Charging and High" }
                8 { $batteryStatus = "Charging and Low" }
                9 { $batteryStatus = "Charging and Critical" }
                10 { $batteryStatus = "Undefined" }
                11 { $batteryStatus = "Partially Charged" }
            }


            PsExec.exe \\$pc "C:\Windows\System32\powercfg.exe" /batteryreport /output "C:\$pc-BatteryReport.html"

            $htmlFile = "\\$pc\C$\$pc-BatteryReport.html"

            Function Get-Html {
                $htmlContent = Get-Content "$htmlFile"

                $htmlContent = "$htmlContent"

                $htmlContent = $htmlContent -replace "\s", ""

                return $htmlContent
            }

            Function CheckMatch {
                param(
                    [string]$choice
                )

                $text = Get-Html

                if ($text -match "FULLCHARGECAPACITY<\/span><\/td><td>(?<fullcharge>.........)" -AND $choice -eq "fullcharge") {
                    $returnValue = $matches['fullcharge']
                    return $returnValue
                }
                elseif ($text -match "DESIGNCAPACITY<\/span><\/td><td>(?<design>.........)" -AND $choice -eq 'design') {
                    $returnValue = $matches['design']
                    return $returnValue
                }
            }

            $fullChargeCapacity = CheckMatch -choice "fullcharge"
            $designCapacity = CheckMatch -choice "design"

            #Get just the number
            $fullChargeCapacity = $fullChargeCapacity -replace '[a-zA-Z]', ''
            $designCapacity = $designCapacity -replace '[a-zA-Z]', ''

            $fullChargeCapacity = [int]$fullChargeCapacity
            $designCapacity = [int]$designCapacity

            $percentDifference = ($designCapacity - $fullChargeCapacity) / (($designCapacity + $fullChargeCapacity) / 2) * 100
            $percentEfficiency = 100 - $percentDifference
            $percentEfficiency = [int]$percentEfficiency

            if ($null -eq $percentDifference) {
                # Couldnt get html battery report
                exit 3
            }

            $json_safe_htmlfile = $htmlFile.Replace("\", "\\")

            $battery_obj = @"
    {
        "Efficiency": "$percentEfficiency%",
        "FullChargeCapacity": "$($fullChargeCapacity)mAh",
        "DesignCapacity": "$($designCapacity)mAh",
        "BatteryReport": "$json_safe_htmlfile"
    }
"@

            $results | add-member -Name "$pc" -value (ConvertFrom-Json $battery_obj) -MemberType NoteProperty
        }
    }

    try {
        Set-Content -Path $result_json_path -Value (ConvertTo-Json $results) -ErrorAction Stop
    }
    catch {
        Write-Host "Couldnt make json $_"
        exit 1
    }

}

CheckBattery