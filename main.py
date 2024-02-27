import flet as ft

def main(page):
    
    # Left tab Pane
    left_tab_pane = ft.Container(
        content=ft.Column(controls=[
            ft.Text("Item1"),
            ft.Text("Item2"),
            ft.Text("Item3"),
            ft.Text("Item4"),
        ])
    )
    
    # Console text output
    console_output = ft.Text("Results", width=500, height=500)
    
    page.add(
        # Initial row containing all children
        ft.Row([
            
            # Left pane tab options
            ft.Column(controls=[left_tab_pane]),
            
            # Column containing Main View
            ft.Column(controls=[
                ft.Row([
                    ft.Column(controls=[ft.TextField(label="Computer Name")]),
                    ft.Column(controls=[ft.FilledButton(text="Ping")]),
                    ft.Column(controls=[ft.IconButton(
                            icon=ft.icons.PERSON,
                            icon_color="blue400",
                            icon_size=20,
                            tooltip="QUser",
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
        
        
    )

ft.app(target=main)