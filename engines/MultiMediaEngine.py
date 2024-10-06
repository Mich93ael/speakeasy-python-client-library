import spacy
from nltk import word_tokenize
from nltk.corpus import stopwords
import requests
import zipfile,json

from NERModel import NERModel
from RelationMapper import RelationMapper
from engines.Querys import Querys


class MultiMediaEngine:

    def download_and_extract_data(self,url, download_path, extract_path):
        response = requests.get(url)
        with open(download_path, 'wb') as zip_file:
            zip_file.write(response.content)

        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

    def process_filtered_json(self,json_path, movie_id, process_function):
        with open(json_path, 'r') as json_file:
            for line in json_file:
                data = json.loads(line)
                if movie_id in data.get("movie", []):
                    process_function(data)

    def process_entry(self,data):
        # Replace this function with your custom processing logic
        print(data)

    def __init__(self, graph,movieList):
        self.graph = graph
        self.movieList=movieList
        self.url = "https://files.ifi.uzh.ch/ddis/teaching/2021/ATAI/dataset/movienet/images.json.zip"
        self.download_path = "images.json.zip"
        self.extract_path = "extracted_data"

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
            if RelationMapper.similar(" "+movie[0].lower()+" ", question.lower()) > value:
                value = RelationMapper.similar(movie[0].lower(), question.lower())
                if (safedValue < value):
                    safedMovie = movie[0]
                    safedValue = value
        if safedValue > 0.9:
            return safedMovie
        return None
    def extractMovies(self, question):
        strippedQuestion = question
        movieList = []

        # Initialisiere 'movie' mit dem ersten Ergebnis
        movie = self.getHighestValueForMovie(strippedQuestion)

        # Schleife, die solange läuft, bis keine Filme mehr gefunden werden
        while movie is not None:
            strippedQuestion = strippedQuestion.replace(movie, "")
            movieList.append(movie)

            # Aktualisiere 'movie' für den nächsten Durchlauf
            movie = self.getHighestValueForMovie(strippedQuestion)

        return movieList
    def answer(self, question):
        nlp=spacy.load("en_core_web_sm")
        message=nlp(question)
        person=None
        for entities in message.ents:
            if(entities.label_=="PERSON"):
                person=entities.text
                question=question.replace(person,"")

        movieList=self.extractMovies(question)
        for movie in movieList:
            question = question.replace(movie, "")
        if person is not None:
            return Querys.picture_of_person(self.graph,person)
        if len(movieList) >=1:
            return Querys.picture_of_movie(self.graph,movieList[0])
        return "Sorry i dont know it"
