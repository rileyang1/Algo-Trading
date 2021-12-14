from binance import Client
import matplotlib
import pandas as pd

# your api_key and api_secret from binance
api_key = " "
api_secret = " "

# instantiating client object
client = Client(api_key, api_secret)

# getting historic 1min interval price data from binance - candlesticks and parsing into dataframe
# pd.DataFrame(client.get_historical_klines('BTCUSDT', '1m', '30 m ago UTC'))

def getMinuteData(symbol, interval, lookback):
    df = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + ' min ago UTC'))
    
    # slicing till 6th column, rest of columns not needed as referenced from python-binance documentation
    df = df.iloc[: , :6]

    # naming columns
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']

    # setting index of df to Time column
    df = df.set_index('Time')

    # manipulating timestamp
    df.index = pd.to_datetime(df.index, unit='ms')

    # changing column data to float values
    df = df.astype(float)

    return df

# test = getMinuteData('BTCUSDT', '1m', '30')
# test.Open.plot()

# simplified test trading strategy
# buy if asset fell more than 0.2% within last 30 min
# sell if asset rises by more than 0.15% (breakeven point) OR falls further by 0.15%

def testStrat(symbol, qty, entry=False):
    df = getMinuteData(symbol, '1m', '30')

    # cumulative returns over last 30min
    cumulreturn = (df.Open.pct_change() + 1).cumprod() - 1

    # if not bought, defining buying condition
    if not entry:
        # checking very last element of vector < -0.002
        if cumulreturn[-1] < -0.002:
            order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
            print(order)
            entry=True
        else:
            print('No trade executed')
            
        
    # if bought, define selling condition
    if entry:
        while True:
            # request data in infinite loop
            df = getMinuteData(symbol, '1m', '30m')

            # how asset is performing since purchase
            # screen for index (time stamp) after time stamp of order
            sincebuy = df.loc[df.index > pd.to_datetime(order['transactTime'], unit='ms')]

            # sincebuy must be > 0 to view returns
            if len(sincebuy) > 0:
                sincebuyreturn = (sincebuy.Open.pct_change() + 1).cumprod() - 1

                # sell condition
                if sincebuyreturn[-1] > 0.0015 or sincebuyreturn[-1] < -0.0015:
                    order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                    print(order)
                    break

testStrat('DEGOUSDT', 0.1)


