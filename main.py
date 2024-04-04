import flet as ft
import the_shell
import datetime
import json
import os, time
import socket, pathlib
from tutorial_btn import TutorialBtn

# Default settings.json values
settings_values = {
    "font_size": 16,
    "app_color": "blue",
    "window_width": 745,
    "window_height": 515,
    "enable_win_rm": True,
    "supress_winrm_results": False,
    "use_24hr": False
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
    global settings_values
    # Check if settings already exists
    if update:
        try:
            with open("settings.json", "r") as file:
                print("settings.json exists, updating")
                data = json.load(file)
                data.update({
                    "font_size": settings_values["font_size"], 
                    "app_color": settings_values["app_color"],
                    "enable_win_rm": settings_values["enable_win_rm"],
                    "supress_winrm_results": settings_values["supress_winrm_results"],
                    "use_24hr": settings_values["use_24hr"]
                    })
        except ValueError as e:
            print(f"Something went wrong, {e}")
        finally:
            with open("settings.json", "w") as settings:
                json.dump(data, settings, indent=4)
            
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
                settings_values["supress_winrm_results"] = settings_data["supress_winrm_results"],
                settings_values["use_24hr"] = settings_data["use_24hr"]
            except json.decoder.JSONDecodeError:
                print("No settings data found")
    except FileNotFoundError:
        print("No settings.json found. Creating a new one.")
        with open("settings.json", "w") as file:
            print("settings.json created")
            json.dump(settings_values, file, indent=4)
    
load_settings(e=None, update=False)

#Cleanup old files
for filename in os.listdir("./results/Printers"):
    pathlib.Path(f"./results/Printers/{filename}").unlink()
for filename in os.listdir("./results/ClearSpace"):
    pathlib.Path(f"./results/ClearSpace/{filename}").unlink()
for filename in os.listdir("./results/Programs"):
    pathlib.Path(f"./results/Programs/{filename}").unlink()

# Program
def main(page: ft.Page):
    page.fonts = {
        "Consola": "assets/fonts/Consola.ttf"
    }
    
    page.window_width = settings_values["window_width"]
    page.window_height = settings_values["window_height"]
    page.window_min_height = 515
    page.window_min_width = 745
    page.dark_theme = ft.Theme(color_scheme_seed=settings_values["app_color"])
    
    def save_page_dimensions(e):
        try:
            with open("settings.json", "r") as settings:
                data = json.load(settings)
                data.update({"window_width": page.width, "window_height": page.height})
        except ValueError:
            print("Something went wrong")
        finally:
            with open("settings.json", "w") as settings:
                json.dump(data, settings, indent=4)
        
    page.on_resize = save_page_dimensions
    page.snack_bar = ft.SnackBar(ft.Text("", ), duration=3000)
    
    def update_settings(e):
        global settings_values
        if cg.value:
            settings_values["app_color"] = cg.value
        results_container.bgcolor = settings_values["app_color"]
        printer_wiz_list_container.bgcolor = settings_values["app_color"]
        page.dark_theme.color_scheme_seed = settings_values["app_color"]
        actions_view_container.bgcolor = settings_values["app_color"]
        settings_values["enable_win_rm"] = winrm_checkbox.value
        settings_values["supress_winrm_results"] = winrm_results_checkbox.value
        settings_values["use_24hr"] = use_24hr_checkbox.value
        load_settings(e, update=True)
        page.update()
    
    def show_message(message):
        page.snack_bar.content.value = message
        page.snack_bar.open = True
        page.update()
    
    # Store list of runing processes here for tooltip
    list_of_processes = []
    
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
                label_content=ft.Text("Home"),
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
    results_label = ft.Text("Results:", weight=ft.FontWeight.BOLD)
    
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
        if computer_name.value.lower() == "localhost":
            computer_name.value = socket.gethostname()
        if computer_name.value == "":
            show_message("Please input a computer hostname")
            return False
        else:
            return True
    
    def date_time():
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
        return f"{day} {month} {day_num}, {time}"
    
    def update_results(title_text, data, **kwargs):
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
        
        if print_log_card:
            data = f"./results/Printers/{computer}-Printers-{type}-logs.json"
        elif print_wiz_card:
            data = f"./results/Printers/{computer}-Printers.json"
        elif check_space_card:
            data = f"./results/ClearSpace/{computer}-Space-Available.json"
        
        id = len(result_data.controls)
        
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
        page.update()
    
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
        if e.control.data == "all":
            # We clicked the remove all results button
            result_data.controls.clear()
        else:
            for control in result_data.controls:
                if e.control.data == control.data:
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
        
        if computer.lower() == "localhost":
            computer = socket.gethostname()
                
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
            data=id
        )
        
        return result_card
    
    # Dynamic Modal
    def show_dynamic_modal():
        page.dialog = dynamic_modal
        dynamic_modal.open = True
        page.update()
    
    def close_dynamic_modal(e):
        dynamic_modal.open = False
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
        space_list_view = ft.ListView(expand=1, padding= 20)
        card_content = ft.Container(
            content=space_list_view,
            expand=1,
            width= 500
        )
        software_json_path = e.control.data["data"]
        with open(software_json_path, "r") as file:
            data = json.load(file)
            for r in data:
                comp = data[r]
                
                list_of_controls = []
                for program in comp['Programs']:
                    new_control = ft.Row([
                            ft.Column([
                                ft.Text(f"{program['Name']}")
                        ])
                    ])
                    list_of_controls.append(new_control)
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"{comp}", weight=ft.FontWeight.BOLD),
                            ft.Column(
                                list_of_controls, 
                                wrap=True
                            )
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
        
    def open_tutorial_modal(e):
        """ 
        Uses print_log_card_modal to show help/topic info
        about features in the app.
        Uses control data to pass the topic info in a list.
        topic at index 0, explanatory text at index 1.
        """
        card_list_view = ft.ListView(expand=1, padding= 20)
        card_content = ft.Container(
            content=card_list_view,
            expand=1,
            width= 500
        )
        
        help_topic = e.control.data[0]
        help_text = e.control.data[1]
                
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"{help_text}"),
                    ], wrap=True)
                ], expand = 1),
                expand = 1,
                padding=20
            ),
            expand = 1
        )
        card_list_view.controls.append(card)
                
        dynamic_modal.content = card_content
        dynamic_modal.title = ft.Text(f"{help_topic}")
        show_dynamic_modal()
        
    def ping(e):
        if check_computer_name():
            id = len(list_of_processes)
            add_new_process(new_process("Ping", [computer_name.value], date_time(), id))
            show_message(f"Pinging {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.ping(computer=computer_name.value)
            update_results("Ping", result)
            end_of_process(id)
    
    def enable_winrm(computer):
        global settings_values
        if settings_values["enable_win_rm"]:
            if computer == None:
                computer = computer_name.value
            id = len(list_of_processes)
            add_new_process(new_process("WinRM", [computer], date_time(), id))
            powershell = the_shell.Power_Shell()
            result = powershell.enable_winrm(computer)
            if settings_values["supress_winrm_results"] == False:
                update_results("WinRM", result)
            end_of_process(id)
    
    def quser(e):
        if check_computer_name():
            id = len(list_of_processes)
            add_new_process(new_process("QUSER", [computer_name.value], date_time(), id))
            show_message(f"Querying logged in users on {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.quser(computer=computer_name.value)
            update_results("QUser", result)
            end_of_process(id)
            
    def rename_printer(e):
        if check_computer_name():
            close_printer_dlg(e)
            id = len(list_of_processes)
            add_new_process(new_process("Rename Printer", [computer_name.value], date_time(), id))
            show_message(f"Renaming printer on {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.rename_printer(computer=computer_name.value, printerName=printer_to_change, newName=new_printer_name.value)
            update_results("Rename Printer", result)
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
        printer_to_change = e.control.data
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
                                                ft.PopupMenuItem(text="Test Page", data=p_name, on_click=printer_wiz_testpage),
                                                ft.PopupMenuItem(text="Rename", data=p_name, on_click=open_printer_name_modal),
                                                ft.PopupMenuItem(text=f"Uninstall {p_name}", data=p_name, on_click=uninstall_printer),
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
                id = len(list_of_processes)
                add_new_process(new_process("Printer Wizard", [computer], date_time(), id))
                powershell = the_shell.Power_Shell()
                result = powershell.printer_wizard(computer=computer)
                update_results("Printer Wizard", data=result, print_wiz=True, computer=computer, subtitle=result)
                load_printers()
                end_of_process(id)
        
    def printer_wiz_testpage(e):
        if check_computer_name():
            id = len(list_of_processes)
            add_new_process(new_process("Test Page", [computer_name.value], date_time(), id))
            show_message(f"Printing test page from {computer_name.value}.")
            powershell = the_shell.Power_Shell()
            result = powershell.test_page(computer=computer_name.value, printerName=e.control.data)
            update_results("Printer Test Page", result)
            end_of_process(id)
    
    def are_you_sure(e, text):
        """
        Global are you sure modal.
        Waits in while loop until answered,
        retuning true or false depending on
        answer.
        """
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
                    ])
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
        if are_you_sure(e, f"Uninstall {e.control.data} from {printer_wiz_computer.data}?"):
            id = len(list_of_processes)
            add_new_process(new_process("Uninstall Printer", [printer_wiz_computer.data], date_time(), id))
            show_message(f"Uninstalling printer from {printer_wiz_computer.data}.")
            powershell = the_shell.Power_Shell()
            result = powershell.uninstall_printer(computer=printer_wiz_computer.data, printerName=e.control.data)
            update_results("Uninstall Printer", result)
            end_of_process(id)
            printer_wizard(e, refresh=True, target_computer=printer_wiz_computer.data)
    
    def open_print_logs(e):
        if check_computer_name():
            computer = computer_name.value
            type = e.control.data
            enable_winrm(computer)
            id = len(list_of_processes)
            add_new_process(new_process(f"{type} Log", [computer], date_time(), id))
            show_message(f"Getting {type} print logs from {computer}.")
            powershell = the_shell.Power_Shell()
            result = powershell.print_logs(computer, type)
            update_results(title_text=f"{type} Log", data=result, print_log=True, computer=computer, type=type, subtitle=result)
            end_of_process(id)
    
    def open_c_share(e):
        pass

    def check_bootup(e):
        pass
    
    def open_event_log(e):
        pass
    
    def open_msinfo32(e):
        pass
    
    def check_battery(e):
        pass

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

    computer_list_btn = ft.IconButton(
        icon=ft.icons.LIST,
        icon_size=20,
        on_click=open_pc_list,
        tooltip="Open list of PCs"
    )
    
    delete_users_checkbox = ft.Checkbox(label="Remove user profiles", value=False)
    logout_users_checkbox = ft.Checkbox(label="Logout users before deletion", value=False)
    use_list_checkbox = ft.Checkbox(label="Use list of computers", value=False)
    
    def clear_space(e):
        users = "False"
        logout = "False"
        if delete_users_checkbox.value == True:
            users = "True"
        if logout_users_checkbox.value == True:
            logout = "True"
            
        def run_operation(computer):
            if computer != "Use-List":
                enable_winrm(computer)
            # else skip winrm here, it will be done in script
            
            id = len(list_of_processes)
            
            # If we are using a list of pcs,
            # get each pc from list and create
            # an array of them.
            if computer == "Use-List":
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
                    update_results("Clear Space", read_pc_result)
                    pc_result.close()
            else:
                results = open(f"./results/ClearSpace/{computer}-ClearSpace.txt", "r")
                result = results.read()
                update_results("Clear Space", result)
            
            end_of_process(id)
            
        if check_computer_name() and use_list_checkbox.value == False:
            run_operation(computer_name.value)
        elif use_list_checkbox.value == True:
            run_operation("Use-List")
    
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
            id = len(list_of_processes)
            add_new_process(new_process("Check Space", [computer], date_time(), id))
            show_message(f"Checking space on {computer}")
            powershell = the_shell.Power_Shell()
            result = powershell.check_space(computer=computer)
            update_results("Check Space", result, check_space=True, subtitle=result, computer=computer)
            end_of_process(id)
    
    def check_software(e):
        if programs_use_list_checkbox.value:
            computer = "Use-List"
            id = len(list_of_processes)
            add_new_process(new_process("Check Software", ["Using list"], date_time(), id))
            show_message(f"Checking software on list of PCs")
            powershell = the_shell.Power_Shell()
            result = powershell.check_software(computer=computer, software=software_textfield.value, date=date_time())
            
            date = date_time()
            date_formatted = date.replace(",", "_")
            date_formatted = date_formatted.replace(" ", "_")
            date_formatted = date_formatted.replace(":", "-")
            data = f"./results/Programs/Programs-{date_formatted}.json"
            
            update_results("Check Software", result, subtitle=result, computer=computer)
            end_of_process(id)
        elif check_computer_name():
            computer = computer_name.value
            enable_winrm(computer)
            id = len(list_of_processes)
            add_new_process(new_process("Check Software", [computer], date_time(), id))
            show_message(f"Checking software on {computer}")
            powershell = the_shell.Power_Shell()
            
            data = f"./results/Programs/{computer}-Programs.json"
            result = powershell.check_software(computer=computer, software=software_textfield.value, date=date)
            
            update_results("Check Software", data=data, subtitle=result, computer=computer)
            end_of_process(id)
    
    def check_all_software(e):
        pass
    
    # File picker for import printer
    def pick_files_result(e: ft.FilePickerResultEvent):
        selected_files = (
            ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
        )
        update_results("Selected Files", selected_files)

    pick_files_dialog = ft.FilePicker(
        on_result=pick_files_result,
    )

    page.overlay.append(pick_files_dialog)

    # "Views". We swap these in and out of current_view
    # when navigating using the rail.
    
    computer_top_row = ft.Row([computer_list_btn,
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
    
    home = ft.Column([
        computer_top_row,
        ft.Row([
            results_label,
            ft.IconButton(
                icon=ft.icons.CLOSE,
                icon_size=10,
                tooltip="Clear Results",
                on_click=remove_card,
                data="all"
            ),
        ]),
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
                    ft.IconButton(icon=ft.icons.UPLOAD_FILE, icon_size=50,
                        on_click=lambda _: pick_files_dialog.pick_files(
                            allow_multiple=True,
                            allowed_extensions=["printerExport"],
                            initial_directory=f"{pathlib.Path.home()}"
                            ),
                        ),
                    ft.Text("Import Printer")
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
        data=["Programs", "You can use this panel to check for a specific program on a computer, or get a list of all detected installed software.\n\nOnly checking for a specific program can be used with a list."],
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

                            ft.FilledTonalButton(text="Check for ALL software")

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
                    ft.IconButton(icon=ft.icons.RESTART_ALT, icon_size=50, on_click=open_c_share, data=""),
                    ft.Text("Restart")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.PEOPLE, icon_size=50, on_click=check_bootup, data=""),
                    ft.Text("Log Off Users")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon=ft.icons.EDIT_SQUARE, icon_size=50, on_click=open_event_log),
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
                    ft.IconButton(icon=ft.icons.MEMORY, icon_size=50, on_click=open_msinfo32),
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
    
    winrm_checkbox = ft.Checkbox(value=settings_values["enable_win_rm"])
    winrm_results_checkbox = ft.Checkbox(value=settings_values["supress_winrm_results"])
    use_24hr_checkbox = ft.Checkbox(value=settings_values["use_24hr"])
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
                ft.Text("Enable WinRM before actions:"),
                winrm_checkbox,
                ft.Text("Supress WinRM results:"),
                winrm_results_checkbox,
                ft.Text("Use 24hr time format:"),
                use_24hr_checkbox,
            ], width=150),
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