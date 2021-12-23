from datetime import date
from ib import ib
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
        self.legs_by_id = None
        self.legs_by_index = None
        self.legs_by_underlying = None
        self.variables = None


    def set_legs(self, legs: List[leg]):

        self.legs_by_id = {}
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

            # replace underlying symbol with underlying object

            leg.underlying = self.underlyings_by_symbol[leg.underlying]

            # set id

            leg.id = f"{leg.underlying.symbol}:{'+' if leg.long else '-'}{'C' if leg.call else 'P'}{str(leg.strike)}"
            self.legs_by_id[leg.id] = leg

            # set expiry (replace index (int) with string (date))

            option_chain = None

            if str(leg.trading_class).isnumeric():

                option_chain = leg.underlying.option_chains_by_index[leg.trading_class]

            else:

                option_chain = leg.underlying.option_chains_by_symbol[leg.trading_class]

            if leg.expiry < 10000000:

                # expiry is an index, replace with date format: int(YYYYMMDD)
            
                leg.expiry = option_chain.expiries[leg.expiry]
            
            # set dte

            leg.dte = get_dte(leg.expiry)

            # set cost and iv

            leg_type = "CALL" if leg.call else "PUT"
            
            for option in option_chain.get_option(leg.expiry, leg.strike):

                if option.type == leg_type:

                    leg.cost = option.get_cost()
                    leg.iv = option.get_iv()

                    break
        
        # legs by index... is this needed?

        self.legs_by_index = sorted(legs, key = lambda l: l.expiry)


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

        for leg in self.legs_by_index:

            self.variables[leg.id] = leg.iv
            
            if leg.dte < self.variables["time"]:

                self.variables["time"] = leg.dte
    

    def get_variables_text(self):

        res = []

        for underlying in self.underlyings_by_index:

            res.append(f"{underlying.symbol}\t\t{underlying.price}")
        
        for leg in self.legs_by_index:

            res.append(f"{leg.id}\t{leg.iv}")

        return ("\n").join(res)

    
    def set_variables_from_text(self, variables_text):

        self.variables = {
            "time": maxsize,
            "rate": 0.10
        }

        for variable_def in variables_text.split("\n"):

            parts = variable_def.split()
            self.variables[parts[0]] = float(parts[1])


    def get_legs_by_id(self):   return self.legs_by_id
    def get_variables(self):    return self.variables