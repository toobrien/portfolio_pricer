from dash import Dash
from ib.ib import ib
from json import loads
from view import view

# TODO: get an underlying from a localSymbol
# TODO: underlying class autofills its option chian
# TODO: underlying.get_option(type, strike, expiration)
# TODO: delete option_chain
# TODO: refactor option

if __name__ == "__main__":

    with open("./config.json") as fd:

        config = loads(fd.read())
        
        ib_client = ib(
            host = config["ib_host"],
            port = config["ib_port"],
            id_ = config["ib_client_id"]
        )

        app = Dash(__name__)
        app.layout = view().get_layout()

        app.run_server(
            host = config["dash_host"],
            port = config["dash_port"], 
            debug = False,
            dev_tools_hot_reload = False
        )
    