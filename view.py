from dash_core_components import Slider, Textarea
from dash_html_components import Br, Button, Div, Table, Td, Tr

class view():

    
    def __init__(self):

        ROWS = 10
        COLS = 30

        # controls

        underlyings_control_cell = Td(
            id = "underlyings_control_cell",
            children = [
                Textarea(
                    id = "underlyings_control_text",
                    rows = ROWS,
                    cols = COLS
                ),
                Br(),
                Button(
                    id = "underlyings_control_submit",
                    children = "submit"
                )
            ]
        )

        legs_control_cell = Td(
            id = "legs_control_cell",
            children = [
                Textarea(
                    id = "legs_text",
                    rows = ROWS,
                    cols = COLS
                ),
                Br(),
                Button(
                    id = "legs_submit",
                    children = "submit"
                )
            ]
        )
        
        variables_control_cell = Td(
            id = "variables_control_cell",
            children = [
                Textarea(
                    id = "variables_text",
                    rows = ROWS,
                    cols = COLS
                ),
                Br(),
                Button(
                    id = "variables_submit",
                    children = "submit"
                )
            ]
        )

        controls_row = Tr(
            id = "controls_row",
            children = [ 
                underlyings_control_cell,
                legs_control_cell,
                variables_control_cell
            ]
        )

        # underlyings_data_cell

        underlyings_data_cell = Td(
            id = "underlyings_data_cell",
            colSpan = 3,
            children = [
                Div(
                    id = "underlyings_data",
                    children = []
                )
            ]
        )

        underlyings_data_row = Tr(
            id = "underlyings_data_row",
            children = [ underlyings_data_cell ]
        )

        # payoffs

        payoff_cell = Td(
            id = "chart_cell",
            colSpan = 3,
            children = [
                Div(
                    id = "payoff_chart_view",
                    children = []
                )
            ]
        )

        payoff_row = Tr(
            id = "payoff_row",
            children = [ payoff_cell ]
        )

        self.layout = Table(
            id = "app_view",
            children = [
                payoff_row,
                underlyings_data_row,
                controls_row ,
                Div(
                    id = "NULL",
                    children = []
                )
            ]
        )


    def get_layout(self): return self.layout