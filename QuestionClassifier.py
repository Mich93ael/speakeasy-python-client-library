from enum import Enum
import rdflib
import random
from joblib import load, dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline

from NERModel import NERModel


class QuestionClassifier:

    def __init__(self, graph: rdflib.Graph):
        self.graph = graph

    def getAllPersonsAndDirectorsAndActors(self):
        query = """
            PREFIX ddis: <http://ddis.ch/atai/> 
            PREFIX wd: <http://www.wikidata.org/entity/> 
            PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
            PREFIX schema: <http://schema.org/> 
            
            SELECT ?movieLabel ?directorLabel ?screenwriterLabel ?actorLabel WHERE { 
                ?movie wdt:P31 wd:Q11424 . 
                
                ?movie wdt:P57 ?directorItem . 
                ?directorItem rdfs:label ?directorLabel . 
                
                OPTIONAL {
                    ?movie wdt:P58 ?screenwriterItem . 
                    ?screenwriterItem rdfs:label ?screenwriterLabel . 
                }
                
                OPTIONAL {
                    ?movie wdt:P161 ?actorItem . 
                    ?actorItem rdfs:label ?actorLabel . 
                }
            } 
            ORDER BY ?movieLabel
        """
        person_list = []
        for result in self.graph.query(query):
            person_list.append(result)
        return person_list

    def getAllDirectorsToMoviesWithYears(self):
        query = """PREFIX ddis: <http://ddis.ch/atai/> 
                PREFIX wd: <http://www.wikidata.org/entity/> 
                PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
                PREFIX schema: <http://schema.org/> 
                
                SELECT ?movieLabel ?directorLabel ?releaseDate WHERE { 
                    ?movie wdt:P31 wd:Q11424 . 
                    ?movie wdt:P57 ?directorItem . 
                    ?movie rdfs:label ?movieLabel . 
                    ?directorItem rdfs:label ?directorLabel . 
                    ?movie wdt:P577 ?releaseDate . 
                } 
                ORDER BY ?movieLabel
                """
        movie_list = []
        for result in self.graph.query(query):
            movie_list.append(result)
        return movie_list

    def createTrainset(self):
        print("Loading Trainset")
        train_data_set = []
        movieList = self.getAllDirectorsToMoviesWithYears()
        random.shuffle(movieList)
        subset_groesse = int(len(movieList) * 0.02)
        subset = movieList[:subset_groesse]
        lastMovie = ""
        for movie in subset:
            train_data_set.append((["Who directed " + movie[0] + "?"], Questions.EmbeddedQuestion))
            train_data_set.append((["When was " + movie[0] + " released?"], Questions.EmbeddedQuestion))
            train_data_set.append((["What is the genre of " + movie[0] + "?"], Questions.EmbeddedQuestion))
            train_data_set.append((["What is the main actor of " + movie[0] + "?"], Questions.EmbeddedQuestion))
            train_data_set.append((["Who is the screenwriter of " + movie[0] + "?"], Questions.EmbeddedQuestion))

            train_data_set.append(
                (["Recommend me a movie of the genre " + movie[0] + "?"], Questions.RecommenderQuestion))
            randomdate = NERModel.random_date(self)
            train_data_set.append((["Recommend me a movie of the genre " + movie[
                0] + " that was released in " + randomdate + "?"], Questions.RecommenderQuestion))
            train_data_set.append((["Can you recommend me a movie similar to " + movie[0] + "," + lastMovie],
                                   Questions.RecommenderQuestion))

            train_data_set.append((["Given i like movies lik " + movie[0] + "," + lastMovie +", recommend me a movie"],
                                   Questions.RecommenderQuestion))
            lastMovie = movie[0]
        personDataSet = self.getAllPersonsAndDirectorsAndActors()
        random.shuffle(personDataSet)
        subset_persons_len = int(len(personDataSet) * 0.01)
        subset_persons = personDataSet[:subset_persons_len]
        for person in subset_persons:
            train_data_set.append((["Is " + person[1] + "a director?"], Questions.EmbeddedQuestion))
            train_data_set.append((["Is " + person[1] + "an actor?"], Questions.EmbeddedQuestion))

            train_data_set.append((["What does " + person[1] + "look like?"], Questions.MultiMediaQuestion))
            train_data_set.append((["Show me a picture of " + person[1] + "?"], Questions.MultiMediaQuestion))
            train_data_set.append((["Let me know what " + person[1] + "look like?"], Questions.MultiMediaQuestion))
            train_data_set.append((["How does " + person[1] + "look like?"], Questions.MultiMediaQuestion))
            train_data_set.append(([
                                       "Display a picture from a classic " + person[1] + "thriller"
                                                                                         " that exemplifies his influence on the suspense and horror genres.?"],
                                   Questions.MultiMediaQuestion))

        print("Trainset loaded!")
        return train_data_set

    def train_model(self):
        X_train = []
        train_labels = []
        print("Start Training")
        for s in self.createTrainset():
            X_train.append(" ".join(s[0]))  # Satz als Ganzer
            train_labels.append(s[1].name)
        model = make_pipeline(TfidfVectorizer(), RandomForestClassifier())
        model.fit(X_train, train_labels)
        print("Training finished")
        dump(model, 'QuestionClasifierModel.joblib')

    def load_model(self):
        return load('QuestionClasifierModel.joblib')


class Questions(Enum):
    EmbeddedQuestion = "EmbeddedQuestion"
    RecommenderQuestion = "RecommenderQuestion"
    MultiMediaQuestion = "MultiMediaQuestion"
    CrowdsourcingQuestion = "CrowdsourcingQuestion"
