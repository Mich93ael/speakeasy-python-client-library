from datetime import datetime
import time
from typing import List

import rdflib
import pickle

import spacy
from pyparsing import ParseException

from speakeasypy import Speakeasy, Chatroom

DEFAULT_HOST_URL = 'https://speakeasy.ifi.uzh.ch'
listen_freq = 2


class Agent:
    def __init__(self, username, password, graph):
        print("NER Model is loading: ...")
        self.nlp = spacy.load("C://Users//debos//speakeasy-python-client-library//myTrainedModel")
        print("Ner Model loaded!")
        self.username = username
        # Initialize the Speakeasy Python framework and login.
        self.speakeasy = Speakeasy(host=DEFAULT_HOST_URL,
                                   username=username,
                                   password=password)
        self.speakeasy.login()
        self.graph = graph

    def listen(self):
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
                    try:
                        answer = self.answer(self.graph, message.message)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        answer = "Question couldnt processed"
                    # Implement your agent here #
                    print(answer)
                    # Send a message to the corresponding chat room using the post_messages method of the room object.
                    room.post_messages(f"{answer}")
                    # Mark the message as processed, so it will be filtered out when retrieving new messages.
                    room.mark_as_processed(message)

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
            return "No result"

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
