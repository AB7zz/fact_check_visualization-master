###########################################################################################################################
#  This file contains the data classes needed in all of the files.                                                        #
#  ______________________________________________________________________________________________________________________ #
#  Author : Israa Qasim Jaradat , IDIR lab, University of Texas at Arlington                                              #
###########################################################################################################################
from settings import global_counter1
class Analyzed_article:
    def __init__(self, text):
        self.id = next(global_counter1)
        self.text = text
        self.preprocessed_text = ""
        self.most_relevant_sent = []
        self.stance = 0
        self.author = "UNKNOWN"
        self.publish_date = "UNKNOWN"
        self.summary = "UNKNOWN"
        self.keywords = "UNKNOWN"
        self.image = "UNKNOWN"
        self.source_url = "UNKNOWN"
        self.url = "UNKNOWN"
        self.year = "UNKNOWN"
        self.html = ""
        self.depth = 0
        self.articleurls = []
class Claim:
    def __init__(self, id, text, claimer, date, year):
        self.id = id
        self.text = text
        self.articles = []  # a list of Analyzed_article objects
        self.claimer = claimer
        self.date = date
        self.year = year


class Hyperlink:
    def __init__(self):
        self.url = ""
        self.text = ""