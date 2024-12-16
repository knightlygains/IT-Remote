from flet import IconButton, icons

class TutorialBtn(IconButton):
    def __init__(self, data, on_click):
        """An icon button with preset attributes. Used to launch a DynamicModal with
        a tutorial on how to use an app's function.

        Args:
            data (string): Pass a string for title and another string for tutorial description.
            on_click (funciton): pass a funciton to open an alert dialog
        """

        super().__init__(
            tooltip=data[0],
            icon = "help",
            data = data,
            on_click = on_click
        )