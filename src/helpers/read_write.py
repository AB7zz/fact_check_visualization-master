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
from helpers.data_structures import *
from datetime import datetime

# called by the google_search's do_research() function 
def read_claims(claims_file):
    claims =[]
    with codecs.open(claims_file, 'r', encoding='utf8') as f:
        lines = f.readlines()
        # lines = all claims
        # line = 1 claim
        i=1
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


# called by do_research
# writes json data for a single claim's articles
# this is called in a for loop iterating over each claim
def dump_data(param,claim):
    data = {}
    data['articles'] = []
    for article in claim.articles:

        data['articles'].append({
            'claim': claim.text,
            'most_relevant_sent': article.most_relevant_sent,
            'publish_date': article.publish_date,
            'authors': article.author,
            'image': article.image,
            'keywords': article.keywords,
            'summary': article.summary,
            'stance': article.stance
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
def write_json_visulization(param, claim):
    data = {}
    data['nodes'] =[]
    data['links'] =[]

    # append the claim to the JSON file as a claim node
    data['nodes'].append({
        'id': 0,
        'snippet': claim.text,
        'claimer': claim.claimer,
        'date': claim.date,
        'type': 'claim',
        'year': claim.year
    })
    # append the relevant documents as evidence documents
    print("ALL ARTICLES");
    print(claim.articles)


    for a in claim.articles:

        data['nodes'].append({
            'id' : a.id,
            'url': a.url,
            'snippet': a.most_relevant_sent[1],
            'type' : 'evidence',
            'year' : a.year
        })

    # append links from each relevant article to the claim node
        data['links'].append({
            'source': a.id,
            'target': '0',
            'value': '1'
        })

        # all urls don't have an id, url, most_relevant_sent. Might have to make a new data structure
        for z in a.all_urls:
            data['nodes'].append({
                'id': z.id,
                'url': z.url,
                'snippet': z.most_relevant_sent[1],
                'type': 'evidence',
                'year': z.year
            })

            # append links from each relevant article to the claim node
            data['links'].append({
                'source': z.id,
                'target': '0',
                'value': '1'
            })

    with open(param['json_visualization'], 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False, indent=4)