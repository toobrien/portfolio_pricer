from ib import ib
from typing import List

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
        option_chains: dict[str, ib.option_chain]
    ):

        self.symbol = symbol
        self.price = price
        self.option_chains_by_symbol = {}
        self.option_chains_by_index = []

        for option_chain in option_chains:

            self.option_chains_by_symbol[
                option_chain.get_trading_class()
            ] = option_chain

            self.option_chains_by_index.append(option_chain)
        

class model():


    def __init__(self):

        self.underlyings_by_index = None
        self.underlyings_by_symbol = None
        self.legs = None


    def set_legs(self, legs: List[leg]):

        self.legs = legs


    def set_underlyings(self, underlyings: List[ib.underlying]):

        self.underlyings_by_index = []
        self.underlyings_by_symbol = {}

        for ul in underlyings:
            
            contract = ul.get_contract()
            symbol = contract.localSymbol

            ul_ = underlying(
                symbol,
                ul.get_price(),
                ul.get_option_chains()
            )
            
            self.underlyings_by_index.append(ul_)
            self.underlyings_by_symbol[symbol] = ul_

    
    def get_leg(self, index: int):

        return self.legs[index]

    
    def get_underlying_by_symbol(self, symbol: str):

        return self.underlyings_by_symbol(symbol)


    def get_underlying_by_index(self, index: int):

        return self.underlyings_by_index[index]