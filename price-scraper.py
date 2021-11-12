from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time

# get full html from tiny chart:
tiny = requests.get('https://tinychart.org/')

# let BeautifulSoup format the html so you can read it
tiny_soup = BeautifulSoup(tiny.content, 'html.parser')

# look for specifically the script we know our data is in:
data = tiny_soup.find('script', id="__NEXT_DATA__", type="application/json")

# unsorted complete data
coin_data = json.loads(data.contents[0])
# print(json.dumps(coin_data, indent=4, sort_keys=True))
AlgData = tiny_soup.find('span', "ant-tag").text
AlgoP = float(AlgData[AlgData.find('$') + 1:])
print(AlgoP)

# basic coin data:
listings = coin_data['props']['pageProps']['assets']
counter = 0
for coin in listings:
    if coin['total_usd_reserves'] > 10000:
        # print(json.dumps(coin, indent=4, sort_keys=True))
        counter += 1
print(counter)
print(json.dumps(listings, indent=4, sort_keys=True))
