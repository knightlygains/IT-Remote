import flet as ft

class DynamicModal(ft.AlertDialog):
    """
    Call get_modal() to return the actual AlertDialog.
    title: Text to show for title.
    content: Parent control, usually a row or column that contains the card content.
    close_modal_func: Pass the function to close the modal.
    """
    def __init__(self, title, content, close_modal_func):
        super().__init__()
        # Create a list view
        self.list_view = ft.ListView(expand=1, width= 500, spacing=5)
        
        # Make a new container that holds content arugments
        self.content_container=ft.Container(
            content=content,
            padding=15,
            expand=1
        )
        
        # append the content_container to the list view
        self.list_view.controls.append(self.content_container)
        
        # Put list view inside a container
        self.modal_content = ft.Container(
            content=self.list_view,
            padding=15
        )
        
        self.modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"{title}"),
            content=self.modal_content,
            actions=[
                ft.TextButton("Close", on_click=close_modal_func),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
    def get_modal(self):
        return self.modal
    
        