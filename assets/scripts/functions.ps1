# Function used to consistently log powershell errors with a time stamp.
Function Set-Error {
    param(
        [string]$Message
    )
    Add-Content ".\assets\settings\log.txt" -Value "[$(Get-Date)]`n$Message`n"
}

Function Enable-WinRM {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computer,
        [string]$winRM = $true
    )

    if ($winRM -eq $true) {
        psexec.exe \\$Computer -s -nobanner -accepteula powershell Enable-PSRemoting -Force

        try {
            $winrm_service = Invoke-Command -ComputerName $Computer -ScriptBlock {
                Get-Service winrm
            } -ErrorAction Stop
            if ( $winrm_service.Status -eq "Running") {
                return $true
            }
            else {
                return $false
            }
        }
        catch {
            Set-Error "$_"
            return $false
        }
    }
}