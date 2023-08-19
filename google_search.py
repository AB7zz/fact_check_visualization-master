# from random import randrange

import nltk
import requests

from flask import Flask, request, render_template
from flask_cors import CORS

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
    



# called from do_research(param)
# search_claim(param,1 claim's text)
# makes google search about that claim and returns an array of all articles in order what appeared on google first
def search_claim(param, claim):
    print("Searching with Google ...")
    urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}
    url = 'https://www.bing.com/search?q=' + preprocess_article_text(claim)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    urls = []
    count = 0
    for link in soup.find_all("div", {"class": "b_title"}):
        if count == 2:
            break

        if link.find('a'):
            urls.append(link.find('a')['href'])
            count += 1
    # urls =[articlelink,articlelink,articlelink] from google

    articles = []

    urls = ['https://www.ajc.com/news/national/immigration-can-undocumented-immigrants-get-federal-public-benefits/nyks4aB0PtTbbwVP9GyogI/', 'https://www.politifact.com/factchecks/2019/jan/28/donald-trump/fact-checking-donald-trumps-claim-cost-illegal-imm/']
    print(urls)
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
    # articles = [articledata,articledata,articledata]
    return articles



# called by do_research to fill up Analyzed_Article.most_relevant_sent[sentences from articles in order of similarity]
# we put those sentences in order using the find_most_similar in bert_embedding

# analyze_article(articles text, claims text, 5)
def analyze_article(article, claim, n_relevant):
    print('Analyzing article ...')
    relevant_sentences = find_most_similar(article, claim)
    # if more than 5 relevant searches get first 5
    if len(relevant_sentences) > n_relevant:
        return relevant_sentences[0: n_relevant - 1]
    else:
        return None
    # image = article.top_image
    # nlp = article.nlp()
    # keywords = article.keywords
    # summary = article.summary
    # authors = article.authors
    # date = article.publish_date


# called from do_research(article.text)
# just put . in the end of article etc
def preprocess_article_text(text):
    text = text.replace('\n', '. ')
    text = text.replace('\t', '')
    return text


def do_research(param, userClaim):
    # claims = read_claims(param['input'])
    readClaim = read_claim(userClaim)
    print("Research started ...")
    c = 1

    printLightPurple(
        " C L A I M     # " + str(c) + " ========================================================================")
    # max 2 articles at a time
    # search_claim(6 links,claims[claim.text])
    # in order of what article came on top of the google search
    relevant_articles = search_claim(param, readClaim.text)
    # relevant articles = [articledata,articledata,articledata]
    analyzed_articles = []
    i = 1
    # a = single article data

    # FROM HERE WE FILL THE ARTICLE DATASTRUCTURE FOR EACH ARTICLE FOR THAT CLAIM

    for a in relevant_articles:
        # articledata.text because of newspaper package
        if a.text != "":
            # links = analyze_urls(a)
            print("Processing article #" + str(
                i))  # NOTE: the article may or may not be added to the output file based on its length")
            # just creates a article data structure and fills up artcle.text and article.id

            article = Analyzed_article(a.text)
            # article.preprocessed_text just the articles text with . and no tabs
            article.preprocessed_text = preprocess_article_text(a.text)

            article.most_relevant_sent = analyze_article(article.preprocessed_text, readClaim.text,
                                                            param['n_relevant_sent'])
            # article.most_relevant_sent = [relevant sentence in order of similarity] we only fill up rest of the
            # article data structure for that article only if there are similar sentences in that article
            # compared to the claim
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

    # claims = [(1,text,claimer, 23-23-3233, 2020),(2,text,claimer, 23-23-3233, 2020)] claim.articles = [[
    # article,article,article,article]] filling up the Claim.articles[] for each claim to have all the articles
    # that are analyzed claims.articles = [relevantartcledatastructure, relevantartcledatastructure,
    # relevantartcledatastructure] in the order of which article came on google search first
    # write_test_file(param,claim)

    readClaim.articles = analyzed_articles
    # calling analyze article with 2 original articles
    for a in readClaim.articles:
        analyze_urls(a, readClaim, 1)

    # called by do_research
    # writes json data for a single claim's articles
    # this is called in a for loop iterating over each claim

    # same thing as dump_data but in a more organized way for D3
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
    app.run(port=8000, debug=True)
    # app.run(host='192.168.1.10', port=8101, debug=True)

# html = requests.get(...).text
# text = fulltext(html)
