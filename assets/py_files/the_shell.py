import subprocess
from os.path import exists
import json
import socket

class Power_Shell():
    def __init__(self):
        self.pspath = "pwsh.exe"
        self.list_path = "assets/settings/lists/computers.txt"
        self.no_window = 0x08000000
    
    def launch_script(self, script, ps_version):
        if ps_version:
            ps = self.pspath
        else:
            ps = "powershell.exe"
        p = subprocess.Popen([ps, script], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    def open_pc_list(self):
        file_exists = exists(self.list_path)
        if file_exists:
            p = subprocess.run(["notepad.exe", self.list_path])
        else:
            with open(self.list_path, "w") as file:
                print("Computer list file created.")
            p = subprocess.run(["notepad.exe", self.list_path])
    
    def enable_winrm(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/enable_winrm.ps1", f"{computer}"], creationflags=self.no_window)
        if p == 0:
            return f"WinRM is enabled on {computer}."
        else:
            return f"WinRM could not be enabled on {computer}."
    
    def ping(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/ping_computer.ps1", f"{computer}"], creationflags=self.no_window)
        if p == 0:
            return f"{computer} is online."
        elif p == 2:
            return f"Connection to {computer} timed out."
        else:
            return f"Couldn't ping {computer}."
    
    def quser(self, computer):
        p = subprocess.getoutput([self.pspath, "-File", f"./assets/scripts/whosLoggedIn.ps1", f"{computer}" ], creationflags=self.no_window)
        return p
    
    def check_printers(self, computer):
        p = subprocess.getoutput([self.pspath, "-File", f"./assets/scripts/check_printers.ps1", f"{computer}" ], creationflags=self.no_window)
        return p
    
    def printer_wizard(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/PrinterWizard.ps1", f"{computer}" ], creationflags=self.no_window)
        if p == 0:
            return f"Printers retrieved from {computer}. Click to open"
        else:
            return f"Failed to retrieve printers from {computer}."

    def test_page(self, computer, printerName):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/test_page.ps1", f"{computer}", f"{printerName}"], creationflags=self.no_window)
        if p == 0:
            return f"Test page sent to {computer}."
        elif p == 2:
            return f"Test page failed to send to {computer}. It is offline."
        else:
            return f"Test page failed to send to {computer}."
    
    def restart_print_spool(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/restart_spool.ps1", f"{computer}"], creationflags=self.no_window)
        if p == 0:
            return f"Print spooler restarted on {computer}."
        elif p == 2:
            return f"Failed to restart print spooler on {computer}. It is offline."
        else:
            return f"Failed to restart print spooler on {computer}."
    
    def print_logs(self, computer, type):
        if computer.lower() == "localhost":
            computer = socket.gethostname()
        p = subprocess.call([self.pspath, "-File", "./assets/scripts/print_logs.ps1", f"{computer}", f"{type}"], creationflags=self.no_window)
        if p == 0:
            result_json = f"./assets/results/printers/{computer}-Printers-{type}-logs.json"
            results = ""
            with open(result_json, "r") as file:
                data = json.load(file)
                for event in data:
                    evt = data[event]
                    results += f"________\nMessage:\n{evt['Message']}\n\nTime Created:\n{evt['TimeCreated']}\n\nId: {evt['Id']}\n\nLevel: {evt['Level']}\n________\n"
            return f"Retreived logs from {computer}. Click to open."
        else:
            return f"Failed to retreive logs from {computer}. Log may be empty."
    
    def rename_printer(self, computer, printerName, newName):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/rename_printer.ps1", f"{computer}", f"{printerName}", f"{newName}"], creationflags=self.no_window)
        if p == 0:
            return f"Renamed a printer on {computer}."
        elif p == 2:
            return f"Failed to rename a printer on {computer}. It is offline."
        else:
            return f"Failed to rename a printer on {computer}."
        
    def uninstall_printer(self, computer, printerName):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/uninstall_printer.ps1", f"{computer}", f"{printerName}"], creationflags=self.no_window)
        if p == 0:
            return f"Uninstalled printer {printerName} on {computer}."
        else:
            return f"Failed to uninstall {printerName} on {computer}."
    
    def clear_space(self, computer, users, logout, winRM):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/disk_cleanup.ps1", f"{computer}", f"{users}", f"{logout}", f"{winRM}"], creationflags=self.no_window)
        return p
    
    def check_space(self, computer, id, winRM):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/check_space.ps1", f"{computer}", f"{id}", f"{winRM}"], creationflags=self.no_window)
        if p == 0:
            return f"Open to view space on {computer}."
        else:
            return f"Failed to retrieve space on {computer}."
    
    def check_battery(self, computer, id, winRM):
        p = subprocess.call([self.pspath, "-File", "./assets/scripts/check_battery.ps1", f"{computer}", f"{id}", f"{winRM}"], creationflags=self.no_window)
        if p == 0:
            return f"Open to view battery info on {computer}."
        elif p == 3:
            return f"Check battery failed. The battery-report.html could not be found. C$ admin share may not enabled for {computer}."
        else:
            return f"Failed to get battery info on {computer}."
    
    def get_uptime(self, computer):
        subprocess.call([self.pspath, "-File", "./assets/scripts/get_uptime.ps1", f"{computer}"], creationflags=self.no_window)
        with open(f"assets/results/Uptime/{computer}-uptime.txt", "r") as result:
            results = result.read()
        return results
    
    def event_viewer(self, computer):
        p = subprocess.call([self.pspath, "-File", "./assets/scripts/event_viewer.ps1", f"{computer}"], creationflags=self.no_window)
        return p
    
    def open_c_share(self, computer):
        p = subprocess.call([self.pspath, "-File", "./assets/scripts/open_cshare.ps1", f"{computer}"], creationflags=self.no_window)
        return p
    
    def check_software(self, computer, software, id, all, winRM):
        p = subprocess.call(
            [
                self.pspath, 
                "-File", 
                f"./assets/scripts/check_software.ps1", 
                f"{computer}", 
                f"{software}", 
                f"{id}", 
                f"{all}", 
                f"{winRM}"
            ], 
            creationflags=self.no_window
        )
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
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/log_off_user.ps1", f"{computer}", f"{id}"], creationflags=self.no_window)
        if p == 0:
            return f"Logged out {name} on {computer}."
        else:
            return f"Failed to log out {name} on {computer}."
    
    def get_user_ids(self, computer):
        p = subprocess.call([self.pspath, "-File", f"./assets/scripts/get_user_ids.ps1", f"{computer}"], creationflags=self.no_window)
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
            use_24hr,
            winRM
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

        p = subprocess.call([
            self.pspath, 
            "-File", 
            f"./assets/scripts/restart.ps1",
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
            f"{timeFormat}",
            f"{winRM}"
        ], creationflags=self.no_window)

        if p == 0:
            with open(f"./assets/results/Restart/{id}-Restart.txt") as results:
                content = results.readlines()
            result = ""
            for line in content:
                result += line
            return f"{result}"
        else:
            return f"Failed to {action} {computer}."
