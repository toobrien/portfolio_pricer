from dash import Dash
from dash_html_components import P
from dash.dependencies import Input, Output, State
from ib.ib import ib
from json import loads
from parsers import parse_ul_def
from view import view


# GLOBALS


app = Dash(__name__)
app.layout = view().get_layout()
MAX_EXPIRIES = 5


# FUNCTIONS

'''
@app.callback(
    Output("underlyings_data", "value"),
    Input("underlyings_control_submit", "n_clicks"),
    State("underlyings_control_text", "value")
)
'''
def set_underlyings_data(_, txt: str) -> P:

    ul_defs = txt.split("\n")
    uls = []
    res = []

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
        
        symbol = contract.localSymbol
        price = ul.get_price()
        expiries = []
        strikes = []
        trading_classes = []

        for option_chain in option_chains:

            trading_classes.append(option_chain.get_trading_class())

        # assume expiries valid for all classes

        expiries.extend(option_chains[0].get_expiries()[:MAX_EXPIRIES])

        # take first, last, and middle strikes (or "-1" if ul price not available)

        strikes.append(option_chains[0].get_strikes()[0])
        if      price: strikes.extend(option_chains[0].get_atm_strikes(1, price))
        else:   strikes.extend([-1, -1])
        strikes.append(option_chains[0].get_strikes()[-1])
        
        strikes = [ str(strike) for strike in strikes ]

        # format strings

        symbol_string = f"{symbol:<6}"
        price_string = f"{price:<6}"
        expiries_string = f"[ {' '.join(expiries):<10} ]"
        strikes_string = f"[ {strikes[0]:<6} ... {' '.join(strikes[1:3]):8} ... {strikes[3]:<6} ]"
        trading_classes_string = f"[ {' '.join(trading_classes):<4} ]"

        res.append(
            symbol_string + 
            price_string +
            expiries_string +
            strikes_string +
            trading_classes_string
        )

    return P(
        id = "underlyings_data_text",
        children = [ "\n".join(res) ]
    )


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

        # TEST
        set_underlyings_data(
            None,
            "\n".join(
                [
                    "TSLA",
                    "NG:5"
                ]
            )
        )

        app.run_server(
            host = config["dash_host"],
            port = config["dash_port"], 
            debug = False,
            dev_tools_hot_reload = False
        )