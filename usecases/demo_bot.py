import time
from typing import List

import rdflib
import pickle

from pyparsing import ParseException

from speakeasypy import Speakeasy, Chatroom

DEFAULT_HOST_URL = 'https://speakeasy.ifi.uzh.ch'
listen_freq = 2


class Agent:
    def __init__(self, username, password, graph):
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
                    answer = self.getAnswer(self.graph, message.message)
                    # Implement your agent here #

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
    graph = load_or_parse_graph()
    demo_bot = Agent("bake-pizzicato-liquor_bot", "taEjieXE6oprgw", graph)
    demo_bot.listen()
