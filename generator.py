import wikipedia
import networkx as nx
import urllib.request
from bs4 import BeautifulSoup
import re
import csv

contents = urllib.request.urlopen("https://en.wikipedia.org/wiki/Historical_federal_electoral_districts_of_Canada").read()

section = wikipedia.WikipediaPage('Historical federal electoral districts of Canada')
years = section.links

regex = re.compile("(List of Canadian electoral districts)")

years = [s for s in years if regex.match(s)]


# Construct a dict for the riding names for the entire set of ridings
riding_dict = {}

class RidingObject:
    def __init__(self, name):
        self.name = name
        self.eras = []

class Era:
    def add_dates(self, start, end):
        self.start = start
        self.end = end

    def add_predecessor(self, predecessor_name):
        self.predecessors.append(predecessor_name)

    def add_successors(self, successors):
        self.successors = successors
    

# Go through and obtain the riding names for every year
for i in range(len(years)):#range(4): #range(len(years)):
    year = years[i]
    section = wikipedia.WikipediaPage(year)
    html = section.html()

    soup = BeautifulSoup(html, 'html.parser')

    # GET ELECTORAL DISTRICT NAMES
    lists = soup.find_all("ul")
    lists.pop(0)
    content = lists[0]

    def getArticleTitles(ul_list):
        content = ul_list.findChildren("li")
        return [getArticleTitle(article) for article in content]

    def getArticleTitle(list_element):
        return list_element.findChildren("a" , recursive=False)[0].get("title")

    ridings_by_province = [getArticleTitles(list_element) for list_element in lists]

    num_districts = 0
    for district_list in ridings_by_province:
        for riding in district_list:
            riding_dict[riding] = RidingObject(riding)
            num_districts += 1
    
    print("Year: ", year)
    print("Number of districts: ", num_districts)
    break

# Construct nodes for each member of the dict
G = nx.Graph()
G.add_nodes_from(riding_dict.items())

print("Number of entries in dict: ", len(riding_dict))
print("Number of nodes in graph: ", G.number_of_nodes())

# EXTRACT SUCCESSORS
def find_table(soup):
    # extract relevant table
    for header in soup.find_all('h2'):
        if (header.findChildren("span", id="Members_of_Parliament")):
            print("FOUND")
            table = header.findNext('table')
    existence_sections = table.find_all("td", align="center")

    # extract information on predecessors
    first = existence_sections[0]
    origin = first.find_all("b")[0]
    contents = origin.contents
    #TODO: may want to verify here that created word appears here
    children = origin.findChildren("a", recursive=False)
    predecessor_titles = [child.get("title") for child in children]

    print(predecessor_titles)

    # an ERA consists of 

    following_dates = first.parent.findNext("tr").findChildren("td", recursive=False)
    #print(following_dates)
    #print(table)

    terms = ["redistributed", "merged", "abolished", "dissolved", "amalgamated", "re-distributed"]

    return False

    """
    all_paragraphs = soup.find_all("p")

    #TODO: concatenate all contents
    contents = all_paragraphs[0].contents
    sliced_contents = contents
    # find first occurence of keyword in paragraph
    terms = ["redistributed", "merged", "abolished", "dissolved", "amalgamated", "re-distributed"]
    content_validator = re.compile("\.?[^\.]*%s[^\.]*" % '|'.join(terms))
    index = -1
    for paragraph in all_paragraphs:
        contents = paragraph.contents
        sliced_contents = contents
        for idx, element in enumerate(contents):
            if (isinstance(element, str) and content_validator.search(element)):
                index = idx
                sliced_contents = contents[index + 1:]
                #print(sliced_contents)
        if index > -1:
            break

    content_validator = re.compile(".*\..*")
    for idx, element in enumerate(sliced_contents):
        if (isinstance(element, str) and content_validator.search(element)):
            index = idx
            sliced_contents = sliced_contents[:index]

    # Filter children for valid electoral districts
    children = paragraph.findChildren("a", recursive=False)
    relevant_children = [child for child in children if child in sliced_contents]

    #print(relevant_children)
    valid_titles = list(riding_dict.keys())
    titles = [child.get("title") for child in relevant_children]
    #titles = [title for title in titles if title in valid_titles]

    print("################")
    print("Article title: ", article_title)
    print("Found successors: ", titles)
    return titles
    """

total = 0
successful = 0
electoral_districts = list(riding_dict.keys())

# Process districts and extract successors
with open('electoral_district_successors.csv', 'w', newline='') as successor_file:
    successor_writer = csv.writer(successor_file)
    
    for i in range(len(electoral_districts)):
        #article_title = electoral_districts[i]
        article_title = "Digby and Annapolis"
        riding_object = riding_dict.get(article_title)

        # Extract dates and successors
        summary = wikipedia.WikipediaPage(article_title).summary

        page = wikipedia.WikipediaPage(article_title)
        html = page.html()
        soup = BeautifulSoup(html, 'html.parser')

        table = find_table(soup)

        print(table)

        

        #successors = extract_successors(article_title)

        # Add data to object
        """
        riding_object.add_successors(successors)

        #NOTE: ASSERT THAT THE DATES WORK OUT WHEN ADDING TO GRAPH
        # Add dates
        extractDates(article_title)


        # Add edges in graph
        for successor in successors:
            successor_object = riding_dict.get(successor)
            if (not successor_object is None):
                successor_object.add_predecessor(article_title)
                G.add_edge(riding_object, successor_object)
        
        if (len(successors) > 0):
            successful += 1
        
        if (len(successors) == 0):
            successors = ["None found"]
        
        successor_contents = [article_title] + successors
        successor_writer.writerow(successor_contents)

        total += 1
        """
        break
"""
print("Percentage of ridings with at least one identified successor: ", 100*successful/total, "%")

total = 0
successful = 0

with open('electoral_district_predecessors.csv', 'w', newline='') as predecessor_file:
    predecessor_writer = csv.writer(predecessor_file)
    
    for i in range(len(electoral_districts)):
        article_title = electoral_districts[i]
        riding_object = riding_dict.get(article_title)
        predecessors = riding_object.predecessors

        if (len(predecessors) > 0):
            successful += 1
        
        if (len(predecessors) == 0):
            predecessors = ["None found"]
        
        predecessor_contents = [article_title] + predecessors
        predecessor_writer.writerow(predecessor_contents)

        total += 1
        break

print("Percentage of ridings with at least one identified predecessor: ", 100*successful/total, "%")
"""