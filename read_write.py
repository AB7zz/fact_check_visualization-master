###########################################################################################################################
#  This file provides the read/write functionalities for the input/output files. It reads and loads the claim file. It    #
#  writes the collected articles that belong to a certain claim (retrieved by searching Google) in a JSON formatted file  #
#  as an initial dump. It also writes the JSON file that is going to be used by D3 in the visualization stage of the      #
#  claim-map.                                                                                                             #
#  ______________________________________________________________________________________________________________________ #
#  Author : Israa Qasim Jaradat , IDIR lab, University of Texas at Arlington                                              #
###########################################################################################################################



import codecs
import json
from data_structures import *
from datetime import datetime

# called by the google_search's do_research() function
def read_claims(claims_file):
    claims =[]
    with codecs.open(claims_file, 'r', encoding='utf8') as f:
        lines = f.readlines()
        # lines = all claims
        # line = 1 claim
        i=0
        for line in lines:
            #print(line)
            line=line.strip()
            fields = line.split('\t')
            dt = datetime.strptime(fields[2], '%Y-%m-%d')
            c = Claim(i,fields[0],fields[1],fields[2],dt.year)
            claims.append(c)
            # claims = [(1,text,claimer, 23-23-3233, 2020),(2,text,claimer, 23-23-3233, 2020)]
            i+=1
        f.close()
    return claims
# def __init__(self, id, text, claimer, date, year):
def read_claim(line):
    c = Claim(0,line,'unknown','unknown','unknown')
    # line=line.strip()
    # fields = line.split('\t')
    # i=0
    # if(len(fields) >= 3):
    #     dt = datetime.strptime(fields[2], '%Y-%m-%d')
    #     c = Claim(i,fields[0],fields[1],fields[2],dt.year)
    #     return c


# called by do_research
# writes json data for a single claim's articles
# this is called in a for loop iterating over each claim
def dump_data(param,claim):
    data = {}
    datatmp = {}
    data['articles'] = []
    datatmp['subarticles'] = []
    for article in claim.articles:
        for subarticle in article.articleurls:
            datatmp['subarticles'].append({
                'claim': claim.text,
                'source': article.text,
                'most_relevant_sent': subarticle.most_relevant_sent,
                'publish_date': subarticle.publish_date,
                'authors': subarticle.author,
                'image': subarticle.image,
                'keywords': subarticle.keywords,
                'summary': subarticle.summary,
                'stance': subarticle.stance,
                'depth': subarticle.depth
            })
        data['articles'].append({
            'claim': claim.text,
            'depth': article.depth,
            'most_relevant_sent': article.most_relevant_sent,
            'publish_date': article.publish_date,
            'authors': article.author,
            'image': article.image,
            'keywords': article.keywords,
            'summary': article.summary,
            'stance': article.stance,
            'articles': datatmp['subarticles']
        })



    with open(param['output']+str(claim.id)+".json", 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False, indent=4)


def write_test_file(param,claim):
    with codecs.open("../output_data/testing_sample.txt",'a',encoding='utf8') as out:
        out.write("Claim :+"+claim+'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
        for article in claim.articles:
            out.write(article.text+'\n'+
                        'most relevant sentence 1: '+article.most_relevant_sent[0]+'\n'+
                        'most relevant sentence 2: '+article.most_relevant_sent[1]+'\n'+
                        '========================================================'+'\n')
        out.close()


# called for every claim in do_research claims for loop
def write_json_visualization(param, claim):
    data = {}
    data['links'] = []
    data['nodes'] = []

    def add_article_node(article,parent):
        # Append links frSom the article to the claim node
        data['links'].append({
            'source': parent.id,
            'value': "1",
            'target': article.id
        })
        data['nodes'].append({
            'claimer': "NA",
            'year': [article.year],
            'id': article.id,
            'type': 'evidence',
            'date': str(article.publish_date),
            'snippet': article.most_relevant_sent[1],
            'source': article.url,
            'truth_value': "NA"
        })


        # Recursively add subarticles as nodes
        for subarticle in article.articleurls:
            # Append links from the subarticle to the current article node
            add_article_node(subarticle,article)


    # Append the claim to the JSON file as a claim node
    data['nodes'].append({
        'claimer': claim.claimer,
        'year': [claim.year],
        'id': 0,
        'type': 'claim',
        'date': claim.date,
        'snippet': claim.text,
        'source': claim.claimer,
        'truth_value': "NA"
    })

    # Append the relevant documents as evidence documents
    for article in claim.articles:
        add_article_node(article,claim)

    # with open(param['json_visualization'], 'w', encoding='utf-8') as out:
    #     json.dump(data, out, ensure_ascii=False, indent=4)

    json_string = json.dumps(data)

    return json_string
