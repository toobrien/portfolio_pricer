from dash import Dash
from dash.dependencies import Input, Output, State
from ib.ib import ib
from json import loads
from parsers import parse_ul_def
from view import view


app = Dash(__name__)
app.layout = view().get_layout()


'''
@app.callback(
    Output("underlyings_cell"),
    Input("underlyings_submit"),
    State("underlyings_text")
)
'''
def get_underlyings(_, txt):

    ul_defs = txt.split("\n")
    res = []

    for ul_def in ul_defs:

        args = parse_ul_def(ul_def, config)
        uls = ib_client.underlying(**args)
        res.extend(uls)

    return res


if __name__ == "__main__":

    with open("./config.json") as fd:

        config = loads(fd.read())
        
        ib_client = ib(
            host = config["ib_host"],
            port = config["ib_port"],
            id_ = config["ib_client_id"]
        )

        ib_client.set_mkt_data_type(4)

        uls = get_underlyings(
            None,
            "\n".join(
                [
                    "TSLA",
                    "NGF2",
                    "NG:3"
                ]
            )
        )

        for underlying in uls:

            print(underlying)
        
        app.run_server(
            host = config["dash_host"],
            port = config["dash_port"], 
            debug = False,
            dev_tools_hot_reload = False
        )