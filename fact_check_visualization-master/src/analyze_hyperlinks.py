from AdvancedHTMLParser import AdvancedHTMLParser
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from helpers.print_colors import *


# called by analyze_urls right below, gets a single claim from the claims for loop in do_research()
# it's meant to extract the urls that are found in the one article (for all articles)
# urls = {1:[elink,elink,elink],2:[elink,elink,elink]}
def extract_urls_from_html(claim):
    urls = dict()
    for i, article in enumerate(claim.articles, start=1):
        print("****************")
        parser = AdvancedHTMLParser()
        parser.parseStr(article.html)
        temp_links = parser.getElementsByTagName('a')
        # we fill up the article.text (datastructure) with article.text default from newspaper.py
        whole_article_text = article.text
        p_article_text = parser.getElementsByTagName('p')
        print(article.url)

        req = Request(
            url=article.url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')
        all_p_urls = [tag['href'] for tag in soup.select('p a[href]')]

        for p in all_p_urls:
            print(p)

        # iterates over all links and takes the ones that are not empty
        tmp_links = [link for link in temp_links if not link.innerHTML.strip() == '']

        # for link in tmp_links:
        #     print(link.innerHTML)
        links = []
        # iterates over all nonempty links in that article
        for link in tmp_links:
            # if link is there in article.text datastructure which was filled up by article.text newspaper library
            if link.innerHTML in whole_article_text:
                # printCyan(link.innerHTML)
                links.append(link)
        urls[i] = links
    # urls = {}
    # claims.articles = for 1 claim you can have 5 articles
    print("****************")
    return urls


# called from do_research for each claim in the for loop
# ideally supposed to return all the relevant urls so that the json file can be filled up with this part
def analyze_urls(claim):
    all_urls = extract_urls_from_html(claim)
    return 0
