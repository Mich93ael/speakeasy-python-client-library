import time
from typing import List
from SPARQLWrapper import SPARQLWrapper, JSON
from speakeasypy import Speakeasy, Chatroom
import rdflib
import networkx as nx
import pandas as pd
import plotly.express as px

URL = "http://localhost"

DEFAULT_HOST_URL = 'https://speakeasy.ifi.uzh.ch'
listen_freq = 2


class Agent:
    def __init__(self, username, password):
        self.username = username
        # Initialize the Speakeasy Python framework and login.
        self.speakeasy = Speakeasy(host=DEFAULT_HOST_URL,
                                   username=username,
                                   password=password)
        self.speakeasy.login()




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

                    answer=self.execute_query(message.message)
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
    def execute_query(self, query):
        endpoint_url = "https://query.wikidata.org/sparql"

        sparql = SPARQLWrapper(endpoint_url)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()

        return result["results"]["bindings"]

if __name__ == '__main__':
    demo_bot = Agent("bake-pizzicato-liquor_bot", "taEjieXE6oprgw")
    demo_bot.listen()
