from datetime import date
from sys import maxsize
from typing import List


def get_dte(exp: str):

        d0 = date.today()
        d1 = date(
                year =  int(exp[0:4]),
                month = int(exp[4:6]),
                day =   int(exp[6:8])
            )

        return (d1 - d0).days


class leg():


    def __init__(
        self,
        call: bool,
        cost: float,
        dte: float,
        expiry: int,
        id: str,
        iv: float,
        long: bool,
        quantity: int,
        strike: float,
        trading_class: str,
        underlying: any
    ):

        self.call = call
        self.cost = cost
        self.dte = dte
        self.expiry = expiry
        self.id = id
        self.iv = iv
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
        self.legs_by_index = None
        self.legs_by_underlying = None
        self.variables = None


    def set_legs(self, legs: List[leg]):

        legs = sorted(legs, key = lambda l: l.expiry)

        self.legs_by_index = legs
        self.legs_by_underlying = {
            symbol : []
            for symbol in self.underlyings_by_symbol
        }
        
        for leg in legs:

            if type(leg.underlying) == int:

                # index is for user convenience, replace with symbol

                symbol = self.underlyings_by_index[leg.underlying].symbol
                self.legs_by_underlying[symbol].append(leg)

                leg.underlying = symbol

            else:

                self.legs_by_underlying[
                    self.underlyings_by_symbol[leg.underlying].symbol
                ].append(leg)

            # set id

            leg.id = f"{leg.underlying}:{'+' if leg.long else '-'}{'C' if leg.call else 'P'}{str(leg.strike)}"

            # set expiry (replace index (int) with string (date))

            underlying_ = self.underlying_by_symbol[leg.underlying]
            option_chain = underlying_.option_chains[leg.trading_class]
            leg.expiry = option_chain.expiries[leg.expiry]
            
            # set dte

            leg.dte = get_dte(leg.expiry)

            # set cost and iv

            leg_type = "CALL" if leg.call else "PUT"
            
            for option in option_chain.get_option(leg.expiry, leg.strike):

                if option.right == leg_type:

                    leg.cost = option.get_cost()
                    leg.iv = option.get_iv()

                    break

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


    def initialize_variables(self):

        self.variables = {
            "time": maxsize,
            "rate": 0.10
        }
        
        for underlying in self.underlyings_by_index:

            self.variables[underlying.symbol] = underlying.price

        for leg in self.legs:

            self.variables[leg.id] = leg.iv
            
            if leg.dte < self.variables["time"]:

                self.variables["time"] = leg.dte
    

    def get_variable_text(self):

        res = []

        for underlying in self.underlyings_by_index:

            res.append(f"{underlying.symbol}:\t\t{underlying.price}")
        
        for leg in self.legs_by_index:

            res.append(f"{leg.id}:\t{leg.iv}")

        return res.join("\n")