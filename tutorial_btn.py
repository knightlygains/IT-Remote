from flet import IconButton, icons

class TutorialBtn(IconButton):
    def __init__(self, data, on_click):
        super().__init__(
            tooltip = "Help",
            icon = icons.HELP,
            data = data,
            on_click = on_click
        )
        
        