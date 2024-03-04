import subprocess
import sys
import flet as ft

class Power_Shell():
    def __init___(self):
        self.pspath = "pwsh.exe"
    
    def ping(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-Command", f"ping {computer}"])
        return p
    
    def quser(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/whosLoggedIn.ps1", f"{computer}" ])
        return p
    
    def check_printers(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/check_printers.ps1", f"{computer}" ])
        return p
    
    def printer_wizard(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/PrinterWiz.ps1", f"{computer}" ])
        return p
    
    def test_commands(self):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/test.ps1"])
        return p

    def test_page(self, computer, printerName):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/test_page.ps1", f"{computer}", f"{printerName}"])
        return p