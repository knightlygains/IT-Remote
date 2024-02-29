import flet as ft
import the_shell
import datetime

font_size = 16
def main(page: ft.Page):
    
    def set_font_size(e):
        global font_size
        font_size = int(e.control.value)
        computer_name.text_size = font_size
        settings_text.size = font_size
        settings_icon.icon_size = font_size
        delprof_text.size = font_size
        delprof_icon.icon_size = font_size
        printers_text.size = font_size
        printers_icon.icon_size = font_size
        programs_text.size = font_size
        programs_icon.icon_size = font_size
        commands_text.size = font_size
        commands_icon.icon_size = font_size
        console_output.size = font_size
        font_size_text.size = font_size
        font_size_num_txt.size = font_size
        font_size_num_txt.text = font_size
        page.update()
    
    page.window_width = 630
    page.window_height = 630
    
    # Left tab Pane
    settings_icon = ft.IconButton(icon=ft.icons.SETTINGS, on_click=lambda _: page.go("/settings"))
    settings_text = ft.Text("Settings", size=font_size)
    delprof_icon = ft.IconButton(icon=ft.icons.DELETE, on_click=lambda _: page.go("/delprof"))
    delprof_text = ft.Text("DelProf", size=font_size)
    printers_icon = ft.IconButton(icon=ft.icons.PRINT, on_click=lambda _: page.go("/printers"))
    printers_text = ft.Text("Printers", size=font_size)
    programs_icon = ft.IconButton(icon=ft.icons.SAVE, on_click=lambda _: page.go("/programs"),)
    programs_text = ft.Text("Programs", size=font_size)
    commands_icon = ft.IconButton(icon=ft.icons.COMPUTER, on_click=lambda _: page.go("/commands"))
    commands_text = ft.Text("Commands", size=font_size)
    
    left_tab_pane = ft.Container(
        content=ft.Column(controls=[
            settings_icon,
            settings_text,
            delprof_icon,
            delprof_text,
            printers_icon,
            printers_text,
            programs_icon,
            programs_text,
            commands_icon,
            commands_text,
        ])
    )
    
    # Console text output
    console_output = ft.Text("", width=500, height=500, overflow=True, selectable=True, size=font_size)
    
    # Computer Text Field
    computer_name = ft.TextField(label="Computer Name")
    
    def date_time():
        x = datetime.datetime.now()
        x = x.strftime("%c")
        return x
    
    def update_console(data):
        console_output.value = f"\n[{date_time()}]: {data}" + f"\n{console_output.value}"
        page.update()
    
    def ping(e):
        if computer_name.value == "":
            update_console("Please input a computer hostname")
        else:
            powershell = the_shell.Power_Shell()
            result = powershell.ping(computer=computer_name.value)
            update_console(result)
    
    def quser(e):
        if computer_name.value == "":
            update_console("Please input a computer hostname")
        else:
            powershell = the_shell.Power_Shell()
            result = powershell.quser(computer=computer_name.value)
            update_console(result)


    ping_btn = ft.FilledButton(text="Ping", on_click=ping)
    quser_btn = ft.IconButton(
                                icon=ft.icons.PERSON,
                                icon_color="blue400",
                                icon_size=20,
                                tooltip="QUser",
                                on_click=quser
                            )
    font_size_text = ft.Text("Font Size:")
    font_size_num_txt = ft.Text(f"{font_size}")
    def route_change(route):
        
        
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    # Initial row containing all children
                    ft.Row([
                        
                        # Left pane tab options
                        ft.Column(controls=[left_tab_pane]),
                        
                        # Column containing Main View
                        ft.Column(controls=[
                            ft.Row([
                                ft.Column(controls=[computer_name]),
                                ft.Column(controls=[ping_btn]),
                                ft.Column(controls=[quser_btn])
                                ]
                            ),
                            # Text Output (Console)
                            ft.Row([
                                ft.Container(
                                content=console_output,
                                bgcolor=ft.colors.BLUE,
                                padding=5,
                                )
                            ])
                        ])
                    ])
                ],
            )
        )
        
        if page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    [
                        ft.AppBar(title=ft.Text("Settings"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
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
                            
                        )
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
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
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