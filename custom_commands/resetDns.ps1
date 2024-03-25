param(
    [string]$computer
)

Function EnableWinRM {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$Computers
    )
    Write-Host "Enabling Windows Remote Management..."
    #accept eula for psexec so it works
    Start-Process cmd -ArgumentList "/c psexec -accepteula" -WindowStyle hidden
    #Enable WinRM to use Get-CimInstance
    foreach ($computer in $Computers) {
        #check if winrm running on computer
        $result = winrm id -r:$Computers 2>$null
        if ($LastExitCode -eq 0) {
            Write-Host "WinRM already enabled on" $computer "..." -ForegroundColor green
        }
        else {
            Write-Host "Enabling WinRM on" $computer "..." -ForegroundColor red
            psexec.exe \\$computer -s C:\Windows\System32\winrm.cmd qc -quiet
        
            if ($LastExitCode -eq 0) {
                psservice.exe \\$computer restart WinRM
                $result = winrm id -r:$computer 2>$null
        
                if ($LastExitCode -eq 0) { Write-Host "WinRM successfully enabled!" -ForegroundColor green }
                else {
                    exit 1
                }
            }
            else {
                Write-Host "Couldn't enable WinRM on $computer."
            }
        }
    }
}

$script:done = $false

Do {

    if (Test-Connection $computer -Count 1) {
        EnableWinRM $computer

        Invoke-Command -ComputerName $computer -ScriptBlock {
            Write-Host "Showing network adapter information..."
            Write-Host "________________"
            $Adapters = Get-DNSClientServerAddress | Select-Object Address, ElementName, InterfaceAlias, InterfaceIndex, ServerAddresses
            foreach ($adapter in $Adapters) {
                if ($adapter.ElementName -match "wi-fi" -OR $adapter.ElementName -match "ethernet" -AND $adapter.ServerAddresses -match ".") {
                    Write-Host "Interface Index: " -ForegroundColor green -NoNewline
                    Write-Host "$($adapter.InterfaceIndex)"
                    Write-Host "Element Name: " -ForegroundColor green -NoNewline
                    Write-Host "$($adapter.ElementName)"
                    Write-Host "Server Addresses: " -ForegroundColor green -NoNewline
                    Write-Host "$($adapter.ServerAddresses)"
                    Write-Host "________________"
                }
            }
            $answer = Read-Host "Enter the InterfaceIndex of the adapter you want to reset"

            Write-Host "Resetting ServerAddresses on interface index $answer..."
            Set-DnsClientServerAddress -InterfaceIndex $answer -ResetServerAddresses

            Write-Host "Showing network adapter information..."
            Write-Host "________________"
            $Adapters = Get-DNSClientServerAddress | Select-Object Address, ElementName, InterfaceAlias, InterfaceIndex, ServerAddresses
            foreach ($adapter in $Adapters) {
                if ($adapter.ElementName -match "wi-fi" -OR $adapter.ElementName -match "ethernet" -AND $adapter.ServerAddresses -match ".") {
                    Write-Host "Interface Index: " -ForegroundColor green -NoNewline
                    Write-Host "$($adapter.InterfaceIndex)"
                    Write-Host "Element Name: " -ForegroundColor green -NoNewline
                    Write-Host "$($adapter.ElementName)"
                    Write-Host "Server Addresses: " -ForegroundColor green -NoNewline
                    Write-Host "$($adapter.ServerAddresses)"
                    Write-Host "________________"
                }
            }
        }
    }
    Do {
        $areWeDone = Read-Host "Do you want to run on another computer?(Y/N)"
    }until($areWeDone -eq "y" -OR $areWeDone -eq "n")

    if ($areWeDone -eq "n") {
        $done = $true
    }

}until($true -eq $done)


powershell -noexit