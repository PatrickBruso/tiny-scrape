from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time

# get full html from tiny chart:
tiny = requests.get('https://tinychart.org/')
akita = requests.get('https://tinychart.org/asset/384303832')

# let BeautifulSoup format the html so you can read it
tiny_soup = BeautifulSoup(tiny.content, 'html.parser')
akita_soup = BeautifulSoup(akita.content, 'html.parser')

# look for the data you want in the output below.  I found it under the
# '<script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"assets":... container

# this took a while to read through, but you can find it by doing a ctrl-f for ' "name": '
#                                                 including double quotes but not single
# print(tiny_soup.prettify())
print(akita_soup.prettify())


# look for specifically the script we know our data is in:
data = tiny_soup.find('script', id="__NEXT_DATA__", type="application/json")

# unsorted complete data
coin_data = json.loads(data.contents[0])
# print(json.dumps(coin_data, indent=4, sort_keys=True))
AlgData = tiny_soup.find('span', "ant-tag").text
AlgoP = float(AlgData[AlgData.find('$') + 1:])
# print(AlgoP)


# we know where the name/supply/url... data is from the block above ({"props":{"pageProps":{"assets":...)

# basic coin data:
listings = coin_data['props']['pageProps']['assets']
counter = 0
for coin in listings:
    if coin['total_usd_reserves'] > 10000:
        # print(json.dumps(coin, indent=4, sort_keys=True))
        counter += 1
print(counter)
# print(json.dumps(listings, indent=4, sort_keys=True))

# but it looks like that's not all we need:

# pull a price dictionary.  By default you give it an id it returns that asset's price
# ie prices['000001'] would return the price of the coin with id=00001 (in theory...):
prices = coin_data['props']['pageProps']['prices']['assets']

# if you can find other properties in the coin_data please add it.  We really only need price and liquidity, which
# we have neither :(

# coin_data is a dictionary, so lets see all the keys (we've already explored the first 'props')
# for key in coin_data:
    # print(key)

# lets see whats in each:
# for key in coin_data:
    # print('------------------------------------------------------------------------------------------------')
    # print(key)
    # print('------------------------------------------------------------------------------------------------')
    # print(coin_data[str(key)])

# so, I guess the 'props' key is doing most of the heavy lifting....
# I can't find liquidity or a price that works, but let's see what we have:
# for poop in listings[0]:
#     print(poop)

# make a list for each data type found above
created = []
ID = []
name = []
ticker = []
decimals = []
total_usd_reserves = []
supply = []
circulating_supply = []
url = []
priority = []
verified = []
volatility = []
change24h = []
transactions = []

for i in listings:
    created.append(i['created'])
    ID.append(i['id'])
    name.append(i['name'])
    ticker.append(i['ticker'])
    decimals.append(i['decimals'])
    total_usd_reserves.append(i['total_usd_reserves'])
    supply.append(i['supply'])
    circulating_supply.append(i['circulating_supply'])
    url.append(i['url'])
    priority.append(i['priority'])
    verified.append(i['verified'])
    volatility.append(i['volatility'])
    change24h.append(i['change24h'])
    transactions.append(i['transactions'])

# make a dataframe out of the lists taken above
df = pd.DataFrame(list(
    zip(created, ID, name, ticker, decimals, total_usd_reserves, supply, circulating_supply, url, priority, verified,
        volatility, change24h, transactions)),
                  columns=['created', 'ID', 'name', 'ticker', 'decimals', 'total_usd_reserves', 'supply',
                           'circulating_supply', 'url', 'priority', 'verified', 'volatility', 'change24h',
                           'transactions'])

# date created is by default a combo of date and time, lets make a column out of each:
df['date_created'] = df['created'].apply(lambda x: x[0:10])
df['time_created'] = df['created'].apply(lambda x: x[11:])

# it looks like we have more coins than we have prices, if you look at the website you'll see
# there are some coins for which the price is untracked
# print(len(prices))
# print(len(df))

# filter out any dataframe elements for which there is no price stored (usually dead coins)
df = df[df['ID'].isin(prices)]
# reset the index because we've now removed a lot of entries and there are gaps in the index:
df.reset_index

# ------------------------------------------------------------------------------------------------------------------
#  Below this point nothing really works:
# I have no idea what the info in the price dictionary represents...
# ------------------------------------------------------------------------------------------------------------------

# make a column called price which takes the id from the ID column, turns it into a string
# and plugs it into the dictionary prices to return whatever value is cointained in the dictionary:
df['price'] = df['ID'].apply(lambda x: prices[str(x)])

# lets see what that looks like:
# df['price'].iloc[0]

# So the price values contain two numbers... at first glance maybe the first is the current price
# and the second is the price 1 hour ago?

# lets check this theory with Akita inu:
# pull the dataframe row that matches the Akita id:
df[df['ID'] == 384303832]

# return the prices value for that id:
prices['384303832']

# I went to tinychart and found Akita at the price:
# 0.008554,

# while the price key returned:
# 'price': 0.003809, 'price1h': 0.003833
# the dictionary value looks to be around half the price listed, maybe it's in algorand coins instead of usd?

# right now algo is selling at 2.20:
prices['384303832']['price'] * 2.20

# this gave me:
# 0.0083798

# as compared to the tinychart value of:
# 0.008554

# it could be arbitrage?  if so we should try to scrape the current algo price from tinycharts

# here's an example of how we can filter the dataframe to automatically pull the id for whatever
# coin had the most change in the last 24h:
maxid = df['ID'][df['change24h'] == df['change24h'].max()].values

# heres the price values for the coin that had the most change in 24h:
prices[str(maxid[0])]
