from asyncio import wait, sleep
from bisect import bisect_left
from ibapi.contract import Contract
from ib.option import option
from time import time


class option_chain():


    def __init__(self, ib, symbol, type, reqSecDefOptParams):

        self.ib = ib
        self.symbol = symbol
        if type == "FUT":   self.type = "FOP"
        else:               self.type = "OPT"
        self.contract_id = reqSecDefOptParams["contract_id"]
        self.exchange = reqSecDefOptParams["exchange"]
        self.expiries = sorted(
            list(reqSecDefOptParams["expirations"])
        )
        self.multiplier = reqSecDefOptParams["multiplier"]
        self.strikes = sorted(
            list(reqSecDefOptParams["strikes"]),
            key = float
        )
        self.trading_class = reqSecDefOptParams["trading_class"]
    

    def get_atm_strikes(self, num_strikes, ul_price):

        res = []

        if ul_price:

            atm = bisect_left(self.strikes, ul_price)
            lo = atm - num_strikes
            hi = atm + num_strikes

            if lo >= 0 and hi < len(self.strikes):

                res = self.strikes[lo:hi]

            else:

                res = self.strikes[:]
        
        return res


    def get_strike_range(self, lo, hi):

        res = []

        left = bisect_left(self.strikes, lo)
        right = bisect_left(self.strikes, hi)

        if left >= 0 and right < len(self.strikes):

            res = self.strikes[left:right]
        
        return res


    def get_expiries(self):

        return self.expiries[:]


    # get N ATM strikes for nearest M expiries
    def get_nearest_options(self, ul_price, expiries, strikes):

        strikes = self.get_atm_strikes(strikes, ul_price)
        expiries = self.get_expiries()[:expiries]

        return self.get_options(expiries, strikes)


    def get_options(self, expiries, strikes):

        res = []
        loop = self.ib.get_loop()

        for expiry in expiries:

            for strike in strikes:

                for type in [ "PUT", "CALL" ]:
                    
                    con = Contract()
                    con.symbol = self.symbol
                    con.currency = "USD"
                    con.exchange = self.exchange
                    con.lastTradeDateOrContractMonth = expiry
                    con.multiplier = self.multiplier
                    con.right = type
                    con.secType = self.type
                    con.strike = strike
                    con.tradingClass = self.trading_class

                    opt = option(self.ib, con)

                    res.append(opt)

        start = time()

        loop.run_until_complete(
            wait(
                [ opt.quote() for opt in res ]
            )
        )

        elapsed = time() - start
        
        print(f"option_chain.get_options: {len(res)} quotes in {elapsed: 0.3f}s")

        return res


    def get_option(self, expiry, strike):

        return self.get_options(self, [ expiry ], [ strike ])


    def get_contract_id(self):      return self.contract_id
    def get_exchange(self):         return self.exchange
    def get_expiries(self):         return self.expiries
    def get_multiplier(self):       return self.multiplier
    def get_strikes(self):          return self.strikes
    def get_symbol(self):           return self.symbol
    def get_trading_class(self):    return self.trading_class
    def get_type(self):             return self.type