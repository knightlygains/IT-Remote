import flet as ft

class YouSure(ft.AlertDialog):
    def __init__(self, text, title, close_modal_func, **kwargs):
        super().__init__()
        self.said_yes = False
        self.modal_not_dismissed = True
        self.no_text = "Cancel"
        self.yes_text = "Yes"
        
        for key, value in kwargs.items():
            if key == "no_text":
                self.no_text = value
            if key == "yes_text":
                self.yes_text = value
        
        def yes(e):
            self.said_yes = True
            print(self.said_yes)
        
        self.modal = ft.AlertDialog(
            modal=False,
            title=ft.Text(f"{title}"),
            content=ft.Column([
                    ft.Text(f"{text}")
                ], height=100, width=300),
            actions=[
                ft.TextButton(f"{self.yes_text}", on_click=yes),
                ft.TextButton(f"{self.no_text}", on_click=close_modal_func),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def get_modal(self):
        return self.modal
    