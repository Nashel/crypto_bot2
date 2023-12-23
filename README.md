# crypto_bot

## Functionality

This bot makes queries to the Poloniex API https://api-docs.poloniex.com/spot/ to check the data and historic of cryptocurrencies and decides the optimal moments to execute trades of a specific cryptocurrency.

## Usage

To execute this bot you have to specify your own keys as Operative System variables ('POLO_API_KEY','POLO_API_SECRET'), and update the poloniex sdk.
The use of dockers is recommended.

## Execution command

```
python3 bot_simple.py -p <period length> -c <currency pair> -n <period of moving average> -q <quantity of the indicated currency> -s <failsafe> -m <maximum to buy> -l <minimum to sell>
```

### -p period
  Indicates the period on which the bot will be checking and calculating if a trade should be placed.
  
### -c currency
  Indicates the currency that will be trading I.e.: "USDT_BTC".
  
### -n length of moving average
  Indicates the number of periods used to calculate the moving average, so the historical data consulted will be the last 'n*p' seconds.
  
### -q quantity to be placed for trade
  Indicates the quantity of the specified cryptocurrency that will be placed for each trade.

### -s failsafe
  Indicates the percentage at which the failsafe is activated stopping the trading because amount lost was too high.

### -m maximum to buy
  Indicates the maximum amount of the specified currency can be held at a time.

### -l minimum to sell
  Indicates the minimum amount of the specified currency can be held at a time. This can be used in case you need to hold some of the currency to make another payments*

## Example of Batch Script starting trading
```
@echo off

REM ------------------ USDT_BTC ---------------------------------
REM Start Python script in a new Command Prompt window
start /high cmd /k python3 "C:\Users\nashel\proj\crypto_bot2\bot_simple.py" -p 60 -c BTC_USDT -n 450 -q 0.001 -s 0.002 -m 0.004


REM ------------------ USDT_ETH ---------------------------------
REM Start Python script in a new Command Prompt window
start /high cmd /k python3 "C:\Users\nashel\proj\crypto_bot2\bot_simple.py" -p 60 -c ETH_USDT -n 450 -q 0.02 -s 0.002 -m 0.06


REM ------------------ USDT_TRX ---------------------------------
REM Start Python script in a new Command Prompt window
start /high/high cmd /k python3 "C:\Users\nashel\proj\crypto_bot2\bot_simple.py" -p 60 -c TRX_USDT -n 450 -q 200 -s 0.002 -m 700 -l 110


REM ------------------ USDT_LTC ---------------------------------
REM Start Python script in a new Command Prompt window
start /high cmd /k python3 "C:\Users\nashel\proj\crypto_bot2\bot_simple.py" -p 60 -c LTC_USDT -n 450 -q 0.3 -s 0.002 -m 0.6
```
  In this case we use the TRX_USDT minimum because we are paying the transaction fees with it
  
## Warning
  Cryptocurrency trading involves significant risk and is highly volatile. Prices can change rapidly, leading to potential gains or losses. Use this bot at your own risk and be aware that I am not responsible for any financial decisions made based on its information. Invest wisely and only what you can afford to lose.