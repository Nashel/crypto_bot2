import time
import os
import sys, getopt
import datetime
from polosdk import RestClient
from wrapper import poloniex

client = RestClient()
api_key = os.environ['POLO_API_KEY']
api_secret = os.environ['POLO_API_SECRET']

def main(argv):
	period = 10
	pair = "ETH_BTC"
	prices = []
	# maxTransDiff = 9999999
	currentMovingAverage = 0
	lengthOfMA = 0
	failsafe = 0.003
	historicalData = False
	tradePlaced = False
	typeOfTrade = False
	dataDate = datetime
	orderNumber = ""
	interval = ""
	total = 0
	quant = 0.0
	buying = []
	selling = []

	try:
		opts, args = getopt.getopt(argv, "h:p:c:n:q:s:", ["period=", "currency=", "points="])
	except getopt.GetoptError:
		print('bot_simple.py -p <period length> -c <currency pair> -n <period of moving average> -q <quantity of the indicated currency> -s <failsafe>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print('bot_simple.py -p <period length> -c <currency pair> -n <period of moving average> -q <quantity of the indicated currency> -s <failsafe>')
			sys.exit()
		elif opt in ("-p", "--period"):
			if int(arg) in [60, 300, 600, 900, 1800, 3600, 7200, 14400, 21600, 43200, 86400, 259200]:
				period = arg
				if period == '60':		# Im so lazy lol
					interval = "MINUTE_1"
				elif period == '300':
					interval = "MINUTE_5"
				elif period == '600':
					interval = "MINUTE_10"
				elif period == '900':
					interval = "MINUTE_15"
				elif period == '1800':
					interval = "MINUTE_30"
				elif period == '3600':
					interval = "HOUR_1"
				elif period == '7200':
					interval = "HOUR_2"
				elif period == '14400':
					interval = "HOUR_4"
				elif period == '21600':
					interval = "HOUR_6"
				elif period == '43200':
					interval = "HOUR_12"
				elif period == '86400':
					interval = "DAY_1"
				elif period == '259200':
					interval = "DAY_3"
			else:
				print('Poloniex requires periods in 60, 300, 600, 900, 1800, 3600, 7200, 14400, 21600, 43200, 86400 or 259200 second increments')
				sys.exit(2)
		elif opt in ("-c", "--currency"):
			pair = arg
		elif opt in ("-n", "--points"):
			lengthOfMA = int(arg)
		elif opt in ("-q", "--quantity"):
			quant = float(arg)
		elif opt in ("-s", "--failsafe"):
			failsafe = float(arg)


	# conn = poloniex('key goes here','key goes here') # TODO: DELETE

	# Prepare previous data
	actualTime = client.get_timestamp()
	historicalData = client.markets().get_candles(pair, interval, int(actualTime['serverTime'])-lengthOfMA*int(period)*1000, int(actualTime['serverTime']))
	while historicalData:
		nextDataPoint = historicalData.pop(0)
		lastPairPrice = nextDataPoint[10]

		prices.append(float(lastPairPrice))
		prices = prices[-(lengthOfMA):]
		currentMovingAverage = sum(prices) / float(len(prices))

	while True:
		currentValues = client.markets().get_ticker24h(pair)
		lastPairPrice = currentValues['close']
		dataDate = datetime.datetime.now()

		if (len(prices) > 0):
			currentMovingAverage = sum(prices) / float(len(prices))
			previousPrice = prices[-1]

			# Trade placing decisions
			if (not tradePlaced):
				if ( (float(lastPairPrice) > currentMovingAverage) and (float(lastPairPrice) < previousPrice)):
					print("SELL ORDER")
					selling.append([pair, float(lastPairPrice), quant])
					#  # Place sell order # orderNumber = conn.sell(pair,float(lastPairPrice),quant) TODO: UPDATE
					tradePlaced = True
					typeOfTrade = "short"
				elif ( (float(lastPairPrice) < currentMovingAverage) and (float(lastPairPrice) > previousPrice) ):
					print("BUY ORDER")
					buying.append([pair, float(lastPairPrice), quant])
					# orderNumber = conn.buy(pair,float(lastPairPrice),quant) TODO: UPDATE
					tradePlaced = True
					typeOfTrade = "long"
			elif (typeOfTrade == "short"):
				if ( float(lastPairPrice) < currentMovingAverage ):
					print("EXIT TRADE")
					#res = conn.cancel(pair, orderNumber) TODO: UPDATE & substract the canceled order from the list
					tradePlaced = False
					typeOfTrade = False
			elif (typeOfTrade == "long"):
				if ( float(lastPairPrice) > currentMovingAverage ):
					print("EXIT TRADE")
					#res = conn.cancel(pair, orderNumber) TODO: UPDATE & substract the canceled order from the list
					tradePlaced = False
					typeOfTrade = False
		else:
			previousPrice = 0

		# Show resultant data
		totalSold = 0
		totalBought = 0
		for x in selling:
			totalSold += x[1]*x[2]
		for x in buying:
			totalBought += x[1]*x[2]


		print("%s Period: %ss %s: %s Moving Average: %s" % (dataDate,period,pair,lastPairPrice,currentMovingAverage))
		print("Sell orders - " + str(len(selling)))
		print(selling)
		print("Buy orders - " + str(len(buying)))
		print(buying)

		print("Bought: " + str(totalBought) + " - Sold: " + str(totalSold))

		if (len(selling) > 0):
			avgSells = sum(x[1] for x in selling)/len(selling)
			if (len(buying) > 0):
				avgBuys = sum(x[1] for x in buying)/len(buying)
				total = avgSells / avgBuys
				print("Total average earns: %5.8f" % (total-1))
				if (total - 1) < -failsafe:
					print('This sesion loses are higher than %5.5f percent. Failsafe activated' % failsafe)
					#res = conn.cancel(pair, orderNumber)
					sys.exit(2)


		prices.append(float(lastPairPrice))
		prices = prices[-(lengthOfMA):]

		time.sleep(int(period))


if __name__ == "__main__":
	main(sys.argv[1:])