

class option():


    def __init__(
        self,
        ib,
        contract
    ):

        self.ib = ib
        self.contract = contract
        self.symbol = contract.symbol
        self.type = contract.right
        self.strike = contract.strike
        self.expiry = contract.lastTradeDateOrContractMonth
        self.iv = None
        self.cost = None
        self.delta = None
        self.gamma = None
        self.vega = None
        self.theta = None
        self.rho = None
        self.underlying_price = None


    async def quote(self):

        res = await self.ib.quote_once(
            self.contract,
            fields = [ 
                #4,      # last
                13      # model option computation: IV and Greeks
            ]
        )

        for tick in res:

            # 13: model option computation
            if tick["field"] == 13:

                self.set_iv(tick["impliedVolatility"])
                self.set_cost(tick["optPrice"])
                self.set_delta(tick["delta"])
                self.set_gamma(tick["gamma"])
                self.set_vega(tick["vega"])
                self.set_theta(tick["theta"])
                self.set_underlying_price(tick["undPrice"])

                break
            
            # 9: previous close, price only
            if tick["field"] == 9:

                self.set_cost(tick["price"])

    def __str__(self):

        return "{0: <5} {1: <10} {2: <5} {3: <0.3f} {4: <0.4f}".format(
            self.strike,
            self.expiry,
            self.type,
            "None" if not self.iv else self.iv,
            "None" if not self.cost else self.cost
        )

    def get_client(self):                   return self.client
    def get_contract(self):                 return self.contract
    def get_type(self):                     return self.type
    def get_strike(self):                   return self.strike
    def get_symbol(self):                   return self.symbol
    def get_expiry(self):                   return self.expiry
    def get_iv(self):                       return self.iv
    def get_cost(self):                    return self.cost
    def get_delta(self):                    return self.delta
    def get_gamma(self):                    return self.gamma
    def get_vega(self):                     return self.vega
    def get_theta(self):                    return self.theta
    def get_rho(self):                      return self.rho
    def get_underlying_price(self):         return self.underlying_price

    def set_client(self, client):           self.client = client
    def set_contract(self, contract):       self.contract = contract
    def set_type(self, type):               self.type = type
    def set_strike(self, strike):           self.strike = strike
    def set_symbol(self, symbol):           self.symbol = symbol
    def set_expiry(self, expiry):           self.expiry = expiry
    def set_iv(self, iv):                   self.iv = iv
    def set_cost(self, cost):               self.cost = cost
    def set_delta(self, delta):             self.delta = delta
    def set_gamma(self, gamma):             self.gamma = gamma
    def set_vega(self, vega):               self.vega = vega
    def set_theta(self, theta):             self.theta = theta
    def set_rho(self, rho):                 self.rho = rho
    def set_underlying_price(self, price):  self.underlying_price = price