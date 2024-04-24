import flet as ft
import the_shell
import datetime
import json
import os, time
import socket, pathlib
from tutorial_btn import TutorialBtn
from dynamic_modal import DynamicModal
import uuid

# Default settings.json values
settings_values = {
    "font_size": 16,
    "app_color": "blue",
    "window_width": 745,
    "window_height": 515,
    "enable_win_rm": True,
    "supress_winrm_results": False,
    "use_24hr": False,
    "warn_about_profile_deletion": True
}

running_processes_count = 0

# Used to track the last computer printer wizard was run on,
# so as to not confuse with the current value in the computername
# text field.
printer_wiz_target_computer = ""
printer_to_change = ""

# Used to store a list of custom scripts
list_of_scripts = []

# Used for are you sure modal
said_yes = False
modal_not_dismissed = True

# Load user settings
def load_settings(e, update):
    # Check if settings already exists
    if update:
        try:
            with open("settings.json", "r") as file:
                print("settings.json exists, updating")
                data = json.load(file)
                for key, value in settings_values.items():
                    print(f"{key} is now set to {value}")
                    data.update({
                        f"{key}": value
                    })
                # data.update({
                #     "font_size": settings_values["font_size"], 
                #     "app_color": settings_values["app_color"],
                #     "enable_win_rm": settings_values["enable_win_rm"],
                #     "supress_winrm_results": settings_values["supress_winrm_results"],
                #     "use_24hr": settings_values["use_24hr"],
                #     "warn_about_profile_deletion": settings_values["warn_about_profile_deletion"]
                # })
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
    
load_settings(e=None, update=False)

# Create recent_computers.json
recent_computers_path = "./results/recent_computers.json"
if os.path.exists(recent_computers_path) == False:
    with open(recent_computers_path, "w") as file:
        print(f"{recent_computers_path} created")
        init_data = {"computers":[]}
        json.dump(init_data, file, indent=4)

#Cleanup old files
if os.path.exists("./results/Printers"):
    for filename in os.listdir("./results/Printers"):
        pathlib.Path(f"./results/Printers/{filename}").unlink()
if os.path.exists("./results/ClearSpace"):   
    for filename in os.listdir("./results/ClearSpace"):
        pathlib.Path(f"./results/ClearSpace/{filename}").unlink()
if os.path.exists("./results/Programs"):  
    for filename in os.listdir("./results/Programs"):
        pathlib.Path(f"./results/Programs/{filename}").unlink()
if os.path.exists("./results/Restart"):  
    for filename in os.listdir("./results/Restart"):
        pathlib.Path(f"./results/Restart/{filename}").unlink()

# Program
def main(page: ft.Page):
    page.fonts = {
        "Consola": "assets/fonts/Consola.ttf"
    }
    
    page.window_width = settings_values["window_width"]
    page.window_height = settings_values["window_height"]
    page.window_min_width = 745
    page.window_min_height = 515
    if page.window_width < page.window_min_width:
        page.window_width = page.window_min_width
    if page.window_height < page.window_min_height:
        page.window_height = page.window_min_height
    page.dark_theme = ft.Theme(color_scheme_seed=settings_values["app_color"])
    
    def save_page_dimensions(e):
        try:
            with open("settings.json", "r") as settings:
                data = json.load(settings)
                data.update({"window_width": page.width, "window_height": page.height})
            with open("settings.json", "w") as settings:
                json.dump(data, settings, indent=4)
        except ValueError as e:
            print(f"Something went wrong with saving page dimensions, {e}")   
        
    page.on_resize = save_page_dimensions
    page.snack_bar = ft.SnackBar(ft.Text("", ), duration=3000)
    
    def update_settings(e):
        if cg.value:
            settings_values["app_color"] = cg.value
        results_container.bgcolor = settings_values["app_color"]
        printer_wiz_list_container.bgcolor = settings_values["app_color"]
        page.dark_theme.color_scheme_seed = settings_values["app_color"]
        actions_view_container.bgcolor = settings_values["app_color"]
        settings_values["enable_win_rm"] = winrm_checkbox.value
        settings_values["supress_winrm_results"] = winrm_results_checkbox.value
        settings_values["use_24hr"] = use_24hr_checkbox.value
        settings_values["warn_about_profile_deletion"] = warn_checkbox.value
        load_settings(e, update=True)
        page.update()
    
    recent_computers_file = "./results/recent_computers.json"
    def update_recent_computers(computer, date, last_action):
        # We need to convert to json.
        # For each computer in data["Computers"]
        try:
            with open(recent_computers_file, "r") as file:
                
                recent_pc = {
                    "name": computer,
                    "date": date,
                    "last_action": last_action
                }
                
                g = json.load(file)
                
                if len(g["computers"]) < 20:
                    g["computers"].insert(0,recent_pc)
                else:
                    g["computers"].pop()
                    g["computers"].insert(0,recent_pc)
            
        except ValueError as e:
            print(f"Something went wrong updating recent computers file. {e}")
        finally:
            with open(recent_computers_file, "w") as file:
                json.dump(g, file, indent=4)
    
    def load_recent_computers(e):
        # Store list of recent computers
        recent_computer_names = []
        recent_computer_items = []
        
        with open(recent_computers_file, "r") as file:
            data = json.load(file)
            for item in data["computers"]:
                if item["name"] not in recent_computer_names:
                    recent_computer_items.append(item)
                    recent_computer_names.append(item["name"])
        
        list_of_recent_pcs_radios = []
        
        for pc in recent_computer_items:
            name = pc["name"]
            date = pc["date"]
            last_action = pc["last_action"]
            radio = ft.Row([
                ft.Column([
                    ft.Radio(value=name),
                    ft.Text(""),
                    ft.Text(""),
                ]),
                ft.Column([
                    ft.Text(f"{name}", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text(f"Date:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{date}")
                    ]),
                    ft.Row([
                        ft.Text(f"Last Action:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{last_action}")
                    ])
                ])
            ], width=260)
            list_of_recent_pcs_radios.append(radio)
        
        recent_pc_radio_grp = ft.RadioGroup(
            content=ft.Row(
                list_of_recent_pcs_radios,
                wrap=True,
                width=800,
                scroll=ft.ScrollMode.ADAPTIVE
            )
        )
        
        modal = DynamicModal(
            title="Select a recent computer:",
            content=recent_pc_radio_grp,
            close_modal_func=close_dynamic_modal,
            nolistview=True
        )
        
        page.dialog = modal.get_modal()
        page.dialog.open = True
        page.update()
        
        while page.dialog.open:
            pass
        
        if recent_pc_radio_grp.value != None:
            computer_name.value = recent_pc_radio_grp.value
            computer_name.update()
    
    def show_message(message):
        page.snack_bar.content.value = message
        page.snack_bar.open = True
        page.update()
    
    # Store list of runing processes here for tooltip
    list_of_processes = []
    
    # Store a list of computernames we have run actions on.
    list_of_computernames = []
    
    #Left pane navigation rail
    def navigate_view(e):
        #If called by a control set equal to control value
        # Otherwise we are likely passing a specific index
        try:
            index = e.control.selected_index
        except AttributeError:
            index = e
        
        if index == 0:
            current_view.controls = [settings_view]
        if index == 1:
            home_notification_badge.label_visible = False
            current_view.controls = [home]
        if index == 2:
            # Actions Tab
            current_view.controls = [actions_view]
        if index == 3:
            current_view.controls = [custom_scripts_view]
        if index == 4:
            pass
        if index == 5:
            pass
        if index == 6:
            # Print Wizard View
            rail.selected_index = 2
            current_view.controls = [print_wizard_view]
        page.update()
    
    home_notification_badge = ft.Badge(
        content=ft.Icon(ft.icons.HOME_OUTLINED),
        label_visible=False
    )
    
    rail = ft.NavigationRail(
        selected_index=1,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                label_content=ft.Text("Settings"),
            ),
            ft.NavigationRailDestination(
                icon_content=home_notification_badge,
                selected_icon_content=ft.Icon(ft.icons.HOME),
                label_content=ft.Text("Results"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.TERMINAL_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.TERMINAL),
                label_content=ft.Text("Actions"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.DESCRIPTION_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.DESCRIPTION),
                label_content=ft.Text("My Scripts"),
            ),
        ],
        on_change=navigate_view
    )
    
    # Other controls
    settings_save_btn = ft.FilledButton("Save", icon=ft.icons.SAVE, on_click=update_settings)
    results_label = ft.Text("Clear Results:", weight=ft.FontWeight.BOLD)
    
    # Container for running process cards
    show_running_processes = ft.ListView(expand_loose=True, spacing=10, padding=20)
    
    # List view for printer wizard
    printer_wiz_listview = ft.ListView(expand=1, spacing=10, padding=20,)
    printer_wiz_list_container = ft.Container(
        bgcolor=settings_values["app_color"],
        content=printer_wiz_listview,
        border_radius=20,
        expand=True,
    )
    
    new_printer_name = ft.TextField(expand=True)
    
    def check_computer_name():
        computer_name.value = computer_name.value.replace(" ", "")
        computer_name.value = computer_name.value.replace("\n", "")
        if computer_name.value.lower() == "localhost":
            computer_name.value = socket.gethostname()
        if computer_name.value == "":
            show_message("Please input a computer hostname")
            return False
        else:
            return True
    
    def date_time(**kwargs):
        x = datetime.datetime.now()
        day = x.strftime("%a")
        day_num = x.strftime("%d")
        month = x.strftime("%b")
        if settings_values["use_24hr"]:
            time = x.strftime("%X")
        else:
            time = x.strftime("%I:%M:%S %p")
            if time[0] == "0":
                time = time.lstrip("0")
                
        for key, value in kwargs.items():
            if key == "force_24" and value == True:
                return x.strftime("%X")
            
        return f"{day} {month} {day_num}, {time}"
    
    def update_results(title_text, data, id, **kwargs):
        print_log_card = False
        print_wiz_card = False
        check_space_card = False
        computer = computer_name.value
        subtitle=data
        for key, value in kwargs.items():
            if key == "print_log":
                print_log_card = True
            if key == "computer":
                computer = value
                if value.lower() == "localhost":
                    computer = socket.gethostname()
            if key == "type":
                type = value
            if key == "print_wiz":
                print_wiz_card = value
            if key == "check_space":
                check_space_card = value
            if key == "subtitle":
                subtitle=value  
        
        if computer not in list_of_computernames and computer != "list of computers":
            list_of_computernames.append(computer)
            comp_checkboxes.append(ft.Checkbox(label=f"{computer}", value=True, data=f"{computer}"))
        
        if computer != "list of computers":
            update_recent_computers(computer, date_time(), title_text)
        
        if print_log_card:
            data = f"./results/Printers/{computer}-Printers-{type}-logs.json"
        elif print_wiz_card:
            data = f"./results/Printers/{computer}-Printers.json"
        elif check_space_card:
            data = f"./results/ClearSpace/{computer}-Space-Available.json"
        
        card = generate_result_card(
            leading = ft.Icon(ft.icons.TERMINAL),
            title=ft.Text(title_text),
            date=date_time(),
            data=data,
            id=id,
            computer=computer,
            subtitle=subtitle
        )
        
        result_data.controls.insert(0, card)
        if rail.selected_index != 1:
            # If home isnt already selected, add notifcation badge
            home_notification_badge.label_visible = True
        
        apply_results_filter(filter_out_PCs, False)
    
    def add_new_process(process_object):
        global running_processes_count
        running_processes_count += 1
        list_of_processes.append(process_object)
        running_processes_count_text.value = f"{running_processes_count}"
        update_processes()
        page.update()
    
    def update_processes():
        """
        Resets list of controls for show_running_processes,
        then loops through list_of_process and re-adds
        existing ones.
        """
        # Reset lsit of controls
        show_running_processes.controls.clear()
        
        # The loop through existing ones and re-add
        for process in list_of_processes:
            comps = "Computers: "

            for comp in process["computers"]:
                comps +=  f"{comp} "
                
            new_proc_card = ft.Card(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(name=ft.icons.TERMINAL_ROUNDED),
                        title=ft.Text(process["name"]),
                        subtitle=ft.Text(comps),
                    )
                ])
            )
            show_running_processes.controls.append(new_proc_card)
        if len(list_of_processes) > 0:
            loading_gif.visible = True
        else:
            loading_gif.visible = False
    
    def end_of_process(id):
        """Remove process from running_processes by id
        """
        global running_processes_count
        for process in list_of_processes:
            if process["id"] == id:
                show_message(f"{process['name']} - {process['computers']}: has finished.")
                list_of_processes.remove(process)
                running_processes_count -= 1
                running_processes_count_text.value = f"{running_processes_count}"
        update_processes()
        page.update()
    
    def new_process(name, computers, date, id):
        """
        Define a new process' details
        """
        new_process = {
            "name": name,
            "computers":  computers,
            "date": date,
            "id": id
        }
        return new_process
    
    # Console text output
    result_data = ft.ListView(expand=1, spacing=10, padding=20)

    results_container = ft.Container(
        content=result_data,
        bgcolor=settings_values["app_color"],
        expand=True,
        alignment=ft.alignment.top_left,
        border_radius=20
    )
    
    # Holds controls we removed from result_data
    filtered_out_results = []
    
    # Computernames we want to filter out
    filter_out_PCs = []
    
    # temp list to hold controls that we removed from result_data
    remove_these_controls = []
    
    # Store all checkboxes generated for PCs we ran actions on
    comp_checkboxes = []
    
    def apply_results_filter(filter, clear_filter):
        
        for control in result_data.controls:
            if clear_filter:
                filter_out_PCs.clear()
    
                # If the controls data is equal to a computer in the filters list
                # Remove it and add it to another list
            if control.data["Computer"] in filter:
                filtered_out_results.append(control)
               
        for control in filtered_out_results:
            # If the controls computer isnt in the filter,
            # we want to re-add it to result_data
            if control.data["Computer"] not in filter:
                result_data.controls.append(control)
                remove_these_controls.append(control)
            else:
                try:
                    result_data.controls.remove(control)
                except ValueError:  # The control was already removed
                    pass
            
        for control in remove_these_controls:
            filtered_out_results.remove(control)
        
        remove_these_controls.clear()
        
        result_data.controls.sort(key=lambda control: control.data["SortDate"], reverse=True)
        if len(filter_out_PCs) > 0:
            filter_btn.icon = ft.icons.FILTER_ALT
            filter_btn.tooltip = "On"
        else:
            filter_btn.icon = ft.icons.FILTER_ALT_OFF
            filter_btn.tooltip = "Off"
        page.update()

    def filter_results(e):
        # Set up modal
        
        content = ft.Column(comp_checkboxes, expand=1, spacing=20)
        
        modal = DynamicModal(
            title=f"Filter results:",
            content=content,
            close_modal_func=close_dynamic_modal
        )
        
        page.dialog = modal.get_modal()
        page.dialog.open = True
        page.update()
        
        while page.dialog.open:
            pass
        
        for checkbox in comp_checkboxes:
            print(f"{checkbox.value} {checkbox.data}")
            
            # If computer is checked and was previously filtered out,
            # remove from filtered out list
            if checkbox.value and checkbox.data in filter_out_PCs:
                filter_out_PCs.remove(checkbox.data)
            
            # Else if computer is not in filtered out list and box isnt checked
            elif checkbox.data not in filter_out_PCs and checkbox.value == False:
                filter_out_PCs.append(checkbox.data)
        
        # result_data.update()
        apply_results_filter(filter_out_PCs, False)
    
    # Running Processes Modal \/
    def show_processes_modal(e):
        page.dialog = processes_modal
        processes_modal.open = True
        page.update()
    
    def close_processes_modal(e):
        processes_modal.open = False
        page.update()
        
    # Define card modal
    processes_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Running Processes", ),
        content=show_running_processes,
        actions=[
            ft.TextButton("Close", on_click=close_processes_modal),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    running_processes_icon = ft.IconButton(
        icon=ft.icons.TERMINAL, 
        on_click=show_processes_modal, 
        tooltip="Running processes",
        )
    
    running_processes_count_text = ft.Text(f"{running_processes_count}", )
    
    loading_gif = ft.Image(
        src=f"assets/images/gifs/loading.gif",
        width=50,
        height=25,
        visible=False,
        fit=ft.ImageFit.SCALE_DOWN,
        offset=ft.transform.Offset(-0.1, 1)
    )
    
    # Card modal Stuff \/
    def show_card_modal():
        page.dialog = result_card_modal
        result_card_modal.open = True
        page.update()
        
    def close_card_modal(e):
        result_card_modal.open = False
        page.update()
    
    # Define card modal
    result_card_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Title"),
        content=ft.Text("No content"),
        actions=[
            ft.TextButton("Close", on_click=close_card_modal),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_card(e):
        """
        Sets card modal content and opens it.
        """
        result_card_modal.content = ft.Container(
            content=ft.Column([
                ft.Text(e.control.data["data"], selectable=True)
            ], scroll=True))
        result_card_modal.title = ft.Text(e.control.title.value, )
        show_card_modal()
    
    def open_card_print_wiz(e):
        printer_wizard(e, target_computer=e.control.data["computer"])
    
    def remove_card(e):
        id = e.control.data
        if id == "all":
            # We clicked the remove all results button
            result_data.controls.clear()
        else:
            for control in result_data.controls:
                if id == control.data["Id"]:
                    result_data.controls.remove(control)
        page.update()
    
    def generate_result_card(leading, title, date, data, id, computer, **kwargs):
        """
        Clickable card that shows in the console.
        Is called from update_results()
        """
        for key,value in kwargs.items():
            if key == "subtitle":
                subtitle_data = value
        
        # if computer.lower() == "localhost":
        #     computer = socket.gethostname()
                
        data_max_length = 60
        # Format and shorten text
        subtitle_text = subtitle_data[0:data_max_length]
        if len(data) > data_max_length:
            subtitle_text += "..."
        
        print_log_options = [
            f"./results/Printers/{computer}-Printers-Operational-logs.json",
            f"./results/Printers/{computer}-Printers-Admin-logs.json"
        ]
        
        # Change card_content controls based on type of card
        # we are making.
        
        # Printer_wizard Card
        if data == f"./results/Printers/{computer}-Printers.json" and "Failed" not in subtitle_data:
            on_click_function = open_card_print_wiz
        # Print_Log card
        elif data in print_log_options:
            print("print log card")
            on_click_function = open_print_log_card
        elif data == f"./results/ClearSpace/{computer}-Space-Available.json" and "Failed" not in subtitle_data:
            on_click_function = open_space_card
        elif "results/Programs/" in data:
            print("software card")
            data = f"{data}"
            on_click_function = open_software_card
        else:
            data = subtitle_data
            on_click_function = open_card

        subtitle_content = ft.Text(f"{subtitle_text}")
        
        card_content = ft.Column([
            ft.ListTile(
                leading=ft.Column([
                    leading,
                    ft.Text(f"{date}")
                    ], width=85, spacing=1),
                trailing=ft.IconButton(
                    icon=ft.icons.CLOSE,
                    icon_size=10,
                    tooltip="Remove",
                    on_click=remove_card,
                    data=id
                ),
                title=title,
                subtitle=subtitle_content,
                on_click=on_click_function,
                data={"data": data, "computer": computer}
            ),
        ])
        
        result_card = ft.Card(
            content=card_content,
            data={"Id": id, "Computer": computer, "SortDate": date_time(force_24=True)}
        )
        
        return result_card
    
    # Dynamic Modal
    def show_dynamic_modal():
        page.dialog = dynamic_modal
        dynamic_modal.open = True
        page.update()
    
    def close_dynamic_modal(e):
        page.dialog.open = False
        page.update()
    
    # The dynamic modal is used to dynamically
    # assign content to its controls, then
    # use the show_dynamic_modal function to
    # display it.
    dynamic_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Title"),
        content=ft.Text("No content"),
        actions=[
            ft.TextButton("Close", on_click=close_dynamic_modal),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_print_log_card(e):
        """
        Sets print log card modal content and opens it.
        """
        logs_list_view = ft.ListView(expand=1, padding= 20)
        card_content = ft.Container(
            content=logs_list_view,
            expand=1,
            width= 500
        )
        log_json_path = e.control.data["data"]
        with open(log_json_path, "r") as file:
            data = json.load(file)
            for event in data:
                num = f"{event}"
                evt = data[event]
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"{num}", weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Text("Time Created:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{evt['TimeCreated']}", selectable=True),
                            ]),
                            ft.Row([
                                ft.Text("Message:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{evt['Message']}", selectable=True),
                            ], wrap=True),
                            ft.Row([
                                ft.Text("Id:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{evt['Id']}", selectable=True),
                            ]),
                            ft.Row([
                                ft.Text("Level:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{evt['Level']}", selectable=True),
                            ]),
                            
                        ], expand = 1),
                        expand = 1,
                        padding=20
                    ),
                    expand = 1
                )
                logs_list_view.controls.append(card)
        
        dynamic_modal.content = card_content
        dynamic_modal.title = ft.Text(f"{e.control.title.value}, {e.control.data["computer"]}")
        show_dynamic_modal()
    
    def open_space_card(e):
        """
        Uses dynamic modal to show info about the disk
        space on a computer.
        """
        space_list_view = ft.ListView(expand=1, padding= 20)
        card_content = ft.Container(
            content=space_list_view,
            expand=1,
            width= 500
        )
        space_json_path = e.control.data["data"]
        with open(space_json_path, "r") as file:
            data = json.load(file)
            for drive in data:
                drive_ltr = data[drive]
                freespace = drive_ltr['FreeSpace']
                maxsize = drive_ltr['MaxSize']
                percentfree = drive_ltr['PercentFree']
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"{drive}", weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Text("Percent Free:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{percentfree}", selectable=True),
                            ], wrap=True),
                            ft.Row([
                                ft.Text("Space:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{freespace} / {maxsize} GB", selectable=True),
                            ]),
                        ], expand = 1),
                        expand = 1,
                        padding=20
                    ),
                    expand = 1
                )
                space_list_view.controls.append(card)
                
        dynamic_modal.content = card_content
        dynamic_modal.title = ft.Text(f"{e.control.title.value}, {e.control.data["computer"]}")
        show_dynamic_modal()
    
    def open_software_card(e):
        software_json_path = e.control.data["data"]
        list_of_pcs = {}
        
        expansion_list = ft.ExpansionPanelList(
            elevation=8,
            controls=[]
        )
        
        with open(software_json_path, "r", encoding='utf-8') as file:
            data = json.load(file)
            for r in data:
                # r is equal to computer name.
                # comp is equal to 'Programs'.
                comp = data[r]
                
                for program in comp['Programs']:
                    
                    pc = program['ComputerName']

                    # First get PC and define an expansiontile for it
                    if pc not in list_of_pcs:
                        exp_panel = ft.ExpansionPanel(
                                header=ft.ListTile(
                                title=ft.Text(f"{pc}", weight=ft.FontWeight.BOLD),
                                trailing=ft.Icon(name=ft.icons.COMPUTER)
                            ),
                            content=ft.Row(wrap=True, spacing=10),
                            can_tap_header=True
                        )
                        
                        # Add dict key of pc name with value of expansiontile
                        list_of_pcs.update({f"{pc}": exp_panel})
                    
                    text = f"""Version: {program['Version']}
Install date: {program['InstallDate']}
Registry path: {program['RegPath']}"""
                    
                    # Then add program info to corresponding PCs in the dict
                    new_control = ft.Container(
                        content=ft.Column([
                            ft.Text(f"{program['Name']}", selectable=True, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{text}", selectable=True),
                        ]),
                        padding=20
                    )
                    
                    list_of_pcs[f"{pc}"].content.controls.append(new_control)

        # Loop through expansionpanels in list and append them to expansion_list
        for pc in list_of_pcs:
            expansion_list.controls.append(list_of_pcs[f"{pc}"])
        
        modal = DynamicModal(
            title=f"{e.control.title.value}, {e.control.data["computer"]}",
            content=ft.Column(controls=[
                expansion_list,
                ft.TextButton("Export results")
            ]),
            close_modal_func=close_dynamic_modal
        )
        page.dialog = modal.get_modal()
        page.dialog.open = True
        page.update()
        
    def open_tutorial_modal(e):
        """
        Uses print_log_card_modal to show help/topic info
        about features in the app.
        Uses control data to pass the topic info in a list.
        topic at index 0, explanatory text at index 1.
        """
        
        help_topic = e.control.data[0]
        help_text = e.control.data[1]
        
        content = ft.Row([
                ft.Text(f"{help_text}"),
            ], wrap=True, width=500)

        modal = DynamicModal(
            title=f"{help_topic}",
            content=content,
            close_modal_func=close_dynamic_modal,
            nolistview=True
        )
        
        page.dialog = modal.get_modal()
        page.dialog.open = True
        page.update()
        
    def ping(e):
        if check_computer_name():
            id = uuid.uuid4()
            add_new_process(new_process("Ping", [computer_name.value], date_time(), id))
            show_message(f"Pinging {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.ping(computer=computer_name.value)
            update_results("Ping", result, id)
            end_of_process(id)
    
    def enable_winrm(computer):
        if settings_values["enable_win_rm"]:
            if computer == None:
                computer = computer_name.value
            id = uuid.uuid4()
            add_new_process(new_process("WinRM", [computer], date_time(), id))
            powershell = the_shell.Power_Shell()
            result = powershell.enable_winrm(computer)
            if settings_values["supress_winrm_results"] != True:
                print("adding winrm result")
                update_results("WinRM", result, id)
            end_of_process(id)
    
    def quser(e):
        if check_computer_name():
            id = uuid.uuid4()
            add_new_process(new_process("QUSER", [computer_name.value], date_time(), id))
            show_message(f"Querying logged in users on {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.quser(computer=computer_name.value)
            update_results("QUser", result, id)
            end_of_process(id)
            
    def rename_printer(e):
        if check_computer_name():
            close_printer_dlg(e)
            id = uuid.uuid4()
            add_new_process(new_process("Rename Printer", [computer_name.value], date_time(), id))
            show_message(f"Renaming printer on {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.rename_printer(computer=computer_name.value, printerName=printer_to_change, newName=new_printer_name.value)
            update_results("Rename Printer", result, id)
            end_of_process(id)
        printer_wizard(e, refresh=True)
        
    # Rename Printer modal
    def close_printer_dlg(e):
        printer_name_modal.open = False
        page.update()

    enter_printer_name = ft.Column([
        ft.Row([
            ft.Text("What's the new name?", expand=True),
        ]),
        ft.Row([
            new_printer_name
        ]),
    ], alignment="center")

    printer_name_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Rename Printer"),
        content=enter_printer_name,
        actions=[
            ft.TextButton("Rename", on_click=rename_printer),
            ft.TextButton("Cancel", on_click=close_printer_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_printer_name_modal(e):
        global printer_to_change
        printer_to_change = e.control.data["printer"]
        page.dialog = printer_name_modal
        printer_name_modal.open = True
        page.update()
    
    # More info printer modal
    def open_printer_more_info_modal(e):
        global printer_wiz_target_computer
        printer_name = e.control.data
        
        def close_more_info_dlg(e):
            more_info_printer_modal.open = False
            page.update()
            return
        
        with open(f"./results/printers/{printer_wiz_target_computer}-Printers.json") as file:
            printers = json.load(file)
        
        for printer in printers:
            p = printers[printer]
            if p['Name'] == printer_name:
                more_info_printer = p
        
        more_info_printer_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"{more_info_printer['Name']}", selectable=True),
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Text(f"Status:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Status']}", selectable=True),
                    ])
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Port:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Port']}", selectable=True),
                    ])
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Published:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Published']}", selectable=True),
                    ])
                ]),ft.Row([
                    ft.Row([
                        ft.Text(f"Type:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Type']}", selectable=True),
                    ])
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Shared:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Shared']}", selectable=True),
                    ])
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Driver:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Driver']}", selectable=True),
                    ])
                ]),
            ]),
            actions=[
                ft.TextButton("Close", on_click=close_more_info_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = more_info_printer_modal
        more_info_printer_modal.open = True
        page.update()
    
    def printer_wizard(e, **kwargs):
        global printer_wiz_target_computer
        if check_computer_name():
            refresh = False
            computer = computer_name.value
            for key, value in kwargs.items():
                # Check if we are just refreshing list
                if key == "refresh":
                    refresh = value
                if key == "target_computer":
                    printer_wiz_target_computer = value
                    computer = printer_wiz_target_computer
            
            def load_printers():
                """Just load printers from existing json
                """
                printer_wiz_listview.controls.clear()
                try:
                    with open(json_file) as file:
                        printers = json.load(file)
                        
                    # For each printer in the json file, show a card
                    # containing text and buttons
                    for printer in printers:
                        new_printer = printers[printer]
                        
                        p_name = new_printer['Name']
                        
                        control_data = {"printer": p_name, "computer": printer_wiz_target_computer}
                        
                        printer_list_item_card = ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.ListTile(
                                        title=ft.Column([
                                                ft.Text(p_name, weight=ft.FontWeight.BOLD,),
                                                ft.Text(f"PortName: {new_printer['Port']}"),
                                                ft.Text(f"Status: {new_printer['Status']}")
                                            ], width=200),
                                        trailing=ft.PopupMenuButton(
                                            icon=ft.icons.MORE_VERT,
                                            items=[
                                                ft.PopupMenuItem(text="Test Page", data=control_data, on_click=printer_wiz_testpage),
                                                ft.PopupMenuItem(text="Rename", data=control_data, on_click=open_printer_name_modal),
                                                ft.PopupMenuItem(text=f"Uninstall {p_name}", data=control_data, on_click=uninstall_printer),
                                            ],
                                        ),
                                        data=p_name,
                                        on_click=open_printer_more_info_modal
                                    )
                                ]),
                            ),
                        )

                        printer_wiz_listview.controls.append(printer_list_item_card)
                    printer_wiz_computer.data = computer
                    printer_wiz_computer.value = f"{computer}'s printers. Last refreshed {date_refreshed}"
                    navigate_view(6)
                except FileNotFoundError:
                    show_message(f"Could not get printers on {computer}")
            
            json_file = f'./results/Printers/{computer}-Printers.json'
            
            if os.path.exists(json_file) and refresh != True:
                # If json file exists and we arent refreshing
                date_refreshed = os.path.getmtime(json_file)
                date_refreshed = time.ctime(date_refreshed)
                load_printers()
            else:
                date_refreshed = date_time()
                if refresh:
                    show_message(f"Refreshing printers on {computer}.")
                else:
                    show_message(f"Getting printers on {computer}")
                    enable_winrm(computer)
                printer_wiz_target_computer = computer
                id = uuid.uuid4()
                add_new_process(new_process("Get Printers", [computer], date_time(), id))
                powershell = the_shell.Power_Shell()
                result = powershell.printer_wizard(computer=computer)
                if refresh == False:
                    update_results("Get Printers", data=result, id=id, print_wiz=True, computer=computer, subtitle=result)
                load_printers()
                end_of_process(id)
        
    def printer_wiz_testpage(e):
        if check_computer_name():
            id = uuid.uuid4()
            add_new_process(new_process("Test Page", [e.control.data["computer"]], date_time(), id))
            show_message(f"Printing test page from {e.control.data["computer"]}.")
            powershell = the_shell.Power_Shell()
            result = powershell.test_page(computer=e.control.data["computer"], printerName=e.control.data["printer"])
            update_results("Printer Test Page", result, id=id)
            end_of_process(id)
    
    def are_you_sure(e, text, **kwargs):
        """
        add_content: a control you wish to add.
        Global are you sure modal.
        Waits in while loop until answered,
        retuning true or false depending on
        answer.
        """
        additional_content = ft.Text("None", visible=False)
        for key, value in kwargs.items():
            if key == "add_content":
                additional_content = value
                additional_content.visible = True
        global said_yes
        global modal_not_dismissed
        
        said_yes = False
        modal_not_dismissed = True
        
        def dismissed(e):
            global modal_not_dismissed
            modal_not_dismissed = False
        
        def close_sure_dlg(e):
            sure_modal.open = False
            page.update()
            return
        
        def answer(e):
            global said_yes
            said_yes = True
            close_sure_dlg(e)
        
        sure_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text("Confirm:"),
            content=ft.Column([
                    ft.Row([
                        ft.Text(f"{text}", weight=ft.FontWeight.BOLD)
                    ]),
                    additional_content
                ], height=100),
            actions=[
                ft.TextButton("Yes", on_click=answer),
                ft.TextButton("Cancel", on_click=close_sure_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=dismissed
        )
        
        page.dialog = sure_modal
        sure_modal.open = True
        page.update()
        
        # Have to sit here in while loop
        # to make sure function doesnt exit
        # early.
        while modal_not_dismissed:
            pass
        
        if said_yes:
            return True
        else:
            return False 
    
    def uninstall_printer(e):
        if are_you_sure(e, f"Uninstall {e.control.data["printer"]} from {e.control.data["computer"]}?"):
            id = uuid.uuid4()
            add_new_process(new_process("Uninstall Printer", [e.control.data["computer"]], date_time(), id))
            show_message(f"Uninstalling printer from {e.control.data["computer"]}.")
            powershell = the_shell.Power_Shell()
            result = powershell.uninstall_printer(computer=e.control.data["computer"], printerName=e.control.data["printer"])
            update_results("Uninstall Printer", result, id)
            end_of_process(id)
            printer_wizard(e, refresh=True, target_computer=e.control.data["computer"])
    
    def open_print_logs(e):
        if check_computer_name():
            computer = computer_name.value
            type = e.control.data
            enable_winrm(computer)
            id = uuid.uuid4()
            add_new_process(new_process(f"{type} Log", [computer], date_time(), id))
            show_message(f"Getting {type} print logs from {computer}.")
            powershell = the_shell.Power_Shell()
            result = powershell.print_logs(computer, type)
            update_results(title_text=f"{type} Log", data=result, id=id, print_log=True, computer=computer, type=type, subtitle=result)
            end_of_process(id)
    
    def open_c_share(e):
        pass

    def check_bootup(e):
        pass
    
    def open_event_log(e):
        pass
    
    def check_battery(e):
        pass
    
    
    def open_restart_modal(e):

        use_list_checkbox = ft.Checkbox(label="Use list of PCs", value=False)
        shutdown_checkbox = ft.Checkbox(label="Shutdown only", value=False)
        def show_schedule_options(e):
            value = e.control.value
            time_button.visible = value
            date_button.visible = value
            page.update()
        
        time_button = ft.ElevatedButton(
            "Pick time",
            icon=ft.icons.SCHEDULE,
            on_click=lambda _: time_picker.pick_time(),
            visible=False
        )
        
        date_button = ft.ElevatedButton(
            "Pick date",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: date_picker.pick_date(),
            visible=False
        )
        
        schedule_checkbox = ft.Checkbox(
            label="Schedule it", 
            value=False,
            on_change=show_schedule_options
        )
        
        def set_time_text(e):
            time_text.value = e.control.value
            page.update()
            
        def set_date_text(e):
            text = str(e.control.value).split()
            text = text[0]
            date_text.value = text
            page.update()
        
        time_picker = ft.TimePicker(
            confirm_text="Confirm",
            error_invalid_text="Time out of range",
            help_text="Choose a time to restart",
            on_change=set_time_text
        )
        
        date_picker = ft.DatePicker(
            first_date=datetime.datetime.now(),
            last_date=datetime.datetime(2099, 10, 1),
            on_change=set_date_text
        )
        
        page.overlay.append(time_picker)
        page.overlay.append(date_picker)
        
        time_text = ft.Text("")
        date_text = ft.Text("")
        
        content = ft.Column([
            use_list_checkbox,
            shutdown_checkbox,
            schedule_checkbox,
            ft.Row([
                time_button,
                time_text
            ]),
            ft.Row([
                date_button,
                date_text
            ])
            
        ])
        
        doing_action = False
        date = None
        year = None
        month = None
        day = None
        time = None
        scheduled = False
        shutdown_only = False
        list = False
        def finalize(e):
            nonlocal doing_action
            nonlocal date
            nonlocal year
            nonlocal month
            nonlocal day
            nonlocal time
            nonlocal scheduled
            nonlocal list
            nonlocal shutdown_only
            
            # If we arent using list and we dont have a computername entered, close
            if use_list_checkbox.value == False and check_computer_name() == False:
                close_dynamic_modal(e)
            else:
                # Schedule restart
                if shutdown_checkbox.value:
                    shutdown_only = True
                if schedule_checkbox.value:
                    try:
                        # print(date_picker.value)
                        # print(time_picker.value)
                        scheduled = schedule_checkbox.value
                        doing_action = True
                        list = use_list_checkbox.value
                        date = str(date_picker.value).split()
                        date = date[0]
                        date = date.split("-")
                        year = date[0]
                        month = date[1]
                        day = date[2]
                        time = time_picker.value
                        print(f"Date: {date}")
                        print(f"Time: {time}")
                        close_dynamic_modal(e)
                    except AttributeError:
                        close_dynamic_modal(e)
                        show_message("Picke a date and time")
                else:
                    print("no times picked")
                    doing_action = True
                    scheduled = schedule_checkbox.value
                    list = use_list_checkbox.value
                    date = datetime.datetime.now()
                    year = date.year
                    month = date.month
                    day = date.day
                    time = str(date).split()
                    time = time[1]
                    print(f"{year},{month},{day},{time}")
                    close_dynamic_modal(e)
                    
                
        
        modal = DynamicModal(
            title=f"Shutdown/Restart",
            content=content,
            close_modal_func=close_dynamic_modal,
            nolistview=True,
            add_action=ft.TextButton("Shutdown/Restart", on_click=finalize)
        )
        
        page.dialog = modal.get_modal()
        page.dialog.open = True
        page.update()
        
        while page.dialog.open:
            pass
        
        if list:
            computer = "list of computers"
        else:
            computer = computer_name.value
        
        if doing_action and shutdown_only == False:
            print(f"restarting {computer}")
            restart(scheduled, shutdown_only, computer, month=month, day=day, year=year, time=time)
        elif doing_action and shutdown_only:
            print(f"Shutting down {computer}")
            restart(scheduled, shutdown_only, computer, month=month, day=day, year=year, time=time)
       
    
    def restart(scheduled, shutdown, computer, **kwargs):
        for key, value in kwargs.items():
            if key == "month":
                month = int(value)
            if key == "day":
                day = int(value)
            if key == "year":
                year = int(value)
            if key == "time":
                time = str(value)
                time = time.split(":")
                hour = int(time[0])
                minute = int(time[1])
                seconds = int(float(time[2]))
        
        if computer != "list of computers":
            enable_winrm(computer)
        else:
            print(f"Computer is use-lsit {computer}")
        
        id = uuid.uuid4()
        add_new_process(new_process("Restart", [computer], date_time(), id))
        show_message(f"Restarting {computer}")
        powershell = the_shell.Power_Shell()
        result = powershell.restart(id, shutdown, scheduled, computer, month, day, year, hour, minute, seconds, settings_values["use_24hr"])
        
        update_results("Restart", result, id, computer=computer)
        end_of_process(id)
        print("restarted")

    # Computer Text Field
    computer_name = ft.TextField(label="Computer Name")
    
    ping_btn = ft.TextButton(text="Ping", icon=ft.icons.NETWORK_PING, on_click=ping)
    quser_btn = ft.IconButton(
        icon=ft.icons.PERSON,
        icon_size=20,
        tooltip="QUser",
        on_click=quser
    )

    def open_pc_list(e):
        powershell = the_shell.Power_Shell()
        powershell.open_pc_list()
    
    delete_users_checkbox = ft.Checkbox(label="Remove user profiles", value=False)
    logout_users_checkbox = ft.Checkbox(label="Logout users before deletion", value=False)
    use_list_checkbox = ft.Checkbox(label="Use list of PCs", value=False)
    
    def clear_space(e):
        users = "False"
        logout = "False"
        if delete_users_checkbox.value == True:
            users = "True"
        if logout_users_checkbox.value == True:
            logout = "True"
            
        def run_operation(computer):
            
            if delete_users_checkbox.value and settings_values["warn_about_profile_deletion"]:
                
                are_you_sure(
                    e, 
                    "Are you sure you want to remove profiles? Users could lose valuable data."
                )
                
                update_settings(e)
            
            if computer != "list of computers":
                enable_winrm(computer)
            # else skip winrm here, it will be done in script
            
            id = uuid.uuid4()
            
            # If we are using a list of pcs,
            # get each pc from list and create
            # an array of them.
            if computer == "list of computers":
                list_of_pcs = []
                list = open("./lists/computers.txt", "r")
                computers = list.readlines()
                for pc in computers:
                    list_of_pcs.append(pc.strip("\\n"))
                add_new_process(new_process("Clear Space", list_of_pcs, date_time(), id))
                show_message(f"Clearing space on list of PCs.")
            else:
                add_new_process(new_process("Clear Space", [computer], date_time(), id))
                show_message(f"Clearing space on {computer}.")
                
            powershell = the_shell.Power_Shell()
            powershell.clear_space(computer=computer, users=users, logout=logout)
            
            if use_list_checkbox.value == True:
                for pc in list_of_pcs:
                    pc_result = open(f"./results/ClearSpace/{pc}-ClearSpace.txt", "r")
                    read_pc_result = pc_result.readlines()
                    update_results("Clear Space", read_pc_result, id)
                    pc_result.close()
            else:
                results = open(f"./results/ClearSpace/{computer}-ClearSpace.txt", "r")
                result = results.read()
                update_results("Clear Space", result, id)
            
            end_of_process(id)
            
        if check_computer_name() and use_list_checkbox.value == False:
            run_operation(computer_name.value)
        elif use_list_checkbox.value == True:
            run_operation("list of computers")
    
    def generate_commands():
        global list_of_scripts
        directory = "./custom_commands"
        
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            # checking if it is a ps1 file
            if os.path.isfile(f) and f.endswith('.ps1'):
                file_dict = {
                    "name": filename,
                    "path": f
                }
                list_of_scripts.append(file_dict)
        
        list_of_controls = []
        for script in list_of_scripts:   
            script_list_tile = ft.ListTile(
                title=ft.Text(f"{script['name']}"),
                leading=ft.IconButton(
                    ft.icons.PLAY_ARROW
                )
            )
            list_of_controls.append(script_list_tile)
            
        return list_of_controls
    
    def check_space(e):
        if check_computer_name():
            computer = computer_name.value
            enable_winrm(computer)
            id = uuid.uuid4()
            add_new_process(new_process("Check Space", [computer], date_time(), id))
            show_message(f"Checking space on {computer}")
            powershell = the_shell.Power_Shell()
            result = powershell.check_space(computer=computer)
            update_results("Check Space", result, id=id, check_space=True, subtitle=result, computer=computer)
            end_of_process(id)
    
    def check_software(e):
        date = date_time()
        date_formatted = date.replace(",", "_")
        date_formatted = date_formatted.replace(" ", "_")
        date_formatted = date_formatted.replace(":", "-")
        
        all = e.control.data
        
        id = uuid.uuid4()
        powershell = the_shell.Power_Shell()
        if programs_use_list_checkbox.value:
            computer = "list of computers"
            add_new_process(new_process("Check Software", ["Using list"], date_time(), id))
            show_message(f"Checking software on list of PCs")
            result = powershell.check_software(computer=computer, software=software_textfield.value, date=date_formatted, all=all)
            data = f"./results/Programs/Programs-{date_formatted}.json"
            update_results("Check Software", data=data, id=id, subtitle=result, computer=computer)
            end_of_process(id)
        elif check_computer_name():
            computer = computer_name.value
            enable_winrm(computer)
            add_new_process(new_process("Check Software", [computer], date_time(), id))
            show_message(f"Checking software on {computer}")
            data = f"./results/Programs/{computer}-Programs.json"
            result = powershell.check_software(computer=computer, software=software_textfield.value, date=date_formatted, all=all)
            update_results("Check Software", data=data, id=id, subtitle=result, computer=computer)
            end_of_process(id)
    
    def msinfo_32(e):
        if check_computer_name():
            id = uuid.uuid4()
            powershell = the_shell.Power_Shell()
            computer = computer_name.value
            enable_winrm(computer)
            add_new_process(new_process("MsInfo32", [computer], date_time(), id))
            show_message(f"Opening MsInfo32 for {computer}")
            result = powershell.msinfo_32(computer)
            update_results("Check Software", data=result, id=id, subtitle=result, computer=computer)
            end_of_process(id)
    
    # File picker for import printer
    def select_files(e: ft.FilePickerResultEvent):
        list_of_files = []
        if e.files != None:
            files = e.files
            for file in files:
                list_of_files.append(file.path)

    pick_files_dialog = ft.FilePicker(
        on_result=select_files,
    )

    page.overlay.append(pick_files_dialog)
    
    def get_user_ids(e):
        if check_computer_name():
            computer = computer_name.value
            show_message(f"Getting user IDs on {computer}")
            id = uuid.uuid4()
            powershell = the_shell.Power_Shell()
            enable_winrm(computer)
            add_new_process(new_process("User IDs", [computer], date_time(), id))
            result = powershell.get_user_ids(computer)
            update_results("User IDs", data=result, id=id, subtitle=result, computer=computer)
            end_of_process(id)
            
            if os.path.exists(f"./results/Users/{computer}-Users.json"):
                open_logoff_modal(computer)    

    def log_off_user(data):
        user_id = data["ID"]
        computer = ["computer"]
        name = data["name"]
        
        id = uuid.uuid4()
        powershell = the_shell.Power_Shell()
        computer = computer_name.value
        add_new_process(new_process("Log Off User", [computer], date_time(), id))
        show_message(f"Logging off {name} on {computer}")
        result = powershell.log_off_user(computer, user_id, name)
        update_results("Log Off Users", data=result, id=id, subtitle=result, computer=computer)
        end_of_process(id)

    def open_logoff_modal(computer):
        
        with open(f"./results/Users/{computer}-Users.json", "r") as file:
            users = json.load(file)
        
        
        def clicked(e):
            # e.control.visible = False
            data = e.control.data
            e.control.text = "logoff sent"
            e.control.on_click = (lambda _: print("Already logged off"))
            page.update()
            log_off_user(data)
            
        list_of_users = []
        for user in users:
            u = users[user]
            id = u["ID"]
            
            new_user = ft.Container(
                content=ft.Row([
                    ft.Text(f"{user}", selectable=True),
                    ft.TextButton(
                        f"Log off", 
                        data={"ID": id, "name": user, "computer": computer}, 
                        on_click=clicked
                    )
                ])
            )
            list_of_users.append(new_user)
        
        if len(list_of_users) == 0:
            none_found = ft.Text("No logged in users.")
            list_of_users.append(none_found)
        
        # Set up modal
        content = ft.Column(list_of_users, expand=1, spacing=20)
        
        modal = DynamicModal(
            title=f"Logged in users for {computer}:",
            content=content,
            close_modal_func=close_dynamic_modal
        )
        
        page.dialog = modal.get_modal()
        page.dialog.open = True
        page.update()
        
        while page.dialog.open:
            pass
        
    # "Views". We swap these in and out of current_view
    # when navigating using the rail.
    computer_list_btn = ft.IconButton(
        icon=ft.icons.LIST,
        icon_size=20,
        on_click=open_pc_list,
        tooltip="Open list of PCs"
    )
    
    recent_computers_btn = ft.IconButton(
        icon=ft.icons.HISTORY,
        icon_size=20,
        on_click=load_recent_computers,
        tooltip="Recent computers"
    )
    
    computer_top_row = ft.Row([
        ft.Column([
            computer_list_btn,
            recent_computers_btn,
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        computer_name,
        ping_btn,
        quser_btn,
        ft.Column([
            ft.Stack([
                running_processes_icon,
                loading_gif
            ])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        running_processes_count_text,
    ])
    
    filter_btn = ft.IconButton(
        icon=ft.icons.FILTER_ALT_OFF,
        icon_size=13,
        tooltip="Off",
        on_click=filter_results,
    )
    
    home = ft.Column([
        computer_top_row,
        ft.Row([
            
            ft.Column([
                ft.Row([
                    ft.Text("Filter:", weight=ft.FontWeight.BOLD),
                    filter_btn,
                ])
            ]),
            
            ft.Column([
                ft.Row([
                    results_label,
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        icon_size=13,
                        tooltip="Clear Results",
                        on_click=remove_card,
                        data="all"
                    ),
                ])
            ]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        results_container
    ], expand=True)
    
    # Actions tab Expansion List items
    check_space_btn =  ft.TextButton(
        text="Check Space", 
        icon=ft.icons.STORAGE,
        on_click=check_space
    )
    
    clear_space_exp_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Clear Space", weight=ft.FontWeight.BOLD),
            trailing=ft.Icon(name=ft.icons.DELETE_FOREVER)
        ),
        content=ft.Container(
            content=ft.Column([
                check_space_btn,
                delete_users_checkbox,
                logout_users_checkbox,
                use_list_checkbox,
                ft.TextButton(text="Clear Disk Space", icon=ft.icons.DELETE_FOREVER, on_click=clear_space)
            ]),
            padding=10
        ),
        can_tap_header=True,
    )
    
    printers_exp_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Printers", weight=ft.FontWeight.BOLD),
            trailing=ft.Icon(name=ft.icons.PRINT)
        ),
        content=ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon=ft.icons.PRINT, icon_size=50, on_click=printer_wizard, data=""),
                    ft.Text("Get Printers")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.TEXT_SNIPPET, data="Operational", icon_size=50, on_click=open_print_logs),
                    ft.Text("Operational Logs")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.TEXT_SNIPPET, data="Admin", icon_size=50, on_click=open_print_logs),
                    ft.Text("Admin Logs")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            ], wrap=True),
            padding=10
        ),
        can_tap_header=True,
    )
    
    programs_tutorial = TutorialBtn(
        data=["Programs", "You can use this panel to check for a specific program on a computer, or get a list of all detected installed software."],
        on_click=open_tutorial_modal
    )
    
    programs_use_list_checkbox = ft.Checkbox(
        label="Use list of PCs",
        value=False
    )
    
    software_textfield = ft.TextField(
        label="Software name"
    )
    
    programs_exp_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Programs", weight=ft.FontWeight.BOLD),
            trailing=ft.Icon(name=ft.icons.WEB_ASSET)
        ),
        content=ft.Container(
            content=ft.Column([
                    ft.Row([
                        software_textfield,
                        programs_tutorial
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Row([
                        ft.Column([
                            programs_use_list_checkbox,
                            ft.FilledTonalButton(text="Check for software", on_click=check_software),

                        ]),
                        ft.Column([

                            ft.FilledTonalButton(text="Check for ALL software", data="True", on_click=check_software)

                        ]),
                    ], vertical_alignment=ft.CrossAxisAlignment.END)
                ]),
            padding=10
        ),
        can_tap_header=True,
    )
    
    computer_control_exp_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Computer Control", weight=ft.FontWeight.BOLD),
            trailing=ft.Icon(name=ft.icons.SETTINGS_POWER)
        ),
        content=ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon=ft.icons.RESTART_ALT, icon_size=50, on_click=open_restart_modal, data=""),
                    ft.Text("Shutdown/Restart")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.PEOPLE, icon_size=50, on_click=get_user_ids, data=""),
                    ft.Text("Log Off Users")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.EDIT_SQUARE, icon_size=40, on_click=open_event_log),
                    ft.Text("Rename Computer")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            ], wrap=True),
            padding=10
        ),
        can_tap_header=True,
    )
    
    other_exp_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Other Tools", weight=ft.FontWeight.BOLD),
            trailing=ft.Icon(name=ft.icons.COMPUTER)
        ),
        content=ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon=ft.icons.FOLDER, icon_size=50, on_click=open_c_share, data=""),
                    ft.Text("C$ Share")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.SCHEDULE, icon_size=50, on_click=check_bootup, data=""),
                    ft.Text("Check Last Bootup")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.TEXT_SNIPPET, icon_size=50, on_click=open_event_log),
                    ft.Text("Event Log")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.MEMORY, icon_size=50, on_click=msinfo_32),
                    ft.Text("MSInfo32")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.BATTERY_4_BAR, icon_size=50, on_click=check_battery),
                    ft.Text("Battery Status")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            ], wrap=True),
            padding=10
        ),
        can_tap_header=True,
    )
    
    exp_panel_list = ft.ExpansionPanelList(
        elevation=8,
        controls=[
            clear_space_exp_panel,
            printers_exp_panel,
            programs_exp_panel,
            computer_control_exp_panel,
            other_exp_panel
        ]
    )
    
    actions_view_container = ft.Container(
        content=ft.ListView(
            [exp_panel_list],
            padding=20,
        ),
        bgcolor=settings_values["app_color"],
        expand = 1,
        border_radius=20
    )
    
    actions_view = ft.Column([
        computer_top_row,
        actions_view_container
    ], expand=1)
    
    # Settings color choice radio
    app_color_label = ft.Text("App Color:", )
    red_color_radio = ft.Radio(value="red", label="Red", fill_color="red")
    blue_color_radio = ft.Radio(value="blue", label="Blue", fill_color="blue")
    green_color_radio = ft.Radio(value="green", label="Green", fill_color="green")
    purple_color_radio = ft.Radio(value="purple", label="Purple", fill_color="purple")
    yellow_color_radio = ft.Radio(value="yellow", label="Yellow", fill_color="yellow")
    cg = ft.RadioGroup(content=ft.Column([
        red_color_radio,
        blue_color_radio,
        green_color_radio,
        purple_color_radio,
        yellow_color_radio
    ]))
    
    winrm_checkbox = ft.Checkbox("Enable WinRM before actions", value=settings_values["enable_win_rm"])
    winrm_results_checkbox = ft.Checkbox("Supress WinRM results", value=settings_values["supress_winrm_results"])
    use_24hr_checkbox = ft.Checkbox("Use 24hr time format", value=settings_values["use_24hr"])
    warn_checkbox = ft.Checkbox("Warn before clearing profiles", value=settings_values["warn_about_profile_deletion"])
    settings_view = ft.Column([
        ft.Row([
            ft.Column([
            app_color_label,
                ft.Row([
                    cg
                ]),
            ]),
            ft.VerticalDivider(),
            ft.Column([
                winrm_checkbox,
                winrm_results_checkbox,
                use_24hr_checkbox,
                warn_checkbox
            ]),
            ft.VerticalDivider(),
        ], expand=1),
        ft.Row([settings_save_btn], alignment=ft.MainAxisAlignment.CENTER)
    ], expand=1)

    # Used to store the computer name
    # that printer_wizard was run on
    printer_wiz_computer = ft.Text("None")
    
    def refresh_printers(e):
        global printer_wiz_target_computer
        printer_wiz_target_computer = printer_wiz_computer.data
        printer_wizard(e, target_computer=printer_wiz_target_computer, refresh=True)
    
    print_wizard_view = ft.Column([
        computer_top_row,
        ft.Divider(height=9, thickness=3),
        ft.Row([
            printer_wiz_computer,
            ft.IconButton(
                icon=ft.icons.REFRESH, 
                on_click=refresh_printers,
            ),
        ]),
        printer_wiz_list_container,
    ], expand=True)
    
    commands_list_view = ft.ListView(expand=1, spacing=10, padding=20)
    commands_list_view.controls = generate_commands()
    commands_list_container = ft.Container(
        content=commands_list_view,
        expand=True,
    )
    
    cust_scripts_tutorial = TutorialBtn(
        data=["Custom Scripts", "Here you can add your own scripts so they are easily accessible and can be launched at the click of a button."],
        on_click=open_tutorial_modal
    )
    
    custom_scripts_view = ft.Column([
        ft.Row([
            cust_scripts_tutorial
        ], spacing=0),
        commands_list_container
    ], expand=True)
    
    current_view = ft.Row([home], expand=True)
    
    #Finally build the page
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=9, thickness=3),
            current_view
        ], expand=True)
    )

ft.app(target=main)