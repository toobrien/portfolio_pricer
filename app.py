from dash import Dash
from dash_core_components import Graph, Slider
from dash_html_components import Div, P, Table, Td, Tr
from dash.dependencies import Input, Output, State
from ib.ib import ib
from json import loads
from model import model
from parsers import parse_ul_def, parse_legs
from payoff import get_payoff_graph
from typing import List, Tuple
from view import view


# GLOBALS

app = Dash(__name__, title = "payoff_2")
app.layout = view().get_layout()

MAX_EXPIRIES = 6
DEBUG = False


# FUNCTIONS

def debug(dash_decorator):

    def decorator(func):

        if DEBUG: return func
        else:     return dash_decorator(func)

    return decorator


@debug(
    app.callback(
        Output("underlyings_data", "children"),
        Input("underlyings_control_submit", "n_clicks"),
        State("underlyings_control_text", "value"),
        prevent_initial_call = True
    )
)
def set_underlyings_data(_, txt: str) -> List[Table]:

    ul_defs = txt.split("\n")
    uls = []
    rows = []
    i = 0

    # get underlyings

    for ul_def in ul_defs:

        args = parse_ul_def(ul_def, config)
        uls.extend(ib_client.underlying(**args))

    # prepare one line for each underlying:
    #  - symbol
    #  - price
    #  - expirations
    #  - strikes
    #  - trading classes

    for ul in uls:

        contract = ul.get_contract()
        option_chains = ul.get_option_chains()
        
        if len(option_chains) == 0:

            i += 1
            continue

        symbol = contract.localSymbol
        price = ul.get_price()
        expiries = []
        strikes = []
        trading_classes = []

        for j in range(len(option_chains)):

            trading_classes.append(f"{j}:{option_chains[j].get_trading_class()}")

        # assume expiries valid for all classes, format and label expiries
        
            expiries.extend(option_chains[0].get_expiries()[:MAX_EXPIRIES])

        for j in range(len(expiries)):

            exp = expiries[j]
            expiries[j] = f"{j}:{str(exp)[4:6]}/{str(exp[6:8])}"    

        # take first, last, and middle strikes (or "-1" if ul price not available)

        strikes.append(option_chains[0].get_strikes()[0])
        if      price: strikes.extend(option_chains[0].get_atm_strikes(1, price))
        else:   strikes.extend([-1, -1])
        strikes.append(option_chains[0].get_strikes()[-1])
        
        strikes = [ str(strike) for strike in strikes ]

        # append this underlying's row to data table
        
        label_cell = Td(
            f"{i}:",
            className = "ul_cell"
        )
        symbol_cell = Td(
            f"{symbol}",
            className = "ul_cell"
        )
        price_cell = Td(
            f"{price}",
            className = "ul_cell"
        )
        expiries_cell = Td(
            f"{'  '.join(expiries)}",
            className = "ul_cell"
        )
        strikes_cell = Td(
            f"{strikes[0]} ... {', '.join(strikes[1:3])} ... {strikes[3]}",
            className = "ul_cell"
        )
        trading_classes_cell = Td(
            f"{'  '.join(trading_classes)}",
            className = "ul_cell"
        )

        rows.append(
            Tr(
                [
                    label_cell,
                    symbol_cell,
                    price_cell,
                    expiries_cell,
                    strikes_cell,
                    trading_classes_cell
                ],
                className = "ul_row"
            )
        )

        i += 1

    res = Table(
        id = "underlyings_data_table",
        children = rows,
        className = "ul_table"
    )

    model_.set_underlyings(uls)

    return [ res ]


@debug(
    app.callback(
        Output("variables_text", "value"),
        Output("time_slider_view", "children"),
        Input("legs_submit", "n_clicks"),
        State("legs_text", "value"),
        prevent_initial_call = True
    )
)
def set_legs(_, legs_text: str) -> Tuple[str, List[Div]]:

    legs = parse_legs(legs_text)
    model_.set_legs(legs)
    model_.initialize_variables()

    variables = model_.get_variables()
    time = variables["time"]

    time_slider_view = Div(
        id = "time_slider_view",
        children = [
            P(
                id = "time_label",
                children = [
                    f"time ({time})"
                ]
            ),
            Slider(
                id = "time_slider",
                min = 0,
                max = time,
                step = 1,
                value = time,
                updatemode = "drag"
            )
        ]
    )

    return model_.get_variables_text(), [ time_slider_view ]


@debug(
    app.callback(
        Output("payoff_chart_view", "children"),
        Output("time_label", "children"),
        Input("variables_submit", "n_clicks"),
        Input("mode_dropdown", "value"),
        Input("time_slider", "value"),
        State("variables_text", "value"),
        prevent_initial_call = True
    )
)
def set_variables_and_payoff_graph(
    _, 
    mode: str,
    time: int,
    variables_text: str,
) -> Tuple[List[Graph], List[str]]:

    model_.set_variables_from_text(variables_text)
    model_.set_time(time)

    legs = model_.get_legs_by_index()
    variables = model_.get_variables()

    payoff_graph = [ 
        get_payoff_graph(
            "payoff_chart",
            legs,
            variables,
            mode
        )
    ]
    time_label = [ f"time: {variables['time']}" ]

    return payoff_graph, time_label


# MAIN

if __name__ == "__main__":

    with open("./config.json") as fd:

        config = loads(fd.read())
        
        ib_client = ib(
            host = config["ib_host"],
            port = config["ib_port"],
            id_ = config["ib_client_id"]
        )

        ib_client.set_mkt_data_type(4)

        model_ = model()

        # TEST
        
        if DEBUG:

            set_underlyings_data(
                None,
                "\n".join(
                    [
                        "TSLA",
                        "NG:3"
                    ]
                )
            )

            variables_text = set_legs(
                None,
                "\n".join(
                    [
                        "0:3:0:-1 C1110",
                        "0:3:0:+1 C1100",
                        "0:3:0:-1 P1000",
                        "0:3:0:+1 P990"
                    ]
                )
            )

            set_variables_and_payoff_graph(None, variables_text)

        if not DEBUG:

            app.run_server(
                host = config["dash_host"],
                port = config["dash_port"], 
                debug = False,
                dev_tools_hot_reload = False
            )