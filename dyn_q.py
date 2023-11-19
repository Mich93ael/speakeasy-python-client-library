import re
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy

class MovieRecommendationBot:
    def __init__(self, sparql_endpoint):
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.nlp = spacy.load("en_core_web_sm")

    def execute_sparql_query(self, query):
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        try:
            results = self.sparql.query().convert()
            return results['results']['bindings']
        except Exception as e:
            print(f"Error executing SPARQL query: {e}")
            return []

    def create_dynamic_query(self, movie, genre_id):
        query_template = """
        SELECT ?movieLabel WHERE {{
            ?movie wdt:P31 wd:Q11424 .
            ?movie wdt:P136 wd:{genre_id} .
            ?movie rdfs:label ?movieLabel .
            FILTER(STR(?movieLabel) != "{liked_movie}" && ?similarity > 80)
            BIND(afn:levenshtein(?movieLabel, "{liked_movie}") AS ?similarity)
        }}
        """
        return query_template.format(liked_movie=movie, genre_id=genre_id)

    def recognize_relation(self, input, ents):
        likes_pattern = r"I like (.*?), (.*?), and (.*?)\. Can you recommend some movies\?"
        like_horror_pattern = r"Recommend movies like (.*?), (.*?), and (.*?)\?"

        likes_match = re.search(likes_pattern, input, re.IGNORECASE)
        if likes_match:
            movies_liked = list(likes_match.groups())
            relation = "recommendation_likes"
            return relation, movies_liked

        like_horror_match = re.search(like_horror_pattern, input, re.IGNORECASE)
        if like_horror_match:
            movies_liked = list(like_horror_match.groups())
            relation = "recommendation_like_horror"
            return relation, movies_liked

        print("No relation recognized.")
        return None, None

    def answer_open_question(self, question):
        doc = self.nlp(question)
        movie_label = next((ent.text for ent in doc.ents if ent.label_ == "MOVIE"), None)

        if movie_label:
            dynamic_query = self.create_dynamic_query(movie_label, "Q12345")  # Replace with the actual genre ID
            try:
                results = self.execute_sparql_query(dynamic_query)
                if results:
                    return f"Based on your input, you might also like: {', '.join([res['movieLabel']['value'] for res in results])}"
                else:
                    return "No similar movies found based on your input."
            except Exception as e:
                print(f"Error processing open question: {e}")
                return "An error occurred while processing the request."

        return "Did not find an answer"

# Example usage
sparql_endpoint = "your_sparql_endpoint"  #???
bot = MovieRecommendationBot(sparql_endpoint)

questions = [
    "I like The Lion King, Pocahontas, and The Beauty and the Beast. Can you recommend some movies?",
    "Recommend movies like Nightmare on Elm Street, Friday the 13th, and Halloween.",
]

for question in questions:
    recognized_relation, recognized_info = bot.recognize_relation(question, ["MOVIE"])
    if recognized_relation and recognized_info:
        print(f"Question: {question}")
        print(f"Recognized Relation: {recognized_relation}")
        print(f"Recognized Information: {recognized_info}")
        print(bot.answer_open_question(question))
        print()
    else:
        print(f"No relation recognized in the question: {question}")
        print()