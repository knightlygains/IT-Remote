# Function used to consistently log powershell errors with a time stamp.

Function Log-Error {
    param(
        [string]$Message
    )
    Add-Content ".\assets\settings\log.txt" -Value "[$(Get-Date)]`n$Message`n"
}