from flet import IconButton, icons

class TutorialBtn(IconButton):
    def __init__(self, data, on_click):
        """_summary_

        Args:
            data (string): Pass a string for title and another string for tutorial description.
            on_click (funciton): pass a funciton to open an alert dialog
        """

        super().__init__(
            tooltip=data[0],
            icon = icons.HELP,
            data = data,
            on_click = on_click
        )
        
        