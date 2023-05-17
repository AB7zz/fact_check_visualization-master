###########################################################################################################################
#  This file contains the data classes needed in all of the files.                                                        #
#  ______________________________________________________________________________________________________________________ #
#  Author : Israa Qasim Jaradat , IDIR lab, University of Texas at Arlington                                              #
###########################################################################################################################

class Analyzed_article:
    def __init__(self, text, id):
        self.id = id
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
        self.html = "",
        self.all_urls = []


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
