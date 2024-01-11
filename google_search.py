# from random import randrange

import nltk
import requests

from flask import Flask, request, render_template
from flask_cors import CORS
import time
from analyze_hyperlinks import *
from bert_embeddings import *
from print_colors import *
# import settings
from read_write import *
from settings import global_counter1
# from googlesearch import search

nltk.download('punkt')

app = Flask(__name__, static_folder='static')
CORS(app)

# tld : tld stands for top level domain which means we want to search our result on google.com or google.in or some other domain.
# lang : lang stands for language.
# num : Number of results we want.
# start : First result to retrieve.
# stop : Last result to retrieve. Use None to keep searching forever.
# pause : Lapse to wait between HTTP requests. Lapse too short may cause Google to block your IP. Keeping significant lapse will make your program slow but its safe and better option.
# Return : Generator (iterator) that yields found URLs. If the stop parameter is None the iterator will loop forever.

# opts has all links defined in optparser
# we do this to make quicker access to these links
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

def parseAgain(url, article):
    printYellow("Trying to parse " + url + " AGAIN")
    try:
        article.download()
    except:
        printRed("Unable to download the article: " + url)
    try:
        article.parse()
        printGreen('OK')
        return True
    except:
        printGreen('NO')
        return False
    

def search_claim(param, claim):
    print("PHASE 1: GETTING UPTO 10 RESULTS FROM BING")
    urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}
    url = 'https://www.bing.com/search?q=' + preprocess_article_text(claim)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    print('URL in bing', url)

    count_results = 0
    articles = []
    downloaded_articles_urls = []
    
    for result in soup.find_all('li', class_='b_algo'):
        count_results += 1
        result_link = result.find('bing_article')['href']
        try:  
            article = Article(result_link)
            article.download()
            article.parse()
            if article.text != None:
                articles.append(article)
        except:
            printRed("Unable to download/parse the article: " + result_link)
    
    print("# Search results from bing: ", count_results)
    print("# Articles successfully downloaded and parsed from BING: ", len(articles))
    print("Articles from BING: ",downloaded_articles_urls)
    print("PHASE 1: COMPLETE!")
    return articles,len(articles)

def preprocess_article_text(text):
    text = text.replace('\n', '. ')
    text = text.replace('\t', '')
    return text

def analyze_article(article, claim, n_relevant):
    relevant_sentences = find_most_similar(article, claim)
    # if more than 5 relevant searches get first 5
    if len(relevant_sentences) > n_relevant:
        return relevant_sentences[0: n_relevant - 1]
    else:
        return None

def check_BING_article_valid(bing_article,total_bing_articles,article_idx)
    print("Processing BING article #" + str(article_idx) + "/" + str(total_bing_articles)) 
    
    article = Analyzed_article(bing_article.text)
    article.preprocessed_text = preprocess_article_text(bing_article.text)
    article.most_relevant_sent = analyze_article(article.preprocessed_text, readClaim.text,param['n_relevant_sent'])
    if article.most_relevant_sent is not None:
        if len(bing_article.authors) > 0:
            article.author = bing_article.authors
        if bing_article.publish_date is not None:
            formatted_date = bing_article.publish_date.strftime("%d-%b-%Y")
            article.publish_date = formatted_date
            article.year = bing_article.publish_date.year
        if bing_article.top_image != '':
            article.image = bing_article.top_image
        if bing_article.summary != '':
            article.summary = bing_article.summary
        if len(bing_article.keywords) > 0:
            article.keywords = bing_article.keywords
        if bing_article.source_url != '':
            article.source_url = bing_article.source_url
        if bing_article.url != '':
            article.url = bing_article.url
        if bing_article.html != '':
            article.html = bing_article.html
        article.depth = 0
        return article
    else:
        print("Bing article"+str(article_idx)+"not relevant")
        return None

                


def do_research(param, userClaim):
    readClaim = read_claim(userClaim)
    print("Research started ...")

    bing_articles_P1,total_bing_articles = search_claim(param, readClaim.text)
    
    print("PHASE 2: FILTERING BING ARTICLES BASED ON RELEVANCY")
    final_bing_articles = []
    article_idx = 1
    for bing_article in bing_articles_P1:
        analyzed_bing_res = check_BING_article_valid(bing_article,total_bing_articles,article_idx) 
        if analyzed_bing_res != None:
            final_bing_articles.append(analyzed_bing_res)
        article_idx += 1
    
    readClaim.articles = final_bing_articles
    print("# Relevant bing articles(final)"+ str(len(final_bing_articles)))
    print("Relevant bing articles:", final_bing_articles)
    print("PHASE 2 COMPLETE!")
    
    # for bing_article in readClaim.articles:
    #     analyze_urls(bing_article, readClaim, 1)
    return write_json_visualization(param, readClaim)




@app.route('/')
def home():
    return render_template('home/index.html')

@app.route('/claimmap/visualization')
def visualization():
    return render_template('visualization/index.html')

@app.route('/claimmap/search', methods=['POST'])
def search():
    print('search is invoked')
    next(global_counter1)
    optparser = optparse.OptionParser()

    data = request.get_json()
    userClaim = data.get('value')

    print(userClaim)

    optparser.add_option(
        "-i", "--input", default="../input_data/enhanced_claims.txt",
        help="path to the file containing claims"
    )
    optparser.add_option(
        "-o", "--output", default="../output_data/claim",
        help="path_to the output file, each file has bing_article claim and its analysis"
    )
    optparser.add_option(
        "-s", "--stop", default=1,
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
    json = do_research(param, userClaim)
    return json


# it's so that you can run it with -i etc
if __name__ == '__main__':
    # app.run(port=8000, debug=True)
    app.run(host='192.168.1.10', port=8101, debug=True)

# html = requests.get(...).text
# text = fulltext(html)
