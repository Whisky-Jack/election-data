import wikipedia
import networkx as nx
import urllib.request
from bs4 import BeautifulSoup
import re

contents = urllib.request.urlopen("https://en.wikipedia.org/wiki/Historical_federal_electoral_districts_of_Canada").read()

section = wikipedia.WikipediaPage('Historical federal electoral districts of Canada')
years = section.links

regex = re.compile("(List of Canadian electoral districts)")

years = [s for s in years if regex.match(s)]


# Construct a dict for the riding names for the entire set of ridings
riding_dict = {}

class RidingObject:
    def __init__(self, name, province):
        self.name = name
        self.province = province

    def add_dates(self, start, end):
        self.start = start
        self.end = end

    def add_data(self, change, successors):
        self.change = change
        self.successors = successors

while True:
# Go through and obtain the riding names for every year
#for year in years:
    year = years[0]
    print(year)
    section = wikipedia.WikipediaPage(year)
    html = section.html()

    soup = BeautifulSoup(html, 'html.parser')

    # GET PROVINCES
    headers = soup.find_all(re.compile('^h[1-6]$'))
    #headers.pop(0)   #TODO: This is a hacky fix, should instead filter based on class or something

    provinces = ["Ontario", "Quebec", "British Columbia", "Manitoba", "Yukon", "Nova Scotia", "New Brunswick", "Newfoundland and Labrador", "Alberta", "Northwest Territories", "Nunavut", "Prince Edward Island", "Saskatchewan"]
    def getProvinceName(header):
        #print(header)
        header_span = header.findChildren("span" , recursive=False)[0]
        span_children = header_span.findChildren("a" , recursive=False)
        if (len(span_children) != 0):
            key = span_children[0].get("title") if len(span_children) == 1 else span_children[1].get("title")
            if (key not in provinces):
                print("")
            return key
        else:
            print("WARNING: missing key")
            content_string = header_span.get_text()
            data = re.findall("^.+?(?=\s\-\s)", content_string)
            if (len(data) == 0):
                raise Exception("Wrong kind of key")
            missing_key = data[0]
            print("Found ", missing_key)
            if (missing_key not in provinces):
                raise Exception("Wrong kind of key")
            return missing_key

    provinces = []
    for header in headers:
        try:
            name = getProvinceName(header)
            provinces.append(name)
        except:
            print("Not a valid province")
    #provinces = [getProvinceName(header) for header in headers]

    print(provinces)

    # GET ELECTORAL DISTRICT NAMES
    lists = soup.find_all("ul")
    lists.pop(0)
    content = lists[0]

    def getArticleTitles(ul_list):
        content = ul_list.findChildren("li")
        return [getArticleTitle(article) for article in content]

    def getArticleTitle(list_element):
        return list_element.findChildren("a" , recursive=False)[0].get("title")

    ridings_by_province = [getArticleTitles(list) for list in lists]

    for index, province in enumerate(provinces):
        for riding in ridings_by_province[index]:
            riding_dict[riding] = RidingObject(riding, province)
    break
#input()
print(len(riding_dict))
G = nx.Graph()

# Construct nodes for each member of the dict
G.add_nodes_from(riding_dict.items())
print(G.number_of_nodes())

article_title = ridings_by_province[0][0]
summary = wikipedia.WikipediaPage(article_title).summary
print(summary)
created_year = "yeet"
abolished_year = "yeet"

terms = ["redistributed", "merged", "abolished"]

# Find paragraph in which a keyword occurs

# Identify names in that paragraph

"""
#section = wikipedia.WikipediaPage('Metropolis (1927 film)').section('Plot')
section = wikipedia.WikipediaPage('Annapolis (electoral district)')
#section = section.replace('\n','').replace("\'","")
print(section)
print(section.summary)
print(section.links)
"""