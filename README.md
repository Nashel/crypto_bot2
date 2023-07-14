# crypto_bot

## Functionality

This bot makes queries to the Poloniex API to check the data and the historic of cryptocurrencies and decides the optimal moments to execute trades of a specific cryptocurrency.

## Usage

To execute this bot you have to modify the file "bot_simple.py" to specify your own keys.
In case that you only want to simulate trades make the changes indicated by comments on this document.

## Execution command

```
python3 bot_simple.py -p <period length> -c <currency pair> -n <period of moving average> -q <quantity of the indicated currency> -d <max difference between sell and buy transactions>
```

### -p period
  Indicates the period on which the bot will be checking and calculating if a trade should be placed.
  
### -c currency
  Indicates the currency that will be trading I.e.: "USDT_BTC".
  
### -n length of moving average
  Indicates the number of periods used to calculate the moving average, so the historical data consulted will be the last 'n*p' seconds.
  
### -q quantity to be placed for trade
  Indicates the quantity of the specified cryptocurrency that will be placed for each trade.

### -d difference between number of sell trades and buy trades
  Indicates the maximum number of sell and buy trades effectuated.
