import logging
import optparse
from collections import OrderedDict
import urllib.parse
from urllib.request import Request, urlopen
from time import sleep
from AdvancedHTMLParser import AdvancedHTMLParser
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException, Config
from bert_embeddings import *
from data_structures import Analyzed_article
from settings import global_counter1
from print_colors import *
from google_search import *

def extract_articles_from_html(article):
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
        citation_urls_webpage = [tag['href'] for tag in soup.select('p a[href]')]
        print("# of citation urls found in article: ", len(citation_urls_webpage))
        
        # Filter out invalid citation articles
        valid_citation_articles = []
        for citation_url in citation_urls_webpage:
            try:
                citation_article = Article(citation_url)
                citation_article.download()
                citation_article.parse()
                if citation_article.text != None:
                    valid_citation_articles.append(citation_article)
            except:
                print(f"Error: Could not parse citation article : ", citation_url)
                
        print("# Citation articles successfully downloaded from article: " + len(valid_citation_articles) + "\n\n")
        return valid_citation_articles, len(valid_citation_articles)
        
    except:
        print("Orignal article could not be parsed for links")
        return None, None


def preprocess_article_text(text):
    processed_text = urllib.parse.quote_plus(text)
    return processed_text


def analyze_article(article, claim, n_relevant):
    print('Analyzing article ...')
    relevant_sentences = find_most_similar(article, claim)
    # if more than 5 relevant searches get first 5
    if len(relevant_sentences) > n_relevant:
        return relevant_sentences[0: n_relevant - 1]
    else:
        return None


def get_citation_articles(originalarticle, original_article_idx, total_original, claim, depth):
    print("Processing citation articles from originalarticle #" + str(original_article_idx) + "/" + str(total_original))
    print("Original article link: ", originalarticle.url)
    # while depth < 3:
    valid_citation_articles, num_citation_articles = extract_articles_from_html(originalarticle)

        
        

        # for url in all_urls:
        #     retries = 0
        #     while retries < MAX_RETRIES:
        #         config = Config()
        #         config.request_timeout = 5  # Increase the timeout to 20 seconds

        #         article = Article(url, config=config)
        #         try:
        #             article.download()
        #             article.parse()
        #             if article.text != "":
        #                 analyzed_article = Analyzed_article(article.text)
        #                 analyzed_article.preprocessed_text = preprocess_article_text(article.text)
        #                 analyzed_article.most_relevant_sent = analyze_article(analyzed_article.preprocessed_text, claim.text, 2)
        #                 if analyzed_article.most_relevant_sent is not None:
        #                     next(global_counter1)
        #                     if len(article.authors) > 0:
        #                         article.author = article.authors or ""
        #                     if article.publish_date is not None:
        #                         formatted_date = article.publish_date.strftime("%d-%b-%Y")
        #                         analyzed_article.publish_date = formatted_date
        #                         analyzed_article.year = article.publish_date.year
        #                     if article.top_image != '':
        #                         analyzed_article.image = article.top_image
        #                     if article.summary != '':
        #                         analyzed_article.summary = article.summary
        #                     if len(article.keywords) > 0:
        #                         analyzed_article.keywords = article.keywords
        #                     if article.source_url != '':
        #                         analyzed_article.source_url = article.source_url
        #                     if article.url != '':
        #                         analyzed_article.url = article.url
        #                     if article.html != '':
        #                         analyzed_article.html = article.html
        #                     analyzed_article.depth = depth
        #                 if analyzed_article.url != "UNKNOWN":
        #                     originalarticle.articleurls.append(analyzed_article)
        #                     analyze_urls(analyzed_article, claim, depth + 1)
        #                 break  # Exit the loop on success
        #         except ArticleException as ae:
        #             printRed("Error parsing the article: " + str(ae))
        #             break
        #             retries += 1
        #             sleep(5)  # Wait for 5 seconds before retrying
        #         except Exception as e:
        #             printRed("Unexpected error: " + str(e))
        #             retries += 1
        #             sleep(5)
