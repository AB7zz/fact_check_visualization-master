###########################################################################################################################
#  This file opens a connection with the claims database (from Duke or sth) and downloads the claims.                     #
#  There is no need to re run this code again, unless we need to recollect claims again. The claims collected from this   #
#  database can be found in the files  claims, enhanced_claims, and second_half_unfiltered_claims. The list               #
#  enhanced_claims.text where only the needed info are kept, and date formats are fixed to a certain format.              #
#  ______________________________________________________________________________________________________________________ #
#  Author : Israa Qasim Jaradat , IDIR lab, University of Texas at Arlington                                              #
###########################################################################################################################

import codecs

import psycopg2
import spacy
from nltk import pos_tag
from nltk.tokenize import word_tokenize


def collect_from_db():
    conn = psycopg2.connect(database="d59gh4qg7hjsc5", user="u6hioa2fipo9p8", password="pb2ut17ergeevk18praoa8icbdm",
                            host="ec2-35-169-140-59.compute-1.amazonaws.com", port="5432")
    print("Opened database successfully")

    cur = conn.cursor()

    cur.execute("SELECT *  from public.facts where language_id = 1")
    rows = cur.fetchall()
    with codecs.open("claims.txt", 'w', encoding='utf8') as out:
        for row in rows:
            quantity_claim = False
            claim = row[1]
            tokens = word_tokenize(claim)
            tagged = pos_tag(tokens)
            for tag in tagged:
                if tag[1] == 'CD':
                    quantity_claim = True
                    break
            if quantity_claim == True:
                out.write(str(row[0]) + '\t' + row[1] + '\t' + row[2] + '\t' + row[3] + '\t' + row[
                    6] + '\n')  # id, claim, speaker, speaker prefix, date
                continue
            else:
                nlp = spacy.load("en_core_web_sm")
                doc = nlp(claim)
                entities = doc.ents
                for e in entities:
                    if e.label_ in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
                        out.write(str(row[0]) + '\t' + row[1] + '\t' + row[2] + '\t' + row[3] + '\t' + row[6] + '\n')
    out.close()
    conn.close()


def enhance_file():
    with codecs.open("claims.txt", 'r', encoding='utf8') as f:
        with codecs.open("enhanced_claims.txt", 'w', encoding='utf8') as out:
            lines = f.readlines()
            for line in lines:
                fields = line.split('\t')
                out.write(fields[1] + '\t' + fields[2] + '\t' + fields[4])


enhance_file()
