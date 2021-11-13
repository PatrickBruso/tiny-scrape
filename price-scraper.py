"""
Program that scrapes the current price of Algorand from tinychart.org
"""

from bs4 import BeautifulSoup
import requests

# get full html from tinychart:
tiny = requests.get('https://tinychart.org/')

# let BeautifulSoup format the html so you can read it
tiny_soup = BeautifulSoup(tiny.content, 'html.parser')

# Find Algo price on tinychart and save to variable
algo_data = tiny_soup.find('span', "ant-tag").text
algo_price = float(algo_data[algo_data.find('$') + 1:])

print(f'Current price of Algo: ${algo_price}')
