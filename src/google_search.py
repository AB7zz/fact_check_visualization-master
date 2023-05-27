import nltk
import requests
from analyze_hyperlinks import *
from bert_embeddings import *
from print_colors import *
import settings
from data_structures import Claim
from read_write import *

nltk.download('punkt')

def parse_parameters(opts):
    param = OrderedDict()
    # param = {'input': inputfilename, 'output': outputfilename, 'stop','n_relevant_sent','top_search_results','json_visualization'}
    param['input'] = opts.input
    param['output'] = opts.output
    param['stop'] = opts.stop
    param['n_relevant_sent'] = opts.n_relevant_sent
    param['top_search_results'] = opts.top_search_results
    param['json_visualization'] = opts.json_visualization
    logging.info("PARAMETER LIST:_______________________________________________________________________")
    logging.info(param)

    return param


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

    articles = []
    for url in urls:
        article = Article(url)
        try:
            article.download()
        except:
            printRed("Unable to download the article: " + url)
        try:
            article.parse()
            articles.append(article)
        except:
            printRed("Unable to parse the article :" + url)

    return articles


def analyze_article(article, claim, n_relevant):
    print('Analyzing article ...')
    relevant_sentences = find_most_similar(article, claim)
    if len(relevant_sentences) > n_relevant:
        return relevant_sentences[0: n_relevant - 1]
    else:
        return None


def preprocess_article_text(text):
    text = text.replace('\n', '. ')
    text = text.replace('\t', '')
    return text


def do_research(param, claim):
    print("Research started ...")
    c = 1
    claims = read_claims(claim)
    for claim in claims:
        if c >= param['stop'] + 1:
            break

        printLightPurple(
            " C L A I M     # " + str(c) + " ========================================================================")
        # max 2 articles at a time
        # search_claim(6 links,claims[claim.text])
        # in order of what article came on top of the google search
        relevant_articles = search_claim(param, claim.text)
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

                article.most_relevant_sent = analyze_article(article.preprocessed_text, claim.text,
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

        claim.articles = analyzed_articles
        # calling analyze article with 2 original articles
        for a in claim.articles:
            analyze_urls(a, claim, 1)

        # called by do_research
        # writes json data for a single claim's articles
        # this is called in a for loop iterating over each claim

        # same thing as dump_data but in a more organized way for D3
        write_json_visualization(param, claim)

def main(opts, claim):
    param = parse_parameters(opts)
    do_research(param, claim)




