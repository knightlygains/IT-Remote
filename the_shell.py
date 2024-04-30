import subprocess
from os.path import exists
import json
import socket

class Power_Shell():
    def __init__(self):
        self.pspath = "pwsh.exe"
        self.list_path = "./lists/computers.txt"
    
    def custom_command(self, path, params):
        run_list = [self.pspath, path]
        for item in params:
            run_list.append(item)
        p = subprocess.run(run_list)
    
    def open_pc_list(self):
        file_exists = exists(self.list_path)
        if file_exists:
            p = subprocess.run(["notepad.exe", self.list_path])
        else:
            with open(self.list_path, "w") as file:
                print("Computer list file created.")
            p = subprocess.run(["notepad.exe", self.list_path])
    
    def enable_winrm(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./scripts/enable_winrm.ps1", f"{computer}" ])
        if p == 0:
            return f"WinRM is enabled on {computer}."
        else:
            return f"WinRM could not be enabled on {computer}."
    
    def ping(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./scripts/ping_computer.ps1", f"{computer}" ])
        if p == 0:
            return f"{computer} is online."
        elif p == 2:
            return f"Connection to {computer} timed out."
        else:
            return f"Couldn't ping {computer}."
    
    def quser(self, computer):
        p = subprocess.getoutput([self.pspath, "-File", f"./scripts/whosLoggedIn.ps1", f"{computer}" ])
        return p
    
    def check_printers(self, computer):
        p = subprocess.getoutput([self.pspath, "-File", f"./scripts/check_printers.ps1", f"{computer}" ])
        return p
    
    def printer_wizard(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./scripts/PrinterWizard.ps1", f"{computer}" ])
        if p == 0:
            return f"Printers retrieved from {computer}. Click to open"
        else:
            return f"Failed to retrieve printers from {computer}."

    def test_page(self, computer, printerName):
        p = subprocess.call([self.pspath, "-File", f"./scripts/test_page.ps1", f"{computer}", f"{printerName}"])
        if p == 0:
            return f"Test page sent to {computer}."
        elif p == 2:
            return f"Test page failed to send to {computer}. It is offline."
        else:
            return f"Test page failed to send to {computer}."
    
    def print_logs(self, computer, type):
        if computer.lower() == "localhost":
            computer = socket.gethostname()
        p = subprocess.call([self.pspath, "-File", "./scripts/print_logs.ps1", f"{computer}", f"{type}"])
        if p == 0:
            result_json = f"./results/printers/{computer}-Printers-{type}-logs.json"
            results = ""
            with open(result_json, "r") as file:
                data = json.load(file)
                for event in data:
                    evt = data[event]
                    results += f"________\nMessage:\n{evt['Message']}\n\nTime Created:\n{evt['TimeCreated']}\n\nId: {evt['Id']}\n\nLevel: {evt['Level']}\n________\n"
            return f"Retreived logs from {computer}. Click to open."
        else:
            return f"Failed to retreive logs from {computer}."
    
    def rename_printer(self, computer, printerName, newName):
        p = subprocess.call([self.pspath, "-File", f"./scripts/rename_printer.ps1", f"{computer}", f"{printerName}", f"{newName}"])
        if p == 0:
            return f"Renamed a printer on {computer}."
        else:
            return f"Failed to rename a printer on {computer}."
        
    def uninstall_printer(self, computer, printerName):
        p = subprocess.call([self.pspath, "-File", f"./scripts/uninstall_printer.ps1", f"{computer}", f"{printerName}"])
        if p == 0:
            return f"Uninstalled printer {printerName} on {computer}."
        else:
            return f"Failed to uninstall {printerName} on {computer}."
    
    def clear_space(self, computer, users, logout, winRM):
        p = subprocess.call([self.pspath, "-File", f"./scripts/disk_cleanup.ps1", f"{computer}", f"{users}", f"{logout}", f"{winRM}"])
        return p
    
    def check_space(self, computer, id, winRM):
        p = subprocess.call([self.pspath, "-File", f"./scripts/check_space.ps1", f"{computer}", f"{id}", f"{winRM}"])
        if p == 0:
            return f"Open to view space on {computer}."
        else:
            return f"Failed to retrieve space on {computer}."
    
    def check_software(self, computer, software, id, all, winRM):
        p = subprocess.call([self.pspath, "-File", f"./scripts/check_software.ps1", f"{computer}", f"{software}", f"{id}", f"{all}", f"{winRM}"])
        if p == 0:
            return f"Open to view software on {computer}."
        else:
            return f"Failed to retrieve software on {computer}."
    
    def msinfo_32(self, computer):
        p = subprocess.run([self.pspath, "-command", f"msinfo32.exe /computer \\\\{computer}"])
        if p.returncode == 0:
            return f"Launched msinfo32 for {computer}."
        else:
            return f"Failed to launch msinfo32 for {computer}."
    
    def log_off_user(self, computer, id, name):
        p = subprocess.call([self.pspath, "-File", f"./scripts/log_off_user.ps1", f"{computer}", f"{id}"])
        if p == 0:
            return f"Logged out {name} on {computer}."
        else:
            return f"Failed to log out {name} on {computer}."
    
    def get_user_ids(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./scripts/get_user_ids.ps1", f"{computer}"])
        if p == 0:
            return f"Got user IDs from {computer}."
        else:
            return f"Failed to get user IDs from {computer}."
    
    def restart(
            self, 
            id, 
            shutdown, 
            scheduled, 
            computer, 
            month, 
            day, 
            year, 
            hour, 
            minute, 
            seconds, 
            use_24hr
        ):
        action = "restart"
        
        if use_24hr:
            timeFormat = "24"
        else:
            timeFormat = "12"
        
        if scheduled:
            scheduled = "True"
        else:
            scheduled = "False"
            
        if shutdown:
            shutdown = "True"
            action = "shutdown"
        else:
            shutdown = "False"
        print(f"print {computer}, shutdown {shutdown}")
        p = subprocess.call([
            self.pspath, 
            "-File", 
            f"./scripts/restart.ps1",
            f"{id}",
            f"{shutdown}",
            f"{scheduled}", 
            f"{computer}", 
            f"{month}",
            f"{day}",
            f"{year}",
            f"{hour}",
            f"{minute}",
            f"{seconds}",
            f"{timeFormat}"
        ])
        scheduled_time = f"{month}/{day}/{year}, {hour}:{minute}:{seconds}"
        print(f"Scheduled time {scheduled_time}")
        if p == 0:
            with open(f"./results/Restart/{id}-Restart.txt") as results:
                content = results.readlines()
            result = ""
            for line in content:
                result += line
            return f"{result}"
        else:
            return f"Failed to {action} {computer}."
