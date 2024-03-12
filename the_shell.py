import subprocess

class Power_Shell():
    def __init___(self):
        self.pspath = "pwsh.exe"
        self.list_path = "./lists/computers.txt"
    
    def enable_winrm(self, computer):
        p = subprocess.call(["pwsh.exe", "-File", f"./scripts/enable_winrm.ps1", f"{computer}" ])
        if p == 0:
            return f"WinRM is enabled on {computer}."
        else:
            return f"WinRM could not be enabled on {computer}."
    
    def ping(self, computer):
        p = subprocess.call(["pwsh.exe", "-File", f"./scripts/ping_computer.ps1", f"{computer}" ])
        if p == 0:
            return f"{computer} is online."
        else:
            return f"{computer} is offline."
    
    def quser(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/whosLoggedIn.ps1", f"{computer}" ])
        return p
    
    def check_printers(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/check_printers.ps1", f"{computer}" ])
        return p
    
    def printer_wizard(self, computer):
        p = subprocess.call(["pwsh.exe", "-File", f"./scripts/PrinterWizard.ps1", f"{computer}" ])
        if p == 0:
            return f"Got the printers from {computer}."
        else:
            return f"Failed to get the printers from {computer}."

    def test_page(self, computer, printerName):
        p = subprocess.call(["pwsh.exe", "-File", f"./scripts/test_page.ps1", f"{computer}", f"{printerName}"])
        if p == 0:
            return f"Test page sent to {computer}."
        else:
            return f"Test page failed to send to {computer}."
    
    def rename_printer(self, computer, printerName, newName):
        p = subprocess.call(["pwsh.exe", "-File", f"./scripts/rename_printer.ps1", f"{computer}", f"{printerName}", f"{newName}"])
        if p == 0:
            return f"Renamed a printer on {computer}."
        else:
            return f"Failed to rename a printer on {computer}."
        
    def uninstall_printer(self, computer, printerName):
        p = subprocess.call(["pwsh.exe", "-File", f"./scripts/uninstall_printer.ps1", f"{computer}", f"{printerName}"])
        if p == 0:
            return f"Uninstalled printer {printerName} on {computer}."
        else:
            return f"Failed to uninstall {printerName} on {computer}."
    
    def clear_space(self, computer, list, users, logout):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/disk_cleanup.ps1", f"{computer}", f"{users}", f"{logout}", f"{list}"])
        return p