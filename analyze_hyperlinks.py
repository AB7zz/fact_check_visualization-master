import logging
import optparse
from collections import OrderedDict
from urllib.request import Request, urlopen
from time import sleep
from AdvancedHTMLParser import AdvancedHTMLParser
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException, Config
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
    try:
        parser = AdvancedHTMLParser()
        parser.parseStr(article.html)
        temp_links = parser.getElementsByTagName('a')
        whole_article_text = article.text
        p_article_text = parser.getElementsByTagName('p')

        req = Request(
            url=article.url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')
        all_p_urls = [tag['href'] for tag in soup.select('p a[href]')]

        # Filter out invalid URLs
        valid_urls = []
        for url in all_p_urls:
            if url.startswith('http://') or url.startswith('https://') and not url.lower().endswith('.pdf'):
                valid_urls.append(url)

        # Return the first two valid URLs
        return valid_urls[:2]

    except Exception as e:
        # Handle parsing or network errors here
        print(f"Error: {e}")
        return []

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


def analyze_urls(originalarticle, claim, depth):
    if depth < 3:
        all_urls = extract_urls_from_html(originalarticle)
        print("*****")
        print("2 URLs from originalarticle ")
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
            "-s", "--stop", default=10,
            help="number of claims to analyze"
        )
        optparser.add_option(
            "-r", "--n_relevant_sent", default=5,
            help="n most releveant sentences in each article."
        )
        optparser.add_option(
            "-t", "--top_search_results", default=15,
            help="limit research to the first r search results retrieved."
        )

        opts = optparser.parse_args()[0]
        param = parse_parameters(opts)
 import logging
import optparse
from collections import OrderedDict
from urllib.request import Request, urlopen

from time import sleep

from AdvancedHTMLParser import AdvancedHTMLParser
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException,Config

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
    try:
        parser = AdvancedHTMLParser()
        parser.parseStr(article.html)
        temp_links = parser.getElementsByTagName('a')
        whole_article_text = article.text
        p_article_text = parser.getElementsByTagName('p')

        req = Request(
            url=article.url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')
        all_p_urls = [tag['href'] for tag in soup.select('p a[href]')]

        # Filter out invalid URLs
        valid_urls = []
        for url in all_p_urls:
            if url.startswith('http://') or url.startswith('https://') and not url.lower().endswith('.pdf'):
                valid_urls.append(url)

        # Return the first two valid URLs
        return valid_urls[:2]

    except Exception as e:
        # Handle parsing or network errors here
        print(f"Error: {e}")
        return []

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


def analyze_urls(originalarticle, claim, depth):
    if depth < 3:
        all_urls = extract_urls_from_html(originalarticle)
        print("*****")
        print("2 URLs from originalarticle ")
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
            "-s", "--stop", default=10,
            help="number of claims to analyze"
        )
        optparser.add_option(
            "-r", "--n_relevant_sent", default=5,
            help="n most releveant sentences in each article."
        )
        optparser.add_option(
            "-t", "--top_search_results", default=15,
            help="limit research to the first r search results retrieved."
        )

        opts = optparser.parse_args()[0]
        param = parse_parameters(opts)
        for url in all_urls:
            retries = 0
            while retries < MAX_RETRIES:
                config = Config()
                config.request_timeout = 20  # Increase the timeout to 20 seconds

                article = Article(url, config=config)
                try:
                    article.download()
                    article.parse()
                    if article.text != "":
                        analyzed_article = Analyzed_article(article.text)
                        analyzed_article.preprocessed_text = preprocess_article_text(article.text)
                        analyzed_article.most_relevant_sent = analyze_article(analyzed_article.preprocessed_text, claim.text, param['n_relevant_sent'])
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
                        if analyzed_article.url != "UNKNOWN":
                            originalarticle.articleurls.append(analyzed_article)
                            analyze_urls(analyzed_article, claim, depth + 1)
                        break  # Exit the loop on success
                except ArticleException as ae:
                    printRed("Error parsing the article: " + str(ae))
                    retries += 1
                    sleep(5)  # Wait for 5 seconds before retrying
                except Exception as e:
                    printRed("Unexpected error: " + str(e))
                    retries += 1
                    sleep(5)
