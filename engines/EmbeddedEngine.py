from nltk import word_tokenize
from nltk.corpus import stopwords

from NERModel import NERModel
from RelationMapper import RelationMapper
from engines.Querys import Querys
import re


def checkgenre(genre):
    genres = [
        "Action", "Adventure", "Comedy", "Crime", "Drama",
        "Fantasy", "Historical", "Horror", "Mystery", "Romance",
        "Science Fiction", "Thriller", "Western", "Animation",
        "Documentary", "Biography", "Musical", "War", "Family",
        "Sport"
    ]
    for expectedgenres in genres:
        if RelationMapper.similar(expectedgenres, genre) > 0.6:
            return expectedgenres
    return None


class EmbeddedEngine:
    def __init__(self, graph, movieList, personList=None):
        self.graph = graph
        self.movieList = movieList
        self.personList = personList

    def remove_stopwords(self, text):
        stop_words = set(stopwords.words('english'))

        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word not in stop_words]
        return ' '.join(filtered_text)

    def find_year_in_string(self, string):
        """
        Find and return the year present in a string.

        Args:
        string (str): The string to search in.

        Returns:
        int: The first year found in the string, or None if no year is found.
        """
        # Regular expression to find a four-digit number that could represent a year
        year_pattern = r"\b(19\d{2}|20\d{2})\b"

        # Search for the pattern in the string
        match = re.search(year_pattern, string)
        if match:
            return int(match.group())
        else:
            return None

    def answer(self, question):
        nlp = NERModel.return_trained_model()
        stripped_question = self.remove_stopwords(question)
        doc = nlp(stripped_question)
        person = None
        release_date = None
        genreList = []
        genre = None
        for entities in doc.ents:
            if (entities.label_ == "PERSON"):
                person = entities.text
            if (entities.label_ == "RELEASE_DATE"):
                release_date = entities.text
            if (entities.label_ == "GENRE"):
                genre = entities.text
                genre = checkgenre(genre)
                genreList.append(genre)

        movieList = self.find_movie_in_text(question, person, release_date, genre)
        if (release_date is None):
            release_date = self.find_year_in_string(question)
        extract_relation = self.extract_relation(question, doc, movieList, person, release_date, genre)
        if extract_relation is None:
            return None
        if (extract_relation.value[0] == "rating") and (len(movieList) == 1):
            return Querys.askRating(self.graph, movieList[0])
        if (len(movieList) == 1) and ((extract_relation.value[0] == "mainActor") or
                                      (extract_relation.value[0] == "mainDirector") or
                                      (extract_relation.value[0] == "actor") or
                                      (extract_relation.value[0] == "mainScreenwriter")
                                      or (extract_relation.value[0] == "mainGenre")
                                      or (extract_relation.value[0] == "genre")
                                      or (extract_relation.value[0] == "screenwriter")
                                      or (extract_relation.value[0] == "director")) and (person is None) \
                and (release_date is None) \
                and (len(genreList) == 0):
            return Querys.askDirector_Screenwriter_Actor_MainActor_MainScreenWriter_Genre_MainDirector(self.graph,
                                                                                                       extract_relation.value[
                                                                                                           0],
                                                                                                       extract_relation.value[
                                                                                                           1],
                                                                                                       movieList[0])
        if (extract_relation.value[0] == "releaseDate") and (len(movieList) == 1):
            return Querys.askReleaseDate(self.graph, movieList[0])
        if ((person is not None) and len(movieList) == 1):
            return Querys.askYesNoQuestionPerson_Movie(self.graph, extract_relation.value[0], extract_relation.value[1],
                                                       movieList[0], person)
        if ((release_date is not None) and len(movieList) == 1):
            return Querys.askYesNoQuestionPerson_ReleasDate(self.graph, movieList[0], release_date)
        if ((release_date is not None) and len(movieList) > 1):
            return Querys.ask_which_movie_in_releaseDate_or_person_or_genre(self.graph, movieList,
                                                                            extract_relation.value[0],
                                                                            extract_relation.value[1],
                                                                            release_date)
        # if len(movieList) > 0:
        #     embeddings = self.dynamic_query_movie(movieList, extract_relation.value[0], extract_relation.value[1],
        #                                           person, release_date, genreList)
        #     if(embeddings=="Yes" or embeddings=="No"):
        #         return embeddings
        #
        #     return embeddings
        # else:
        #     embeddings = self.dynamic_query_no_movie(extract_relation.value[1], extract_relation.value[2], person,
        #                                              release_date, genreList)
        #     return embeddings

    def extract_relation(self, question, doc, movieList, person, release_date, genre):
        if person is None:
            person = ""
        if release_date is None:
            release_date = ""
        if genre is None:
            genre = ""

        relevant_text = question.replace(person, "").replace(str(release_date), "").replace(genre, "")

        for movie in movieList:
            relevant_text = relevant_text.replace(movie[0], "")
        extract_matching_relation_from_mapping = RelationMapper().extract_matching_relation_from_mapping(relevant_text)

        return extract_matching_relation_from_mapping

    def find_movie_in_text(self, text, person, release_date, genre):
        if person is not None:
            text = text.replace(person, "")
        if release_date is not None:
            text = text.replace(str(release_date), "")
        if genre is not None:
            text = text.replace(genre, "")
        movieList = []
        movie = ""
        safedMovie = None
        value = 0
        for movie in self.movieList:
            if RelationMapper.similar(movie[0], text) > value:
                safedMovie = movie[0]
                value = RelationMapper.similar(movie[0], text)
                if (value > 0.9):
                    movieList.append(movie)
                    text = text.replace(str(movie[0]), "")
                    value = 0

        if (len(movieList) == 1 and value < 0.35):
            return None
        if (len(movieList) > 1):
            return movieList
        return movieList

    def dynamic_query_movie(self, movieList, object, relation, person, release_date, genreList):
        if (len(movieList) == 1) and (person is None) and (release_date is None) and (len(genreList) == 0):
            if relation == "P345":
                query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                            PREFIX wd: <http://www.wikidata.org/entity/>
                            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                            PREFIX schema: <http://schema.org/>
                            
                            SELECT ?rating WHERE {{
                                ?movie rdfs:label "{movieList[0]}"@en .
                                ?movie wdt:P31 wd:Q11424 .
                                ?movie wdt:P31 ?rating .
                            }}
                            """
                result = self.graph.query(query)
                for row in result:
                    return "The rating of " + movieList[0] + " is " + row[0]
            query = f"""
                            PREFIX ddis: <http://ddis.ch/atai/>
                            PREFIX wd: <http://www.wikidata.org/entity/>
                            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                            PREFIX schema: <http://schema.org/>
                    
                            SELECT ?{object} WHERE {{
                                ?movie rdfs:label "{movieList[0]}"@en .
                                ?movie wdt:{relation} ?{object}Item .
                                ?{object}Item rdfs:label ?{object} .
                            }}
                            """
            result = self.graph.query(query)
            sentence = ""
            if len(result) == 1:
                for row in result:
                    sentence = "The " + object + " of " + movieList[0] + " is " + row[0]
            else:
                sentence = "The " + object + " of " + movieList[0] + " are "
                for row in result:
                    sentence = sentence + row[0] + ", "

            return sentence
        elif (len(movieList) > 1) and (person is None) and (release_date is None) and (len(genreList) == 0):
            resultList = []
            sentence = ""
            for movie in movieList:
                query = f"""
                            PREFIX ddis: <http://ddis.ch/atai/>
                            PREFIX wd: <http://www.wikidata.org/entity/>
                            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                            PREFIX schema: <http://schema.org/>
                    
                            SELECT ?{object} WHERE {{
                                ?movie rdfs:label "{movie}"@en .
                                ?movie wdt:{relation} ?{object}Item .
                                ?{object}Item rdfs:label ?{object} .
                            }}
                            """
                result = self.graph.query(query)
                resultList.append(self.graph.query(query))
                if len(result) == 1:
                    for row in result:
                        sentence = "The " + object + " of " + movieList[0] + " is " + row[0]
                else:
                    sentence = "The " + object + " of " + movieList[0] + " are "
                for row in result:
                    sentence = sentence + row[0] + ", "
            return sentence
        elif len(movieList) == 1 and person is not None:
            query = f"""
                PREFIX ddis: <http://ddis.ch/atai/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX schema: <http://schema.org/>
        
                ASK WHERE {{
                    ?movie rdfs:label "{movieList[0]}"@en .
                    ?movie wdt:{relation} ?{object}Item .
                    ?{object}Item rdfs:label "{person}"@en .
                }}
                """
            result = self.graph.query(query)
            if (result.askAnswer):
                return "Yes"
            else:
                return "No"
        elif len(movieList) == 1 and release_date is not None:
            query = f"""
                PREFIX ddis: <http://ddis.ch/atai/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX schema: <http://schema.org/>
        
                ASK WHERE {{
                    ?movie rdfs:label "{movieList[0]}"@en .
                    ?movie wdt:{relation} ?{object}Item .
                    ?{object}Item rdfs:label "{release_date}"@en .
                }}
                """
            result = self.graph.query(query)
            if (result.askAnswer):
                return "Yes"
            else:
                return "No"
        elif len(movieList) == 1 and len(genreList) == 1:
            query = f"""
                PREFIX ddis: <http://ddis.ch/atai/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX schema: <http://schema.org/>
        
                ASK WHERE {{
                    ?movie rdfs:label "{movieList[0]}"@en .
                    ?movie wdt:{relation} ?{object}Item .
                    ?{object}Item rdfs:label "{genreList[0]}"@en .
                }}
                """
            result = self.graph.query(query)
            if (result.askAnswer):
                return "Yes"
            else:
                return "No"
        return None

    def dynamic_query_no_movie(self, object, relation, person, release_date, genreList):
        sentence = ""
        if (person is not None) and (release_date is None) and (len(genreList) == 0):
            query = f"""
                        PREFIX ddis: <http://ddis.ch/atai/>
                        PREFIX wd: <http://www.wikidata.org/entity/>
                        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                        PREFIX schema: <http://schema.org/>
                
                        SELECT ?{object} WHERE {{
                            ?person rdfs:label "{person}"@en .
                            ?person wdt:{relation} ?{object}Item .
                            ?{object}Item rdfs:label ?{object} .
                        }}
                        Limit 5
                        """
            result = self.graph.query(query)
            if (len(result) == 1):
                for row in result:
                    sentence = "The" + relation + " of " + person + " is " + row[0]
            else:
                sentence = "The" + relation + " of " + person + " are "
                for row in result:
                    sentence = sentence + row[0] + ","
            return sentence

        if (person is None) and (release_date is not None) and (len(genreList) == 0):
            query = f"""
                        PREFIX ddis: <http://ddis.ch/atai/>
                        PREFIX wd: <http://www.wikidata.org/entity/>
                        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                        PREFIX schema: <http://schema.org/>
                
                        SELECT ?{object} WHERE {{
                            ?releaseDate rdfs:label "{release_date}"@en .
                            ?releaseDate wdt:{relation} ?{object}Item .
                            ?{object}Item rdfs:label ?{object} .
                        }}
                        Limit 5
                        """
            result = self.graph.query(query)
            if (len(result) == 1):
                for row in result:
                    sentence = "The " + relation + "which released in " + release_date + " is " + row[0]
            else:
                sentence = "The " + relation + "which released in " + release_date + " are "
                for row in result:
                    sentence = sentence + row[0] + ","
            return sentence
        if (person is None) and (release_date is None) and (len(genreList) == 1):
            query = f"""
                        PREFIX ddis: <http://ddis.ch/atai/>
                        PREFIX wd: <http://www.wikidata.org/entity/>
                        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                        PREFIX schema: <http://schema.org/>
                
                        SELECT ?{object} WHERE {{
                            ?genre rdfs:label "{genreList[0]}"@en .
                            ?genre wdt:{relation} ?{object}Item .
                            ?{object}Item rdfs:label ?{object} .
                        }}
                        Limit 5
                        """
            result = self.graph.query(query)
            if (len(result) == 1):
                for row in result:
                    sentence = "The genre of" + relation + " is " + row[0]
            else:
                sentence = "The genre of" + relation + " are "
                for row in result:
                    sentence = sentence + row[0] + ","
            return sentence
