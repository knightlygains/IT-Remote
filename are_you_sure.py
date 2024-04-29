import flet as ft

class YouSure(ft.AlertDialog):
    def __init__(self, text, close_modal_func):
        super().__init__()
        self._title = "Confirm:"
        self.said_yes = False
        self.modal_not_dismissed = True
        
        def yes(e):
            self.said_yes = True
            print(self.said_yes)
        
        self.modal = ft.AlertDialog(
            modal=False,
            title=ft.Text("Confirm:"),
            content=ft.Column([
                    ft.Row([
                        ft.Text(f"{text}")
                    ])
                ], height=100),
            actions=[
                ft.TextButton("Yes", on_click=yes),
                ft.TextButton("Cancel", on_click=close_modal_func),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def get_modal(self):
        return self.modal
    