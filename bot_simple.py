import time
import os
import sys, getopt
import datetime
import uuid
import regex

import polosdk
from polosdk import RestClient


api_key = os.environ['POLO_API_KEY']
api_secret = os.environ['POLO_API_SECRET']
client = RestClient(api_key, api_secret)

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
	generatedUuid = ""
	interval = ""
	total = 0
	maxBuy = 0.0
	quant = 0.0
	minimum = 0.0
	i=0
	buying = []
	selling = []

	try:
		opts, args = getopt.getopt(argv, "h:p:c:n:q:s:m:l:", ["period=", "currency=", "points="])
	except getopt.GetoptError:
		print('bot_simple.py -p <period length> -c <currency pair> -n <period of moving average> -q <quantity of the indicated currency> -s <failsafe> -m <maximum to buy> -l <minimum to sell>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print('bot_simple.py -p <period length> -c <currency pair> -n <period of moving average> -q <quantity of the indicated currency> -s <failsafe> -m <maximum to buy> -l <minimum to sell>')
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
		elif opt in ("-m", "--maxMultiplier"):
			maxBuy = float(arg)
		elif opt in ("-l", "--minimum"):
			minimum = float(arg)


	# Prepare previous data
	actualTime = client.get_timestamp()
	historicalData = client.markets().get_candles(pair, interval, int(actualTime['serverTime'])-lengthOfMA*int(period)*1000, int(actualTime['serverTime']))
	fees = client.accounts().get_fee_info()
	while historicalData:
		nextDataPoint = historicalData.pop(0)
		lastPairPrice = nextDataPoint[10]

		prices.append(float(lastPairPrice))
		prices = prices[-(lengthOfMA):]
		currentMovingAverage = sum(prices) / float(len(prices))

	previousPrice = prices[-1]

	while True:
		try:
			currentValues = client.markets().get_price(pair)
			lastPairPrice = currentValues['price']
			balances = client.subaccounts().get_balances()
			spotAccount = next((item for item in balances if item["accountType"] == "SPOT" and item["isPrimary"] == "true"), None)
			actualCurrency = next((item for item in spotAccount["balances"] if item["currency"] == regex.search(r"^(.*?)_", pair).group(1)), None)

			if actualCurrency is None:
				actualCurrency = {"available": "0.0"}

			dataDate = datetime.datetime.now()

			if (len(prices) > 0):
				currentMovingAverage = sum(prices) / float(len(prices))
				#previousPrice = prices[-1]

				# Trade placing decisions
				if (typeOfTrade == "short"):
					if ( float(lastPairPrice) < currentMovingAverage*(1-float(fees["takerRate"])) ):
						try:
							print("EXIT TRADE")
							tradePlaced = False
							typeOfTrade = False
							response = client.orders().cancel_by_id(client_order_id=generatedUuid)
							selling.pop()
						except polosdk.rest.request.RequestError as e:
							print(f"CAN'T CANCEL ORDER: {e}")
				elif (typeOfTrade == "long"):
					if ( float(lastPairPrice) > currentMovingAverage*(1+float(fees["takerRate"])) ):
						try:
							print("EXIT TRADE")
							tradePlaced = False
							typeOfTrade = False
							response = client.orders().cancel_by_id(client_order_id=generatedUuid)
							buying.pop()
						except polosdk.rest.request.RequestError as e:
							print(f"CAN'T CANCEL ORDER: {e}")
				if (not tradePlaced):
					generatedUuid = str(uuid.uuid4())
					if ( float(lastPairPrice) > currentMovingAverage*(1+float(fees["takerRate"])) and float(actualCurrency["available"]) > float(minimum)) and (float(lastPairPrice) < previousPrice):
						try:
							response = client.orders().create(price=float(lastPairPrice), quantity=quant, side='SELL', symbol=pair, type='LIMIT', client_order_id=generatedUuid) # maybe try market orders in the future
							selling.append([pair, float(lastPairPrice), quant, dataDate])
							print("SELL ORDER")
							tradePlaced = True
							typeOfTrade = "short"
						except polosdk.rest.request.RequestError as e:
							print(f"COULDN'T SELL: {e}")
					elif ( float(lastPairPrice) < currentMovingAverage*(1-float(fees["takerRate"])) and float(actualCurrency["available"]) < float(maxBuy) and (float(lastPairPrice) > previousPrice)):
						try:
							response = client.orders().create(price=float(lastPairPrice), quantity=quant, side='BUY', symbol=pair, type='LIMIT', client_order_id=generatedUuid) # maybe try market orders in the future
							buying.append([pair, float(lastPairPrice), quant, dataDate])
							print("BUY ORDER")
							tradePlaced = True
							typeOfTrade = "long"
						except polosdk.rest.request.RequestError as e:
							print(f"COULDN'T BUY: {e}")
			else:
				previousPrice = 0

			# Show resultant data
			totalSold = 0
			totalBought = 0
			for x in selling:
				if x[3] >= dataDate - datetime.timedelta(hours=12):
					totalSold += x[1]*x[2]
				else:
					selling.remove(x)
			for x in buying:
				if x[3] >= dataDate - datetime.timedelta(hours=12):
					totalBought += x[1]*x[2]
				else:
					buying.remove(x)


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
						response = client.orders().cancel(symbol=pair)
						sys.exit(2)


			if i >= 10:
				prices.append(float(lastPairPrice))
				prices = prices[-(lengthOfMA):]
				i = 0

			previousPrice = float(lastPairPrice)
		except polosdk.rest.request.RequestError as e:
			print(f"SOMETHING HAPPENED: {e}")
		i = i + 1
		time.sleep(int(period)/10)


if __name__ == "__main__":
	main(sys.argv[1:])