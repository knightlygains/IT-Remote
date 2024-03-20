import flet as ft
import the_shell
import datetime
import json

# Default settings.json values
font_size = 16
console_color = "blue"
console_text_color = "white"
window_width = 735
window_height = 515

running_processes_count = 0

printer_wiz_target_computer = ""
printer_to_change = ""

# Load user settings
def load_settings(e, update):
    global font_size
    global console_color
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
                    "console_color": console_color,
                    "console_text_color": console_text_color})
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
                console_color = settings_data["console_color"]
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
                "console_color": console_color,
                "console_text_color": console_text_color,
                "window_width": 735,
                "window_height": 515
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
    page.theme = ft.Theme(font_family="Consola", color_scheme_seed=console_color)
    
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
        global console_color
        if cg.value:
            console_color = cg.value
        load_settings(e, update=True )
        console_container.bgcolor = console_color
        page.theme.color_scheme_seed = console_color
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
            pass
        if index == 5:
            pass
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
        # extended=True,
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
                icon=ft.icons.SAVE_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.SAVE),
                label_content=ft.Text("Programs"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.LAPTOP_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.LAPTOP),
                label_content=ft.Text("Commands"),
            ),
        ],
        on_change=navigate_view
    )
    
    # Other controls
    settings_save_btn = ft.FilledButton("Save", icon=ft.icons.SAVE, on_click=update_settings)
    console_label = ft.Text("Results:", )
    
    # Container for running process cards
    show_running_processes = ft.ListView(expand=1, spacing=10, padding=20)
    
    # List view for printer wizard
    printer_wiz_listview = ft.ListView(expand=1, spacing=10, padding=20,)
    new_printer_name = ft.TextField(expand=True)
    
    def date_time():
        x = datetime.datetime.now()
        full = x.strftime("%c")
        day = x.strftime("%a")
        day_num = x.strftime("%d")
        month = x.strftime("%b")
        time = x.strftime("%X")
        return f"{day} {month} {day_num}, {time}"
    
    def update_console(title_text, data):
        title_text = f"{date_time()}: {title_text}"
        id = len(console_data.controls)
        card = generate_console_card(
            leading = ft.Icon(ft.icons.TERMINAL),
            title=ft.Text(title_text),
            data=data,
            id=id
        )
        console_data.controls.insert(0, card)
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
    console_data = ft.ListView(expand=1, spacing=10, padding=20)

    console_container = ft.Container(
                                content=console_data,
                                bgcolor=console_color,
                                expand=True,
                                alignment=ft.alignment.top_left,
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
        offset=ft.transform.Offset(-0.11, 1)
    )
    
    # Card modal Stuff \/
    def show_card_modal():
        page.dialog = console_card_modal
        console_card_modal.open = True
        page.update()
    
    def close_card_modal(e):
        console_card_modal.open = False
        page.update()
    
    # Define card modal
    console_card_modal = ft.AlertDialog(
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
        console_card_modal.content = ft.Container(
            content=ft.Column([
                ft.Text(e.control.data, selectable=True)
            ], scroll=True))
        console_card_modal.title = ft.Text(e.control.title.value, )
        show_card_modal()
    
    def remove_card(e):
        if e.control.data == "all":
            console_data.controls.clear()
        else:
            for control in console_data.controls:
                if e.control.data == control.data:
                    console_data.controls.remove(control)
        page.update()
    
    def generate_console_card(leading, title, data, id):
        """
        Clickable card that shows in the console.
        Is called from update_console()
        """
        # Format and shorten text
        subtitle_text = data[0:40]
        if len(data) > 40:
            subtitle_text += "..."
        
        #Define card attributes
        console_card = ft.Card(
            content=ft.Column([
                        ft.ListTile(
                            leading=leading,
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
        return console_card
    
    def ping(e):
        if check_computer_name():
            id = len(list_of_processes)
            add_new_process(new_process("Ping", [computer_name.value], date_time(), id))
            show_message(f"Pinging {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.ping(computer=computer_name.value)
            update_console("Ping", result)
            end_of_process(id)
    
    def enable_winrm(computer):
        if computer == None:
            computer = computer_name.value
        id = len(list_of_processes)
        add_new_process(new_process("WinRM", [computer], date_time(), id))
        powershell = the_shell.Power_Shell()
        result = powershell.enable_winrm(computer)
        update_console("WinRM", result)
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
            update_console("QUser", result)
            end_of_process(id)
            
    def rename_printer(e):
        if check_computer_name():
            close_printer_dlg(e)
            id = len(list_of_processes)
            add_new_process(new_process("Rename Printer", [computer_name.value], date_time(), id))
            show_message(f"Renaming printer on {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.rename_printer(computer=computer_name.value, printerName=printer_to_change, newName=new_printer_name.value)
            update_console("Rename Printer", result)
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
    
    def printer_wizard(e):
        global printer_wiz_target_computer
        if e.control.text == "Last result":
            if len(printer_wiz_listview.controls) > 0:
                navigate_view(6)
            else:
                show_message("No previous results.")
        else:
            if check_computer_name():
                show_message(f"Running printer wizard on {computer_name.value}")
                enable_winrm(computer_name.value)
                printer_wiz_target_computer = computer_name.value
                id = len(list_of_processes)
                add_new_process(new_process("Printer Wizard", [computer_name.value], date_time(), id))
                powershell = the_shell.Power_Shell()
                result = powershell.printer_wizard(computer=computer_name.value)
                print(result) # Debugging purposes only
                update_console("Printer Wizard", result)
                printer_wiz_listview.controls.clear()
                try:
                    with open(f"./results/{computer_name.value}-Printers.json") as file:
                        printers = json.load(file)
                    # For each printer in the json file, show a ft.Row
                    # containing text and buttons
                    for printer in printers:
                        new_printer = printers[printer]
                        printer_list_item = ft.Column([
                            ft.Divider(),
                            ft.Row([
                                ft.Column([
                                    ft.Row([
                                        ft.Column([
                                            ft.Text(f"{new_printer['Name']}", selectable=True, weight=ft.FontWeight.BOLD,),
                                            ft.Text(f"PortName: {new_printer['Port']}", selectable=True),
                                            ft.Text(f"Status: {new_printer['Status']}", selectable=True)
                                        ], width=200),
                                        
                                        ft.IconButton(
                                            icon=ft.icons.INFO,
                                            icon_size=20,
                                            tooltip="More info",
                                        ),
                                    ]),
                                ], expand_loose=True),
                                ft.Column([
                                    ft.FilledButton("Test Page", data=f"{new_printer["Name"]}", on_click=printer_wiz_testpage)
                                ]),
                                ft.Column([
                                    ft.FilledButton("Rename", data=f"{new_printer["Name"]}", on_click=open_printer_name_modal), 
                                ]),
                                ft.Column([
                                    ft.FilledButton("Uninstall", data=f"{new_printer["Name"]}", on_click=uninstall_printer)
                                ]),
                            ]),
                        ])
                        
                        printer_wiz_listview.controls.append(printer_list_item)
                        printer_wiz_computer.value = f"{computer_name.value}'s printers:"
                        printer_wiz_computer.data = computer_name.value
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
            update_console("Printer Test Page", result)
            end_of_process(id)
    
    def uninstall_printer(e):
        id = len(list_of_processes)
        add_new_process(new_process("Uninstall Printer", [printer_wiz_computer.data], date_time(), id))
        show_message(f"Uninstalling printer from {printer_wiz_computer.data}.")
        powershell = the_shell.Power_Shell()
        result = powershell.uninstall_printer(computer=printer_wiz_computer.data, printerName=e.control.data)
        update_console("Printer Test Page", result)
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
            console_label,
            ft.IconButton(
                icon=ft.icons.CLOSE,
                icon_size=10,
                tooltip="Clear Results",
                on_click=remove_card,
                data="all"
            ),
        ]),
        console_container
    ], expand=True)
    
    # Settings color choice radio
    console_color_label = ft.Text("App Color:", )
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
            console_color_label,
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
        ft.ElevatedButton("Get printers", on_click=printer_wizard),
        ft.ElevatedButton("Last result", on_click=printer_wizard)
    ], expand=True)
    
    current_view = ft.Row([home], expand=True)

    # Used to store and later update with the computer
    # that printer_wizard was run on
    printer_wiz_computer = ft.Text("None")
    
    print_wizard_view = ft.Row([
        ft.Column([
            printer_wiz_computer,
            printer_wiz_listview,
        ], expand_loose=1),
    ], expand=True, scroll=True)
    
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
                    update_console("Clear Space", read_pc_result)
                    pc_result.close()
            else:
                results = open(f"./results/ClearSpace/{computer}-ClearSpace.txt", "r")
                result = results.read()
                update_console("Clear Space", result)
            
            end_of_process(id)
            
        if check_computer_name() and use_list_checkbox.value == False:
            run_operation(computer_name.value)
        elif use_list_checkbox.value == True:
            run_operation("Use-List")
    
    delete_users_checkbox = ft.Checkbox(label="Remove user profiles", value=False)
    logout_users_checkbox = ft.Checkbox(label="Logout users before deletion", value=False)
    use_list_checkbox = ft.Checkbox(label="Use list of computers", value=False)
    
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
    
    #Finally build the page
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=9, thickness=3),
            current_view
        ], expand=True)
    )

ft.app(target=main)