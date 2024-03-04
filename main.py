import flet as ft
import the_shell
import datetime
import json
import powershell_functions

# Initial settings.json values
font_size = 16
console_color = "blue"
console_text_color = "white"
window_width = 680
window_height = 680

running_processes_count = 0

printer_wiz_target_computer = ""

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
                "window_width": 680,
                "window_height": 680
            }
            json.dump(data, file, indent=4)
    
load_settings(e=None, update=False)

def main(page: ft.Page):
    
    page.window_width = window_width
    page.window_height = window_height
    
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
    page.snack_bar = page.snack_bar = ft.SnackBar(ft.Text("", size=font_size), duration=3000)
    
    def update_settings(e):
        global console_color
        if cg.value:
            console_color = cg.value
        load_settings(e, update=True )
        console_container.bgcolor = console_color
    
    def show_message(message):
        page.snack_bar.content.value = message
        page.snack_bar.open = True
        page.update()
    
    def set_font_size(e):
        global font_size
        font_size = int(e.control.value)
        computer_name.text_size = font_size
        settings_icon.icon_size = font_size
        delprof_icon.icon_size = font_size
        printers_icon.icon_size = font_size
        programs_icon.icon_size = font_size
        commands_icon.icon_size = font_size
        console_output.size = font_size
        font_size_text.size = font_size
        font_size_num_txt.size = font_size
        font_size_num_txt.value = f"{font_size}"
        settings_save_btn.size = font_size
        console_color_label.size = font_size
        running_processes_icon.size = font_size
        running_processes_count_text.size = font_size
        show_running_processes.size = font_size
        page.update()

    
    # Store list of runing processes here for tooltip
    list_of_processes = []
    
    # Left tab Pane
    settings_icon = ft.FilledButton("Settings", icon=ft.icons.SETTINGS, on_click=lambda _: page.go("/settings"))
    delprof_icon = ft.FilledButton("DelProf2", icon=ft.icons.DELETE, on_click=lambda _: page.go("/delprof"))
    printers_icon = ft.FilledButton("Printers", icon=ft.icons.PRINT, on_click=lambda _: page.go("/printers"))
    programs_icon = ft.FilledButton("Programs", icon=ft.icons.SAVE, on_click=lambda _: page.go("/programs"))
    commands_icon = ft.FilledButton("Commands", icon=ft.icons.COMPUTER, on_click=lambda _: page.go("/commands"))
    
    # Other controls
    settings_save_btn = ft.FilledButton("Save", icon=ft.icons.SAVE, on_click=update_settings)
    running_processes_icon = ft.Icon(name=ft.icons.TERMINAL, size=font_size, tooltip=list_of_processes)
    running_processes_count_text = ft.Text(f"{running_processes_count}", size=font_size)
    show_running_processes = ft.Text("", size=font_size)
    
    # List view for printer wizard
    printer_wiz_listview = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    
    # Settings color choice radio
    console_color_label = ft.Text("Console Color:", size=font_size)
    red_color_radio = ft.Radio(value="red", label="Red", fill_color="red")
    blue_color_radio = ft.Radio(value="blue", label="Blue", fill_color="blue")
    green_color_radio = ft.Radio(value="green", label="Green", fill_color="green")
    black_color_radio = ft.Radio(value="black", label="Black", fill_color="black")
    cg = ft.RadioGroup(content=ft.Column([
            red_color_radio,
            blue_color_radio,
            green_color_radio,
            black_color_radio
        ]))
    
    
    left_tab_pane = ft.Container(
        content=ft.Column(controls=[
            settings_icon,
            delprof_icon,
            printers_icon,
            programs_icon,
            commands_icon,
        ])
    )
    
    # Console text output
    console_output = ft.Text("", overflow=True, selectable=True, size=font_size, color=console_text_color)
    console_container = ft.Container(
                                content=console_output,
                                bgcolor=console_color,
                                expand=True,
                                alignment=ft.alignment.top_left,
                                )
    
    # Computer Text Field
    computer_name = ft.TextField(label="Computer Name")
    
    def date_time():
        x = datetime.datetime.now()
        x = x.strftime("%c")
        return x
    
    def update_console(data):
        console_output.value = f"\n[{date_time()}]: {data}" + f"\n{console_output.value}"
        page.update()
    
    def update_processes(op, name):
        global running_processes_count
        if op == "-":
            running_processes_count -= 1
            list_of_processes.remove(name)
            running_processes_count_text.value = f"{running_processes_count}"
        else:
            running_processes_count += 1
            list_of_processes.append(name)
            running_processes_count_text.value = f"{running_processes_count}"
        if len(list_of_processes) > 0:
            processes = ""
            for process in list_of_processes:
                processes += f"{process} "
            show_running_processes.value = processes
        else:
            show_running_processes.value = ""
        page.update()
    
    def check_computer_name():
        if computer_name.value == "":
            update_console("Please input a computer hostname")
            return False
        else:
            return True
        
    def ping(e):
        if check_computer_name():
            update_processes("+", "PING")
            show_message(f"Pinging {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.ping(computer=computer_name.value)
            update_console(result)
            update_processes("-", "PING")
    
    def quser(e):
        if check_computer_name():
            update_processes("+", "QUSER")
            show_message(f"Querying logged in users on {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.quser(computer=computer_name.value)
            update_console(result)
            update_processes("-", "QUSER")

    def check_printers(e):
        if check_computer_name():
            page.go("/")
            update_processes("+", "CHECK-PRINTERS")
            show_message(f"Getting printers on {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.check_printers(computer=computer_name.value)
            update_console(result)
            update_processes("-", "CHECK-PRINTERS")
    
    
    def printer_wizard(e):
        global printer_wiz_target_computer
        if check_computer_name():
            printer_wiz_target_computer = computer_name.value
            update_processes("+", "PRINTER_WIZARD")
            show_message(f"Running printer wizard on {computer_name.value}")
            powershell = the_shell.Power_Shell()
            result = powershell.printer_wizard(computer=computer_name.value)
            update_processes("-", "PRINTER_WIZARD")
            printer_wiz_listview.controls.clear()
            with open(f"./results/{computer_name.value}-Printers.json") as file:
                printers = json.load(file)
            for printer in printers:
                new_printer = printers[printer]
                printer_list_item = ft.Row([
                    ft.Column([
                        ft.Text(f"{new_printer["Name"]}, Status: {new_printer["Status"]}", size=font_size)
                    ], width=200),
                    ft.Column([
                        ft.FilledButton("Test Page", data=f"{new_printer["Name"]}", on_click=printer_wiz_testpage)
                    ]),
                    ft.Column([
                        ft.FilledButton("Rename")
                    ]),
                    ft.Column([
                        ft.FilledButton("Uninstall")
                    ]),
                ])
                
                printer_wiz_listview.controls.append(printer_list_item)
            page.go("/printerwizard")
        
    def printer_wiz_testpage(e):
        if check_computer_name():
            update_processes("+", "TEST-PAGE")
            show_message(f"Printing test page from {computer_name.value}.")
            powershell = the_shell.Power_Shell()
            result = powershell.test_page(computer=computer_name.value, printerName=e.control.data)
            update_console(result)
            update_processes("-", "TEST-PAGE")
    
    # def test_command(e):
    #     page.go("/")
    #     update_processes("+", "TEST")
    #     show_message(f"Running test.ps1")
    #     powershell = the_shell.Power_Shell()
    #     result = powershell.test_commands()
    #     for item in result:
    #         print("print statement", item)
    #     update_processes("-", "TEST")
            

    ping_btn = ft.FilledButton(text="Ping", on_click=ping)
    quser_btn = ft.IconButton(
                                icon=ft.icons.PERSON,
                                icon_color="blue400",
                                icon_size=20,
                                tooltip="QUser",
                                on_click=quser
                            )
    font_size_text = ft.Text("Font Size:", size=font_size)
    font_size_num_txt = ft.Text(f"{font_size}",size=font_size)
    def route_change(route):
        
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [ 
                    ft.Row([
                        ft.Column(controls=[left_tab_pane], alignment="center"),
                        ft.Column([
                            ft.Row([
                                computer_name,
                                ping_btn,
                                quser_btn,
                                running_processes_icon,
                                running_processes_count_text,
                                ft.Column([
                                    ft.Row([
                                        show_running_processes
                                    ], scroll=True, width=200)
                                ])
                            ]),
                            ft.Row([
                                console_container
                            ], expand=True)
                        ], expand=True),
                        
                    ], expand=True),
                ],
            )
        )
        
        if page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    [
                        ft.AppBar(title=ft.Text("Settings"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.Row(
                            [
                                font_size_text,
                                font_size_num_txt,
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Slider(value=font_size, min=10, max=36, divisions=26, on_change=set_font_size),
                            ]
                        ),
                        ft.Row([
                            console_color_label,
                            cg
                        ]),
                        ft.Row([
                            settings_save_btn,
                        ])
                    ],
                )
            )
        if page.route == "/delprof":
            page.views.append(
                ft.View(
                    "/delprof",
                    [
                        ft.AppBar(title=ft.Text("DelProf2"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        if page.route == "/printers":
            page.views.append(
                ft.View(
                    "/printers",
                    [
                        ft.AppBar(title=ft.Text("Printers"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Check Printers", on_click=check_printers),
                        ft.ElevatedButton("Printer Wizard", on_click=printer_wizard),
                    ],
                )
            )
        if page.route == "/printerwizard":
            page.views.append(
                ft.View(
                    "/printerwizard",
                    [
                        ft.AppBar(title=ft.Text("Printer Wizard"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.Row([
                            ft.Column([
                            printer_wiz_listview,
                            ], expand=True),
                            ft.Column([
                                console_container
                            ], expand=True)
                        ], expand=True)
                        
                    ],
                )
            )
        if page.route == "/programs":
            page.views.append(
                ft.View(
                    "/programs",
                    [
                        ft.AppBar(title=ft.Text("Programs"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        if page.route == "/commands":
            page.views.append(
                ft.View(
                    "/commands",
                    [
                        ft.AppBar(title=ft.Text("Commands"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        page.update()
        
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)
    
    # page.add(
        
    # )

ft.app(target=main)