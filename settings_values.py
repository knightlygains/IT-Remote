import json, os

settings_values = {
    "app_color": "blue",
    "window_width": 745,
    "window_height": 515,
    "enable_win_rm": True,
    "supress_winrm_results": False,
    "use_24hr": False,
    "dark_theme": True,
    "warn_about_profile_deletion": True,
    "pwsh_path": "C:\\Program Files\\Powershell\\7\\pwsh.exe",
    "pstools_path": "C:\\Windows\\System32",
    "home_tab": 1
}

custom_scripts = {
    
}

custom_scripts_path = "assets/settings/custom_scripts.json"
settings_path = "assets/settings/settings.json"
computerlist_path = "assets/settings/lists/computers.txt"
logging_path = "assets/settings/log.txt"

# Make settings directory
if not os.path.exists("assets/settings"):
    try:
        os.mkdir("assets/settings")
    except Exception as e:
        print(e)
        
if not os.path.exists(logging_path):
    try:
        with open(logging_path, "w") as file:
            print("Created log.txt")
    except Exception as e:
        print(e)

# Make lists directory
if not os.path.exists("assets/settings/lists"):
    try:
        os.mkdir("assets/settings/lists")
    except Exception as e:
        print(e)

def script_sort_key(e):
    return e['index']

def re_index_scripts(e):
    print(custom_scripts)
    custom_scripts.sort(key=script_sort_key)
    print(custom_scripts)

def update_scripts(e):
    try:
        # Update custom scripts.
        # Should pull from dictionary and
        # replace all values in the json.
        with open(custom_scripts_path, "r") as file:
            data = {}
            
            # Get current scripts and save to data
            for script, properties in custom_scripts.items():
                data.update({
                    f"{script}": properties
                })
        
        # Dump to the json
        with open(custom_scripts_path, "w") as scripts:
            json.dump(data, scripts, indent=4)
        return True
    except ValueError as error:
        print(f"Something went wrong updating custom scripts, {error}")
        return False

def load_settings(e, update):
    
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
        
        update_scripts(e)
            
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

    # Load custom script data
    if os.path.exists(custom_scripts_path):
        with open(custom_scripts_path, "r") as file:
            data = json.load(file)
            for key, value in data.items():
                custom_scripts.update({key: value})
