import json, os

settings_values = {
    "app_color": "blue",
    "window_width": 745,
    "window_height": 515,
    "enable_win_rm": True,
    "supress_winrm_results": False,
    "use_24hr": False,
    "warn_about_profile_deletion": True,
    "pwsh_path": "C:\\Program Files\\Powershell\\7\\pwsh.exe",
    "pstools_path": "C:\\Windows\\System32"
}

custom_scripts = {
    
}

def load_settings(e, update):
    custom_scripts_path = "assets/custom_scripts.json"
    settings_path = "assets/settings.json"
    # Check if settings already exists
    if update:
        try:
            with open(settings_path, "r") as file:
                print("settings.json exists, updating")
                data = json.load(file)
                # Update each setting with value
                # stored in settings_values
                for key, value in settings_values.items():
                    data.update({
                        f"{key}": value
                    })
            with open(settings_path, "w") as settings:
                json.dump(data, settings, indent=4)
        except ValueError as e:
            print(f"Something went wrong updating settings, {e}")
        
        try:
            # Update custom scripts.
            # Should pull from dictionary and
            # replace all values in the json.
            with open(custom_scripts_path, "r") as file:
                data = {}
                
                # Get current scripts and apply to data
                for key, value in custom_scripts.items():
                    data.update({
                        f"{key}": value
                    })
            
            # Dump to the json
            with open(custom_scripts_path, "w") as scripts:
                json.dump(data, scripts, indent=4)
        except ValueError as e:
            print(f"Something went wrong updating settings, {e}")
            
    # Apply settings
    try:
        # Check for keys in settings, add non-existing ones
        # if necessary
        with open(settings_path, "r") as file:
            settings_data = json.load(file)
        for key, value in  settings_values.items():
            if key not in settings_data:
                # This line creates the key and assigns the value
                settings_data[key] = value
        
        # Save new keys
        with open(settings_path, "w") as file:
            json.dump(settings_data, file, indent=4)
            
        # Now set dict values equal to values stored in settings
        with open(settings_path, "r") as file:
            try:
                settings_data = json.load(file)
                for key, value in settings_data.items():
                    settings_values[key] = value
            except json.decoder.JSONDecodeError:
                print("No settings data found")
    except FileNotFoundError:
        print("No settings.json found. Creating a new one.")
        with open(settings_path, "w") as file:
            print("settings.json created")
            json.dump(settings_values, file, indent=4)

    # Create custom_scripts json
    if os.path.exists(custom_scripts_path) == False:
        with open(custom_scripts_path, "w")as file:
            json.dump({}, file)
            print(f"{custom_scripts_path} created")

    if os.path.exists(custom_scripts_path):
        with open(custom_scripts_path, "r") as file:
            data = json.load(file)
            for key, value in data.items():
                custom_scripts.update({key: value})
