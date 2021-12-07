

'''
there are three formats:

  a) <stock>[:<exchange>]                   "TSLA", "TSLA:NASDAQ"
  b) <future>:<# contracts>:[:<exchange>]   "NG:5", "NG:5:NYMEX"
  c) <future (local symbol)>[:<exchange>]   "NGF2", "NGF2:NYMEX"

if the exchange is not provided in the definition,
it must be loaded from config.json (see example file)
'''
def parse_ul_def(ul_def: str, config: dict) -> dict:

    parts = ul_def.split(":")
    args = {
        "symbol": None,
        "exchange": None,
        "security_type": None,
        "local_symbol": None,
        "max_contracts": None
    }

    # security type

    if len(parts) > 1 and parts[1].isnumeric() or parts[0][-1].isnumeric():

        args["security_type"] = "FUT"

    else:

        args["security_type"] = "STK"

    # symbol and local_symbol

    if parts[0][-1].isnumeric():

        args["symbol"] = parts[0][:-2]
        args["local_symbol"] = parts[0]

    else:

        args["symbol"] = parts[0]
        args["local_symbol"] = ""

    # max_contracts

    if len(parts) > 1 and parts[1].isnumeric():

        args["max_contracts"] = int(parts[1])

    else:

        args["max_contracts"] = 1

    # exchange

    if args["security_type"] == "STK":

        if len(parts) == 1:

            args["exchange"] = config["exchanges"]["STK"]

        else:

            args["exchange"] = parts[1]

    elif args["security_type"] == "FUT":

        if args["local_symbol"] != "":

            if len(parts) == 2:

                args["exchange"] = parts[1]

            else:

                args["exchange"] = config["exchanges"]["FUT"][args["symbol"]]
        
        else:

            if len(parts) == 3:

                args["exchange"] = parts[2]
            
            else:

                args["exchange"] = config["exchanges"]["FUT"][args["symbol"]]
    
    return args