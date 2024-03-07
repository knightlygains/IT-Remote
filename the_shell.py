import subprocess
import sys
import flet as ft

class Power_Shell():
    def __init___(self):
        self.pspath = "pwsh.exe"
        self.list_path = "./lists/computers.txt"
    
    def enable_winrm(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/enable_winrm.ps1", f"{computer}" ])
        return p
    
    def ping(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/ping_computer.ps1", f"{computer}" ])
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
    
    def rename_printer(self, computer, printerName, newName):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/rename_printer.ps1", f"{computer}", f"{printerName}", f"{newName}"])
        return p
    
    def clear_space(self, computer, list, users, logout):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/disk_cleanup.ps1", f"{computer}", f"{users}", f"{logout}", f"{list}"])
        return p