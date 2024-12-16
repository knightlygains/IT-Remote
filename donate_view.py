import flet as ft

def on_donate_hover(e):
        e.control.bgcolor = "grey" if e.data == "true" else None
        e.control.content.controls[1].color = "black" if e.data == "true" else "white"
        e.control.border_radius = 10 if e.data =="true" else 0
        e.control.update()
    
def on_github_hover(e):
    e.control.bgcolor = "white" if e.data == "true" else None
    e.control.border_radius = 50 if e.data =="true" else 0
    e.control.update()

donate_view = ft.Column([
    ft.Row([
        ft.Column([
            ft.Text("Created by:", size=40),
        ]),
        ft.Column([
            ft.Stack([
                ft.Image(
                    src="https://avatars.githubusercontent.com/u/56776962?v=4",
                    border_radius=60,
                    width=210
                ),
                ft.Container(
                    content=ft.Image(src="images/Github.png", width=70),
                    url="https://github.com/knightlygains/it-remote",
                    offset=ft.transform.Offset(2, 2),
                    on_hover=on_github_hover,
                    tooltip="https://github.com/knightlygains"
                )
            ]),
            ft.Text("Steven Whitney (KnightlyGains)", weight=ft.FontWeight.BOLD)
        ]),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
    ft.Divider(),
    ft.Row([
        ft.Text("If you like this app and would like to support me, please consider donating:"),
    ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
    ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Image(src="images/ko-fi.png", width=70),
                ft.Text("Ko-Fi", weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.margin.only(top=20),
            url="https://ko-fi.com/knightlygains",
            on_hover=on_donate_hover,
            padding=10
        ),
        ft.Container(
            content=ft.Column([
                ft.Image(src="images/patreon.png", width=70),
                ft.Text("Patreon", weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.margin.only(top=20),
            url="https://www.patreon.com/KnightlyGains",
            on_hover=on_donate_hover,
            padding=10
        )
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=30)
], expand=1)