from asyncio import new_event_loop, wait
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper
from ib.option_chain import option_chain
from ib.underlying import underlying
from threading import get_ident, Thread


# sleep before any call to EClient
# no more than 50 requests per second
SLEEP = 0.02

# 1 = ???
# 2 = ???
# 3 = delayed, frozen
# 4 = ???
DEFAULT_DATA_TYPE = 4

# maximum concurrent data lines
MAX_DATA_LINES = 50

NOT_FOUND = 0


class wrapper(EWrapper):


    def __init__(self):

        EWrapper.__init__(self)


    def connectAck(self):

        print(f"{get_ident()}:wrapper:connectAck")


    def nextValidId(self, orderId):

        print(f"{get_ident()}:wrapper:nextValidId:{orderId}")


    def connectionClosed(self):

        print(f"{get_ident()}:wrapper:connectionClosed")


    def error(self, reqId, errorCode, errorString):
        
        # this will print the message
        super().error(reqId, errorCode, errorString)
        
        if errorCode == 10090:

            # market data warning
            pass

        if errorCode == 200:
        
            # attempt to quote nonexistent option, probably
            self.resolve(reqId)
    
        elif errorCode == 300:

            # attempt to cancel stream, but not open... dont worry
            pass


    def securityDefinitionOptionParameter(
        self,
        reqId,
        exchange,
        underlyingConId,
        tradingClass,
        multiplier,
        expirations,
        strikes
    ):

        super().securityDefinitionOptionParameter(
            reqId,
            exchange,
            underlyingConId,
            tradingClass,
            multiplier,
            expirations,
            strikes
        )

        result = self.results[reqId]["res"]
        result.append({
            "exchange": exchange,
            "contract_id": underlyingConId,
            "trading_class": tradingClass,
            "multiplier": multiplier,
            "expirations": expirations,
            "strikes": strikes
        })


    def securityDefinitionOptionParameterEnd(self, reqId):
        
        self.resolve(reqId)


    def contractDetails(self, reqId, contractDetails):

        super().contractDetails(reqId, contractDetails)

        result = self.results[reqId]["res"]
        result.append(contractDetails)


    def contractDetailsEnd(self, reqId):

        self.resolve(reqId)


    def tickOptionComputation(
        self,
        reqId,
        field,
        impliedVolatility,
        delta,
        optPrice,
        pvDividend,
        gamma,
        vega,
        theta,
        undPrice = None
    ):

        try:

            f = self.results[reqId]
            f["res"].append(
                {
                    "field": field,
                    "impliedVolatility": impliedVolatility,
                    "delta": delta,
                    "optPrice": optPrice,
                    "pvDividend": pvDividend,
                    "gamma": gamma,
                    "vega": vega,
                    "theta": theta,
                    "undPrice": undPrice
                }
            )

            self.check_mkt_data_finished(reqId, f["params"], field)
        
        except KeyError:

            # snapshot received, future already resolved
            pass


    def tickPrice(self, reqId, field, price, attribs):

        try: 
            
            f = self.results[reqId]
            f["res"].append(
                {
                    "field": field,
                    "price": price,
                    "attribs": attribs
                }
            )

            self.check_mkt_data_finished(reqId, f["params"], field)           
        
        except KeyError:

            # snapshot received, future already resolved
            pass


    def check_mkt_data_finished(self, reqId, params, field):

        if field in params["fields"]: 
            
            self.resolve(reqId)


    def resolve(self, reqId):
            
        f = self.results[reqId]

        self.loop.call_soon_threadsafe(
            f["fut"].set_result,
            f["res"]
        )

        del self.results[reqId]


class ib(wrapper, EClient):

    def __init__(self, host, port, id_):
        
        wrapper.__init__(self)
        EClient.__init__(self, wrapper = self)

        # connection
        self.host = host
        self.port = port
        self.id = id_

        # requests and results
        self.reqId = -1
        self.results = {}

        # concurrency
        self.open_data_lines = 0
        self.market_data_queue = []
        self.loop = new_event_loop()
        self.last_exec = -1

        # initialize connection
        super().connect(host, port, id_)
        
        thread = Thread(target=self.run)
        thread.start()

        # set to receive delayed and frozen data
        self.set_mkt_data_type(DEFAULT_DATA_TYPE)


    # see constants at top of file
    def set_mkt_data_type(self, mkt_data_type):

        self.schedule(
            self.reqMarketDataType, [ mkt_data_type ]
        )


    # start with this function to get a contract (particularly,
    # its conId), when you only know its symbol. then, invoke 
    # the rest of the functions using the contract.
    #
    # only returns one contract, assumes no ambiguity
    async def contract_details(
        self,
        symbol,
        type,
        currency = "USD",
        exchange = "SMART",
        expiration = None,
        localSymbol = None
    ):

        self.reqId += 1
        fut = self.get_future(self.reqId)

        con = Contract()
        con.symbol = symbol
        con.secType = type
        con.currency = currency
        con.exchange = exchange
        con.localSymbol = localSymbol
        
        if expiration != None:
            
            con.lastTradeDateOrContractMonth = expiration

        self.schedule(
            self.reqContractDetails, 
            [ self.reqId, con ]
        )

        return await fut

    # subscribe to market data stream and cancel
    # shortly thereafter, gathering minimal ticks
    async def quote_once(self, contract, fields):

        self.reqId += 1
        handle = self.reqId
        fut = self.get_future(
            self.reqId,
            params = { "fields": fields }
        )

        #print(f"START XXXX {contract.right} {contract.strike}")
        #start = time()
        
        self.reqMktDataWrapper(
            [
                self.reqId,
                contract,
                "",
                False,
                False,
                None
            ]
        )

        #elapsed = time() - start
        #print(f"END {elapsed: <0.3f} {contract.right} {contract.strike}\n")

        res = await fut
   
        self.cancelMktDataWrapper([ handle ])

        return res


    # returns all option chains for an underlying
    async def option_chains(self, contract):

        self.reqId += 1
        fut = self.get_future(self.reqId)

        exchange =  "" if contract.secType == "STK" \
                    else contract.exchange

        self.schedule(
            self.reqSecDefOptParams,
            [ 
                self.reqId,
                contract.symbol,
                exchange,
                contract.secType,
                contract.conId
            ]
        )

        res = await fut

        if contract.secType == "STK":

            # for whatever reason, you can't put an exchange
            # in above, need to get all exchanges and filter
            res = list(
                filter(
                    lambda o: o["exchange"] == "SMART", 
                    res
                )
            )

        for i in range(len(res)):
                
            res[i] = option_chain(
                self,
                contract.symbol,
                contract.secType,
                res[i]
            )

        return res


    # client facing, synchronous
    # returns nearest N contracts for a given symbol
    def underlying(
        self, 
        symbol,
        exchange = "SMART",
        security_type = "STK",
        max_contracts = 1,
        local_symbol = ""
    ):

        details = self.loop.run_until_complete(
                self.contract_details(
                symbol = symbol, 
                type = security_type, 
                exchange = exchange,
                localSymbol = local_symbol
            )
        )

        contracts = sorted(
            [ d.contract for d in details ],
            key = lambda c: c.lastTradeDateOrContractMonth
        )[:max_contracts]

        res = [ underlying(self, c) for c in contracts ]

        # initialize quotes and option chains
        update_ul_prices = wait(
            [
                self.loop.create_task(ul.update_price())
                for ul in res
            ]
        )

        update_option_chains = wait(
            [
                self.loop.create_task(ul.update_option_chains())
                for ul in res
            ]
        )

        self.loop.run_until_complete(update_ul_prices)
        self.loop.run_until_complete(update_option_chains)

        return res


    #########################
    # CONCURRENCY FUNCTIONS #
    #########################


    def reqMktDataWrapper(self, args):

        if self.open_data_lines <= 50:

            self.schedule(
                self.reqMktData,
                args
            )
            self.open_data_lines = self.open_data_lines + 1
        
        else:

            self.market_data_queue.append(args)


    def cancelMktDataWrapper(self, args):

        self.schedule(
            self.cancelMktData,
            args
        )
        self.open_data_lines = self.open_data_lines - 1

        if self.market_data_queue:

            # only one retry per cancel!
            # any function that calls reqMktData
            # should also call cancelMktData
            self.schedule(
                self.reqMktData,
                self.market_data_queue.pop()
            )


    # do not call EClient methods directly, instead
    # schedule them SLEEP ms apart
    def schedule(self, func, args):

        now = self.loop.time()
        next_exec = max(now, self.last_exec + SLEEP)
        self.loop.call_at(next_exec, func, *args)
        self.last_exec = next_exec


    # for synchronizing with EWrapper
    def get_future(self, reqId, params = None):

        fut = self.loop.create_future()

        self.results[reqId] = {
            "fut": fut,
            "params": params,
            "res": []
        }

        return fut


    def get_last_exec(self):                return self.last_exec
    def get_loop(self):                     return self.loop
    def get_market_data_queue(self):        return self.market_data_queue
    def get_open_data_liens(self):          return self.open_data_lines
    def get_results(self):                  return self.results

    def set_last_exec(self, time):          self.last_exec = time
    def set_loop(self, loop):               self.loop = loop
    def set_market_data_queue(self, queue): self.queue = queue
    def set_open_data_lines(self, lines):   self.open_data_lines = lines
    def set_results(self, results):         self.results = results