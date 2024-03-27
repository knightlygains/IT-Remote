param (
    [string] $Computer,
    [string] $type
)

if ($Computer -like "localhost") {
    $Computer = $env:COMPUTERNAME
}

# Enable print service log
$enable_log_sb = {
    $logName = 'Microsoft-Windows-PrintService/Operational'

    $log = New-Object System.Diagnostics.Eventing.Reader.EventLogConfiguration $logName
    $log.IsEnabled = $true
    $log.SaveChanges()
}

try {
    Invoke-Command -ComputerName $Computer -ScriptBlock $enable_log_sb -ErrorAction Stop
}
catch {
    exit 1
}

$result_json_path = ".\results\Printers\$Computer-Printers-$type-logs.json"

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

$event_obj = ConvertFrom-Json $json_format

$event_num = 1

try {
    $result = Invoke-Command -ComputerName $Computer -ScriptBlock {
        param($type)
        $logs = Get-WinEvent "Microsoft-Windows-PrintService/$type" -MaxEvents 100
        return $logs
    } -ArgumentList $type -ErrorAction Stop

    function Escape-Text {
        param($text)
        $text = $text.Replace("\", "\\")
        return "$text"
    }

    foreach ( $log in $result) {

        $time_created = Escape-Text -text "$($log.TimeCreated)"
        $id = Escape-Text -text "$($log.Id)"
        $level = Escape-Text -text "$($log.Level)"
        $displayname = Escape-Text -text "$($log.DisplayName)"
        $message = Escape-Text -text "$($log.Message)"

        $log_object = @"
        {
            "TimeCreated": "$time_created",
            "Id": "$id",
            "Level": "$level",
            "DisplayName": "$displayname",
            "Message": "$message"
        }
"@
    
        $event_obj | add-member -Name "$event_num" -value (ConvertFrom-Json $log_object) -MemberType NoteProperty
    
        $event_num += 1
    }
}
catch {
    exit 1
}

try {
    Set-Content -Path $result_json_path -Value (ConvertTo-Json $event_obj) -ErrorAction Stop
}
catch {
    exit 1
}