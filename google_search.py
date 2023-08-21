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
    urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}
    url = 'https://www.bing.com/search?q=' + preprocess_article_text(claim)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    count = 0
    for link in soup.find_all("div", {"class": "b_title"}):
        if count == 7:
            break
        if link.find('a'):
            urls.append(link.find('a')['href'])
            count += 1
    articles = []

    # urls = ['https://www.ajc.com/news/national/immigration-can-undocumented-immigrants-get-federal-public-benefits/nyks4aB0PtTbbwVP9GyogI/', 'https://www.politifact.com/factchecks/2019/jan/28/donald-trump/fact-checking-donald-trumps-claim-cost-illegal-imm/']
    if(len(urls) == 0):
        return search_claim(param, claim)
    else:
        for url in urls:
            article = Article(url)
            try:
                article.download()
            except:
                printRed("Unable to download the article: " + url)
            try:
                article.parse()
                printGreen("Successfully parsed article " + url)
                articles.append(article)
            except:
                if parseAgain(url, article):
                    articles.append(articleAgain)
                    printGreen("Successfully parsed the article again :" + url)
                else:
                    printRed("Unable to parse the article again :" + url)
    return articles


def analyze_article(article, claim, n_relevant):
    print('Analyzing article ...')
    relevant_sentences = find_most_similar(article, claim)
    # if more than 5 relevant searches get first 5
    if len(relevant_sentences) > n_relevant:
        return relevant_sentences[0: n_relevant - 1]
    else:
        return None

def preprocess_article_text(text):
    text = text.replace('\n', '. ')
    text = text.replace('\t', '')
    return text


def do_research(param, userClaim):
    readClaim = read_claim(userClaim)
    print("Research started ...")
    c = 1
    printLightPurple(
        " C L A I M     # " + str(c) + " ========================================================================")
    relevant_articles = search_claim(param, readClaim.text)
    print(relevant_articles)
    analyzed_articles = []
    i = 1

    for a in relevant_articles:
        # articledata.text because of newspaper package
        if a.text != "":
            # links = analyze_urls(a)
            print("Processing article #" + str(i))  # NOTE: the article may or may not be added to the output file based on its length")
            # just creates a article data structure and fills up artcle.text and article.id

            article = Analyzed_article(a.text)
            # article.preprocessed_text just the articles text with . and no tabs
            article.preprocessed_text = preprocess_article_text(a.text)

            article.most_relevant_sent = analyze_article(article.preprocessed_text, readClaim.text,param['n_relevant_sent'])
            if article.most_relevant_sent is not None:
                if len(a.authors) > 0:
                    article.author = a.authors
                if a.publish_date is not None:
                    formatted_date = a.publish_date.strftime("%d-%b-%Y")
                    article.publish_date = formatted_date
                    article.year = a.publish_date.year
                if a.top_image != '':
                    article.image = a.top_image
                if a.summary != '':
                    article.summary = a.summary
                if len(a.keywords) > 0:
                    article.keywords = a.keywords
                if a.source_url != '':
                    article.source_url = a.source_url
                if a.url != '':
                    article.url = a.url
                if a.html != '':
                    article.html = a.html
                article.depth = 0
                analyzed_articles.append(article)
                i += 1
    c += 1

    readClaim.articles = analyzed_articles
    for a in readClaim.articles:
        analyze_urls(a, readClaim, 1)
        time.sleep(5)
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
        help="path_to the output file, each file has a claim and its analysis"
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
