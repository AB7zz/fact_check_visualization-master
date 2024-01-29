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
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36'}
            
        )
        webpage = urlopen(req,timeout=2000).read()
        soup = BeautifulSoup(webpage, 'html.parser')
        

        citation_urls_webpage = [tag['href'] for tag in soup.select('p a[href]')]
        print("# of citation urls found in article: ", len(citation_urls_webpage))
        

        valid_citation_articles = []
        for citation_url in citation_urls_webpage:
            try:
                citation_article = Article(citation_url)
                citation_article.download()
                citation_article.parse()
                if citation_article.text:
                    valid_citation_articles.append(citation_article)
            except Exception as e:
                print(f"Error: Could not parse citation article:" + str(citation_url))
                
        print("# Citation articles successfully downloaded from article: " + str(len(valid_citation_articles)) + "\n\n")
        return valid_citation_articles, len(valid_citation_articles)
        
    except Exception as e:
        print(f"Original article could not be parsed for links")
        return [], 0


def preprocess_article_text(text):
    text = text.replace('\n', '. ')
    text = text.replace('\t', '')
    return text


def analyze_article(article, claim, n_relevant):
    relevant_sentences, num_relevant_sentences = find_most_similar(article, claim)
    print("# relevant sentences", num_relevant_sentences)
    if len(relevant_sentences) > n_relevant:
        return relevant_sentences[0: n_relevant - 1], num_relevant_sentences
    else:
        return None, None
        
def check_citation_article_valid(citation_article,total_citation_articles, citation_article_idx, readClaim, depth):
    print("Processing citation article #" + str(citation_article_idx) + "/" + str(total_citation_articles)) 
    article = Analyzed_article(citation_article.text)
    article.preprocessed_text = preprocess_article_text(citation_article.text)
    article.most_relevant_sent, num_relevant_sentences = analyze_article(article.preprocessed_text, readClaim.text, 50)
    if article.most_relevant_sent is not None:
        next(global_counter1)
        if len(citation_article.authors) > 0:
            article.author = citation_article.authors
        if citation_article.publish_date is not None:
            formatted_date = citation_article.publish_date.strftime("%d-%b-%Y")
            article.publish_date = formatted_date
            article.year = citation_article.publish_date.year
        if citation_article.top_image != '':
            article.image = citation_article.top_image
        if citation_article.summary != '':
            article.summary = citation_article.summary
        if len(citation_article.keywords) > 0:
            article.keywords = citation_article.keywords
        if citation_article.source_url != '':
            article.source_url = citation_article.source_url
        if citation_article.url != '':
            article.url = citation_article.url
        if citation_article.html != '':
            article.html = citation_article.html
        article.depth = depth
        return [article, num_relevant_sentences]
    else:
        print("Citation article"+ str(citation_article_idx) +"not relevant")
        return None, None


def get_citation_articles(originalarticle, original_article_idx, total_original, readClaim, depth):
    if depth == 3:
        return
    print("Processing citation articles from originalarticle #" + str(original_article_idx) + "/" + str(total_original) + " depth: " + str(depth))
    print("Original article link (or recursive original article): ", originalarticle.url + "\n")
    
    valid_citation_articles, num_citation_articles = extract_articles_from_html(originalarticle)
    print("PHASE 4: CHECKING CITATION ARTICLES FOR RELEVANCY")
    final_citation_articles = []
    if num_citation_articles != 0:
        citation_article_idx = 1
        for citation_article in valid_citation_articles:
            analyzed_citation_res, num_relevant_sentences  = check_citation_article_valid(citation_article, num_citation_articles, citation_article_idx, readClaim, depth) 
            if analyzed_citation_res != None:
                final_citation_articles.append([analyzed_citation_res, num_relevant_sentences])
            citation_article_idx += 1
    final_citation_articles =  [x[0] for x in sorted(final_citation_articles, key=lambda x: x[1], reverse=True)[:5]]
    print("# Relevant citation articles(final)"+ str(len(final_citation_articles)) + "/" + str(num_citation_articles))
    print("PHASE 4: COMPLETE!\n\n")
    originalarticle.articleurls = final_citation_articles

    print("PHASE 5: RECURSIVE CALLS FOR CITATION ARTICLES")
    print("Recursive call for original article #" + str(original_article_idx))
    
    for final_citation_article in final_citation_articles:
        get_citation_articles(final_citation_article, original_article_idx, total_original, readClaim, depth+1)
        
    print("PHASE 5: COMPLETE!\n\n")

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
