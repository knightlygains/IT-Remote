import flet as ft
import the_shell
import datetime
import json
import os

# Default settings.json values
font_size = 16
app_color = "blue"
window_width = 745
window_height = 515

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
    global font_size
    global app_color
    global window_width
    global window_height
    # Check if settings already exists
    
    if update:
        try:
            with open("settings.json", "r") as file:
                print("settings.json exists, updating")
                data = json.load(file)
                data.update({
                    "font_size": font_size, 
                    "app_color": app_color,
                    })
        except ValueError:
            print("Something went wrong")
        finally:
            with open("settings.json", "w") as settings:
                json.dump(data, settings, indent=4)
            
    # Apply settings
    try:
        with open("settings.json", "r") as file:
            try:
                settings_data = json.load(file)
                font_size = settings_data["font_size"]
                app_color = settings_data["app_color"]
                window_width = settings_data["window_width"]
                window_height = settings_data["window_height"]
            except json.decoder.JSONDecodeError:
                print("No settings data found")
    except FileNotFoundError:
        print("No settings.json found. Creating a new one.")
        with open("settings.json", "w") as file:
            print("settings.json created")
            data = {
                "font_size": font_size,
                "app_color": app_color,
                "window_width": window_width,
                "window_height": window_height
            }
            json.dump(data, file, indent=4)
    
load_settings(e=None, update=False)

def main(page: ft.Page):
    page.fonts = {
        "Consola": "assets/fonts/Consola.ttf"
    }
    
    page.window_width = window_width
    page.window_height = window_height
    page.window_min_height = 515
    page.window_min_width = 745
    page.theme = ft.Theme(font_family="Consola", color_scheme_seed=app_color)
    
    def save_page_dimensions(e):
        print("page resize")
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
    page.snack_bar = page.snack_bar = ft.SnackBar(ft.Text("", ), duration=3000)
    
    def update_settings(e):
        global app_color
        if cg.value:
            app_color = cg.value
        load_settings(e, update=True )
        results_container.bgcolor = app_color
        printer_wiz_list_container.bgcolor = app_color
        page.theme.color_scheme_seed = app_color
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
            current_view.controls = [settings]
        if index == 1:
            current_view.controls = [home]
        if index == 2:
            current_view.controls = [delprof_view]
        if index == 3:
            current_view.controls = [printers]
        if index == 4:
            current_view.controls = [commands_view]
        if index == 5:
            current_view.controls = [custom_scripts_view]
        if index == 6:
            # Print Wizard View
            rail.selected_index = 3
            current_view.controls = [print_wizard_view]
        if index == 7:
            # Custom scripts view
            pass
        page.update()
    
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
                icon=ft.icons.HOME_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.HOME),
                label_content=ft.Text("Home"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.DELETE_OUTLINE,
                selected_icon_content=ft.Icon(ft.icons.DELETE),
                label_content=ft.Text("Clear Space"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.PRINT_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.PRINT),
                label_content=ft.Text("Printers"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.TERMINAL_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.TERMINAL),
                label_content=ft.Text("Commands"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.PLAY_ARROW_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.PLAY_ARROW),
                label_content=ft.Text("Custom Scripts"),
            ),
        ],
        on_change=navigate_view
    )
    
    # Other controls
    settings_save_btn = ft.FilledButton("Save", icon=ft.icons.SAVE, on_click=update_settings)
    results_label = ft.Text("Results:")
    
    # Container for running process cards
    show_running_processes = ft.ListView(expand=1, spacing=10, padding=20)
    
    # List view for printer wizard
    printer_wiz_listview = ft.ListView(expand=1, spacing=10, padding=20,)
    printer_wiz_list_container = ft.Container(
        bgcolor=app_color,
        content=printer_wiz_listview,
        border_radius=20,
        expand=True,
    )
    
    new_printer_name = ft.TextField(expand=True)
    
    def date_time():
        x = datetime.datetime.now()
        day = x.strftime("%a")
        day_num = x.strftime("%d")
        month = x.strftime("%b")
        time = x.strftime("%X")
        return f"{day} {month} {day_num}, {time}"
    
    def update_results(title_text, data):
        # title_text = f"{date_time()}: {title_text}"
        id = len(result_data.controls)
        card = generate_result_card(
            leading = ft.Icon(ft.icons.TERMINAL),
            title=ft.Text(title_text),
            date=date_time(),
            data=data,
            id=id
        )
        result_data.controls.insert(0, card)
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
                                bgcolor=app_color,
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
    
    # Local lottie files dont work currently
    # loading = ft.Lottie(
    #         src=f"assets/images/loading.json",
    #         repeat=True,
    #         reverse=False,
    #         visible=True,
    #     )
    
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
                ft.Text(e.control.data, selectable=True)
            ], scroll=True))
        result_card_modal.title = ft.Text(e.control.title.value, )
        show_card_modal()
    
    def remove_card(e):
        if e.control.data == "all":
            result_data.controls.clear()
        else:
            for control in result_data.controls:
                if e.control.data == control.data:
                    result_data.controls.remove(control)
        page.update()
    
    def generate_result_card(leading, title, date, data, id):
        """
        Clickable card that shows in the console.
        Is called from update_results()
        """
        data_max_length = 60
        # Format and shorten text
        subtitle_text = data[0:data_max_length]
        if len(data) > data_max_length:
            subtitle_text += "..."
        
        # subtitle_text = "Perspiciatis dolores placeat perspiciatis corrupti doloremque esse non. Repellendus hic quis temporibus doloremque velit quidem. Dignissimos quia nihil nisi alias minima nobis. Nisi sed qui sapiente sint voluptas fugiat.Tempore ut ratione perspiciatis et. Veniam eum quis deserunt. Alias animi dolor asperiores autem. Autem iste aut adipisci repellat."
        
        #Define card attributes
        result_card = ft.Card(
            content=ft.Column([
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
                            subtitle=ft.Text(subtitle_text),
                            on_click=open_card,
                            data=data
                        ),
                    ]), 
            data=id
        )
        return result_card
    
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
        if computer == None:
            computer = computer_name.value
        id = len(list_of_processes)
        add_new_process(new_process("WinRM", [computer], date_time(), id))
        powershell = the_shell.Power_Shell()
        result = powershell.enable_winrm(computer)
        update_results("WinRM", result)
        end_of_process(id)
    
    def check_computer_name():
        if computer_name.value == "":
            show_message("Please input a computer hostname")
            return False
        else:
            return True
    
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
        printer_wizard(e)
        
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
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
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
            title=ft.Text(f"{more_info_printer['Name']}: Additional printer info"),
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
    
    def printer_wizard(e):
        global printer_wiz_target_computer
        if e.control.data == "Last result":
            if len(printer_wiz_listview.controls) > 0:
                navigate_view(6)
            else:
                show_message("No previous results.")
        else:
            if check_computer_name():
                show_message(f"Getting printers on {computer_name.value}")
                enable_winrm(computer_name.value)
                printer_wiz_target_computer = computer_name.value
                id = len(list_of_processes)
                add_new_process(new_process("Printer Wizard", [computer_name.value], date_time(), id))
                powershell = the_shell.Power_Shell()
                result = powershell.printer_wizard(computer=computer_name.value)
                print(result) # Debugging purposes only
                update_results("Printer Wizard", result)
                printer_wiz_listview.controls.clear()
                try:
                    with open(f"./results/printers/{printer_wiz_target_computer}-Printers.json") as file:
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
                    printer_wiz_computer.data = computer_name.value
                    printer_wiz_computer.value = f"{computer_name.value}'s printers:"
                except FileNotFoundError:
                    show_message(f"Could not get printers on {computer_name.value}")
                end_of_process(id)
                navigate_view(6)
        
    def printer_wiz_testpage(e):
        if check_computer_name():
            id = len(list_of_processes)
            add_new_process(new_process("Test Page", [computer_name.value], date_time(), id))
            show_message(f"Printing test page from {computer_name.value}.")
            powershell = the_shell.Power_Shell()
            result = powershell.test_page(computer=computer_name.value, printerName=e.control.data)
            update_results("Printer Test Page", result)
            end_of_process(id)
    
    def are_you_sure(e):
        global said_yes
        global modal_not_dismissed
        
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
            modal=True,
            title=ft.Text("Are you sure?"),
            content=ft.Column([
                    ft.Row([
                        ft.Text(f"Uninstall {e.control.data}?")
                    ])
                ]),
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
            # Reset global tracker variables before exit function
            # So function doesnt automatically return True next time
            said_yes = False
            modal_not_dismissed = True
            return True
        else:
            said_yes = False
            modal_not_dismissed = True
            return False 
    
    def uninstall_printer(e):
        if are_you_sure(e):
            id = len(list_of_processes)
            add_new_process(new_process("Uninstall Printer", [printer_wiz_computer.data], date_time(), id))
            show_message(f"Uninstalling printer from {printer_wiz_computer.data}.")
            powershell = the_shell.Power_Shell()
            result = powershell.uninstall_printer(computer=printer_wiz_computer.data, printerName=e.control.data)
            update_results("Uninstall Printer", result)
            end_of_process(id)

    # Computer Text Field
    computer_name = ft.TextField(label="Computer Name")
    
    ping_btn = ft.FilledButton(text="Ping", on_click=ping)
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
    
    def run_custom_command(e):
        powershell = the_shell.Power_Shell()
        powershell.custom_command()
    
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
    
    settings = ft.Column([
        ft.Row([
            ft.Column([
            app_color_label,
                ft.Row([
                    cg
                ]),
            ], width=200),
        ]),
        ft.Row([settings_save_btn])
    ])
    
    printers = ft.Column([
        computer_top_row,
        ft.Divider(height=9, thickness=3),
        ft.Row([
            ft.Column([
                ft.IconButton(icon=ft.icons.PRINT, icon_size=50, on_click=printer_wizard, data=""),
                ft.Text("Get Printers")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            ft.VerticalDivider(),
            ft.Column([
                ft.IconButton(icon=ft.icons.RESTORE, icon_size=50, on_click=printer_wizard, data="Last result"),
                ft.Text("Previous Result")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            ft.VerticalDivider(),
            ft.Column([
                ft.IconButton(icon=ft.icons.UPLOAD_FILE, icon_size=50,),
                ft.Text("Import Printer")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
        ])
    ], expand=True)

    # Used to store and later update with the computer
    # that printer_wizard was run on
    printer_wiz_computer = ft.Text("None")
    
    print_wizard_view = ft.Column([
        ft.Row([
            printer_wiz_computer,
        ]),
            printer_wiz_list_container,
        ], expand=True)
    
    delprof_view = ft.Column([
        computer_top_row,
        ft.Divider(height=9, thickness=3),
        ft.Column([
            delete_users_checkbox,
            logout_users_checkbox,
            use_list_checkbox,
            ft.FilledButton(text="Clear Disk Space", on_click=clear_space)
        ]),
    ], expand=True)
    
    
    commands_list_view = ft.ListView(expand=1, spacing=10, padding=20)
    commands_list_view.controls = generate_commands()
    commands_list_container = ft.Container(
        content=commands_list_view,
        expand=True,
    )
    
    custom_scripts_view = ft.Column([
        computer_top_row,
        ft.Divider(height=9, thickness=3),
        commands_list_container
    ], expand=True)
    
    
    commands_view = ft.Column([
        computer_top_row,
        ft.Divider(height=9, thickness=3),
        ft.ListView([
            ft.Column([
                ft.Text("Printers", weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Column([
                        ft.IconButton(icon=ft.icons.PRINT, icon_size=50, on_click=printer_wizard, data=""),
                        ft.Text("Get Printers")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                    ft.VerticalDivider(),
                    ft.Column([
                        ft.IconButton(icon=ft.icons.RESTORE, icon_size=50, on_click=printer_wizard, data="Last result"),
                        ft.Text("Previous Result")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                    ft.VerticalDivider(),
                    ft.Column([
                        ft.IconButton(icon=ft.icons.UPLOAD_FILE, icon_size=50,),
                        ft.Text("Import Printer")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ]),
            ]),
            ft.Divider(),
            ft.Column([
                ft.Text("Programs", weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Column([
                        ft.IconButton(icon=ft.icons.PRINT, icon_size=50, on_click=printer_wizard, data=""),
                        ft.Text("Get Printers")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                    ft.VerticalDivider(),
                    ft.Column([
                        ft.IconButton(icon=ft.icons.RESTORE, icon_size=50, on_click=printer_wizard, data="Last result"),
                        ft.Text("Previous Result")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                    ft.VerticalDivider(),
                    ft.Column([
                        ft.IconButton(icon=ft.icons.UPLOAD_FILE, icon_size=50,),
                        ft.Text("Import Printer")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ]),
            ]),
            ft.Divider(),
            ft.Column([
                ft.Text("Printers", weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Column([
                        ft.IconButton(icon=ft.icons.PRINT, icon_size=50, on_click=printer_wizard, data=""),
                        ft.Text("Get Printers")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                    ft.VerticalDivider(),
                    ft.Column([
                        ft.IconButton(icon=ft.icons.RESTORE, icon_size=50, on_click=printer_wizard, data="Last result"),
                        ft.Text("Previous Result")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                    ft.VerticalDivider(),
                    ft.Column([
                        ft.IconButton(icon=ft.icons.UPLOAD_FILE, icon_size=50,),
                        ft.Text("Import Printer")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ]),
            ])
        ], expand=1, padding=20, spacing=10),
        
        
        
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