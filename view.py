from dash_core_components import Slider, Textarea
from dash_html_components import Button, Div, Table, Td, Tr

class view():

    
    def __init__(self):

        ROWS = 10
        COLS = 30

        control_cell = Td(
            id = "control_cell",
            children = [
                Textarea(
                    id = "underlyings_text",
                    rows = ROWS,
                    cols = COLS
                ),
                Button(
                    id = "underlyings_submit"
                ),
                Textarea(
                    id = "legs_text",
                    rows = ROWS,
                    cols = COLS
                ),
                Button(
                    id = "legs_submit"
                ),
                Textarea(
                    id = "variables_text",
                    rows = ROWS,
                    cols = COLS
                ),
                Button(
                    id = "variables_submit"
                )
            ]
        )

        underlyings_cell = Td(
            id = "underlyings_cell"
        )

        chart_cell = Td(
            id = "chart_cell"
        )

        main_row = Tr(
            id = "main_row",
            children = [
                control_cell,
                underlyings_cell,
                chart_cell
            ]
        )
        
        self.layout = Table(
            id = "app_view",
            children = [ main_row ]
        )

    
    def get_layout(self): return self.layout