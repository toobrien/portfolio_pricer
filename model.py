from ib.ib import option_chain

class leg():


    def __init__(
        self,
        call: bool,
        expiry: int,
        long: bool,
        quantity: int,
        strike: float,
        trading_class: str,
        underlying: str
    ):

        self.call = call,
        self.expiry = expiry
        self.long = long
        self.quantity = quantity
        self.strike = strike
        self.trading_class = trading_class
        self.underlying = underlying


class underlying():


    def __init__(
        self,
        symbol: str,
        price: float,
        option_chains: dict[str, option_chain]
    ):

        self.symbol = symbol
        self.price = price
        self.option_chains = option_chains


class model():


    def __init__(self):

        pass


    def set_legs(self, legs):

        pass


    def set_underlyings(self, underlyings):

        pass