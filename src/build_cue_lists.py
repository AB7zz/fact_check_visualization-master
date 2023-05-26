###########################################################################################################################
#  This file loads word2vec embeddings and extracts the most similar 10 words to a given cue word from the lists of cue   #
#  words in the folder : input_data/cue_words. Then outputs expanded lists of cue words by appnding the most similar 10   #
#  words to each word in every list. The expanded lists are found in input_data/expanded_cue_words. There is no need to   #
#  re-run this code unless we want to expand the words to more than most similar ten. This code is written to enhance the #
#  baseline of the stance aggregation system of the Fake News Challenge based on one of the papers participated in the    #
#  contest: paper by Bilal sth..                                                                                          #
#  ______________________________________________________________________________________________________________________ #
#  Author : Israa Qasim Jaradat , IDIR lab, University of Texas at Arlington                                              #
###########################################################################################################################


from nltk.tokenize import word_tokenize
from gensim.models.keyedvectors import KeyedVectors
import numpy as np
import codecs
import os
import animation
import time
from scipy.spatial.distance import cosine

# I am usig a function here just for the sake of the animated waiting icon :P
@animation.wait('bar')
def load_word2vec(wrd2vec_file):
    embdngs = KeyedVectors.load_word2vec_format(wrd2vec_file, binary = True)
    return embdngs
#get the vector of every word, then average the vectors to get the sentence vector
def get_sent_vector(text):

    tokenized = text if text == "" else word_tokenize(text)
    result = np.mean([np.array(embeddings[w]) for w in tokenized if w in embeddings], axis=0)
    if type(result) is np.float64 and np.isnan(result):
        result = np.zeros(300)
    return [float(i) for i in result]


def get_word_vector(word):
    word_vector = np.array(embeddings[word])
    return word_vector


def read_cue_words(cue_words_dir):
    directory = os.fsencode(cue_words_dir)
    cue_lists = dict()
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        cue_list = []
        file_path = cue_words_dir+filename
        with codecs.open(file_path,'r',encoding='utf8') as f:
            lines = f.readlines()
            for line in lines:
                cue_word = line.replace('\n','')
                cue_word = cue_word.replace('\r','')
                cue_list.append(cue_word)
            f.close()
        cue_lists[filename] = cue_list

    return cue_lists


def most_similar_ten(word):
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print ("word given = "+word)
    top_ten = []
    try:
        word_index = embeddings.index2word.index(word)
        word_vector = embeddings.syn0[word_index]
        similarities = []
        for index, vec in enumerate(embeddings.syn0):
            sim = 1 - cosine(word_vector, vec)
            if np.isnan(sim):
                sim = -1
                # similarities.append((index, sim))
            similarities.append((index, sim))
        similarities = sorted(similarities, reverse=True, key=lambda x: x[1])
        i = 0
        print("most 10 similar words :")
        print("word index,\tsimilarity,\tword")
        for indx, sim in similarities:
            i += 1
            wrd = embeddings.index2word[indx]
            top_ten.append(wrd)
            print(str(indx) + '\t' + str(sim) + '\t' + str(wrd) + '\n')
            if i > 10:
                break

    except:
        pass
    return top_ten


def expand_cue_lists(expanded_cues_dir,cue_lists):

    for cue_category, cue_list in cue_lists.items():
        with codecs.open(expanded_cues_dir+cue_category+'.txt','w',encoding='utf8') as out:
            for cue_word in cue_list:
                sim_10 = most_similar_ten(cue_word)
                out.write(cue_word + '\n')
                if len(sim_10)>0:
                    for w in sim_10:
                        out.write(w+'\n')
            out.close()




cue_lists_dir="../input_data/cue_words/"
expanded_cues_dir = "../input_data/expanded_cue_words/"
print("loading word2vec ...")
embeddings = load_word2vec("../input_data/GoogleNews-vectors-negative300.bin.gz")
print("finished loading word2vec!")
cue_lists = read_cue_words(cue_lists_dir)
expand_cue_lists(expanded_cues_dir,cue_lists)
print("finitto !!")


