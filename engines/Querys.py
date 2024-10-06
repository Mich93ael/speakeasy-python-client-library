from collections import Counter

import pandas as pd


class Querys:
    @staticmethod
    def askDirector_Screenwriter_Actor_MainActor_MainScreenWriter_Genre_MainDirector(graph, object, relation, movie):
        query = f"""
                            PREFIX ddis: <http://ddis.ch/atai/>
                            PREFIX wd: <http://www.wikidata.org/entity/>
                            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                            PREFIX schema: <http://schema.org/>
                    
                            SELECT ?{object} WHERE {{
                                ?movie rdfs:label "{movie[0]}"@en .
                                ?movie wdt:{relation} ?{object}Item .
                                ?{object}Item rdfs:label ?{object} .
                            }}
                            """
        result = graph.query(query)
        if (len(result) == 0):
            return None
        if (len(result) == 1):
            for row in result:
                return "The " + object + " of " + movie[0] + " is " + row[0]

        else:
            sentence = "The " + object + " of " + movie[0] + " are "
            for row in result:
                sentence += row[0] + ", "

            return sentence
        return None

    @staticmethod
    def askYesNoQuestionPerson_Movie(graph, object, relation, movie, person):
        query = f"""
                PREFIX ddis: <http://ddis.ch/atai/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX schema: <http://schema.org/>
        
                ASK WHERE {{
                    ?movie rdfs:label "{movie[0]}"@en .
                    ?movie wdt:{relation} ?{object}Item .
                    ?{object}Item rdfs:label "{person}"@en .
                }}
                """
        result = graph.query(query)
        if (result.askAnswer):
            return "Yes"
        else:
            return "No"

    @staticmethod
    def askYesNoQuestionPerson_ReleasDate(graph, movie, releasedate):
        query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
                                
                                ASK WHERE {{
                                    ?movie rdfs:label "{movie[0]}"@en .
                                    ?movie wdt:P577 ?releaseDate .
                                    FILTER (YEAR(?releaseDate) = {releasedate})
                                }}
                                
                                """
        result = graph.query(query)
        if (result.askAnswer):
            return "Yes"
        else:
            return "No"

    @staticmethod
    def askRatingOnly(graph, movie):
        query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
        SELECT ?rating WHERE {{
        ?movie rdfs:label "{movie[0]}"@en .
        ?movie ddis:rating ?rating  }}
        """
        rating = "0"
        for row in graph.query(query):
            rating = row[0]
        return rating

    @staticmethod
    def askRating(graph, movie):
        query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
        SELECT ?rating WHERE {{
        ?movie rdfs:label "{movie[0]}"@en .
        ?movie ddis:rating ?rating  }}
        """
        rating = "Not Found"
        for row in graph.query(query):
            rating = row[0]
        return "The rating of the" + movie[0] + " is " + rating

    @staticmethod
    def askReleaseDate(graph, movie):
        query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
                                
                                SELECT ?releaseDate WHERE {{
                                    ?movie rdfs:label "{movie[0]}"@en .
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
            return f"The release date of {movie[0]} was {textback}"

    @staticmethod
    def recommend_movie_from_with_highest_rating_from_genre(graph, genreList):
        movieList = []
        for genre in genreList:
            query = f"""PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
                    SELECT DISTINCT ?movieLabel WHERE {{
                            ?genre rdfs:label "{genre}"@en .
                        ?movie wdt:P136 ?genre .
                        ?movie rdfs:label ?movieLabel .
                        FILTER (LANG(?movieLabel) = "en")
                    }}
    
                """
            result = graph.query(query)
            rating = 0
            safedRating = 0
            for movie in result:
                try:
                    safedRating = Querys.askRatingOnly(graph, movie)

                    if (float(safedRating) > rating) and (float(safedRating) > 5):
                        movieList.append(movie)
                        rating = safedRating
                except(Exception):
                    pass
            movieList = movieList[:3]
            if (len(movieList) == 0):
                if (len(result) == 0):
                    return "Sorry i dont have any Recommandations for you"
                else:
                    sentence = "I recommend the movies for you:"
                    for index, movie in enumerate(result):
                        sentence += movie[0] + ", "
                        if (index > 4):
                            break
                    return sentence
        if (len(movieList) == 1):
            for movie in movieList:
                return "I would recommend you this movie " + " " + movie[0]
        sentence = "The top " + str(len(movieList)) + " movies in the genre '" + str(genreList) + "' are "
        for movie in movieList:
            sentence += movie[0] + ", "
        return sentence

    @staticmethod
    def get_genre_List(graph):
        query = f"""PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                
                SELECT DISTINCT ?genreLabel WHERE {{
                    ?movie wdt:P136 ?genre .
                    ?genre rdfs:label ?genreLabel .
                    FILTER (LANG(?genreLabel) = "en")
                }}
                """""
        result = graph.query(query)
        genreList = []
        for row in result:
            genreList.append(row[0])
        return genreList

    @staticmethod
    def ask_which_movie_in_releaseDate_or_person_or_genre(graph, movieList, object, relation, release_date):

        if release_date is not None:
            for movie in movieList:
                result = Querys.askReleaseDateOnly(graph, movie[0])
                if result is not None:
                    for row in result:
                        if (row[0] in release_date):
                            return "The movie is " + movie
        return "No movie was realesed in " + release_date

    @staticmethod
    def askReleaseDateOnly(graph, movie):
        query = f"""PREFIX ddis: <http://ddis.ch/atai/>
                                PREFIX wd: <http://www.wikidata.org/entity/>
                                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                                PREFIX schema: <http://schema.org/>
                                
                                SELECT ?releaseDate WHERE {{
                                    ?movie rdfs:label "{movie}"@en .
                                    ?movie wdt:P577 ?releaseDate .
                                }}
                                
                                """
        return graph.query(query)

    @staticmethod
    def recommend_from_similar_movies(graph, movieList):
        genreList = []
        for movie in movieList:
            query = f"""
                            PREFIX ddis: <http://ddis.ch/atai/>
                            PREFIX wd: <http://www.wikidata.org/entity/>
                            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                            PREFIX schema: <http://schema.org/>
                    
                            SELECT ?genre WHERE {{
                                ?movie rdfs:label "{movie}"@en .
                                ?movie wdt:P136 ?genreItem .
                                ?genreItem rdfs:label ?genre .
                            }}
                            """
            result = graph.query(query)
            for row in result:
                genreList.append(row[0])

        # Zählen, wie oft jedes Genre vorkommt
        genre_counts = Counter(genreList)

        # Behalten Sie nur Genres, die mehr als einmal vorkommen
        selectedGenreList = [genre for genre, count in genre_counts.items() if count > 1]
        querysuffix = ""
        for genre in selectedGenreList:
            val = genre.split(" ")[0]
            querysuffix += f'?movie wdt:P136 ?genreItem{val.capitalize()} .?genreItem{val.capitalize()} rdfs:label "{genre}"@en .'
        queryMovie = f"""PREFIX wd: <http://www.wikidata.org/entity/>
                        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                        SELECT DISTINCT ?movie ?movieLabel WHERE {{
                            {querysuffix}
                        
                            ?movie rdfs:label ?movieLabel .
                            FILTER(LANG(?movieLabel) = "en")
                            }}
                                    """
        resultMovie = graph.query(queryMovie)
        recommandationList = []
        for row in resultMovie:
            if (row[1] not in movieList):
                recommandationList.append(row[1])
        sentence = "I recommend you the movies: "
        for movie in recommandationList:
            sentence += movie + ", "
        return sentence

    @staticmethod
    def recommend_movie_from_genre_and_release_date(graph, genre, release_date):
        pass
    @staticmethod
    def picture_of_movie(graph, movie):
        imdbId= Querys.getIMDBForMovie(graph, movie)
        if imdbId is not None:
            return "The picture for the movie " + movie + " is " + imdbId
        return "Sorry, I don't have a picture about the movie " + movie
    @staticmethod
    def picture_of_person(graph, person):
        imdbId= Querys.getIMDBForPerson(graph, person)
        if imdbId is not None:
            return "The picture for the person " + person + " is " + imdbId
        return "Sorry, I don't have a picture about the person " + person

    @staticmethod
    def getIMDBForPerson(graph, person):
        query = f"""PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    
                    SELECT DISTINCT ?person ?imdbId WHERE {{
                      ?person wdt:P31 wd:Q5;  # Personen
                              wdt:P345 ?imdbId.  # IMDb-ID
                      ?person rdfs:label "{person}"@en.  
                    }}
                    """
        result = graph.query(query)
        for row in result:
            return "https://www.imdb.com/name/"+str(row[1])
        return None

    @staticmethod
    def getIMDBForMovie(graph, movie):
        query = f"""PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    
                    SELECT DISTINCT ?film ?imdbId WHERE {{
                      ?film wdt:P31 wd:Q11424;  # Filme
                            wdt:P345 ?imdbId.  # IMDb-ID
                      ?film rdfs:label "{movie}"@en.  # Filter nach dem Filmtitel
                    }}
                    """
        result = graph.query(query)
        for row in result:
            return "https://www.imdb.com/title/"+str(row[1])
        return None

    @staticmethod
    def answerCrowdsourcingMovie(graph,movie):
        query=f"""PREFIX wd: <http://www.wikidata.org/entity/>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                
                SELECT ?film WHERE {{
                  ?film rdfs:label "{movie}"@en.
                  ?film wdt:P31 wd:Q11424.
                }}
                """
        result=graph.query(query)
        filmdID=None
        for row in result:
            filmdID=row[0].replace("http://www.wikidata.org/entity/","")
        return filmdID

    @staticmethod
    def answerCrowdsourcingPerson( graph, person, relation):
        pass
