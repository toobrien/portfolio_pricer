

class underlying():

    
    def __init__(self,
        ib, 
        contract = None,
        price = None,
        option_chains = None
    ):

        self.ib = ib
        self.contract = contract
        self.price = price
        self.option_chains = option_chains


    async def update_price(self):

        ticks = await self.ib.quote_once(
            self.contract, 
            fields = [ 
                4,          # last price
                9,          # close price
                68          # delayed last
            ]
        )

        last = None
        delayed_last = None
        prev_close = None

        for tick in ticks:

            field = tick["field"]

            if field ==     4:    last = tick["price"]
            elif field ==   9:    prev_close = tick["price"]
            elif field ==   68:   delayed_last = tick["price"]

        if   last:          self.price = last
        elif delayed_last:  self.price = delayed_last
        elif prev_close:    self.price = prev_close


    async def update_option_chains(self):

        self.option_chains = await self.ib.option_chains(
            self.contract
        )


    def __str__(self):

        c = self.contract
        
        return  f"{c.conId}, "                          +\
                f"{c.symbol}, "                         +\
                f"{c.secType}, "                        +\
                f"{c.exchange}, "                       +\
                f"{c.currency}, "                       +\
                f"{c.lastTradeDateOrContractMonth}, "   +\
                f"{c.localSymbol}"


    def get_contract(self): return self.contract
    def get_expiration(self): return self.contract.lastTradeDateOrContractMonth
    def get_option_chains(self): return self.option_chains
    def get_price(self): return self.price

    def set_contract(self, contract): self.contract = contract
    def set_price(self, price): self.price = price