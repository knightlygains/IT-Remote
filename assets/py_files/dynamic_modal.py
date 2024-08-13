import flet as ft

class DynamicModal(ft.AlertDialog):
    """
    Call get_modal() to return the actual AlertDialog.
    title: Text to show for title.
    content: Parent control, usually a row or column that contains the card content.
    close_modal_func: Pass the function to close the modal.
    """
    def __init__(self, title, content, close_modal_func, **kwargs):
        super().__init__()
        # Create a list view
        self.list_view = ft.ListView(expand=1, width=500, spacing=5)
        
        # Make a new container that holds content arugments
        self.content_container=ft.Container(
            content=content,
            padding=15,
            width=500
        )
        
        self.title = title
        
        self.actions = [
            ft.TextButton("Close", on_click=close_modal_func)
        ]
        
        self.content = self.list_view
        self.list_view.controls.append(self.content_container)
        
        for key, value in kwargs.items():
            if key == "nolistview" and value == True:
                self.content = self.content_container
            if key == "add_action":
                self.actions.insert(0, value)
            if key == "width":
                self.content_container.width = value
        
        self.modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.title),
            content=self.content,
            actions=self.actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
    def get_modal(self):
        return self.modal
    
        