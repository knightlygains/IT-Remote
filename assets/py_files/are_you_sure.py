import flet as ft

class YouSure(ft.AlertDialog):
    def __init__(self, text, title, close_modal_func, **kwargs):
        super().__init__()
        self.said_yes = None
        self.modal_not_dismissed = True
        self.no_text = "Cancel"
        self.yes_text = "Yes"
        self.yes_color = None
        self.no_color = None
        
        for key, value in kwargs.items():
            if key == "no_text":
                self.no_text = value
            if key == "yes_text":
                self.yes_text = value
            if key == "yes_color":
                self.yes_color = value
            if key == "no_color":
                self.no_color = value
        
        def yes(e = None):
            self.said_yes = True
            
        
        def no(e = None):
            self.said_yes = False

        
        self.modal = ft.AlertDialog(
            modal=False,
            title=ft.Text(f"{title}"),
            content=ft.Column([
                    ft.Text(f"{text}")
                ], height=100, width=300),
            actions=[
                ft.Container(
                    content=ft.Text(f"{self.yes_text}"),
                    on_click=yes,
                    bgcolor=self.yes_color,
                    padding=10,
                    border_radius=15
                ),
                ft.Container(
                    content=ft.Text(f"{self.no_text}"),
                    on_click=no,
                    bgcolor=self.no_color,
                    padding=10,
                    border_radius=15
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def get_modal(self):
        return self.modal
    