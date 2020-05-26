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
#years = years[9:]
years = years[-5:]


# Construct a dict for the riding names for the entire set of ridings
riding_dict = {}

class RidingObject:
    def __init__(self, name):
        self.name = name
        self.eras = []
        self.elections = []

class Era:
    def __init__(self, start, end, predecessors, successors):
        self.start = start
        self.end = end
        self.predecessors = predecessors
        self.successors = successors

    def add_dates(self, start, end):
        self.start = start
        self.end = end

    def add_predecessors (self, predecessors):
        self.predecessors = predecessors

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
    #break

# Construct nodes for each member of the dict
G = nx.Graph()
G.add_nodes_from(riding_dict.items())

print("Number of entries in dict: ", len(riding_dict))
print("Number of nodes in graph: ", G.number_of_nodes())

# Want to create a series of eras:
# Want to extract predecessors, successors and dates for each era
# Need to handle edge cases

# EXTRACT SUCCESSORS
# TODO: handle case where predecessors are not explictly indicated (assume they are the previous successors)
def scrape_table_information(soup):
    # extract relevant table
    table = None
    for header in soup.find_all('h2'):
        #valid_ids = ["Members_of_Parliament", "Members of the Legislative Assembly"]
        """
        print("#################################")
        print(header)
        print("#######")
        print(header.findChildren("span", id="Members_of_the_Legislative_Assembly"))
        """
        if (header.findChildren("span", id="Members_of_Parliament")):# or header.findChildren("span", id="Members_of_the_Legislative_Assembly_.2F_National_Assembly")):
            table = header.findNext('table')
    if table is None:
        for header in soup.find_all('h2'):
        #valid_ids = ["Members_of_Parliament", "Members of the Legislative Assembly"]
        #print("#################################")
        #print(header)
        #print(header.findChildren("span", id="Members_of_the_Legislative_Assembly"))
            if header.findChildren("span", id="History"):# or header.findChildren("span", id="Members_of_the_Legislative_Assembly")):
                table = header.findNext('table')
    if table is None:
        return False

    table_tds = table.find_all("td", align="center")

    def check_inclusion(table_td):
        if (table_td.parent.has_attr('bgcolor') and table_td.has_attr('bgcolor')):
            return table_td.parent['bgcolor'] == '#F0F0F0' or table_td['bgcolor'] == '#F0F0F0'
        elif table_td.parent.has_attr('bgcolor'):
            return table_td.parent['bgcolor'] == '#F0F0F0'
        elif table_td.has_attr('bgcolor'):
            return table_td['bgcolor'] == '#F0F0F0'
        else:
            return False

    table_tds = [table_td for table_td in table_tds if check_inclusion(table_td)]
    parents = [table_td.parent for table_td in table_tds]
    table_trs = table.find_all("tr")

    # an ERA consists of a start date, and end date a set of predecessors and a set of successors
    dates_regex = re.compile("[0-9]{4}\s?(\-|\–)\s?[0-9]{4}") # re.compile(".*")#
    first_date_regex = re.compile("[0-9]{4}")
    #print(existence_sections[2])
    eras = []
    for existence_section in table_tds:
        #print("EXISTENCE: ", existence_section)
        # find start date
        tr = existence_section.findNext("tr")
        
        # if there is no next section, exit loop
        if tr not in table_trs:
            break

        # handle case where riding is recreated
        if existence_section.parent.next_sibling.next_sibling not in parents:
            tds = tr.findChildren("td", recursive=False)
            td_text = [td.get_text() for td in tds]
            next_dates = list(filter(dates_regex.search, td_text))
            start_date = first_date_regex.findall(next_dates[0])[0]

            # find predecessors
            origin = existence_section.find_all("b")[0]
            contents = origin.contents
            #TODO: may want to verify here that created word appears here
            children = origin.findChildren("a", recursive=False)
            predecessor_titles = [child.get("title") for child in children]

            # find sibling section
            partner = existence_section.findNext("td", align="center")
            if partner is None or partner not in table_tds:
                last_dates = table_trs[-1]

                td_text = [td.get_text() for td in tds]
                next_dates = list(filter(dates_regex.search, td_text))
                end_date = first_date_regex.findall(next_dates[0])[-1]
                successor_titles = ["None found"]
            else:
                tds = partner.parent.findPrevious("tr").findChildren("td", recursive=False)
                td_text = [td.get_text() for td in tds]
                next_dates = list(filter(dates_regex.search, td_text))
                end_date = first_date_regex.findall(next_dates[0])[-1]

                # find successors
                origin = partner.find_all("b")[0]
                contents = origin.contents
                #TODO: may want to verify here that created word appears here
                children = origin.findChildren("a", recursive=False)
                successor_titles = [child.get("title") for child in children]

                # handle case of renaming
                if (len(successor_titles) == 0):
                    print("Well shit")
            
            # create era
            print("Start date: ", start_date)
            print("End date: ", end_date)
            print("Predecessors :", predecessor_titles)
            print("Successors", successor_titles)
            eras.append(Era(start_date, end_date, predecessor_titles, successor_titles))
        else:
            print("Riding re-created")

    #print(following_dates)
    #print(table)

    #terms = ["redistributed", "merged", "abolished", "dissolved", "amalgamated", "re-distributed"]

    return eras

def scrape_non_table_information(soup):
    all_paragraphs = soup.find_all("p")
    #TODO: concatenate all contents
    contents = all_paragraphs[0].contents
    sliced_contents = contents

    def extract_titles(keywords):
        content_validator = re.compile("\.?[^\.]*%s[^\.]*" % '|'.join(predecessor_terms))
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
        return titles
    
    # find predecessors, if any
    predecessor_terms = ["created"]
    predecessor_titles = extract_titles(predecessor_terms)
    
    # find successors, if any

    # find first occurence of keyword in paragraph
    successor_terms = ["redistributed", "merged", "abolished", "dissolved", "amalgamated", "re-distributed"]
    successor_titles = extract_titles(predecessor_terms)

    # find dates of existence
    start_date = "Not implemented"
    end_date = "Not implemented"

    # construct simple era
    eras = [Era(start_date, end_date, predecessor_titles, successor_titles)]

    print("################")
    print("Article title: ", article_title)
    print("Found successors: ", titles)
    return titles


total = 0
approach_1 = 0
approach_2 = 0
electoral_districts = list(riding_dict.keys())

# Process districts and extract successors
with open('electoral_district_successors.csv', 'w', newline='') as successor_file:
    successor_writer = csv.writer(successor_file)
    
    for i in range(len(electoral_districts)):
        article_title = electoral_districts[i]
        #article_title = "Digby and Annapolis"Shelburne—Yarmouth—Clare
        #article_title = "Shelburne—Yarmouth—Clare"
        #article_title = "New Westminster—Coquitlam"
        #article_title = "New Westminster—Burnaby"

        print("#########################################################")
        print(article_title, " with index ", i)

       # if (i != 2 and i != 7):
        riding_object = riding_dict.get(article_title)

        # Extract dates and successors
        bad_names = ["Brant North", "Brant South"]
        if (article_title not in bad_names):
            summary = wikipedia.WikipediaPage(article_title).summary

            page = wikipedia.WikipediaPage(article_title)
            html = page.html()
            soup = BeautifulSoup(html, 'html.parser')

            eras = scrape_table_information(soup)

            if (eras):
                riding_object.eras = eras
                riding_object.approach = "Table approach"
                approach_1 += 1
            """
            else:
                eras = scrape_non_table_information(article_title)
                riding_object.approach = "Summary approach"
                approach_2 += 1
            """
        total += 1
        print("Running percentage: ", 100*approach_1/total)
        

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
        #break
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