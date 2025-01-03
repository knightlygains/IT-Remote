import flet as ft
import the_shell
import datetime, json, re, subprocess, ctypes, os, time, socket, pathlib, csv
from tutorial_btn import TutorialBtn
import text_values as text_values # Long text values stored in separate file
from dynamic_modal import DynamicModal
from are_you_sure import YouSure
from donate_view import donate_view
from settings_values import *

# Create settings.json if not exists and/or load saved values
load_settings(e=None, update=False)

# Create recent_computers.json
if os.path.exists(recent_computers_path) == False:
    with open(recent_computers_path, "w") as file:
        print(f"{recent_computers_path} created")
        init_data = {"computers":[]}
        json.dump(init_data, file, indent=4)

#Cleanup old files
printers_path = "assets/results/Printers"
clearspace_path = "assets/results/ClearSpace"
programs_path = "assets/results/Programs"
restart_path = "assets/results/Restart"
battery_path = "assets/results/Battery"
users_path = "assets/results/Users"
uptime_path = "assets/results/Uptime"
if os.path.exists(printers_path):
    for filename in os.listdir(printers_path):
        pathlib.Path(f"{printers_path}/{filename}").unlink()
if os.path.exists(clearspace_path):   
    for filename in os.listdir(clearspace_path):
        pathlib.Path(f"{clearspace_path}/{filename}").unlink()
if os.path.exists(programs_path):  
    for filename in os.listdir(programs_path):
        pathlib.Path(f"{programs_path}/{filename}").unlink()
if os.path.exists(restart_path):  
    for filename in os.listdir(restart_path):
        pathlib.Path(f"{restart_path}/{filename}").unlink()
if os.path.exists(battery_path):  
    for filename in os.listdir(battery_path):
        pathlib.Path(f"{battery_path}/{filename}").unlink()
if os.path.exists(users_path):  
    for filename in os.listdir(users_path):
        pathlib.Path(f"{users_path}/{filename}").unlink()
if os.path.exists(uptime_path):  
    for filename in os.listdir(uptime_path):
        pathlib.Path(f"{uptime_path}/{filename}").unlink()

# Program
def main(page: ft.Page):
    #Setup PowerShell
    powershell = the_shell.Power_Shell()
    
    page.fonts = {
        "Consola": "fonts/Consola.ttf"
    }
    
    def min_max(e):
        if e.control.data == "min":
            page.window.minimized = True
            page.update()
            return
        
        if page.window.maximized == False:
            page.window.maximized = True
        else:
            page.window.maximized = False
        page.update()
    
    page.window.title_bar_hidden = True
    
    drag_window = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Image(src="images/itremote.svg", width=32),
                padding=ft.padding.only(left=10, top=3)
            ),
            ft.WindowDragArea(ft.Container(
            ), height=37, expand=True),
            ft.IconButton("minimize", data="min", on_click=min_max),
            ft.IconButton("square_outlined", data="toggle", on_click=min_max),
            ft.IconButton("close", on_click=lambda _: page.window.close())
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=settings_values['app_color']
    )
    
    page.window.width = settings_values['window_width']
    page.window.height = settings_values['window_height']
    page.window.min_width = 745
    page.window.min_height = 525
    page.padding=0
    if page.window.width < page.window.min_width:
        page.window.width = page.window.min_width
    if page.window.height < page.window.min_height:
        page.window.height = page.window.min_height
    page.dark_theme = ft.Theme(color_scheme_seed=settings_values['app_color'])
    page.theme = ft.Theme(color_scheme_seed=settings_values['app_color'])
    
    def page_theme():
        if settings_values['dark_theme']: 
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
    
    page_theme()
    
    def save_page_dimensions(e):
        try:
            with open(settings_path, "r") as settings:
                data = json.load(settings)
                data.update({"window_width": page.width, "window_height": page.height})
            with open(settings_path, "w") as settings:
                json.dump(data, settings, indent=4)
        except ValueError as e:
            print(f"Something went wrong with saving page dimensions, {e}")
        
    page.on_resized = save_page_dimensions
    snack_bar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snack_bar)
    
    def update_settings(e):
        # App color setting updates
        if app_color_radio_group.value:
            settings_values['app_color'] = app_color_radio_group.value
        settings_values['dark_theme'] = theme_mode.value
        page_theme() # Set light/dark theme accordingly
        results_container.bgcolor = settings_values['app_color']
        printer_wiz_list_container.bgcolor = settings_values['app_color']
        page.dark_theme.color_scheme_seed = settings_values['app_color']
        page.theme.color_scheme_seed = settings_values['app_color']
        actions_view_container.bgcolor = settings_values['app_color']
        custom_scripts_container.bgcolor = settings_values['app_color']
        running_processes_container.bgcolor = settings_values['app_color']
        drag_window.bgcolor = settings_values['app_color']
        settings_values['enable_win_rm'] = winrm_checkbox.value
        settings_values['supress_winrm_results'] = winrm_results_checkbox.value
        settings_values['use_24hr'] = use_24hr_checkbox.value
        settings_values['warn_about_profile_deletion'] = warn_checkbox.value
        settings_values['home_tab'] = home_tab_radio_grp.value
        settings_save_btn.disabled = True
        load_settings(e, update=True)
        try:
            if e.control.text == "Save":
                show_message("Saved.", duration=700)
        except AttributeError:
            pass
        generate_scripts() # Call this mainly to update colors
        page.update()
    
    
    
    # generate a unique ID string for results
    result_id_num = 0
    def gen_result_id():
        nonlocal result_id_num
        result_id_num += 1
        return f"result_{result_id_num}"
    
    # -------------------- COMPUTER NAME --------------------
    def ping(e):
        nonlocal powershell
        if check_computer_name() and process_not_running("Ping", computer_name.value):
            computer = computer_name.value
            id = gen_result_id()
            add_new_process(new_process("Ping", [computer_name.value], date_time(), id))
            show_message(f"Pinging {computer_name.value}")
            
            result = powershell.ping(computer=computer_name.value)
            update_results("Ping", result, id, computer)
            end_of_process(id)
    
    computer_name = ft.TextField(label="Computer Name", on_submit=ping)
    
    # -------------------- RECENT PCS --------------------
    def update_recent_computers(computer, date, last_action):
        # We need to convert to json.
        # For each computer in data['Computers']
        try:
            with open(recent_computers_path, "r") as file:
                
                recent_pc = {
                    "name": computer,
                    "date": date,
                    "last_action": last_action
                }
                
                g = json.load(file)
                
                for comp in g['computers']:
                    if comp['name'] == recent_pc['name']:
                        g['computers'].remove(comp)
                
                if len(g['computers']) < 20:
                    g['computers'].insert(0,recent_pc)
                else:
                    g['computers'].pop()
                    g['computers'].insert(0,recent_pc)
            
        except ValueError as e:
            print(f"Something went wrong updating recent computers file. {e}")
        finally:
            with open(recent_computers_path, "w") as file:
                json.dump(g, file, indent=4)
    
    def load_recent_computers(e):
        # Store list of recent computers
        recent_computer_names = []
        recent_computer_items = []
        
        try:
            with open(recent_computers_path, "r") as file:
                data = json.load(file)
                for item in data['computers']:
                    if item['name'] not in recent_computer_names:
                        recent_computer_items.append(item)
                        recent_computer_names.append(item['name'])
        except FileNotFoundError as e:
            show_message("recent_computers.json is missing. Please relaunch program.")
            print(e)
            return
        
        list_of_recent_pcs_radios = []
        
        for pc in recent_computer_items:
            name = pc['name']
            date = pc['date']
            last_action = pc['last_action']
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
        
        def clear_recent_pcs(e):
            with open(recent_computers_path, "w") as file:
                g = {
                    "computers": []
                }
                json.dump(g, file, indent=4)
            close_dialog()
            show_message("Cleared recent PCs.")
        
        clear_recent_pcs_btn = ft.TextButton("Clear Recent PCs", on_click=clear_recent_pcs)
        
        content = ft.Container(
            content=ft.Column([
                recent_pc_radio_grp,
                clear_recent_pcs_btn
            ])
        )
        
        modal = DynamicModal(
            title="Select a recent computer",
            content=content,
            close_modal_func=close_dialog,
            nolistview=False,
            width=700
        )

        page.open(modal.get_modal())
        page.update()
        
        while modal.modal.open:
            pass
        
        if recent_pc_radio_grp.value != None:
            computer_name.value = recent_pc_radio_grp.value
            page.update()
    
    def date_time(**kwargs):
        x = datetime.datetime.now()
        day = x.strftime("%a")
        day_num = x.strftime("%d")
        month = x.strftime("%b")
        if settings_values['use_24hr']:
            time = x.strftime("%X")
        else:
            time = x.strftime("%I:%M:%S %p")
            if time[0] == "0":
                time = time.lstrip("0")
                
        for key, value in kwargs.items():
            if key == "force_24" and value == True:
                return x.strftime("%X")
            if key == "result_card" and value == True:
                return x.strftime("%c") #Ex: Mon Dec 31 17:41:00 2018
            
        return f"{day} {month} {day_num}, {time}"
    
    def format_text_specialchar(e):
        # Remove spaces
        e.control.value = str(e.control.value).replace(" ", "")
        # Use regex to remove speical chars
        e.control.value = re.sub('[^a-zA-Z0-9 \\n\\._-]', '', e.control.value)
        # Remove period
        e.control.value = str(e.control.value).replace(".", "")
        e.control.update()
    
    # -------------------- Dynamic Modal --------------------
    def close_dialog(e = None):
        """Close all currently
        open dialog boxes
        """
        for dialog in page.overlay:
            try:
                if dialog.open:
                    page.close(dialog)
            except AttributeError as e:
                pass
    
    # -------------------- PROCESSES --------------------
    running_processes_count = 0
    
    # Store list of runing processes here for tooltip
    list_of_processes = []
    
    # Store a list of computernames we have run actions on.
    list_of_computernames = []
    
    # Store a list of actions we have run.
    list_of_actions = []
    
    # Store a list of dates logged by result cards
    list_of_days = []
    
    # Running Processes Modal \/
    
    running_processes_controls = []
    # Container for running process cards
    running_processes_container = ft.Container(
        content=ft.Column(
            running_processes_controls,
            scroll=ft.ScrollMode.ADAPTIVE
        ),
        bgcolor=settings_values['app_color'],
        border_radius=10
    )
    
    def show_processes_modal(e):
        nonlocal running_processes_container
        
        running_proc_modal = DynamicModal(
            title="Running Processes",
            content=running_processes_container,
            close_modal_func=close_dialog,
            nolistview=True,
            width=400
        ).get_modal()
        
        if len(running_processes_controls) == 0:
            # Change content to say nothing here if there are no running processes
            running_proc_modal.content = ft.Text("Nothing here")
        
        page.open(running_proc_modal)
        page.update()
    
    running_processes_icon = ft.IconButton(
        icon="terminal", 
        on_click=show_processes_modal, 
        tooltip="Running processes",
    )
    
    running_processes_count_text = ft.Text(f"{running_processes_count}", )
    
    loading_ring = ft.ProgressRing(visible=False, width=30, height=30,offset=ft.transform.Offset(0.18, 0.18))
    
    def process_not_running(name, computer):
        for process in list_of_processes:
            if process['name'] == "WinRM" and computer in process['computers']:
                # Check if WinRM is running on computer
                show_message(f"Wait until process 'WinRM' on {computer} finishes.")
                return False
            elif computer in process['computers'] and process['name'] == name:
                # Proc is running on computer already
                show_message(f"Wait until process '{name}' on {computer} finishes.")
                return False
        return True
    
    def add_new_process(process_dict):
        nonlocal running_processes_count
        running_processes_count += 1
        list_of_processes.append(process_dict)
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
        running_processes_controls.clear()
        
        # The loop through existing ones and re-add
        for process in list_of_processes:
            comps = "Computers: "

            for comp in process['computers']:
                comps +=  f"{comp} "
                
            new_proc_card = ft.Card(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(name="terminal_rounded"),
                        title=ft.Text(process['name']),
                        subtitle=ft.Text(comps),
                    )
                ])
            )
            running_processes_controls.append(new_proc_card)
        
        running_processes_container.content.controls = running_processes_controls
        
        if len(list_of_processes) > 0:
            loading_ring.visible = True
        else:
            loading_ring.visible = False
    
    def end_of_process(id):
        """Remove process from running_processes by id
        """
        nonlocal running_processes_count
        for process in list_of_processes:
            if process['id'] == id:
                show_message(f"{process['name']} - {process['computers']}: has finished")
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
    
    # -------------------- NAVIGATION --------------------
    def navigate_view(e):
        # If called by a control set equal to control value
        # Otherwise we are likely passing a specific index
        try:
            index = e.control.selected_index
        except AttributeError:
            index = int(e)
            rail.selected_index = index
        if index == 0:
            current_view.controls = [settings_view]
        if index == 1:
            home_badge(reset=True)
            current_view.controls = [home]
        if index == 2:
            # Actions Tab
            current_view.controls = [actions_view]
        if index == 3:
            current_view.controls = [custom_scripts_view]
        if index == 4:
            # Donate
            current_view.controls = [donate_view]
        if index == 5:
            pass
        if index == 6:
            # Print Wizard View
            rail.selected_index = 2
            current_view.controls = [print_wizard_view]
        page.update()
    
    def home_badge(e=None, reset=False):
        if reset:
            # I have to fully re-assign the icon control
            # to reset the badge to None. Simply
            # setting it = None doesn't work.
            home_icon.icon = ft.Icon(
                name="home_outlined",
                badge=None
            )
        else:
            home_icon.icon.badge = ft.Badge(small_size=10)
            
        try:
            home_icon.icon.update()
        except AssertionError as e:
            # Control isn't added to page yet so ignore
            pass
    
    home_icon = ft.NavigationRailDestination(
        icon=ft.Icon(
            name="home_outlined",
            badge=None
        ),
        selected_icon=ft.Icon(
            name="home"
        ),
        label_content=ft.Text("Results")
    )
    
    rail = ft.NavigationRail(
        selected_index=1,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=50,
        min_extended_width=400,
        group_alignment=-1,
        destinations=[
            ft.NavigationRailDestination(
                icon="settings_outlined",
                selected_icon="settings",
                label_content=ft.Text("Settings"),
            ),
            home_icon,
            ft.NavigationRailDestination(
                icon="terminal_outlined",
                selected_icon="terminal",
                label_content=ft.Text("Actions"),
            ),
            ft.NavigationRailDestination(
                icon="description_outlined",
                selected_icon="description",
                label_content=ft.Text("My Scripts"), # custom_scripts_view
            ),
            ft.NavigationRailDestination(
                icon="favorite_outline_outlined",
                selected_icon="favorite",
                label_content=ft.Text("Donate"),
            ),
        ],
        on_change=navigate_view
    )
    
    # -------------------- APP FUNCTIONS --------------------
    def are_you_sure(e, text, **kwargs):
        title = "Confirm:"
        no_text = "Cancel"
        yes_text = "Yes"
        yes_color = None
        no_color = None
        for key, value in kwargs.items():
            if key == "title":
                title = value
            if key == "no_text":
                no_text = value
            if key == "yes_text":
                yes_text = value
            if key == "yes_color":
                yes_color = value
            if key == "no_color":
                no_color = value
        
        sure_modal = YouSure(text, title, close_dialog, no_text=no_text, yes_text=yes_text, yes_color=yes_color, no_color=no_color)

        page.open(sure_modal.get_modal())
        page.update()
        answer = False
        while sure_modal.modal.open:
            answer = sure_modal.said_yes
            if answer != None:
                return answer
            else:
                pass
    
    snack_bar = ft.SnackBar(content=ft.Text(""))
    page.overlay.append(snack_bar)
    
    def show_message(message, **kwargs):
        nonlocal snack_bar
        snack_bar.duration = 3000
        for key, value in kwargs.items():
            if key == "duration":
                snack_bar.duration = value
        
        snack_bar.content.value = message
        snack_bar.open = True
        page.update()
    
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
    
    def check_list():
        
        try:
            with open(computerlist_path, "r") as file:
                
                contents = file.read()
                if contents == "":
                    show_message("List is empty.")
                    return False
        except FileNotFoundError as e:
            with open(computerlist_path, "x") as file:
                print("Computer list file created.")
                
        try:
            with open(computerlist_path, "r") as list:
                computers = list.read()
                if computers == "":
                    show_message("List is empty.")
                    return False
                
                if re.compile('[^a-zA-Z0-9\\n-]').search(computers): # Regex: match a single character not present in the set
                    show_message("The list is not formatted properly or contains illegal characters.")
                    return False
                else:
                    return True
        except FileNotFoundError as e:
            with open(computerlist_path, "x") as file:
                print("Computer list file created.")
        
    def find_day(date):
        """Feed this function a date and it will return the  day of the week

        Args:
            date (string): the date

        Returns:
            string: "Mon"
        """
        p = re.compile("^([A-Z][a-z]{2,})") # Wed
        day = p.search(date)
        day = day.group(1)
        return day
    
    def update_results(title_text = None, data = None, id = None, computer = None, **kwargs):
        print_log_card = False
        print_wiz_card = False
        check_space_card = False
        app_result = False
        subtitle=data
        
        date = date_time()
        
        if computer != None:
            if computer.lower() == "localhost":
                computer = socket.gethostname()
        
        for key, value in kwargs.items():
            if key == "print_log":
                print_log_card = True
            if key == "type":
                type = value
            if key == "print_wiz":
                print_wiz_card = value
            if key == "check_space":
                check_space_card = value
            if key == "subtitle":
                subtitle=value  
            if key == "app_result":
                app_result = value
                
        
        if app_result != True:
        
            if computer not in list_of_computernames and computer != "list of computers":
                list_of_computernames.append(computer)
                comp_checkboxes.append(ft.Checkbox(label=f"{computer}", value=True, data=f"{computer}"))
            
            if title_text not in list_of_actions:
                list_of_actions.append(title_text)
                action_checkboxes.append(ft.Checkbox(label=f"{title_text}", value=True, data=f"{title_text}"))
            
            # Get the day of the week the result was generated
            day = find_day(date)
            if day not in list_of_days:
                list_of_days.append(day)
                date_checkboxes.append(ft.Checkbox(label=f"{day}", value=True, data=f"{day}"))
            
            if computer != "list of computers":
                update_recent_computers(computer, date, title_text)
            
            if print_log_card:
                data = f"assets/results/Printers/{computer}-Printers-{type}-logs.json"
            elif print_wiz_card:
                data = f"assets/results/Printers/{computer}-Printers.json"
            elif check_space_card:
                data = f"assets/results/ClearSpace/{id}-Space-Available.json"
        
        card = generate_result_card(
            leading = ft.Icon("terminal"),
            title=ft.Text(f"{title_text} - {computer}"),
            date=date_time(),
            data=data,
            id=id,
            computer=computer,
            subtitle=subtitle,
            action=title_text
        )
        
        result_data.controls.insert(0, card)
        if rail.selected_index != 1:
            # If home isnt already selected, add notifcation badge
            home_badge()
        
        apply_results_filter(False)
    
    result_count = 0 # Used to store as an ID in a result_card to sort results
    
    # Console text output
    result_data = ft.ListView(expand=1, spacing=10, padding=20)

    results_container = ft.Container(
        content=result_data,
        bgcolor=settings_values['app_color'],
        expand=True,
        alignment=ft.alignment.top_left,
        border_radius=10
    )
    
    # Holds controls we removed from result_data
    filtered_out_results = []
    
    # Computernames we want to filter out
    filter_out_PCs = []
    
    # Actions we want to filter out
    filter_out_actions = []
    
    # Days of the week we want to filter out
    filter_out_days = []
    
    # Informational control to show if there are no attributes to filter by.
    # We will change to not visible when there are filterable attributes.
    comp_checkbx_nothing_here = ft.Text("Nothing here")
    action_checkbx_nothing_here = ft.Text("Nothing here")
    day_checkbx_nothing_here = ft.Text("Nothing here")
    
    # Store all action checkboxes generated for PCs we ran actions on
    date_checkboxes = [day_checkbx_nothing_here]
    
    # Store all action checkboxes generated for PCs we ran actions on
    action_checkboxes = [action_checkbx_nothing_here]
    
    # Store all checkboxes generated for PCs we ran actions on
    comp_checkboxes = [comp_checkbx_nothing_here]
    
    def apply_results_filter(clear_filter):
        """Removes result cards from result_data based on filter settings

        Args:
            clear_filter (bool): If True, will reset the filtering
        """
        show_filter_message = False
        results = result_data.controls
        
        if clear_filter:
                filter_out_PCs.clear()
                filter_out_actions.clear()
                filter_out_days.clear()
        total_filtered_controls = 0
        for control in results:
                # If the controls data:'Computer', 'action' or 'day'
                # is found in the the filter_out lists
                # Remove the control and add it to another list
            if control.data['Computer'] in filter_out_PCs or control.data['action'] in filter_out_actions or control.data['day'] in filter_out_days:
                show_filter_message = True
                total_filtered_controls += 1
                filtered_out_results.append(control)

        restore_filtered_results = [] # Reference controls to be restored
        # If we remove the controls while looping through them it messes up the loop iterations
        
        for control in filtered_out_results:
            # If the controls data isnt in the filter_out lists,
            # we want to re-add it to result_data
            if control.data['Computer'] not in filter_out_PCs and control.data['action'] not in filter_out_actions and control.data['day'] not in filter_out_days:
                results.append(control)
                restore_filtered_results.append(control)
            else:
                try:
                    results.remove(control)
                except ValueError:  # The control was already removed
                    pass

        # Now loop through referenced controls and remove them from filtered_out_results
        for control in restore_filtered_results:
            filtered_out_results.remove(control)

        # Sort results by their date
        results.sort(key=lambda control: control.data['SortId'], reverse=True)
        if len(filter_out_PCs) > 0:
            filter_btn.icon = "filter_alt"
            filter_btn.tooltip = "On"
        else:
            filter_btn.icon = "filter_alt_off"
            filter_btn.tooltip = "Off"
        
        if show_filter_message:
            show_message(f"Filtered out {total_filtered_controls} results")
        
        page.update()

    def filter_results(e):
        nonlocal comp_checkboxes
        # Set up filter modal
        
        def is_filterable(checkboxes: list):
            """Checks comp_checkboxes, date_checkboxes, and action_checkboxes
            to see if there are any checkboxes in them. If there are we change
            the crresponding 'nothing_here' Text control to not visible.

            Args:
                checkboxes (list): a list of controls,.
            """
            for list in checkboxes:
                if len(list) > 1:
                    for item in list:
                        if item.value == "Nothing here":
                            item.visible = False
                else:
                    for item in list:
                        if item.value == "Nothing here":
                            item.visible = True

        is_filterable([date_checkboxes, action_checkboxes, comp_checkboxes])
        
        date_tile = ft.ExpansionPanel(
            header=ft.ListTile(
                title=ft.Text("Day")
            ),
            content=ft.Row(
                date_checkboxes,
                wrap=True,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            can_tap_header=True
        )
        
        comp_checkboxes_tile = ft.ExpansionPanel(
            header=ft.ListTile(
                title=ft.Text("Computers")
            ),
            content=ft.Row(
                comp_checkboxes,  
                wrap=True,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            can_tap_header=True
        )
        
        actions_checkboxes_tile = ft.ExpansionPanel(
            header=ft.ListTile(
                title=ft.Text("Actions"),
            ),
            content=ft.Row(
                action_checkboxes,  
                wrap=True,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            can_tap_header=True
        )
        
        def select(e):
            for box in comp_checkboxes:
                if e.control.data == "select":
                    box.value = True
                else:
                    box.value = False
            for box in action_checkboxes:
                if e.control.data == "select":
                    box.value = True
                else:
                    box.value = False
            for box in date_checkboxes:
                if e.control.data == "select":
                    box.value = True
                else:
                    box.value = False
            page.update()
        
        select_all_btn = ft.FilledTonalButton("Select All", 
            icon="check_box", 
            data="select",
            on_click=select
        )
        deselect_all_btn = ft.FilledTonalButton("Deselect All", 
            icon="check_box_outline_blank", 
            data="deselect",
            on_click=select
        )
        
        content_container = ft.Container(
            content=ft.Column([
                    ft.Row([
                        select_all_btn,
                        deselect_all_btn
                    ]),
                    ft.ListView([
                        ft.ExpansionPanelList([
                            date_tile,
                            comp_checkboxes_tile,
                            actions_checkboxes_tile
                        ]),
                    ], expand=1)
                ]),
            bgcolor=settings_values['app_color'],
            border_radius=10,
            border=ft.border.all(1, settings_values['app_color'])
        )
        
        modal = DynamicModal(
            title=f"Filter results",
            content=content_container,
            close_modal_func=close_dialog,
            nolistview=True
        )
        
        page.open(modal.get_modal())
        page.update()
        
        while modal.modal.open:
            pass
        
        if len(comp_checkboxes) != 1:
            for checkbox in comp_checkboxes:
                
                if checkbox.value and checkbox.data in filter_out_PCs:
                    filter_out_PCs.remove(checkbox.data)
                elif checkbox.data not in filter_out_PCs and checkbox.value == False:
                    filter_out_PCs.append(checkbox.data)
        
        
        if len(comp_checkboxes) != 1:
            for checkbox in action_checkboxes:
                
                if checkbox.value and checkbox.data in filter_out_actions:
                    filter_out_actions.remove(checkbox.data)
                elif checkbox.data not in filter_out_actions and checkbox.value == False:
                    filter_out_actions.append(checkbox.data)
        
        if len(comp_checkboxes) != 1:
            for checkbox in date_checkboxes:
                
                if checkbox.value and checkbox.data in filter_out_days:
                    filter_out_days.remove(checkbox.data)
                elif checkbox.data not in filter_out_days and checkbox.value == False:
                    filter_out_days.append(checkbox.data)
        
        apply_results_filter(False)
    
    # Card modal Stuff \/
    def show_card_modal(modal):
        page.open(modal)
        page.update()
    
    def open_results_card(e):
        """
        Sets card modal content and opens it.
        """
        
        ctr_data = "None"
        ctr_computer = "None"
        for key, value in e.control.data.items():
            if key == "data":
                ctr_data = value
            if key == "computer":
                ctr_computer = value
        
        # Define card modal
        result_card_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text(e.control.title.value),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(ctr_data, selectable=True)
            ], scroll=True)),
            actions=[
                ft.TextButton("Close", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        show_card_modal(result_card_modal)
    
    def remove_results_card(e):
        id = e.control.data
        if id == "all":
            # We clicked the remove all results button
            amt_cleared = len(result_data.controls)
            result_data.controls.clear()
            show_message(f"Removed {amt_cleared} results.")
        else:
            for control in result_data.controls:
                if id == control.data['Id']:
                    result_data.controls.remove(control)
                    show_message(f"Removed {control.data['action']} - {control.data['Computer']}.")
        page.update()
    
    def generate_result_card(leading, title, date, data, id, computer, action, **kwargs):
        """
        Clickable card that shows in the console.
        Is called from update_results()
        """
        nonlocal result_count
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
            f"assets/results/Printers/{computer}-Printers-Operational-logs.json",
            f"assets/results/Printers/{computer}-Printers-Admin-logs.json"
        ]
        
        # Change card_content controls based on type of card
        # we are making.
        
        # Printer_wizard Card
        if data == f"assets/results/Printers/{computer}-Printers.json" and "Failed" not in subtitle_data:
            on_click_function = open_card_print_wiz
        # Print_Log card
        elif data in print_log_options:
            on_click_function = open_print_log_card
        elif data == f"assets/results/ClearSpace/{id}-Space-Available.json" and "Failed" not in subtitle_data:
            on_click_function = open_space_card
        elif "results/Programs/" in data:
            data = f"{data}"
            on_click_function = open_software_card
        elif "results/Battery/" in data:
            on_click_function = open_battery_card
        else:
            data = subtitle_data
            on_click_function = open_results_card

        subtitle_content = ft.Text(f"{subtitle_text}")
        
        card_content = ft.Column([
            ft.ListTile(
                leading=ft.Column([
                    leading,
                    ft.Text(f"{date}")
                    ], width=85, spacing=1),
                trailing=ft.IconButton(
                    icon="close",
                    icon_size=10,
                    tooltip="Remove",
                    on_click=remove_results_card,
                    data=id
                ),
                title=title,
                subtitle=subtitle_content,
                on_click=on_click_function,
                data={"data": data, "computer": computer, "date": date}
            ),
        ])
        
        result_card = ft.Card(
            content=card_content,
            data={"Id": id, "Computer": computer, "SortId": result_count, "action": action, "day": f"{find_day(date)}"}
        )
        
        result_count += 1
        
        return result_card
    
    # List view for printer wizard
    printer_wiz_listview = ft.ListView(expand=1, spacing=10, padding=20,)
    printer_wiz_list_container = ft.Container(
        bgcolor=settings_values['app_color'],
        content=printer_wiz_listview,
        border_radius=10,
        expand=True,
    )
    
    new_printer_name = ft.TextField(expand=True)
    
    # Used to track the last computer printer wizard was run on,
    # so as to not confuse with the current value in the computername
    # text field.
    printer_wiz_target_computer = ""
    printer_to_change = ""
    
    is_log_empty = False # Track if log returned 0 items
    def open_print_log_card(e):
        """
        Sets print log card modal content and opens it.
        """
        
        logs_list_view = ft.ListView(expand=1, padding= 20)
        
        ctr_data = "None"
        ctr_computer = "None"
        for key, value in e.control.data.items():
            if key == "data":
                ctr_data = value
            if key == "computer":
                ctr_computer = value
        log_json_path = ctr_data
        
        with open(log_json_path, "r") as file:
            nonlocal is_log_empty
            try:
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
                is_log_empty = False
            except Exception as e:
                is_log_empty = True
                print(e)
        
        ctr_data = "None"
        ctr_computer = "None"
        
        if is_log_empty:
            card_content = ft.Container(
                content=ft.Text("Test"),
                expand=1,
                width= 500
            )
        else:
            card_content = ft.Container(
                content=logs_list_view,
                expand=1,
                width= 500
            )

            for key, value in e.control.data.items():
                if key == "data":
                    ctr_data = value
                if key == "computer":
                    ctr_computer = value
        
        if "Operational" in ctr_data:
            title = f"{ctr_computer}'s Operational Print Logs"
        else:
            title = f"{ctr_computer}'s Admin Print Logs"
        
        print_log_card_modal = DynamicModal(
            title=title,
            content=card_content,
            close_modal_func=close_dialog
        )
        
        page.open(print_log_card_modal.get_modal())
        page.update()
    
    def open_card_print_wiz(e):
        ctr_data = "None"
        ctr_computer = "None"
        for key, value in e.control.data.items():
            if key == "data":
                ctr_data = value
            if key == "computer":
                ctr_computer = value
        get_printers(e, target_computer=ctr_computer)
    
    # Used to store the computer name
    # that "Get Printers" was run on
    printer_wiz_computer_text = ft.Text("None")
    
    def refresh_printers(e):
        nonlocal printer_wiz_target_computer
        printer_wiz_target_computer = printer_wiz_computer_text.data
        get_printers(e, target_computer=printer_wiz_target_computer, refresh=True)
    
    def restart_print_spooler(e):
        printer_wiz_target_computer = printer_wiz_computer_text.data
        print_wiz_view = False

        if e.control.data == "print_wiz_view":
            print_wiz_view = True
        
        def check_processes(computer):
            if (
                process_not_running("Test Page", computer) and
                process_not_running("Uninstall Printer", computer) and
                process_not_running("Rename Printer", computer) and
                process_not_running("Get Printers", computer) and
                process_not_running("Restart Print Spooler", computer)
            ):
                return True
            else:
                return False
            
        id = gen_result_id()
        if print_wiz_view:
            computer = printer_wiz_target_computer
            if check_processes(computer):
                enable_winrm(computer)
                add_new_process(new_process("Restart Print Spooler", [computer], date_time(), id))
                show_message(f"Restarting Print Spooler on {computer}")
                result = powershell.restart_print_spool(computer=computer)
                end_of_process(id)
        else:
            if check_computer_name() and check_processes(computer_name.value):
                computer = computer_name.value
                enable_winrm(computer)
                add_new_process(new_process("Restart Print Spooler", [computer], date_time(), id))
                show_message(f"Restarting Print Spooler on {computer}")
                
                result = powershell.restart_print_spool(computer=computer)
                update_results("Restart Print Spooler", result, id, computer)
                end_of_process(id)
    
    
    def open_space_card(e):
        
        """
        Uses dynamic modal to show info about the disk
        space on a computer.
        """
        # AlertDialog for when we click on a result from checking space on
        # a computer.
        
        ctr_data = "None"
        ctr_computer = "None"
        for key, value in e.control.data.items():
            if key == "data":
                ctr_data = value
            if key == "computer":
                ctr_computer = value
        
        disk_space_expansion_list = ft.ExpansionPanelList(
            elevation=8
        )
        
        # card_content = ft.Container(
        #     content=disk_space_expansion_list,
        #     expand=1,
        #     width= 500
        # )
        
        space_json_path = ctr_data
        with open(space_json_path, "r") as file:
            print(f"Opened {file}")
            data = json.load(file)
            
            for comp in data:
                print(comp)
                drives_list = [] # Drives found for this computer in the loop
                for disk in data[comp]:  # Loop through each disk
                    drive = data[comp][disk]
                    drive_ltr = drive['DiskId']
                    freespace = drive['FreeSpace']
                    maxsize = drive['MaxSize']
                    percentfree = drive['PercentFree']
                    drives_list.append(
                        ft.Column([
                            ft.Text(f"{drive_ltr}", weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Text("Percent Free:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{percentfree}", selectable=True),
                            ], wrap=True),
                            ft.Row([
                                ft.Text("Space:", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{freespace} / {maxsize} GB", selectable=True),
                            ]),
                        ])
                    )
                
                card = ft.ExpansionPanel(
                    header=ft.ListTile(
                            title=ft.Text(f"{comp}", weight=ft.FontWeight.BOLD),
                            trailing=ft.Icon(name="computer")
                        ),
                    content=ft.Container(
                            content=ft.Column(drives_list, expand = 1),
                            expand = 1,
                            padding=ft.padding.only(left=10, right=10, bottom=10)
                        ),
                    can_tap_header=True,
                    expand = 1
                )
                disk_space_expansion_list.controls.append(card)
        
        for key, value in e.control.data.items():
            if key == "computer":
                ctr_computer = value
        
        check_space_card = DynamicModal(
            title=f"{e.control.title.value}",
            content=disk_space_expansion_list,
            close_modal_func=close_dialog,
            nolistview=True
        )
        
        page.open(check_space_card.get_modal())
        page.update()
    
    
    
    
    def export_data(e):
        """on_click: pass the control's data as a dict.

        Args:
            e (dict): a dict that should contain either values for csv data or a
            value for txt_document (bool) and txt_data (string)
        """
        filename = None
        data = None
        list_of_column_names = None
        txt_document = None
        txt_data = None
        for key, value in e.control.data.items():
            if key == "FileName":
                filename = value
            if key == "results":
                data = value
            if key == "columns":
                list_of_column_names = value
            if key == "txt_document":
                txt_document = value
            if key == "txt_data":
                txt_data = value
        
        # Filepicker for picking directory
        def select_directory(e: ft.FilePickerResultEvent):
            save_location.value = e.path
            save_location.error_text = None
            save_location.update()
        
        pick_directory_dialog = ft.FilePicker(
            on_result=select_directory,
        )
            
        page.overlay.append(pick_directory_dialog)
        
        def check_directory(e):
            if os.path.exists(f"{e.control.value}"):
                e.control.error_text=None
            else:
                e.control.error_text="Directory does not exist."
            save_location.update()
        
        name = ft.TextField(
            label="Filename",
            on_change=format_text_specialchar,
            value=filename
        )
        
        save_location = ft.TextField(
            label="Save location",
            on_change=check_directory,
            value=pathlib.Path.home()
        )
        
        def save(e):
            if txt_document == None or txt_document == False: # saving csv
                
                if save_location.error_text == None and name.value != "":
                    with open(f"{save_location.value}\\{name.value}.csv", "w", encoding='utf-8', newline='') as file:
                        writer = csv.writer(file)
                        # Write column names
                        writer.writerow(list_of_column_names)
                        
                        # for each result, write a row
                        for result in data:
                            list_of_results = []
                            for key, value in result.items():
                                list_of_results.append(value)
                            writer.writerow(list_of_results)
                        
                    close_dialog(e)
                else:
                    if os.path.exists(f"{save_location.value}") == False:
                        save_location.error_text = "Path must be correct"
                    if name.value == "":
                        name.error_text = "Cannot be empty"
                    page.update()
                    
            else: # saving txt
                
                if save_location.error_text == None and name.value != "":
                    
                    with open(txt_data, "r") as txt:
                        txt_content = txt.readlines()
                        
                    with open(f"{save_location.value}\\{name.value}.txt", "w") as file:
                        # for each result, write a row
                        print("Saved:", f"{save_location.value}\\{name.value}.txt")

                        for result in txt_content:
                            file.write(result)
                        
                    close_dialog(e)
                else:
                    if os.path.exists(f"{save_location.value}") == False:
                        save_location.error_text = "Path must be correct"
                    if name.value == "":
                        name.error_text = "Cannot be empty"
                    page.update()
        
        def browse(e):
            pick_directory_dialog.get_directory_path(
                initial_directory=pathlib.Path.home(),
                dialog_title="Choose a save location"
            )
            page.update()
        
        content = ft.Column([
            ft.Text("(Do not include file extension)"),
            name,
            ft.Row([
                save_location,
                ft.FilledTonalButton(
                    "Browse",
                    on_click=browse
                )
            ]),
            ft.FilledTonalButton("Save", on_click=save)
        ])
        export_modal = DynamicModal("Export data:", content, close_dialog)
        
        page.open(export_modal.get_modal())
        page.update()
        
        while export_modal.modal.open:
            pass
    
    def open_software_card(e):
        ctr_data = "None"
        ctr_computer = "None"
        for key, value in e.control.data.items():
            if key == "data":
                ctr_data = value
            if key == "computer":
                ctr_computer = value
        software_json_path = ctr_data
        list_of_pcs = {}
        
        expansion_list = ft.ExpansionPanelList(
            elevation=8,
            controls=[]
        )
        
        # Append each software result here as dict
        # so we can export it.
        list_of_results = []
        
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
                                trailing=ft.Icon(name="computer")
                            ),
                            content=ft.Row(wrap=True, spacing=10),
                            can_tap_header=True
                        )
                        
                        # Add dict key of pc name with value of expansiontile
                        list_of_pcs.update({f"{pc}": exp_panel})
                    
                    text = f"""Version: {program['Version']}
Install date: {program['InstallDate']}
Registry path: {program['RegPath']}"""

                    result = {
                        "computer": f"{pc}",
                        "name": f"{program['Name']}",
                        "version": f"{program['Version']}",
                        "installdate": f"{program['InstallDate']}",
                        "registrypath": f"{program['RegPath']}"
                    }
                    
                    list_of_results.append(result)
                    
                    # Then add program info to corresponding PCs in the dict
                    new_control = ft.Container(
                        content=ft.Column([
                            ft.Text(f"{program['Name']}", selectable=True, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{text}", selectable=True),
                        ]),
                        padding=20
                    )
                    
                    list_of_pcs[f'{pc}'].content.controls.append(new_control)

        # Loop through expansionpanels in list and append them to expansion_list
        for pc in list_of_pcs:
            expansion_list.controls.append(list_of_pcs[f'{pc}'])
        
        for key, value in e.control.data.items():
            if key == "computer":
                ctr_computer = value
            if key == "date":
                date = value.replace(":", "-")
                date = date.replace(",", "")
                date = date = " - "
        
        btn_data = {"FileName": f"{date}{ctr_computer} software results", "columns": ['Computer", "Program", "Version", "Install Date", "Registry Path'], "results": list_of_results}
        
        modal = DynamicModal(
            title=f"{e.control.title.value}",
            content=ft.Column(controls=[
                expansion_list,
                ft.TextButton(
                    "Export csv", 
                    on_click=export_data,
                    data=btn_data
                )
            ]),
            close_modal_func=close_dialog
        )
        page.open(modal.get_modal())

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
        
        content = ft.Container(
            ft.Row([
                ft.Text(f"{help_text}"),
            ], wrap=True, width=500),
            border_radius=10,
            border=ft.border.all(1, settings_values['app_color']),
            padding=10,
        )

        modal = DynamicModal(
            title=f"{help_topic}",
            content=content,
            close_modal_func=close_dialog,
            nolistview=True
        )
        
        page.open(modal.get_modal())
        page.update()
    
    def enable_winrm(computer):
        if settings_values['enable_win_rm'] and check_computer_name() and process_not_running("WinRM", computer_name.value):
            if computer == None:
                computer = computer_name.value
            id = gen_result_id()
            add_new_process(new_process("WinRM", [computer], date_time(), id))
            
            result = powershell.enable_winrm(computer)
            if settings_values['supress_winrm_results'] != True:
                update_results("WinRM", result, id, computer)
            end_of_process(id)
            
    def rename_printer(e):
        computer = printer_wiz_target_computer
        if (
                process_not_running("Test Page", computer) and
                process_not_running("Uninstall Printer", computer) and
                process_not_running("Rename Printer", computer) and
                process_not_running("Get Printers", computer)
            ):
            close_printer_dlg(e)
            id = gen_result_id()
            add_new_process(new_process("Rename Printer", [computer], date_time(), id))
            show_message(f"Renaming printer on {computer}")
            
            result = powershell.rename_printer(computer=computer, printerName=printer_to_change, newName=new_printer_name.value)
            update_results("Rename Printer", result, id, computer)
            end_of_process(id)
        get_printers(e, refresh=True)
        
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
        nonlocal printer_to_change
        for key, value in e.control.data.items():
            if key == "printer":
                printer_to_change = value
        page.open(printer_name_modal)
        page.update()
    
    # More info printer modal
    def open_printer_more_info_modal(e):
        nonlocal printer_wiz_target_computer
        printer_name = e.control.data
        
        with open(f"assets/results/printers/{printer_wiz_target_computer}-Printers.json") as file:
            printers = json.load(file)
        
        for printer in printers:
            p = printers[printer]
            if p['Name'] == printer_name:
                more_info_printer = p
        
        content = ft.Column(
            [
                ft.Row([
                    ft.Row([
                        ft.Text(f"Name:", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"{more_info_printer['Name']}", 
                            selectable=True),
                    ], expand=True, wrap=True)
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Status:", weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"{more_info_printer['Status']}", 
                            selectable=True),
                    ], expand=True, wrap=True)
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Port:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Port']}", selectable=True),
                    ], expand=True, wrap=True)
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Published:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Published']}", selectable=True),
                    ], expand=True, wrap=True)
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Type:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Type']}", selectable=True),
                    ], expand=True, wrap=True)
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Shared:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Shared']}", selectable=True),
                    ], expand=True, wrap=True)
                ]),
                ft.Row([
                    ft.Row([
                        ft.Text(f"Driver:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{more_info_printer['Driver']}", selectable=True),
                    ], expand=True, wrap=True)
                ])
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        modal = DynamicModal(
            title=f"{more_info_printer['Name']}",
            content=content,
            close_modal_func=close_dialog,
            nolistview=True,
            width=300
        )
        
        page.open(modal.get_modal())
        page.update()
    
    def get_printers(e, **kwargs):
        nonlocal printer_wiz_target_computer
        if check_computer_name() and process_not_running("Get Printers", computer_name.value):
            refresh = False
            computer = computer_name.value
            printer_wiz_target_computer = computer
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
                                            icon="more_vert",
                                            items=[
                                                ft.PopupMenuItem(text="Test Page", data=control_data, on_click=testpage_printer),
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
                    printer_wiz_computer_text.data = computer
                    printer_wiz_computer_text.value = f"{computer}'s printers. Refreshed: {date_refreshed}"
                    navigate_view(6)
                except FileNotFoundError:
                    show_message(f"Could not get printers on {computer}")
            
            json_file = f'assets/results/Printers/{computer}-Printers.json'
            
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
                id = gen_result_id()
                add_new_process(new_process("Get Printers", [computer], date_time(), id))
                
                result = powershell.printer_wizard(computer=computer)
                if refresh == False:
                    update_results("Get Printers", data=result, id=id, computer=computer, print_wiz=True, subtitle=result)
                load_printers()
                end_of_process(id)
        
    def testpage_printer(e):
        for key, value in e.control.data.items():
                if key == "printer":
                    ctr_printer = value
                if key == "computer":
                    ctr_computer = value
        if (
                process_not_running("Test Page", ctr_computer) and
                process_not_running("Uninstall Printer", ctr_computer) and
                process_not_running("Rename Printer", ctr_computer) and
                process_not_running("Get Printers", ctr_computer)
            ):
            id = gen_result_id()
            add_new_process(new_process("Test Page", [ctr_computer], date_time(), id))
            show_message(f"Printing test page from {ctr_computer}.")
            
            result = powershell.test_page(computer=ctr_computer, printerName=ctr_printer)
            update_results("Printer Test Page", data=result, id=id, computer=ctr_computer)
            end_of_process(id)
    
    def uninstall_printer(e):
        for key, value in e.control.data.items():
            if key == "printer":
                ctr_printer = value
            if key == "computer":
                ctr_computer = value
        if (
                are_you_sure(e, f"Uninstall {ctr_printer} from {ctr_computer}?") and 
                process_not_running("Uninstall Printer", ctr_computer) and
                process_not_running("Get Printers", ctr_computer) and
                process_not_running("Test Page", ctr_computer) and
                process_not_running("Rename Printer", ctr_computer)
            ):
            close_dialog()
            id = gen_result_id()
            add_new_process(new_process("Uninstall Printer", [ctr_computer], date_time(), id))
            show_message(f"Uninstalling printer from {ctr_computer}.")
            
            result = powershell.uninstall_printer(computer=ctr_computer, printerName=ctr_printer)
            update_results("Uninstall Printer", result, id, ctr_computer)
            end_of_process(id)
            get_printers(e, refresh=True, target_computer=ctr_computer)
    
    def open_print_logs(e):
        type = e.control.data
        if check_computer_name() and process_not_running(f"{type} Log", computer_name.value):
            computer = computer_name.value
            enable_winrm(computer)
            id = gen_result_id()
            add_new_process(new_process(f"{type} Log", [computer], date_time(), id))
            show_message(f"Getting {type} print logs from {computer}.")
            
            result = powershell.print_logs(computer, type)
            update_results(title_text=f"{type} Log", data=result, id=id, computer=computer, print_log=True, type=type, subtitle=result)
            end_of_process(id)
    
    def open_c_share(e):
        if check_computer_name():
            computer = computer_name.value
            id = gen_result_id()
            add_new_process(new_process("C$ Share", [computer], date_time(), id))
            show_message(f"Opening c$ share for {computer}")
            
            result = powershell.open_c_share(computer)
            if result != 0:
                update_results(title_text="C$ Share", data=result, id=id, computer=computer, subtitle=f"Couldn't open C$ share on {computer}.")
            end_of_process(id)

    def open_event_log(e):
        if check_computer_name() and process_not_running("Event Viewer", computer_name.value):
            computer = computer_name.value
            id = gen_result_id()
            add_new_process(new_process("Event Viewer", [computer], date_time(), id))
            show_message(f"Opening event viewer for {computer}")
            
            result = powershell.event_viewer(computer)
            if result != 0:
                update_results(title_text="Event Viewer", data=f"Couldn't open event viewer on {computer}.", id=id, computer=computer, subtitle=f"Couldn't open event viewer on {computer}.")
            end_of_process(id)
    
    def open_restart_modal(e):

        use_list_checkbox = ft.Checkbox(label="Use list of PCs", value=False)
        shutdown_checkbox = ft.Checkbox(label="Shutdown only", value=False)
        
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
        
        def show_schedule_options(e):
            value = e.control.value
            time_button.visible = value
            date_button.visible = value
            page.update()
        
        time_button = ft.ElevatedButton(
            "Pick time",
            icon="schedule",
            on_click=lambda _: page.open(time_picker),
            visible=False
        )
        
        date_button = ft.ElevatedButton(
            "Pick date",
            icon="calendar_month",
            on_click=lambda _: page.open(date_picker),
            visible=False
        )
        
        schedule_checkbox = ft.Checkbox(
            label="Schedule it", 
            value=False,
            on_change=show_schedule_options
        )
        
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
        def finalize(e): # 
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
                close_dialog(e)
            else:
                # Schedule restart
                if shutdown_checkbox.value:
                    shutdown_only = True
                if schedule_checkbox.value:
                    if date_text.value == "" or time_text.value == "":
                        show_message("Date or Time was not specified.")
                        close_dialog(e)
                        return
                    try:
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
                        close_dialog(e)
                    except AttributeError:
                        close_dialog(e)
                        show_message("Picke a date and time")
                else:
                    doing_action = True
                    scheduled = schedule_checkbox.value
                    list = use_list_checkbox.value
                    date = datetime.datetime.now()
                    year = date.year
                    month = date.month
                    day = date.day
                    time = str(date).split()
                    time = time[1]
                    close_dialog(e)
        
        modal = DynamicModal(
            title=f"Shutdown/Restart",
            content=content,
            close_modal_func=close_dialog,
            nolistview=True,
            add_action=ft.TextButton("Shutdown/Restart", on_click=finalize)
        )
        
        page.open(modal.get_modal()) 
        page.update()
        
        while modal.modal.open:
            pass
        
        if list:
            computer = "list of computers"
        else:
            computer = computer_name.value
        
        if doing_action and shutdown_only == False:
            restart(scheduled, shutdown_only, computer, settings_values['enable_win_rm'], month=month, day=day, year=year, time=time)
        elif doing_action and shutdown_only:
            restart(scheduled, shutdown_only, computer, settings_values['enable_win_rm'], month=month, day=day, year=year, time=time)
    
    def restart(scheduled, shutdown, computer, winRM, **kwargs):
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
        
        if computer == "list of computers":
            use_list = True
        else:
            use_list = False
        
        id = gen_result_id()
        
        if use_list and check_list():
            add_new_process(new_process("Restart", [computer], date_time(), id))
            show_message(f"Restarting {computer}")
            result = powershell.restart(id, shutdown, scheduled, computer, month, day, year, hour, minute, seconds, settings_values['use_24hr'], winRM)
            update_results("Restart", result, id, computer=computer)
            end_of_process(id)
        if use_list != True:
            if check_computer_name() and process_not_running("Restart", computer_name.value):
                enable_winrm(computer)
                add_new_process(new_process("Restart", [computer], date_time(), id))
                show_message(f"Restarting {computer}")
                result = powershell.restart(id, shutdown, scheduled, computer, month, day, year, hour, minute, seconds, settings_values['use_24hr'], winRM)
                update_results("Restart", result, id, computer=computer)
                end_of_process(id) 
    
    def get_user_ids(e):
        if check_computer_name() and process_not_running("User IDs", computer_name.value):
            computer = computer_name.value
            show_message(f"Getting user IDs on {computer}")
            id = gen_result_id()
            
            enable_winrm(computer)
            add_new_process(new_process("User IDs", [computer], date_time(), id))
            result = powershell.get_user_ids(computer)
            update_results("User IDs", data=result, id=id, computer=computer, subtitle=result)
            end_of_process(id)
            
            if os.path.exists(f"assets/results/Users/{computer}-Users.json"):
                open_logoff_modal(computer)
    
    ping_btn = ft.TextButton(text="Ping", icon="network_ping", on_click=ping)
    quser_btn = ft.IconButton(
        icon="person",
        icon_size=20,
        tooltip="QUser",
        on_click=get_user_ids
    )

    def open_pc_list(e):
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
            nonlocal users
            nonlocal logout
            if delete_users_checkbox.value and settings_values['warn_about_profile_deletion']:
                
                answer = are_you_sure(
                    e, 
                    "Are you sure you want to remove profiles? Users could lose valuable data.",
                    no_text = "Don't remove profiles"
                )
                
                close_dialog()
                
                if answer == False:
                    users = "False"
                
                update_settings(e)
            
            if computer != "list of computers":
                enable_winrm(computer)
            # else skip winrm here, it will be done in script
            
            id = gen_result_id()
            
            # If we are using a list of pcs,
            # get each pc from list and create
            # an array of them.
            if computer == "list of computers":
                list_of_pcs = []
                list = open(computerlist_path, "r")
                computers = list.readlines()
                for pc in computers:
                    list_of_pcs.append(pc.strip("\\n"))
                add_new_process(new_process("Clear Space", list_of_pcs, date_time(), id))
                show_message(f"Clearing space on list of PCs.")
            
            if computer != "list of computers":
                add_new_process(new_process("Clear Space", [computer], date_time(), id))
                show_message(f"Clearing space on {computer}.")
                
            
            powershell.clear_space(computer=computer, users=users, logout=logout, winRM=settings_values['enable_win_rm'])
            
            if use_list_checkbox.value == True:
                for pc in list_of_pcs:
                    pc_result = open(f"assets/results/ClearSpace/{pc}-ClearSpace.txt", "r")
                    read_pc_result = pc_result.read()
                    update_results("Clear Space", read_pc_result, id, computer)
                    pc_result.close()
            else:
                results = open(f"assets/results/ClearSpace/{computer}-ClearSpace.txt", "r")
                result = results.read()
                update_results("Clear Space", result, id, computer)
            
            end_of_process(id)
        
        use_list = use_list_checkbox.value
        
        if use_list and check_list():
            run_operation("list of computers")
        if use_list != True:
            if check_computer_name() and process_not_running("Clear Space", computer_name.value):
                run_operation(computer_name.value)
    
    def launch_script(e):
        script = e.control.data
        if os.path.exists(script):
            ps_version = use_ps1.value
            
            powershell.launch_script(script, ps_version)
            show_message(f"Launching {script}.")
        else:
            show_message("The script path is no longer valid.")
    
    def remove_script(e):
        remove_me = e.control.data
        
        if are_you_sure(e, f"Remove {remove_me}?", yes_text="REMOVE", yes_color="red"):
            custom_scripts.pop(f"{remove_me}")
            update_settings(e)
            generate_scripts()
            close_dialog()
            show_message(f"Removed {remove_me}")
        else:
            close_dialog()
            
    
    list_of_script_cards = []
    scripts_column = ft.Column(list_of_script_cards, scroll="auto")
    
    def drag_script_will_accept(e):
        pass

    # Reorder scripts
    def drag_script_accept(e: ft.DragTargetAcceptEvent):
        print("drag_accept")
        
        # First collect info about dragged item and drop target
        script_info = e.control.data.items()
        for key, value in script_info:
            print(key, value)
            if key == "index":
                drag_target_index = value # Index of where we drop the item

        dragged_script = page.get_control(e.src_id)
        
            # Find the index of the dragged item
        for key, value in dragged_script.data.items():
            if key == "index":  
                dragged_index = value
        
            # If we dragged a dropped to the same place
        if drag_target_index == dragged_index:
            print("Same index")
            return
        
        # Now changed indices
        if dragged_script.data['name'] in custom_scripts:
            custom_scripts[dragged_script.data['name']]['index'] = drag_target_index
        if e.control.data['name'] in custom_scripts:
            custom_scripts[e.control.data['name']]['index'] = dragged_index
        update = update_scripts(e)
        if update:
            print("generate")
            generate_scripts()
        else:
            print("no generate")
            show_message("Failed to reorder scripts")
    
    def drag_script_leave(e):
        pass
    
    def description_edit(e):
        if e.control.value != e.control.data['description']:
            e.control.helper_text = "Press ENTER to save"
        else:
            e.control.helper_text = None
        e.control.update()
    
    def submit_script_description(e):
        script_name = e.control.data['name']
        script = custom_scripts[script_name]
        script.update({"description": f"{e.control.value}"})
        e.control.helper_text = None
        e.control.update()
        update_scripts(e)
        generate_scripts()
    
    def pin_script(e):
        script = e.control.data
        custom_scripts[script]['pinned'] = not custom_scripts[script]['pinned']
        generate_scripts()
        if custom_scripts[script]['pinned']:
            show_message(f"Pinned {script}")
        else:
            show_message(f"Unpinned {script}")
        update_scripts(e)

    def generate_scripts():
        nonlocal list_of_script_cards
        nonlocal scripts_column
        # This breaks if flet is updated to 0.24
        list_of_script_cards.clear()
        
        pinned_scripts = []
        
        def draggable_hover(e): # Store this function in the script_draggable variable
            e.control.bgcolor = ft.Colors.with_opacity(0.5, '#ffffff') if e.data == "true" else None
            e.control.update()
        
        def sort_scripts_by_index(dict): # Use this to sort scripts by index before appending to controls
            return dict.data['index']
        
        for script in custom_scripts:
            print(script)
            script_info = custom_scripts[script]
            # Check for existing script description
            try: 
                description = script_info["description"]
            except KeyError:
                description = ""
            
            feedback = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            name="description",
                        ),
                        ft.Text(f"{script}", size=12)
                    ]),
                    padding=10,
                    border=ft.border.all(1, settings_values['app_color']),
                    border_radius=10
                )
            )
            
            script_data = {"index": script_info['index'], "name": script, "description": description}
            
            script_draggable = ft.Draggable(
                group="scripts",
                content=ft.Container(
                    content=ft.Text(f"{script}", weight="bold"),
                    border=ft.border.all(1, settings_values['app_color']),
                    padding=ft.padding.only(5, 0, 5, 0),
                    on_hover=draggable_hover
                ),
                content_feedback=feedback,
                data=script_data
            )
            
            if script_info['pinned']:
                # Remove draggable component since it will be pinned
                script_draggable = ft.Container(
                    content=ft.Container(
                        content=ft.Text(f"{script}", weight="bold"),
                        border=ft.border.all(1, settings_values['app_color']),
                        padding=ft.padding.only(5, 0, 5, 0),
                        on_hover=draggable_hover
                    ),
                    data=script_data
                )
            
            if not os.path.exists(script_info['path']):
                script_draggable.content.content = ft.Row([
                    ft.Text(f"(Missing)", color="red"),
                    ft.Text(f"{script}", weight="bold")
                ])
            
            pin_icon = "push_pin_outlined"
            if script_info['pinned']:
                pin_icon = "push_pin"
            
            pin = ft.IconButton(
                pin_icon,
                data=f"{script}",
                on_click=pin_script,
                tooltip="Pin to top"
            )
            
            new_script_card = ft.Row([
                ft.Row([
                    ft.IconButton(
                        "PLAY_ARROW",
                        data=f"{script_info['path']}",
                        on_click=launch_script,
                        tooltip="Launch script"
                    ),
                    script_draggable,
                ]),
                ft.Row([
                    pin,
                    ft.IconButton(
                        "DELETE",
                        data=f"{script}",
                        on_click=remove_script,
                        tooltip="Remove script"
                    )
                ])
                
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            draggable = ft.Container(
                content=ft.Column([
                    new_script_card,
                    ft.Row([
                        ft.Text("Description:", weight="bold"),
                        ft.Container(
                            content=ft.TextField(
                                value=description,
                                on_change=description_edit,
                                on_submit=submit_script_description,
                                expand=True,
                                multiline=True,
                                shift_enter=True,
                                max_lines=3,
                                data={"index": script_info['index'], "name": script, "description": description}
                            ),
                            padding=ft.padding.only(0, 0, 20, 0),
                            expand=True
                        )
                    ])
                ]),
                border_radius=10,
                padding=10,
                data=script_data
            )
            
            script_card = ft.Container(
                content=ft.Card(
                    content=draggable
                )
            )
            
            drag_target=ft.Container(
                content=ft.DragTarget(
                    group="scripts",
                    content=script_card,
                    on_accept=drag_script_accept,
                    on_will_accept=drag_script_will_accept,
                    on_leave=drag_script_leave,
                    data=script_data
                ),
                data=script_data
            )
            
            if script_info['pinned']:
                drag_target=ft.Container(
                content=script_card,
                data=script_data
            )
            
            if script_info['pinned']:
                pinned_scripts.append(drag_target)
            else:
                list_of_script_cards.append(drag_target)
                
        list_of_script_cards.sort(key=sort_scripts_by_index)
        
        if len(pinned_scripts) > 0:
            pinned_scripts.sort(key=lambda s: s.data['name'].casefold(), reverse=True) #sort alphabetically
            for script in pinned_scripts: # Insert pinned scripts at start of list so they are always on top
                list_of_script_cards.insert(0, script)
        
        # Set padding so things look good
        for card in list_of_script_cards:
            if card == list_of_script_cards[0]:
                card.padding = ft.padding.only(5, 10, 5, 5)
            if card == list_of_script_cards[len(list_of_script_cards)-1]:
                card.padding = ft.padding.only(5, 5, 5, 10)
        
        no_scripts = ft.Container( # Show this if no scripts are added
            content=ft.Row([
                ft.Text("No scripts added yet", expand=True, text_align="center", color="black")
            ], expand=True),
            padding=ft.padding.only(0, 20, 0, 0)
        )
        
        if len(list_of_script_cards) <= 0:
            list_of_script_cards.append(no_scripts)
        scripts_column.controls = list_of_script_cards
        try:
            scripts_column.update()
        except AssertionError as e:
            # Control isn't added to page yet so ignore
            pass
    
    # Populate script controls on initial app load
    generate_scripts()
    
    def check_space(e):
        id = gen_result_id()
        use_list = use_list_checkbox.value
        if use_list and check_list():
            computer = "list of computers"
            add_new_process(new_process("Check Space", [computer], date_time(), id))
            show_message(f"Checking space on {computer}")
            
            result = powershell.check_space(computer=computer, id=id, winRM=settings_values['enable_win_rm'])
            update_results("Check Space", result, id=id, computer=computer, check_space=True, subtitle=result)
            end_of_process(id)
        if use_list != True:
            if check_computer_name() and process_not_running("Check Space", computer_name.value):
                computer = computer_name.value
                enable_winrm(computer)
                add_new_process(new_process("Check Space", [computer], date_time(), id))
                show_message(f"Checking space on {computer}")
                
                result = powershell.check_space(computer=computer, id=id, winRM=False)
                update_results("Check Space", result, id=id, computer=computer, check_space=True, subtitle=result)
                end_of_process(id)
    
    def check_software(e):
        date = date_time()
        date_formatted = date.replace(",", "_")
        date_formatted = date_formatted.replace(" ", "_")
        date_formatted = date_formatted.replace(":", "-")
        
        all = e.control.data
        
        id = gen_result_id()
        
        use_list = programs_use_list_checkbox.value
        if use_list and check_list():
            computer = "list of computers"
            add_new_process(new_process("Check Software", ['Using list'], date_time(), id))
            show_message(f"Checking software on list of PCs")
            result = powershell.check_software(computer=computer, software=software_textfield.value, id=id, all=all, winRM=settings_values['enable_win_rm'])
            data = f"assets/results/Programs/Programs-{id}.json"
            update_results("Check Software", data=data, id=id, computer=computer, subtitle=result)
            end_of_process(id)
        if use_list != True:
            if check_computer_name() and process_not_running("Check Software", computer_name.value):
                computer = computer_name.value
                enable_winrm(computer)
                add_new_process(new_process("Check Software", [computer], date_time(), id))
                show_message(f"Checking software on {computer}")
                data = f"assets/results/Programs/{computer}-Programs.json"
                result = powershell.check_software(computer=computer, software=software_textfield.value, id=id, all=all, winRM=settings_values['enable_win_rm'])
                update_results("Check Software", data=data, id=id, computer=computer, subtitle=result)
                end_of_process(id)
    
    def open_battery_report(e):
        html = e.control.data
        subprocess.call(["cmd.exe", "/c" f"{html}"])
    
    def open_battery_card(e):
        ctr_data = "None"
        ctr_computer = "None"
        for key, value in e.control.data.items():
            if key == "data":
                ctr_data = value
            if key == "computer":
                ctr_computer = value
        battery_json_path = ctr_data
        list_of_pcs = {}
        
        expansion_list = ft.ExpansionPanelList(
            elevation=8,
            controls=[]
        )
        
        # Append each battery result here as dict
        # so we can export it.
        list_of_results = []
        
        with open(battery_json_path, "r", encoding='utf-8') as file:
            data = json.load(file)
            
            # For each computer in data
            for r in data:
                # r is equal to computer name.
                # comp is equal to battery details.
                battery_details = data[r]
                
                for batt_detail in battery_details:

                    # First get PC and define an expansiontile for it
                    if r not in list_of_pcs:
                        exp_panel = ft.ExpansionPanel(
                                header=ft.ListTile(
                                    title=ft.Text(f"{r}", weight=ft.FontWeight.BOLD),
                                    trailing=ft.Icon(name="computer")
                                ),
                            content=ft.Row(wrap=True, spacing=10),
                            can_tap_header=True
                        )
                        
                        # Add dict key of pc name with value of expansiontile
                        list_of_pcs.update({f"{r}": exp_panel})
                    
                    # Then add battery info to corresponding PCs in the dict
                    if batt_detail == "BatteryReport":
                        new_control = ft.Container(
                            content=ft.Row([
                                ft.Text(f"{batt_detail}:", selectable=True, weight=ft.FontWeight.BOLD),
                                ft.TextButton(f"Open", data=battery_details[batt_detail], on_click=open_battery_report),
                            ]),
                            padding=ft.padding.only(left=10, right=10, bottom=10)
                        )
                    else:
                        new_control = ft.Container(
                            content=ft.Row([
                                ft.Text(f"{batt_detail}:", selectable=True, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{battery_details[batt_detail]}", selectable=True),
                            ]),
                            padding=ft.padding.only(left=10, right=10, bottom=10)
                        )
                        
                    list_of_pcs[f"{r}"].content.controls.append(new_control)
                
                details = {
                    "computer": f"{r}",
                    "batterystatus": f"{battery_details['BatteryStatus']}",
                    "Charge": f"{battery_details['Charge']}",
                    "efficiency": f"{battery_details['Efficiency']}",
                    "fullchargecapacity": f"{battery_details['FullChargeCapacity']}",
                    "designcapacity": f"{battery_details['DesignCapacity']}",
                    "batteryreport": f"{battery_details['BatteryReport']}"
                }
                    
                list_of_results.append(details)

        # Loop through expansionpanels in list and append them to expansion_list
        for pc in list_of_pcs:
            expansion_list.controls.append(list_of_pcs[f'{pc}'])
        
        # Format export data
        btn_data = {"columns": ['Computer', 'BatteryStatus', 'Charge', 'Efficiency', 'Full Charge Capacity', 'Design Capacity', 'Battery Report'], "results": list_of_results}
        
        modal = DynamicModal(
            title=f"{e.control.title.value}",
            content=ft.Container(
                    content=ft.Column(
                        controls=[
                        expansion_list,
                        ft.TextButton(
                            "Export csv", 
                            on_click=export_data, 
                            data=btn_data
                        )
                    ]),
                    width= 500
                ),
            close_modal_func=close_dialog
        )
        page.open(modal.get_modal())
        page.update()
    
    def check_battery(e):
        id = gen_result_id()
        
        use_list = are_you_sure(
            e, 
            text="Do you want to check the battery status for each computer in the list of computers?", 
            title="Use List of Computers?", 
            no_text="Use Computer Name", 
            yes_text="Use list"
        )
        
        if use_list and check_list():
            close_dialog()
            computer = "list of computers"
            add_new_process(new_process("Check Battery", [computer], date_time(), id))
            show_message(f"Checking battery on {computer}")
            result = powershell.check_battery(computer, id, settings_values['enable_win_rm'])
            update_results(
                    "Check Battery", 
                    data=f"assets/results/Battery/{id}-BatteryStatus.json", 
                    id=id,
                    computer=computer,
                    subtitle=result
                )
            end_of_process(id)

        if use_list != True and use_list != None:
            close_dialog()
            if check_computer_name() and process_not_running("Check Battery", computer_name.value):
                computer = computer_name.value
                enable_winrm(computer)
                add_new_process(new_process("Check Battery", [computer], date_time(), id))
                show_message(f"Checking battery on {computer}")
                result = powershell.check_battery(computer, id, settings_values['enable_win_rm'])
                if "failed" in result:
                    update_results(
                        "Check Battery", 
                        data=result, 
                        id=id,
                        computer=computer,
                        subtitle=result
                    )
                else:
                    update_results(
                        "Check Battery", 
                        data=f"assets/results/Battery/{id}-BatteryStatus.json", 
                        id=id, 
                        computer=computer,
                        subtitle=result
                    )
                end_of_process(id)
            
    def get_uptime(e):
        if check_computer_name() and process_not_running("Get Uptime", computer_name.value):
            id = gen_result_id()
            
            computer = computer_name.value
            enable_winrm(computer)
            add_new_process(new_process("Get Uptime", [computer], date_time(), id))
            show_message(f"Getting uptime for {computer}")
            result = powershell.get_uptime(computer)
            update_results("Get Uptime", data=result, id=id, computer=computer, subtitle=result)
            end_of_process(id)
    
    def msinfo_32(e):
        if check_computer_name() and process_not_running("MsInfo32", computer_name.value):
            id = gen_result_id()
            
            computer = computer_name.value
            enable_winrm(computer)
            add_new_process(new_process("MsInfo32", [computer], date_time(), id))
            show_message(f"Opening MsInfo32 for {computer}")
            result = powershell.msinfo_32(computer)
            update_results("MsInfo32", data=result, id=id, computer=computer, subtitle=result)
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

    def log_off_user(data):
        user_id = data['ID']
        computer = ['computer']
        name = data['name']
        
        if process_not_running("Log Off User", computer):
            id = gen_result_id()
            
            computer = computer_name.value
            add_new_process(new_process("Log Off User", [computer], date_time(), id))
            show_message(f"Logging off {name} on {computer}")
            result = powershell.log_off_user(computer, user_id, name)
            update_results("Log Off Users", data=result, id=id, computer=computer, subtitle=result)
            end_of_process(id)
            return True
        return False

    def open_logoff_modal(computer):
        
        with open(f"assets/results/Users/{computer}-Users.json", "r") as file:
            users = json.load(file)
        
        def clicked(e):
            # e.control.visible = False
            data = e.control.data
            page.update()
            if log_off_user(data):
                e.control.text = "logged out"
                e.control.update()
                e.control.on_click = (lambda _: print("Already logged off"))
            
        list_of_users = []
        for user in users:
            u = users[user]
            id = u['ID']
            
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
            close_modal_func=close_dialog
        )
        
        page.open(modal.get_modal())
        page.update()
        
        while modal.modal.open:
            pass
        
    # "Views". We swap these in and out of current_view
    # when navigating using the rail.
    computer_list_btn = ft.IconButton(
        icon="list",
        icon_size=20,
        on_click=open_pc_list,
        tooltip="Open list of PCs"
    )
    
    recent_computers_btn = ft.IconButton(
        icon="history",
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
                loading_ring,
                running_processes_icon
            ])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        running_processes_count_text,
    ])
    
    filter_btn = ft.IconButton(
        icon="FILTER_ALT_OFF",
        icon_size=13,
        tooltip="Off",
        on_click=filter_results,
    )
    
    def open_errors(e):
        try:
            with open(logging_path, "r") as file:
                errors = file.readlines()
                list_of_errors = []
                
                for err in errors:
                    
                    err_container = ft.Container(
                        content=ft.Row([
                            ft.Text(f"{err}", selectable=True)    
                        ], wrap=True),
                        padding=2,
                        border=ft.border.all(2, settings_values['app_color']),
                        width=500
                    )
                    
                    list_of_errors.append(err_container)
                
                if len(list_of_errors) < 1:
                    list_of_errors.append(ft.Text("No errors found"))
                
                data = {
                    "txt_document": True,
                    "txt_data": f"{logging_path}"
                }
                
                content_container = ft.Column([
                    ft.TextButton("Export", on_click=export_data, data=data),
                    ft.Column(
                        list_of_errors,
                        spacing=1,
                        scroll="auto"
                    )
                ], expand=True)
                
                modal = DynamicModal(
                    title=f"PowerShell Error Log",
                    content=content_container,
                    close_modal_func=close_dialog,
                    nolistview=False
                )
                
                page.open(modal.get_modal())
                page.update()
                
                while modal.modal.open:
                    pass
                
        except Exception as e:
            update_results("Error Logs", f"Error: {e}", gen_result_id(), app_result=True)
        
    clear_results_label = ft.Text("Clear Results:", weight=ft.FontWeight.BOLD)
    error_log = ft.TextButton("View errors", on_click=open_errors)
    
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
                    error_log,
                    clear_results_label,
                    ft.IconButton(
                        icon="close",
                        icon_size=13,
                        tooltip="Clear Results",
                        on_click=remove_results_card,
                        data="all"
                    ),
                ])
            ]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        results_container
    ], expand=True)
    
    # -------------------- SETTINGS --------------------
    def check_for_changes(e):
        """Re-enables the apply button for settings window.
        This function should only be triggered if a setting
        option was clicked or changed.

        Args:
            e (Flet control): Nothing happens with this arg
        """
        settings_save_btn.disabled = False
        settings_save_btn.update()
    
    # Settings color choice radio
    app_color_label = ft.Text("App appearance", weight="bold")
    red_color_radio = ft.Radio(value="red", label="Red", fill_color="red")
    blue_color_radio = ft.Radio(value="blue", label="Blue", fill_color="blue")
    green_color_radio = ft.Radio(value="green", label="Green", fill_color="green")
    purple_color_radio = ft.Radio(value="purple", label="Purple", fill_color="purple")
    yellow_color_radio = ft.Radio(value="yellow", label="Yellow", fill_color="yellow")
    white_color_radio = ft.Radio(value="white", label="White", fill_color="white")
    orange_color_radio = ft.Radio(value="orange", label="Orange", fill_color="orange")
    app_color_radio_group = ft.RadioGroup(
        content=ft.Column([
            red_color_radio,
            blue_color_radio,
            green_color_radio,
            purple_color_radio,
            yellow_color_radio,
            orange_color_radio,
            white_color_radio
        ]),
        value=settings_values['app_color'],
        on_change=check_for_changes
    )
    
    actions_settings_label = ft.Text("Actions", weight="bold")
    winrm_checkbox = ft.Checkbox("Enable WinRM before actions", value=settings_values['enable_win_rm'], on_change=check_for_changes)
    winrm_results_checkbox = ft.Checkbox("Supress WinRM results", value=settings_values['supress_winrm_results'], on_change=check_for_changes)
    use_24hr_checkbox = ft.Checkbox("Use 24hr time format", value=settings_values['use_24hr'], on_change=check_for_changes)
    warn_checkbox = ft.Checkbox("Warn before clearing profiles", value=settings_values['warn_about_profile_deletion'], on_change=check_for_changes)
    settings_save_btn = ft.FilledButton("Apply", tooltip="test", icon="save", on_click=update_settings, disabled=True)
    settings_about_app = TutorialBtn(["About IT Remote", text_values.settings_about_app_txt], on_click=open_tutorial_modal)
    
    theme_mode = ft.Switch(label="Dark Theme", value=settings_values['dark_theme'], on_change=check_for_changes)
    
    home_tab_radio_grp = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value=1, label="Results"),
            ft.Radio(value=2, label="Actions"),
            ft.Radio(value=3, label="My Scripts")
        ]),
        value = settings_values['home_tab'],
        on_change=check_for_changes
    )
    
    settings_view = ft.Column([
        
        ft.Row([
            
            ft.Container(
                content=ft.Column([
                    app_color_label,
                    ft.Row([
                        app_color_radio_group
                    ]),
                    ft.Row([
                        theme_mode
                    ]),
                ]),
                border=ft.border.only(right=ft.border.BorderSide(1, "grey")),
                padding=ft.padding.only(0, 0, 10, 0)
            ),

            ft.Container(
                content=ft.Column([
                    actions_settings_label,
                    winrm_checkbox,
                    winrm_results_checkbox,
                    use_24hr_checkbox,
                    warn_checkbox,
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Home Tab", weight="bold"),
                            home_tab_radio_grp
                        ]),
                        border=ft.border.only(top=ft.border.BorderSide(1, "grey")),
                        padding=ft.padding.only(0, 10, 10, 0)
                    )
                ]),
                border=ft.border.only(right=ft.border.BorderSide(1, "grey")),
                padding=ft.padding.only(0, 0, 10, 0)
            ),

            ft.Column([
                settings_about_app
            ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.END)
        ], expand=1),
        ft.Row([settings_save_btn], alignment=ft.MainAxisAlignment.END)
    ], expand=1)
    
    # -------------------- ACTIONS VIEWS --------------------
    # Actions tab Expansion List items
    check_space_btn =  ft.TextButton(
        text="Check Space", 
        icon="storage",
        on_click=check_space
    )
    
    clear_space_tut = TutorialBtn(
        data=[
            "About Clear Space", 
            text_values.clear_space_tut_txt
        ],
        on_click=open_tutorial_modal
    )
    
    clear_space_exp_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Disk Space", weight=ft.FontWeight.BOLD),
            trailing=ft.Icon(name="album")
        ),
        content=ft.Container(
            content=ft.Column([
                
                ft.Container(
                    content=ft.Row(
                        [use_list_checkbox],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, "grey")),
                ),
                
                ft.Row([
                    
                    # Column 1
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                delete_users_checkbox,
                                clear_space_tut
                            ]),
                            logout_users_checkbox,
                            ft.TextButton(text="Clear Disk Space", icon="delete_forever", on_click=clear_space),
                        ]),
                        border=ft.border.only(right=ft.border.BorderSide(1, "grey")),
                        padding=ft.padding.only(0,0,10,0)
                    ),
                    
                    # Column 2
                    ft.Container(
                        content=ft.Column([
                            check_space_btn
                        ], alignment=ft.MainAxisAlignment.END),
                        padding=ft.padding.only(0,0,5,0)
                    ),
                    
                ])
            ], alignment=ft.CrossAxisAlignment.END),
            padding=10
        ),
        can_tap_header=True,
    )
    
    printers_exp_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Printers", weight=ft.FontWeight.BOLD),
            trailing=ft.Icon(name="print")
        ),
        content=ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon="print", icon_size=50, on_click=get_printers, data=""),
                    ft.Text("Get Printers")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon="miscellaneous_services", icon_size=50, on_click=restart_print_spooler),
                    ft.Text("Restart Print Spooler")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon="text_snippet", data="Operational", icon_size=50, on_click=open_print_logs),
                    ft.Text("Operational Logs")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon="text_snippet", data="Admin", icon_size=50, on_click=open_print_logs),
                    ft.Text("Admin Logs")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            ], wrap=True),
            padding=10
        ),
        can_tap_header=True,
    )
    
    programs_tutorial = TutorialBtn(
        data=['About Programs', text_values.programs_tutorial_txt],
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
            trailing=ft.Icon(name="web_asset")
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

                            ft.TextButton(text="Check for ALL software", data="True", on_click=check_software)

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
            trailing=ft.Icon(name="settings_power")
        ),
        content=ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon="restart_alt", icon_size=50, on_click=open_restart_modal, data=""),
                    ft.Text("Shutdown/Restart")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            ], wrap=True),
            padding=10
        ),
        can_tap_header=True,
    )
    
    other_exp_panel = ft.ExpansionPanel(
        header=ft.ListTile(
            title=ft.Text("Other Tools", weight=ft.FontWeight.BOLD),
            trailing=ft.Icon(name="computer")
        ),
        content=ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.IconButton(icon="folder", icon_size=50, on_click=open_c_share, data=""),
                    ft.Text("C$ Share")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon="schedule", icon_size=50, on_click=get_uptime, data=""),
                    ft.Text("Get Uptime")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon="text_snippet", icon_size=50, on_click=open_event_log),
                    ft.Text("Event Viewer")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon="memory", icon_size=50, on_click=msinfo_32),
                    ft.Text("MSInfo32")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(icon="battery_3_bar", icon_size=50, on_click=check_battery),
                    ft.Text("Battery Status")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1)
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
        bgcolor=settings_values['app_color'],
        expand = 1,
        border_radius=10
    )
    
    actions_view = ft.Column([
        computer_top_row,
        actions_view_container
    ], expand=1)
    
    print_spooler_button = ft.TextButton(
        "Restart Print Spooler", 
        on_click=restart_print_spooler,
        data="print_wiz_view"
    )
    
    print_wizard_view = ft.Column([
        computer_top_row,
        ft.Divider(height=9, thickness=3),
        ft.Row([
            printer_wiz_computer_text,
            ft.IconButton(
                icon="refresh", 
                on_click=refresh_printers,
                tooltip="Refresh"
            ),
            print_spooler_button,
        ], wrap=True),
        printer_wiz_list_container,
    ], expand=True)
    
    # Filepicker for picking custom scripts
    def select_script(e: ft.FilePickerResultEvent):
        try:
            for file in e.files:
                
                # Figure out the index
                if file.name in custom_scripts:
                    index = custom_scripts[f'{file.name}']['index']
                elif len(custom_scripts) == 0:
                    index = 0
                else:
                    index = len(custom_scripts)
                
                custom_scripts.update({
                    f"{file.name}": {
                        "path": f"{file.path}",
                        "index": index,
                        "description": "",
                        "pinned": False
                    }
                })
            update_settings(e)
            generate_scripts()
        except TypeError as e:
            pass
        

    pick_script_dialog = ft.FilePicker(
        on_result=select_script,
    )

    page.overlay.append(pick_script_dialog) 
    
    scripts_list_view = ft.ListView([scripts_column], expand=True)
    custom_scripts_container = ft.Container(
        content=scripts_list_view,
        expand=True,
        bgcolor=settings_values['app_color'],
        border_radius=10,
        padding=ft.padding.only(10,0,10,0)
    )
    
    def script_search(e = None):
        if e != None:
            search_term = e.control.value.lower()
            search_term = search_term.split(' ') # Convert search to array of words
            if '' in search_term:
                search_term.remove('')
        else:
            search_term = None
            
        scripts_to_search = scripts_list_view.controls
        scripts_matching_search = len(scripts_to_search)
        if search_term != None and len(search_term) > 0 and len(list(custom_scripts)) > 0:
            scripts_matching_search = 0
            for control in scripts_to_search:
                script_name = control.data['name'].lower()
                script_description = control.data['description'].lower()
                # Find scripts with any of the words in search_term
                if len(search_term) > 1:
                    if any(term in script_name or term in script_description for term in search_term):
                        control.visible = True
                        scripts_matching_search += 1
                    else:
                        control.visible = False
                
                # Else If there's only 1 search term
                elif len(search_term) == 1:
                    if search_term[0] in script_name or search_term[0] in script_description:
                        control.visible = True
                        scripts_matching_search += 1
                    else:
                        control.visible = False
                    
                else:
                    for control in scripts_to_search:
                        control.visible = True
        else:
            for control in scripts_to_search:
                control.visible = True
        
        if scripts_matching_search <= 0 and e != None:
            for control in scripts_to_search:
                control.visible = True
            e.control.error_text = "No results"
        elif e != None and e.control.value == "":
            e.control.error_text = None
        
        page.update()
    
    def reset_script_search(e):
        script_search_field.value = None
        script_search_field.error_text = None
        script_search()
    
    cust_scripts_tutorial = TutorialBtn(
        data=["About Custom Scripts", text_values.cust_scripts_tutorial_txt],
        on_click=open_tutorial_modal
    )
    
    use_ps1 = ft.Switch(label="Use Powershell 7", value=True)
    script_search_field = ft.TextField(on_change=script_search, width=200, hint_text="Search scripts")
    custom_scripts_view = ft.Column([
        
        ft.Row([
            
            ft.Row([
                ft.IconButton(
                    icon="add",
                    tooltip="Add a script",
                    on_click=lambda _: pick_script_dialog.pick_files(
                        allow_multiple=True,
                        allowed_extensions=['ps1']
                    )
                ),
                ft.Container(
                    content=ft.Row([
                        script_search_field,
                        ft.IconButton("close", on_click=reset_script_search, tooltip="Clear search")
                    ])
                ),
            ]),
            
            ft.Row([
                use_ps1,
                cust_scripts_tutorial
            ])
            
        ], spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

        custom_scripts_container
            
    ], expand=True)
    
    # We assign different views to this in navigation
    current_view = ft.Row([home], expand=True)
    navigate_view(settings_values['home_tab']) #Set view to home tab saved in settings
    
    # Filepicker for picking paths
    def select_path(e: ft.FilePickerResultEvent):
        nonlocal page_view
        for file in e.files:
            if file.name == "pwsh.exe":
                powershell_path_text.value = f"{file.path}"
                settings_values['pwsh_path'] = f"{file.path}"
                powershell_checkmark.visible = True
            elif file.name == "PsExec.exe" or file.name == "PsService.exe": 
                pstools_path_text.value = f"{file.path}"
                settings_values['pstools_path'] = f"{file.path}"
                pstools_checkmark.visible = True
            else:
                show_message("Invalid program.")
        update_settings(e)
        if powershell_checkmark.visible and pstools_checkmark.visible:
            page.controls = [drag_window, main_view]
            show_message("Setup complete.")
        page.update()

    pick_path_dialog = ft.FilePicker(
        on_result=select_path,
    )

    page.overlay.append(pick_path_dialog)
    
    powershell_path_text = ft.Text()
    powershell_checkmark = ft.Icon(name="check", visible=False)
    pstools_path_text = ft.Text()
    pstools_checkmark = ft.Icon(name="check", visible=False)
    
    # This is the "main" view for when we have passed setup
    main_view = ft.Container(
        content=ft.Row([
            ft.Container(
                content=rail,
                border=ft.border.only(right=ft.border.BorderSide(1, "grey")),
                width=80
            ),
            current_view
        ], expand=True),
        padding=ft.padding.only(left=5, bottom=10, right=10, top=0),
        expand=True
    )
    
    def has_admin():
        try:
            is_admin = os.getuid() == 0
            return is_admin
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            return is_admin
    
    setup_view = ft.Container(
        content=ft.Column([
            ft.Text(text_values.setup_pstools),
            ft.Text("Click browse to select the respective executables in their install location."),
            ft.TextButton("Browse", on_click=lambda _: pick_path_dialog.pick_files(
                allow_multiple=False,
                allowed_extensions=['exe'],
                initial_directory="C:\\"
            )),
            ft.Row([
                ft.Text("pwsh.exe: ", weight=ft.FontWeight.BOLD),
                powershell_path_text,
                powershell_checkmark
            ]),
            ft.Row([
                ft.Text("PsExec.exe\\PsService.exe: ", weight=ft.FontWeight.BOLD),
                pstools_path_text,
                pstools_checkmark
            ])
        ]),
        padding=ft.padding.only(top=10, left=10, bottom=10, right=10)
    )
    
    page_view = setup_view
    
    if not has_admin() == True:
        update_results("No Admin", "Please re-run this app as admin.", gen_result_id, "localhost")
        print("No admin detected")
    else:
        print("Admin detected")

    
    # Check if paths to tools are valid, if so show main program view
    if os.path.exists(f"{settings_values['pwsh_path']}") and os.path.exists(f"{settings_values['pstools_path']}"):
        # Main Program page view
        print("Valid PsTools")
        page_view = main_view
        page.update()
    
    #Finally build the page
    page.add(
        drag_window,
        page_view
    )

ft.app(target=main, assets_dir="assets")