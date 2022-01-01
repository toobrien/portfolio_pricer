from dash_core_components import Dropdown, Slider, Textarea
from dash_html_components import Br, Button, Div, P, Table, Td, Tr

class view():

    
    def __init__(self):

        ROWS = 10
        UL_COLS = 20
        LEG_COLS = 20
        VARS_COLS = 40

        # text controls

        underlyings_control_cell = Td(
            id = "underlyings_control_cell",
            children = [
                Textarea(
                    id = "underlyings_control_text",
                    rows = ROWS,
                    cols = UL_COLS
                ),
                Br(),
                Button(
                    id = "underlyings_control_submit",
                    children = "submit"
                )
            ],
            style = {
                "text-align": "left"
            }
        )

        legs_control_cell = Td(
            id = "legs_control_cell",
            children = [
                Textarea(
                    id = "legs_text",
                    rows = ROWS,
                    cols = LEG_COLS
                ),
                Br(),
                Button(
                    id = "legs_submit",
                    children = "submit"
                )
            ],
            style = {
                "text-align": "middle"
            }
        )
        
        variables_control_cell = Td(
            id = "variables_control_cell",
            children = [
                Textarea(
                    id = "variables_text",
                    rows = ROWS,
                    cols = VARS_COLS
                ),
                Br(),
                Button(
                    id = "variables_submit",
                    children = "submit"
                )
            ],
            style = {
                "text-align": "right"
            }
        )

        controls_row = Tr(
            id = "controls_row",
            children = [ 
                underlyings_control_cell,
                legs_control_cell,
                variables_control_cell
            ]
        )

        # sliders

        time_slider_cell = Td(
            id = "time_slider_cell",
            colSpan = 2,
            children = [
                Div(
                    id = "time_slider_view",
                    children = [
                        P(
                            id = "time_label",
                            children = [
                                f"time: 0"
                            ]
                        ),
                        Slider(
                            id = "time_slider",
                            min = 0,
                            max = 252,
                            step = 1,
                            value = 0,
                            updatemode = "drag"
                        )
                    ]
                )
            ]
        )

        mode_cell = Td(
            id = "mode_cell",
            children = [
                P(
                    id = "mode_label",
                    children = [
                        "mode"
                    ]
                ),
                Dropdown(
                    id = "mode_dropdown",
                    options = [
                        {
                            "label": "pnl", "value": "pnl"
                        },
                        {
                            "label": "value", "value": "value"
                        }
                    ],
                    value = "value"
                )
            ]
        )

        sliders_row = Tr(
            id = "sliders_row",
            children = [
                time_slider_cell,
                mode_cell
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
                sliders_row,
                underlyings_data_row,
                controls_row ,
                Div(
                    id = "NULL",
                    children = []
                )
            ]
        )


    def get_layout(self): return self.layout