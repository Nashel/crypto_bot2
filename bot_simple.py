import time
import sys, getopt
import datetime
from wrapper import poloniex

def main(argv):
	period = 10
	pair = "ETH_BTC"
	prices = []
	maxTransDiff = 9999999
	currentMovingAverage = 0
	lengthOfMA = 0
	historicalData = False
	tradePlaced = False
	typeOfTrade = False
	dataDate = datetime
	orderNumber = ""
	total = 0
	quant = 0.0
	buying = []
	selling = []

	try:
		opts, args = getopt.getopt(argv,"h:p:c:n:q:d:",["period=","currency=","points="])
	except getopt.GetoptError:
		print('bot_simple.py -p <period length> -c <currency pair> -n <period of moving average> -q <quantity of the indicated currency> -d <max difference between sell and buy transactions>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print('bot_simple.py -p <period length> -c <currency pair> -n <period of moving average> -q <quantity of the indicated currency> -d <max difference between sell and buy transactions>')
			sys.exit()
		elif opt in ("-p", "--period"):
			if (int(arg) in [300,900,1800,7200,14400,86400]):
				period = arg
			else:
				print('Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments')
				sys.exit(2)
		elif opt in ("-c", "--currency"):
			pair = arg
		elif opt in ("-n", "--points"):
			lengthOfMA = int(arg)
		elif opt in ("-q", "--quantity"):
			quant = float(arg)
		elif opt in ("-d"):
			maxTransDiff = int(arg)


	conn = poloniex('key goes here','key goes here') # To try without keys substitute by: conn = poloniex()

	# Prepare previous data
	historicalData = conn.api_query("returnChartData",{"currencyPair":pair,"start":int(time.time())-lengthOfMA*int(period),"end":int(time.time()),"period":period}) #TODO: investigate period
	while historicalData:
		nextDataPoint = historicalData.pop(0)
		lastPairPrice = nextDataPoint['weightedAverage']
		# dataDate = datetime.datetime.fromtimestamp(int(nextDataPoint['date'])).strftime("%d/%m/%Y")

		prices.append(float(lastPairPrice))
		prices = prices[-(lengthOfMA):]
		currentMovingAverage = sum(prices) / float(len(prices))

	while True:
		currentValues = conn.api_query("returnTicker")
		lastPairPrice = currentValues[pair]["last"]
		dataDate = datetime.datetime.now()

		if (len(prices) > 0):
			currentMovingAverage = sum(prices) / float(len(prices))
			previousPrice = prices[-1]
			
			# Trade placing decisions
			if (not tradePlaced):
				if (abs(len(buying)-len(selling)) < maxTransDiff):
					if ( (float(lastPairPrice) > currentMovingAverage) and (float(lastPairPrice) < previousPrice) ):
						print("SELL ORDER")
						selling.append([pair, float(lastPairPrice),quant])
						# orderNumber = conn.sell(pair,float(lastPairPrice),quant) # To try without keys substitute by: orderNumber = 0
						tradePlaced = True
						typeOfTrade = "short"
					elif ( (float(lastPairPrice) < currentMovingAverage) and (float(lastPairPrice) > previousPrice) ):
						print("BUY ORDER")
						buying.append([pair,float(lastPairPrice),quant])
						# orderNumber = conn.buy(pair,float(lastPairPrice),quant) # To try without keys substitute by: orderNumber = 0
						tradePlaced = True
						typeOfTrade = "long"
			elif (typeOfTrade == "short"):
				if ( float(lastPairPrice) < currentMovingAverage ):
					print("EXIT TRADE")
					# conn.cancel(pair,orderNumber) # To try without keys delete this line
					tradePlaced = False
					typeOfTrade = False
			elif (typeOfTrade == "long"):
				if ( float(lastPairPrice) > currentMovingAverage ):
					print("EXIT TRADE")
					# conn.cancel(pair,orderNumber) # To try without keys delete this line
					tradePlaced = False
					typeOfTrade = False
		else:
			previousPrice = 0

		# TODO: Añadir trayectoria
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
		
		print("After max fees -- Bought: " + str(totalBought*0.99855) + " - Sold: " + str(totalSold*0.99855))

		if (len(selling) > 0):
			avgSells = sum(x[1] for x in selling)/len(selling)
			if (len(buying) > 0):
				avgBuys = sum(x[1] for x in buying)/len(buying)
				total = avgSells / avgBuys
				print("Total earns: %5.8f" % (total-1))

		prices.append(float(lastPairPrice))
		prices = prices[-(lengthOfMA):]

		time.sleep(int(period))


if __name__ == "__main__":
	main(sys.argv[1:])