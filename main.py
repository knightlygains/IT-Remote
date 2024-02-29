import flet as ft
import the_shell
import datetime

def main(page: ft.Page):
    
    page.window_width = 630
    page.window_height = 630
    
    # Left tab Pane
    left_tab_pane = ft.Container(
        content=ft.Column(controls=[
            ft.IconButton(icon=ft.icons.SETTINGS, on_click=lambda _: page.go("/settings")),
            ft.Text("Settings"),
            ft.IconButton(icon=ft.icons.DELETE, on_click=lambda _: page.go("/delprof")),
            ft.Text("DelProf"),
            ft.IconButton(icon=ft.icons.PRINT, on_click=lambda _: page.go("/printers")),
            ft.Text("Printers"),
            ft.IconButton(icon=ft.icons.SAVE, on_click=lambda _: page.go("/programs")),
            ft.Text("Programs"),
            ft.IconButton(icon=ft.icons.COMPUTER, on_click=lambda _: page.go("/commands")),
            ft.Text("Commands"),
        ])
    )
    
    # Console text output
    console_output = ft.Text("", width=500, height=500, overflow=True, selectable=True)
    
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
                                ft.Column(controls=[ft.FilledButton(text="Ping", on_click=ping)]),
                                ft.Column(controls=[ft.IconButton(
                                        icon=ft.icons.PERSON,
                                        icon_color="blue400",
                                        icon_size=20,
                                        tooltip="QUser",
                                        on_click=quser
                                    )])
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