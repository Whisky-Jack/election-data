import wikipedia
import networkx as nw
import urllib.request
from bs4 import BeautifulSoup
import re

contents = urllib.request.urlopen("https://en.wikipedia.org/wiki/Historical_federal_electoral_districts_of_Canada").read()

section = wikipedia.WikipediaPage('Historical federal electoral districts of Canada')
years = section.links

regex = re.compile("(List of Canadian electoral districts)")

years = [s for s in years if regex.match(s)]
#print(years)

year = years[0]

print(year)
section = wikipedia.WikipediaPage(year)
html = section.html()

soup = BeautifulSoup(html, 'html.parser')

headers = soup.find_all(re.compile('^h[1-6]$'))#, "span"])
headers.pop(0)   #TODO: This is a hacky fix, should instead filter based on class or something

def getProvinceName(header):
    return header.findChildren("span" , recursive=False)[0].findChildren("a" , recursive=False)[0].get("title")

provinces = [getProvinceName(header) for header in headers]

print(provinces)

"""
print(headers[1])
print("HOLY FUCK ###################################################")
print(headers[1].findChildren("span" , recursive=False)[0].findChildren("a" , recursive=False)[0].get("title"))
print("HOLY FUCK ###################################################")
print(header_contents)
provinces = [elem.get("title") for elem in header_contents]
"""


lists = soup.find_all("ul")#, {"id": "h2"})
#print(lists)

"""
#section = wikipedia.WikipediaPage('Metropolis (1927 film)').section('Plot')
section = wikipedia.WikipediaPage('Annapolis (electoral district)')
#section = section.replace('\n','').replace("\'","")
print(section)
print(section.summary)
print(section.links)
"""