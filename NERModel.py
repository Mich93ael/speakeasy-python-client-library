import rdflib
import spacy
import random
from datetime import datetime
from spacy.training import Example
import time


class NERModel:
    def __init__(self, graph: rdflib.Graph):
        self.graph = graph
        self.nlp = self.prepare_nlp()
        self.train_data=self.createTrainset(self.getAllDirectorsToMoviesWithYears())

    @staticmethod
    def random_date(self, start_year=1900, end_year=2023):
        # Generate a random year, month, and day
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # This ensures we don't exceed the number of days in February

        # Convert to datetime object
        date_obj = datetime(year, month, day)

        # Format the date
        formatted_date = date_obj.strftime("%B %d,%Y")

        return formatted_date

    def createTrainset(self, movies):
        TRAIN_DATA = [
            ("Who is the director of 'Star Wars'?", {"entities": [(24, 34, "MOVIE")]}),
            ("Is Christopher Nolan the director of 'Inception'?",
             {"entities": [(3, 20, "PERSON"), (38, 48, "MOVIE")]}),
            ("Did Martin Scorsese direct 'The Wolf of Wall Street'?",
             {"entities": [(4, 19, "PERSON"), (28, 51, "MOVIE")]}),
            ("Who directed 'The Godfather'?", {"entities": [(13, 27, "MOVIE")]}),
            ("Who is the director of 'The Godfather'?", {"entities": [(24, 38, "MOVIE")]}),
            ("When was Titanic released? ", {"entities": [(9, 16, "MOVIE")]}),
            ("Did 'Avengers: Endgame' release in 2019? ", {"entities": [(5, 22, "MOVIE"), (35, 39, "RELEASE_DATE")]}),
            ("Is 'Parasite' a South Korean movie?", {"entities": [(4, 12, "MOVIE"), (16, 28, "NORP")]}),
            ("Did Peter Jackson direct 'The Lord of the Rings' trilogy?",
             {"entities": [(4, 17, "PERSON"), (26, 47, "MOVIE")]}),
            ("Was 'Black Panther' released in 2018?", {"entities": [(5, 19, "MOVIE"), (32, 36, "RELEASE_DATE")]}),
            ("Did Steven Spielberg direct 'Jurassic Park'?", {"entities": [(4, 20, "PERSON"), (29, 42, "MOVIE")]}),
            ("Who is the screenwriter of the Masked Gang: Cyprus", {"entities": [(27, 50, "MOVIE")]}),
            (
                "Did Quentin Tarantino direct 'Django Unchained'?",
                {"entities": [(4, 21, "PERSON"), (30, 46, "MOVIE")]}),
            ("Was The Dark Knight released in 2008?", {"entities": [(4, 19, "MOVIE"), (32, 36, "RELEASE_DATE")]}),
            ("Is 'Mad Max: Fury Road' an Australian film?", {"entities": [(4, 22, "MOVIE"), (27, 37, "NORP")]}),
            ("Did James Cameron direct 'Avatar'?", {"entities": [(4, 17, "PERSON"), (26, 32, "MOVIE")]}),
            ("Was 'The Matrix' released in 1999?", {"entities": [(5, 16, "MOVIE"), (29, 33, "RELEASE_DATE")]}),
            ("Is George Lucas the director of 'Star Wars: Episode I'?",
             {"entities": [(3, 15, "PERSON"), (33, 53, "MOVIE")]}),
            ("Was 'Forrest Gump' released in the 1990s?", {"entities": [(5, 17, "MOVIE"), (35, 40, "RELEASE_DATE")]}),
            ("Did Ridley Scott direct Alien?", {"entities": [(4, 16, "PERSON"), (24, 29, "MOVIE")]}),
            ("Was 'Schindler's List' released in 1993?", {"entities": [(5, 21, "MOVIE"), (35, 39, "RELEASE_DATE")]}),
            ("Is Wes Anderson the director of 'The Grand Budapest Hotel'?",
             {"entities": [(3, 15, "PERSON"), (33, 57, "MOVIE")]}),
            ("Did Bryan Singer direct 'X-Men'?", {"entities": [(4, 16, "PERSON"), (25, 30, "MOVIE")]}),
            ("Was 'Frozen II' released in 2019?", {"entities": [(5, 15, "MOVIE"), (28, 32, "RELEASE_DATE")]}),
            ("Is 'Finding Nemo' a Pixar film?", {"entities": [(4, 16, "MOVIE"), (20, 25, "ORG")]}),
            ("Did Guy Ritchie direct Snatch?", {"entities": [(4, 15, "PERSON"), (23, 29, "MOVIE")]}),
            ("Was 'Jaws' released in the 1970s?", {"entities": [(5, 9, "MOVIE"), (27, 32, "RELEASE_DATE")]}),
            ("Did the Coen Brothers direct 'Fargo'?", {"entities": [(4, 21, "PERSON"), (30, 35, "MOVIE")]}),
            ("Is 'The Silence of the Lambs' a thriller?", {"entities": [(4, 28, "MOVIE")]}),
            ("Did Stanley Kubrick direct '2001: A Space Odyssey'?",
             {"entities": [(4, 19, "PERSON"), (28, 49, "MOVIE")]}),
            ("Was 'Back to the Future' released in 1985?", {"entities": [(5, 24, "MOVIE"), (37, 41, "RELEASE_DATE")]}),
            ("Did Tim Burton direct 'Corpse Bride'?", {"entities": [(4, 14, "PERSON"), (23, 35, "MOVIE")]}),
            ("Is 'Braveheart' set in Scotland?", {"entities": [(4, 14, "MOVIE"), (23, 31, "GPE")]}),
            ("Did Ron Howard direct 'A Beautiful Mind'?", {"entities": [(4, 14, "PERSON"), (23, 39, "MOVIE")]})]
        for movie in movies:
            movieName = movie[0]
            director = movie[1]
            date = movie[2][:4]
            TRAIN_DATA.append((f"Was {movieName} released in 2010?", {"entities": [(4, 4 + len(movieName), "MOVIE"),
                                                                                   (4 + 13 + len(movieName),
                                                                                    4 + 13 + len(movieName) + 4,"RELEASE_DATE")]}))
            TRAIN_DATA.append(
                (f"Who is the director of {movieName}?", {"entities": [(23, 23 + len(movieName), "MOVIE")]}))
            TRAIN_DATA.append((f"Is {director} the director of {movieName}?", {
                "entities": [(3, 3 + len(director), "PERSON"),
                             (20 + len(director), 20 + len(director) + len(movieName), "MOVIE")]}))
            TRAIN_DATA.append((f"Did {director} direct {movieName}?", {"entities": [(4, 4 + len(director), "PERSON"), (
                12 + len(director), 12 + len(director) + len(movieName), "MOVIE")]}))
            TRAIN_DATA.append((f"Who directed {movieName}?", {"entities": [(13, 13 + len(movieName), "MOVIE")]}))
            TRAIN_DATA.append((f"Did {director} direct {movieName}?", {"entities": [(4, 4 + len(director), "PERSON"), (
                12 + len(director), 12 + len(director) + len(movieName), "MOVIE")]}))
            TRAIN_DATA.append((f"When was {movieName} released?", {"entities": [(9, 9 + len(movieName), "MOVIE")]}))
            TRAIN_DATA.append(
                (f"Who is the screenwriter of {movieName}?", {"entities": [(27, 27 + len(movieName), "MOVIE")]}))
            TRAIN_DATA.append(
                (f"Was {movieName} released in {date}?", {"entities": [(4, 4 + len(movieName), "MOVIE"), (
                    17 + len(movieName), 17 + len(movieName) + len(date), "RELEASE_DATE")]}))
            TRAIN_DATA.append(
                (f"Which movie released in {date}: Jurassic Park, Forrest Gump or Titanic?",
                 {"entities": [(24, 24 + len(date), "RELEASE_DATE"), (24 + len(date), 24 + len(date) + 15, "MOVIE"),
                               (24 + len(date) + 17, 24 + len(date) + 29, "MOVIE"),
                               (24 + len(date) + 33, 24 + len(date) + 40, "MOVIE")]}))
            randdate = self.random_date(1980, 2022)
            genre = self.randGenre()
            TRAIN_DATA.append(
                (f"Recommend me a {genre} Movie which was released in {randdate}?",
                 {"entities": [(15, 15 + len(genre), "GENRE"),
                               (15 + len(genre) + 29, 15 + len(genre) + 29 + len(randdate), "RELEASE_DATE"), ]}))
            TRAIN_DATA.append(
                (f"Can you recommend me a movie of the genre {genre}?",
                 {"entities": [(42, 42 + len(genre), "GENRE")]}))
            TRAIN_DATA.append(
                (f"Recommend me a {genre} Movie which was released in {randdate}?",
                 {"entities": [(15, 15 + len(genre), "GENRE"),( 15 + len(genre)+29,15+29+len(genre)+len(randdate), "RELEASE_DATE") ]}))
            TRAIN_DATA.append(
                (f"What is the genre of {movieName}?",
                 {"entities": [(21, 21+len(movieName), "MOVIE")]}))

            TRAIN_DATA.append(
                (f"The {genre} genre is something i like recommend me something like that?",
                 {"entities": [(4, 4 + len(genre), "GENRE") ]}))

        print("loaded Data")
        return TRAIN_DATA
    def prepare_nlp(self):
        # Laden des vortrainierten Modells
        nlp = spacy.load("en_core_web_sm")
        if "ner" not in nlp.pipe_names:
            ner = nlp.create_pipe("ner")
            nlp.add_pipe(ner)

        else:
            ner = nlp.get_pipe("ner")

        ner.add_label("MOVIE")
        ner.add_label("RELEASE_DATE")
        ner.add_label("GENRE")
        return nlp
    def train_nlp_model(self):
        # Create optimizer
        optimizer = self.nlp.create_optimizer()

        examples = [Example.from_dict(self.nlp.make_doc(text), annotations) for text, annotations in self.train_data]
        random.shuffle(examples)
        examples = examples[:int(len(examples) * 0.05)]
        # Training loop
        print("Start Training")
        for _ in range(5):  # 5 epochs
            start = time.time()
            random.shuffle(examples)
            for example in examples:
                self.nlp.update([example], sgd=optimizer, drop=0.5)
            print("epoch:" + str(_) + "  Time-needed:" + str(time.time() - start))
        print("Training Ended")
        self.nlp.to_disk("NERModel")

    @staticmethod
    def randGenre():
        genres = [
            "Action", "Adventure", "Comedy", "Crime", "Drama",
            "Fantasy", "Historical", "Horror", "Mystery", "Romance",
            "Science Fiction", "Thriller", "Western", "Animation",
            "Documentary", "Biography", "Musical", "War", "Family",
            "Sport"
        ]

        chosen_genre = random.choice(genres)

        # Randomly decide to convert to lowercase
        if random.random() < 0.5:  # 50% chance
            return chosen_genre.lower()
        else:
            return chosen_genre

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
    @staticmethod
    def return_trained_model():
        return spacy.load("NERModel")

    @staticmethod
    def return_second_model():
        return spacy.load("myTrainedModel")
