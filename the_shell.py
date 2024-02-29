import subprocess
import sys

class Power_Shell():
    def __init___(self):
        self.pspath = "pwsh.exe"
    
    def ping(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-Command", f"ping {computer}"])
        return p
    
    def quser(self, computer):
        p = subprocess.getoutput(["pwsh.exe", "-File", f"./scripts/whosLoggedIn.ps1", f"{computer}" ])
        return p