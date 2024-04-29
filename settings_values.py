import json

settings_values = {
    "app_color": "blue",
    "window_width": 745,
    "window_height": 515,
    "enable_win_rm": True,
    "supress_winrm_results": False,
    "use_24hr": False,
    "warn_about_profile_deletion": True
}

def load_settings(e, update):
    # Check if settings already exists
    if update:
        try:
            with open("settings.json", "r") as file:
                print("settings.json exists, updating")
                data = json.load(file)
                # Update each setting with value
                # stored in settings_values
                for key, value in settings_values.items():
                    print(f"{key} is now set to {value}")
                    data.update({
                        f"{key}": value
                    })
            with open("settings.json", "w") as settings:
                json.dump(data, settings, indent=4)
        except ValueError as e:
            print(f"Something went wrong updating settings, {e}")
            
    # Apply settings
    try:
        # Check for keys in settings, add non-existing ones
        # if necessary
        with open("settings.json", "r") as file:
            settings_data = json.load(file)
        for key, value in  settings_values.items():
            if key not in settings_data:
                # This line creates the key and assigns the value
                settings_data[key] = value
        
        # Save new keys
        with open("settings.json", "w") as file:
            json.dump(settings_data, file, indent=4)
            
        # Now set dict values equal to values stored in settings
        with open("settings.json", "r") as file:
            try:
                settings_data = json.load(file)
                settings_values["font_size"] = settings_data["font_size"]
                settings_values["app_color"] = settings_data["app_color"]
                settings_values["window_width"] = settings_data["window_width"]
                settings_values["window_height"] = settings_data["window_height"]
                settings_values["enable_win_rm"] = settings_data["enable_win_rm"]
                settings_values["supress_winrm_results"] = settings_data["supress_winrm_results"]
                settings_values["use_24hr"] = settings_data["use_24hr"]
                settings_values["warn_about_profile_deletion"] = settings_data["warn_about_profile_deletion"]
            except json.decoder.JSONDecodeError:
                print("No settings data found")
    except FileNotFoundError:
        print("No settings.json found. Creating a new one.")
        with open("settings.json", "w") as file:
            print("settings.json created")
            json.dump(settings_values, file, indent=4)