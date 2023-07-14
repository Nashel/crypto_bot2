import urllib.parse
import urllib.request
import json
import time
import hmac,hashlib

def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))

class poloniex:
    
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in range(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                            
        return after

    def api_query(self, command, req={}):

        if(command == "returnTicker" or command == "return24Volume"):
            ret = urllib.request.urlopen('https://poloniex.com/public?command=' + command)
            return json.loads(ret.read())
        elif(command == "returnOrderBook"):
            ret = urllib.request.urlopen('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair']))
            return json.loads(ret.read())
        elif(command == "returnMarketTradeHistory"):
            ret = urllib.request.urlopen('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair']))
            return json.loads(ret.read())
        elif(command == "returnChartData"):
            ret = urllib.request.urlopen('https://poloniex.com/public?command=returnChartData&currencyPair=' + str(req['currencyPair']) + '&start=' + str(req['start']) + '&end=' + str(req['end']) + '&period=' + str(req['period']))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.parse.urlencode(req)

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            ret = urllib.request.urlopen('https://poloniex.com/tradingApi', post_data, headers)
            jsonRet = json.loads(ret.read())
            return self.post_process(jsonRet)


    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})


    # Returns all of your balances.
    # Outputs: 
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair	    A string that defines the market, "USDT_BTC" for example. Use "all" for all markets.
    # Outputs: 
    # orderNumber	    The number uniquely identifying this order.
    # type      	    Denotes this order as a "buy" or "sell".
    # rate	            The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    # startingAmount	The size of the original order.
    # amount	        The amount left to fill in this order.
    # total	            The total cost of this order in base units.
    # date	            The UTC date of order creation.
    # margin	        Denotes this as a margin order (1) or not. (0)
    # clientOrderId	User specified 64-bit integer identifier.
    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair	    A string that defines the market, "USDT_BTC" for example. Use "all" for all markets.
    # Outputs: 
    # globalTradeID	    The globally unique identifier of this trade.
    # tradeID	        The identifier of this trade unique only within this trading pair.
    # date	            The UTC date at which this trade executed.
    # rate	            The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    # amount	        The amount transacted in this trade.
    # total	            The total cost in base units of this trade.
    # fee	            The fee paid for this trade.
    # orderNumber	    The order number to which this trade is associated.
    # type	            Denotes a "buy" or a "sell" execution.
    # category	        Denotes if this was a standard or margin exchange.
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair	    A string that defines the market, "USDT_BTC" for example.
    # rate	            The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    # amount	        The total amount offered in this buy order.
    # Output Example: 
    # { "orderNumber": "514845991795",
    #   "resultingTrades":
    #    [ { "amount": "3.0",
    #        "date": "2018-10-25 23:03:21",
    #        "rate": "0.0002",
    #        "total": "0.0006",
    #        "tradeID": "251834",
    #        "type": "buy" } ],
    #   "fee": "0.01000000",
    #   "clientOrderId": "12345",
    #   "currencyPair": "BTC_ETH" }
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair	    A string that defines the market, "USDT_BTC" for example.
    # rate	            The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    # amount	        The total amount offered in this buy order.
    # Output Example: 
    # { "orderNumber": "514845991926",
    #   "resultingTrades":
    #    [ { "amount": "1.0",
    #        "date": "2018-10-25 23:03:21",
    #        "rate": "10.0",
    #        "total": "10.0",
    #        "tradeID": "251869",
    #        "type": "sell" } ],
    #   "fee": "0.01000000",
    #   "clientOrderId": "12345",
    #   "currencyPair": "BTC_ETH" }
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair      User specified 64-bit integer identifier.
    # orderNumber       The identity number of the order to be canceled.
    # Outputs: 
    # success	        A boolean indication of the success or failure of this operation.
    # amount	        The remaning unfilled amount that was canceled in this operation.
    # message	        A human readable description of the result of the action.
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."} 
    # Inputs:
    # currency              The currency to withdraw
    # amount                The amount of this coin to withdraw
    # address               The withdrawal address
    # Outputs: 
    # response              Text containing message about the withdrawal
    # withdrawalNumber	    Withdrawal reference ID that can be matched with results from the returnDepositsWithdrawals API to poll for status updates.
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})