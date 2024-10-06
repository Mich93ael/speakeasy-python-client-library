from enum import Enum

from QuestionClassifier import Questions
from RelationMapper import RelationMapper
from engines.Querys import Querys
from nltk import word_tokenize
from nltk.corpus import stopwords
import csv
import pandas as pd
from sklearn.metrics import cohen_kappa_score

class CrowdsourcingEngine:

    def __init__(self, graph, movieList):
        self.graph = graph
        self.movieList = movieList
        # Beispielaufruf
        file_path = 'crowd_data.tsv'
        self.crowdsourced_data = self.read_tsv(file_path)


    def read_tsv(self,file_path):
        data = []
        with open(file_path, 'r', encoding='utf-8', newline='') as file:
            tsv_reader = csv.DictReader(file, delimiter='\t')
            for row in tsv_reader:
                data.append(row)
        return data


    def remove_stopwords(self, text):
        stop_words = set(stopwords.words('english'))

        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word not in stop_words]
        return ' '.join(filtered_text)

    def getHighestValueForMovie(self, question):
        safedValue = 0
        safedMovie = ""
        value = 0
        for movie in self.movieList:
            if RelationMapper.similar(" " + movie[0].lower() + " ", question.lower()) > value:
                value = RelationMapper.similar(movie[0].lower(), question.lower())
                if (safedValue < value):
                    safedMovie = movie[0]
                    safedValue = value
        if safedValue > 0.9:
            return safedMovie
        return None

    def search_wd_wdt(self,data, wd, wdt):
        # Erstellen Sie ein Pandas DataFrame aus Ihren Daten
        df = pd.DataFrame(data)

        # Filtern Sie die Daten nach den gewünschten Kriterien
        filtered_data = df[(df['Input1ID'].str.startswith("wd:"+wd)) | (df['Input2ID'].str.startswith("wdt:"+wdt))]

        return filtered_data.to_dict('records')
    def extractMovies(self, question):
        strippedQuestion = question
        movieList = []

        # Initialisiere 'movie' mit dem ersten Ergebnis
        movie = self.getHighestValueForMovie(strippedQuestion)

        return movie
    def extractRelation(self, question):
        for relation in CrowdsourcingKeys:
            if relation.value[1] in question:
                return str(relation.value[1])
        return None

    def answer(self, question, relation):
        movie = self.extractMovies(question)
        movidId= None
        if movie is not None:
            movidId=Querys.answerCrowdsourcingMovie(self.graph, movie)
            records=self.search_wd_wdt(self.crowdsourced_data, movidId, relation.value[0])
            if len(records)==0:
                return "Didnt find any Crowdsourcing Data about the movie "+movie
            else:
                return "These are the datas i found on Crowdsourcing: " +self.formatRecords(records,relation)
        return "Sorry i didnt find any Crowdsourcing Data"


    def calculate_fleiss_kappa(self,data):
        # Erstellen Sie ein Pandas DataFrame aus den Daten
        df = pd.DataFrame(data)

        # Erstellen Sie eine Kreuztabelle (Contingency Table)
        contingency_table = pd.crosstab(df['WorkerId'], df['AnswerLabel'])

        # Berechnen Sie den Fleiss' Kappa
        kappa = 1+cohen_kappa_score(contingency_table.values.T[0], contingency_table.values.T[1])

        return kappa
    def formatRecords(self, records,relation):
        countAgreement=0
        countDisagreement=0
        value=[]
        for record in records:
            if record['AnswerLabel'] in "CORRECT":
                countAgreement+=1
            else:
                countDisagreement+=1
            value.append(record['Input3ID'])
        kappa_score=self.calculate_fleiss_kappa(records)
        return "The "+relation.value[1] +"is"+value[0]+".And the inter agreement rate score is : "+str(kappa_score)+str(countAgreement)+" people agree and "+str(countDisagreement)+" people disagree"


class CrowdsourcingKeys(Enum):
    Publicationdate = "P577", "publication date"
    Boxoffice = "P2142", "box office"
    CastMember = "P161", "cast member"
    ExecutiveProducer = "P1431", "executive producer"
    CountryOfOrigin = "P495", "country of origin"
    DistributedBy = "P750", "distributied by"
