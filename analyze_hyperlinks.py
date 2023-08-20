import logging
import optparse
from collections import OrderedDict
from urllib.request import Request, urlopen

from time import sleep

from AdvancedHTMLParser import AdvancedHTMLParser
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException

from bert_embeddings import *
from data_structures import Analyzed_article
from settings import global_counter1

from print_colors import *

from google_search import parseAgain

# called by analyze_urls right below, gets a single claim from the claims for loop in do_research()
# it's meant to extract the urls that are found in the one article (for all articles)
# urls = {1:[elink,elink,elink],2:[elink,elink,elink]}

MAX_RETRIES = 2


def parse_parameters(opts):
    param = OrderedDict()
    # param = {'input': inputfilename, 'output': outputfilename, 'stop','n_relevant_sent','top_search_results','json_visualization'}
    param['input'] = opts.input
    param['output'] = opts.output
    param['stop'] = opts.stop
    param['n_relevant_sent'] = opts.n_relevant_sent
    param['top_search_results'] = opts.top_search_results
    logging.info("PARAMETER LIST:_______________________________________________________________________")
    logging.info(param)

    return param


def extract_urls_from_html(article):
    urls = dict()
    # if i == 1:
    #     req = Request(
    #         url=article.url,
    #         headers={'User-Agent': 'Mozilla/5.0'}
    #     )
    #     webpage = urlopen(req).read()
    #     soup = BeautifulSoup(webpage, 'html.parser')
    #     all_p_urls = [tag['href'] for tag in soup.select('p a[href]')]
    #     for i, val in enumerate(all_p_urls):
    #         if "http" not in val:
    #             all_p_urls.pop(i)
    #     return all_p_urls
    parser = AdvancedHTMLParser()
    parser.parseStr(article.html)
    temp_links = parser.getElementsByTagName('a')
    # we fill up the article.text (datastructure) with article.text default from newspaper.py
    whole_article_text = article.text
    p_article_text = parser.getElementsByTagName('p')
    req = Request(
        url=article.url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    all_p_urls = [tag['href'] for tag in soup.select('p a[href]')]
    for i, val in enumerate(all_p_urls):
        if "http" not in val:
            all_p_urls.pop(i)
    # iterates over all links and takes the ones that are not empty
    tmp_links = [link for link in temp_links if not link.innerHTML.strip() == '']
    links = []
    # iterates over all nonempty links in that article
    for link in tmp_links:
        # if link is there in article.text datastructure which was filled up by article.text newspaper library
        if link.innerHTML in whole_article_text:
            # printCyan(link.innerHTML)
            links.append(link)
    urls[i] = links
    return all_p_urls[0:2]


def preprocess_article_text(text):
    text = text.replace('\n', '. ')
    text = text.replace('\t', '')
    return text


def analyze_article(article, claim, n_relevant):
    print('Analyzing article ...')
    relevant_sentences = find_most_similar(article, claim)
    # if more than 5 relevant searches get first 5
    if len(relevant_sentences) > n_relevant:
        return relevant_sentences[0: n_relevant - 1]
    else:
        return None


# called from do_research for each claim in the for loop
# ideally supposed to return all the relevant urls so that the json file can be filled up with this part
def analyze_urls(originalarticle, claim, depth):
    if depth < 2:
        all_urls = extract_urls_from_html(originalarticle)
        # all_urls = ['https://www.whitehouse.gov/briefings-statements/remarks-president-trump-signing-h-r-2-agriculture-improvement-act-2018/', 'https://www.nbcnews.com/politics/donald-trump/fact-check-how-much-does-illegal-immigration-cost-america-not-n950981', 'https://www.nbcnews.com/politics/donald-trump/fact-check-how-much-does-illegal-immigration-cost-america-not-n950981', 'https://www.nbcnews.com/politics/donald-trump/fact-check-how-much-does-illegal-immigration-cost-america-not-n950981', 'https://www.nbcnews.com/politics/donald-trump/fact-check-how-much-does-illegal-immigration-cost-america-not-n950981', 'https://www.nbcnews.com/politics/donald-trump/fact-check-how-much-does-illegal-immigration-cost-america-not-n950981']
        print("*****")
        print("URLs from articles")
        if claim.articles[0] == originalarticle:
            print("Links from orginal article 1")
        elif claim.articles[1] and claim.articles[1] == originalarticle:
            print("Links from orginal article 2")
        print(all_urls)
        print("*****")
        optparser = optparse.OptionParser()

        optparser.add_option(
            "-i", "--input", default="../input_data/enhanced_claims.txt",
            help="path to the file containing claims"
        )
        optparser.add_option(
            "-o", "--output", default="../output_data/claim",
            help="path_to the output file, each file has a claim and its analysis"
        )
        optparser.add_option(
            "-s", "--stop", default=2,
            help="number of claims to analyze"
        )
        optparser.add_option(
            "-r", "--n_relevant_sent", default=5,
            help="n most releveant sentences in each article."
        )
        optparser.add_option(
            "-t", "--top_search_results", default=10,
            help="limit research to the first r search results retrieved."
        )

        opts = optparser.parse_args()[0]
        param = parse_parameters(opts)
        # all_urls is the 5 urls
        for url in all_urls:
            article = Article(url)
            retries = 0
            while retries < MAX_RETRIES:
                article = Article(url)
                try:
                    article.download()
                    article.parse()
                    printGreen("Successfully parsed article " + url)
                    break
                except ArticleException as ae:
                    printRed("Error parsing the article: " + str(ae))
                    retries += 1
                    sleep(5)
                except Exception as e:
                    printRed("Unexpected error: " + str(e))
                    retries += 1
                    sleep(5)


            if article.text != "":
                printYellow(url)
                analyzed_article = Analyzed_article(article.text)

                # article.preprocessed_text just the articles text with . and no tabs
                analyzed_article.preprocessed_text = preprocess_article_text(article.text)

                analyzed_article.most_relevant_sent = analyze_article(analyzed_article.preprocessed_text, claim.text,
                                                                      param['n_relevant_sent'])

                if analyzed_article.most_relevant_sent is not None:
                    next(global_counter1)
                    if len(article.authors) > 0:
                        article.author = article.authors or ""
                    if article.publish_date is not None:
                        formatted_date = article.publish_date.strftime("%d-%b-%Y")
                        analyzed_article.publish_date = formatted_date
                        analyzed_article.year = article.publish_date.year
                    if article.top_image != '':
                        analyzed_article.image = article.top_image
                    if article.summary != '':
                        analyzed_article.summary = article.summary
                    if len(article.keywords) > 0:
                        analyzed_article.keywords = article.keywords
                    if article.source_url != '':
                        analyzed_article.source_url = article.source_url
                    if article.url != '':
                        analyzed_article.url = article.url
                    if article.html != '':
                        analyzed_article.html = article.html
                    analyzed_article.depth = depth
                if (analyzed_article.url != "UNKNOWN"):
                    printYellow(url)
                    originalarticle.articleurls.append(analyzed_article)
                    # loop with each article from original article
                    analyze_urls(analyzed_article, claim, depth + 1)
