from AdvancedHTMLParser import AdvancedHTMLParser
from helpers.print_colors import *

# called by analyze_urls right below, gets a single claim from the claims for loop in do_research()
# it's meant to extract the urls that are found in the one article (for all articles)
# urls = {1:[elink,elink,elink],2:[elink,elink,elink]}
def extract_urls_from_html(claim):
    urls = dict()
    for i, article in enumerate(claim.articles, start=1):
        parser = AdvancedHTMLParser()
        parser.parseStr(article.html)
        temp_links = parser.getElementsByTagName("a")
        # we fill up the article.text (datastructure) with article.text default from newspaper.py
        article_text = article.text
        printPurple(article_text)
        # iterates over all links and takes the ones that are not empty
        tmp_links = [link for link in temp_links if not link.innerHTML.strip()=='']
        links =[]
        # iterates over all nonempty links in that article
        for link in tmp_links :
            # if link is there in article.text datastructure which was filled up by article.text newspaper library
            if link.innerHTML in article_text:
                printCyan(link.innerHTML)
                links.append(link)
        urls[i] = links
    # urls = {}
    # claims.articles = for 1 claim you can have 5 articles
    return urls


# called from do_research for each claim in the for loop
# ideally supposed to return all the relevant urls so that the json file can be filled up with this part
def analyze_urls(claim):
    all_urls = extract_urls_from_html(claim)
    return all_urls