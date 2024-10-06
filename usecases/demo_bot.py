import pickle
import re
import time
from datetime import datetime
from difflib import SequenceMatcher
from enum import Enum
from typing import List

import rdflib
import spacy
from joblib import load
from pyparsing import ParseException

from QuestionClassifier import QuestionClassifier
from engines.AnswerEngine import AnswerEngine
from speakeasypy import Speakeasy, Chatroom

DEFAULT_HOST_URL = 'https://speakeasy.ifi.uzh.ch'
listen_freq = 2


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_movie_in_text(movie_list, text):
    safedMovie = None
    value = 0
    for movie in movie_list:
        if similar(movie[0], text) > value:
            safedMovie = movie[0]
            value = similar(movie[0], text)
    if (value < 0.4):
        return "None"
    return safedMovie


def find_release_date_in_text(text):
    match = re.search(r'(\d{4})', text)
    if match:
        return match.group(1)
    else:
        return ""


def find_person_in_text(person_list, text):
    for person in person_list:
        if similar(person[1], text) >= 0.4:
            return person[1]
        if similar(person[2], text) >= 0.4:
            return person[2]
        if similar(person[3], text) >= 0.4:
            return person[3]
    return "None"


class Intentions(Enum):
    AskDirector = "AskDirector"
    AskScreenwriter = "AskScreenwriter"
    AskMainActor = "AskMainActor"
    AskReleaseDate = "AskReleaseDate"
    AskIsDirector = "AskIsDirector"
    AskIsScreenwriter = "AskIsScreenwriter"
    AskIsMainActor = "AskIsMainActor"
    AskIsReleaseDate = "AskIsReleaseDate"


class Agent:
    def __init__(self, username, password, graph):
        print("Models are loading: ...")
        # self.nlp = spacy.load("C://Users//debos//speakeasy-python-client-library//myTrainedModel")
        self.nlp = spacy.load("myTrainedModel2")
        self.questionclassifier = QuestionClassifier(graph)
        # questionclassifier.train_model()
        self.questionclassifier = self.questionclassifier.load_model()
        self.intentmodel = load("intentmodel.joblib")
        print("Model Loaded!")
        print("MovieList and PersonList loading:...")

        self.movieList = self.getAllDirectorsToMoviesWithYears(graph)
        self.personList = self.getAllPersonsAndDirectors(graph)
        print("MovieList and PersonList loaded!")

        self.engine = AnswerEngine(graph, self.movieList)
        self.username = username
        # Initialize the Speakeasy Python framework and login.
        self.speakeasy = Speakeasy(host=DEFAULT_HOST_URL,
                                   username=username,
                                   password=password)
        self.speakeasy.login()
        self.graph = graph

    def listen(self):
        global answer
        while True:
            # only check active chatrooms (i.e., remaining_time > 0) if active=True.
            rooms: List[Chatroom] = self.speakeasy.get_rooms(active=True)
            for room in rooms:
                if not room.initiated:
                    # send a welcome message if room is not initiated
                    room.post_messages(f'Hello! This is a welcome message from {room.my_alias}.')
                    room.initiated = True
                # Retrieve messages from this chat room.
                # If only_partner=True, it filters out messages sent by the current bot.
                # If only_new=True, it filters out messages that have already been marked as processed.
                for message in room.get_messages(only_partner=True, only_new=True):
                    answer = ""
                    try:
                        print(message.message)
                        # answer = self.answerPro(self.graph, message.message)

                        print("The question was: " + message.message)
                        print("Classifier predicted: " + str(self.questionclassifier.predict([message.message])))
                        result = self.engine.answer(self.questionclassifier.predict([message.message]), message.message)
                        print(result)
                        # Send a message to the corresponding chat room using the post_messages method of the room object.
                        room.post_messages(f"{result}")
                        # Mark the message as processed, so it will be filtered out when retrieving new messages.
                        room.mark_as_processed(message)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        try:
                            answer = self.answerPro(self.graph, message.message)
                            print(answer)
                            room.post_messages(f"{answer}")
                            # Mark the message as processed, so it will be filtered out when retrieving new messages.
                            room.mark_as_processed(message)
                        except Exception as e:
                            answer = f"An error occurred: {e}\n" + "Query wasnt valid"
                            print(answer)
                            # Send a message to the corresponding chat room using the post_messages method of the room object.
                            room.post_messages(f"{answer}")
                            # Mark the message as processed, so it will be filtered out when retrieving new messages.
                            room.mark_as_processed(message)
                        # Implement your agent here #

                # Retrieve reactions from this chat room.
                # If only_new=True, it filters out reactions that have already been marked as processed.
                for reaction in room.get_reactions(only_new=True):
                    print(
                        f"\t- Chatroom {room.room_id} "
                        f"- new reaction #{reaction.message_ordinal}: '{reaction.type}' "
                        f"- {self.get_time()}")

                    # Implement your agent here #

                    room.post_messages(f"Received your reaction: '{reaction.type}' ")
                    room.mark_as_processed(reaction)

            time.sleep(listen_freq)

    @staticmethod
    def get_time():
        return time.strftime("%H:%M:%S, %d-%m-%Y", time.localtime())

    def getAllPersonsAndDirectors(self, graph):
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
        for result in graph.query(query):
            person_list.append(result)
        return person_list

    def getAllDirectorsToMoviesWithYears(self, graph):
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
        for result in graph.query(query):
            movie_list.append(result)
        return movie_list

    def getAnswer(self, graph, query):
        try:
            answer = ""
            for result in graph.query(query):
                if (len(result) > 0):
                    answer = answer + result[0]
            if (len(answer) <= 0):
                answer = "No Result Found"
            return answer
        except(ParseException):
            return "Parse Exception occured. The Query wasnt valid!"

    def answer_closed_yes_no_question(self, graph, doc):
        movie_label = None
        person_label = None
        entities = doc.ents
        for entity in entities:
            if entity.label_ == "PERSON":
                person_label = str(entity)
            elif entity.label_ == "MOVIE":
                movie_label = str(entity)
        if person_label and movie_label:

            person_label = person_label.replace("'", "")
            person_label = person_label.replace("\"", "")
            movie_label = movie_label.replace("'", "")
            movie_label = movie_label.replace("\"", "")
            # SPARQL-Abfrage um zu überprüfen, ob die Person das Kunstwerk (Film) direktiert hat
            q = f"""
            PREFIX ddis: <http://ddis.ch/atai/>
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX schema: <http://schema.org/>
    
            ASK WHERE {{
                ?movie rdfs:label "{movie_label}"@en .
                ?movie wdt:P57 ?directorItem .
                ?directorItem rdfs:label "{person_label}"@en .
            }}
            """

            result = graph.query(q)
            if result.askAnswer:
                return "Yes"
            else:
                return "No"

        return "Didnt find an answer"

    def answer_relation_closed_question_who(self, graph, doc):
        movie_label = None

        entities = doc.ents
        for entity in entities:
            if entity.label_ == "MOVIE":
                movie_label = str(entity)

        if movie_label:
            movie_label = movie_label.replace("'", "")
            movie_label = movie_label.replace("\"", "")
            # SPARQL-Abfrage um zu überprüfen, ob die Person das Kunstwerk (Film) direktiert hat
            if "direc" in doc.text:
                q = f"""
                PREFIX ddis: <http://ddis.ch/atai/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX schema: <http://schema.org/>
        
                SELECT ?director WHERE {{
                    ?movie rdfs:label "{movie_label}"@en .
                    ?movie wdt:P57 ?directorItem .
                    ?directorItem rdfs:label ?director .
                }}
                """

                result = graph.query(q)
                if (len(result) > 0):
                    textback = ""
                    for res in result:
                        if len(textback) > 0:
                            textback = textback + ", "
                        textback = textback + res[0]
                    return "The director is " + textback
                else:
                    return "Didnt Found any Data"
            if "screenwri" in doc.text:
                q = f"""
                PREFIX ddis: <http://ddis.ch/atai/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX schema: <http://schema.org/>
        
                SELECT ?screenwriter WHERE{{
                    ?movie rdfs:label "{movie_label}"@en .
                    ?movie wdt:P57 ?directorItem .
                    ?directorItem rdfs:label ?screenwriter .
                }}
                """

                result = graph.query(q)
                if (len(result) > 0):
                    textback = ""
                    for res in result:
                        if len(textback) > 0:
                            textback = textback + ", "
                        textback = textback + res[0]
                    return "The screenwriter is " + textback
                else:
                    return "Didnt Found any Data"

        return "Didnt find an answer"

    def answer_released_when(self, graph, doc):
        movie_label = None

        entities = doc.ents
        for entity in entities:
            if entity.label_ == "MOVIE":
                movie_label = str(entity)

        if movie_label:
            movie_label = movie_label.replace("'", "")
            movie_label = movie_label.replace("\"", "")
            # SPARQL-Abfrage um zu überprüfen, ob die Person das Kunstwerk (Film) direktiert hat
            if "release" in doc.text:
                q = f"""
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
                    
                    SELECT ?releaseDate WHERE {{
                        ?movie rdfs:label "{movie_label}"@en .
                        ?movie wdt:P577 ?releaseDate . 
                    }}
                    """

                result = graph.query(q)
                if (len(result) > 0):
                    year = None
                    for res in result:
                        date_object = datetime.strptime(str(res[0]), '%Y-%m-%d')
                        year = date_object.year
                    if not year:
                        return "Didnt Found Data"
                    return "The movie was released in " + str(year)
                else:
                    return "Didnt Found any Data"

        return "Didnt find an answer"

    def replace_entities_with_labels(self, doc):
        text = doc.text
        for ent in doc.ents:
            text = text.replace(str(ent), ent.label_)
        return text

    def answer(self, graph, message):
        if self.nlp is None:
            self.nlp = spacy.load("myTrainedModel")
        doc = self.nlp(message)

        if (("did" in doc.text[:3].lower()) or ("is" in doc.text[:3].lower())) and ("direct" in doc.text.lower()):
            return self.answer_closed_yes_no_question(graph, doc)
        if ("who" in doc.text[:3].lower()) and ("direc" in doc.text.lower()):
            return self.answer_relation_closed_question_who(graph, doc)
        if ("who" in doc.text[:3].lower()) and ("screenwrit" in doc.text.lower()):
            return self.answer_relation_closed_question_who(graph, doc)
        if ("when" in doc.text[:4].lower()) and ("relea" in doc.text.lower()):
            return self.answer_released_when(graph, doc)

    def correctAnswer(self, doc, intent):
        print(doc)
        print(intent)
        nlp2 = spacy.load("myTrainedModel")
        doc = nlp2(doc.text)
        answer = self.prepareEntitiesAndAnswerWithIntent(graph, doc, intent)
        if answer is None or answer in "None":
            answer = self.correctEntitiesAndAnswer(graph, doc.text, intent)
        else:
            return answer
        return answer

    def correctEntitiesAndAnswer(self, graph, text, intent):
        movie = find_movie_in_text(self.movieList, text)
        if str(intent[0]) == Intentions.AskDirector.name \
                or str(intent[0]) == Intentions.AskScreenwriter.name \
                or str(intent[0]) == Intentions.AskMainActor.name \
                or str(intent[0]) == Intentions.AskReleaseDate.name:

            if movie is None:
                return "None"
            else:
                anwser = self.answerWithIntentRecognition(graph, intent, movie, "", "")
                return anwser
        person = find_person_in_text(self.personList, text)
        releasedate = find_release_date_in_text(text)
        return self.answerWithIntentRecognition(graph, intent, movie, person, releasedate)

    def answerPro(self, graph, message):
        if self.nlp is None:
            self.nlp = spacy.load("myTrainedModel")
        doc = self.nlp(message)
        intent = self.intentmodel.predict([self.replace_entities_with_labels(doc)])
        answer = self.prepareEntitiesAndAnswerWithIntent(graph, doc, intent)
        if (answer is None) or (answer in "None"):
            return self.correctAnswer(doc, intent)
        else:
            return answer

    def prepareEntitiesAndAnswerWithIntent(self, graph, doc, intent):
        movie = ""
        person = ""
        releasedate = ""
        for ent in doc.ents:
            if (ent.label_ == "MOVIE"):
                movie = str(ent)
                movie = movie.replace("'", "")
                movie = movie.replace("\"", "")
                movie = movie.replace("\n", "")
            if (ent.label_ == "PERSON"):
                person = str(ent)
            if (ent.label_ == "DATE"):
                releasedate = str(ent)
        return self.answerWithIntentRecognition(graph, intent, movie, person, releasedate)

    def answerWithIntentRecognition(self, graph, intent, movie, person, releasedate):

        if str(intent[0]) == Intentions.AskDirector.name:
            movie = find_movie_in_text(self.movieList, movie)
            query = f"""
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
            
                    SELECT ?director WHERE {{
                        ?movie rdfs:label "{movie}"@en .
                        ?movie wdt:P57 ?directorItem .
                        ?directorItem rdfs:label ?director .
                    }}
                    """
            result = graph.query(query)
            if (len(result) > 0):
                textback = ""
                for res in result:
                    if len(textback) > 0:
                        textback = textback + ", "
                    textback = textback + res[0]
                return f"The director of {movie} is {textback}"
        elif str(intent[0]) == Intentions.AskScreenwriter.name:
            movie = find_movie_in_text(self.movieList, movie)
            query = f"""
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
            
                    SELECT ?screenwriter WHERE {{
                        ?movie rdfs:label "{movie}"@en .
                        ?movie wdt:P57 ?directorItem .
                        ?directorItem rdfs:label ?screenwriter .
                    }}
                    """
            result = graph.query(query)
            if (len(result) > 0):
                textback = ""
                for res in result:
                    if len(textback) > 0:
                        textback = textback + ", "
                    textback = textback + res[0]
                return f"The screenwriter of {movie} is {textback}"
        elif str(intent[0]) == Intentions.AskMainActor.name:
            movie = find_movie_in_text(self.movieList, movie)
            query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
                                
                                SELECT ?actor WHERE {{
                                    ?movie rdfs:label "{movie}"@en .
                                    ?movie wdt:P161 ?actorItem .
                                    ?actorItem rdfs:label ?actor .
                                }}
    
                                """
            result = graph.query(query)
            if (len(result) > 0):
                textback = ""
                for res in result:
                    if len(textback) > 0:
                        textback = textback + ", "
                    textback = textback + res[0]
                return f"The main actor of {movie} are {textback}"
        elif str(intent[0]) == Intentions.AskReleaseDate.name:
            movie = find_movie_in_text(self.movieList, movie)
            query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
                                
                                SELECT ?releaseDate WHERE {{
                                    ?movie rdfs:label "{movie}"@en .
                                    ?movie wdt:P577 ?releaseDate .
                                }}
                                
                                """
            result = graph.query(query)
            if (len(result) > 0):
                textback = ""
                for res in result:
                    if len(textback) > 0:
                        textback = textback + ", "
                    textback = textback + res[0]
                return f"The release date of {movie} was {textback}"
        elif str(intent[0]) == Intentions.AskIsDirector.name:
            # Handle AskIsDirector
            movie = find_movie_in_text(self.movieList, movie)
            query = f"""
                PREFIX ddis: <http://ddis.ch/atai/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX schema: <http://schema.org/>
        
                ASK WHERE {{
                    ?movie rdfs:label "{movie}"@en .
                    ?movie wdt:P57 ?directorItem .
                    ?directorItem rdfs:label "{person}"@en .
                }}
                """

            result = graph.query(query)
            if result is None:
                return None
            if (result.askAnswer):
                return "Yes"
            else:
                return "No"
        elif str(intent[0]) == Intentions.AskIsScreenwriter.name:
            # Handle AskIsScreenwriter
            movie = find_movie_in_text(self.movieList, movie)
            query = f"""
                PREFIX ddis: <http://ddis.ch/atai/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX schema: <http://schema.org/>
        
                ASK WHERE {{
                    ?movie rdfs:label "{movie}"@en .
                    ?movie wdt:P58 ?screenwriterItem .
                    ?screenwriterItem rdfs:label "{person}"@en .
                }}
                """

            result = graph.query(query)
            if result is None:
                return None
            if (result.askAnswer):
                return "Yes"
            else:
                return "No"
        elif str(intent[0]) == Intentions.AskIsMainActor.name:
            # Handle AskIsMainActor
            movie = find_movie_in_text(self.movieList, movie)
            query = graph.query(f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
                                
                                ASK WHERE {{
                                    ?movie rdfs:label "{movie}"@en .
                                    ?movie wdt:P161 ?mainActorItem .
                                    ?mainActorItem rdfs:label "{person}"@en .
                                }}""")
            result = graph.query(query)
            if result is None:
                return None
            if (result.askAnswer):
                return "Yes"
            else:
                return "No"
        elif str(intent[0]) == Intentions.AskIsReleaseDate.name:
            # Handle AskIsReleaseDate
            movie = find_movie_in_text(self.movieList, movie)
            query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
                                
                                ASK WHERE {{
                                    ?movie rdfs:label "{movie}"@en .
                                    ?movie wdt:P577 ?releaseDate .
                                    FILTER (YEAR(?releaseDate) = {releasedate})
                                }}
                                
                                """
            result = graph.query(query)
            if result is None:
                return None
            if (result.askAnswer):
                return "Yes"
            else:
                return "No"


        else:
            # Handle other cases or unknown intent
            return "None"


def load_or_parse_graph(graph_path='./14_graph.nt', cache_path='cached_graph.pkl'):
    """
    Lädt einen gecachten Graphen oder parst ihn neu und speichert ihn im Cache.

    Args:
    - graph_path (str): Pfad zur Graphen-Datei.
    - cache_path (str): Pfad zur Cache-Datei.

    Returns:
    - rdflib.Graph: Der geladene oder geparste Graph.
    """
    try:
        # Versuche, den gecachten Graphen zu laden
        with open(cache_path, 'rb') as f:
            graph = pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError):
        # Wenn das Laden fehlschlägt, parst den Graphen neu
        graph = rdflib.Graph()
        graph.parse(graph_path, format='turtle')

        # Speichere den neu geparsten Graphen im Cache
        with open(cache_path, 'wb') as f:
            pickle.dump(graph, f)

    return graph


# Verwendung der Methode:


if __name__ == '__main__':
    print("Graph is loading: ...")
    graph = load_or_parse_graph()
    print("Graph Loaded!")
    demo_bot = Agent("bake-pizzicato-liquor_bot", "taEjieXE6oprgw", graph)
    demo_bot.listen()
