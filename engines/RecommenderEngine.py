import re

from nltk import word_tokenize
from nltk.corpus import stopwords

from NERModel import NERModel
from QuestionClassifier import Questions
from RelationMapper import RelationMapper
from engines.Querys import Querys


class RecommenderEngine:

    def __init__(self, graph, movieList):
        self.graph = graph
        self.movieList = movieList
        print("genreList loading:")
        self.genreListOfDataset = Querys.get_genre_List(graph)
        print("genreList loaded")

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

    def getRightGenre(self, genre):
        safedGenreValue = 0
        safedGenre = ""
        for genreInDataset in self.genreListOfDataset:
            value = RelationMapper.similar(genreInDataset.lower(), genre.lower())
            if (safedGenreValue < value):
                safedGenre = genreInDataset
                safedGenreValue = value
        return safedGenre

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
        safedValue = 0
        value = 0
        for movie in self.movieList:
            if RelationMapper.similar(movie[0], text) > value:
                value = RelationMapper.similar(movie[0], text)
                if (safedValue < value):
                    safedMovie = movie[0]
                    safedValue = value
                if (value > 0.9):
                    movieList.append(movie)
                    text = text.replace(str(movie[0]), "")
                    value = 0

        if (len(movieList) == 1 and safedValue < 0.4):
            return []
        if (len(movieList) > 1):
            return movieList
        return movieList

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
            if RelationMapper.similar(movie[0].lower(), question.lower()) > value:
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

    def getHighestValueForGenre(self, question):
        safedValue = 0
        safedGenre = ""
        value = 0
        for genre in self.genreListOfDataset:
            genreTocompare=genre.replace("film","")
            genreTocompare=genreTocompare.replace("movie","")
            if RelationMapper.similar(genreTocompare.lower(), question.lower()) > value:
                value = RelationMapper.similar(genreTocompare.lower(), question.lower())
                if (safedValue < value):
                    safedGenre = genre
                    safedValue = value
        if safedValue > 0.9:
            return safedGenre
        return None

    def extractGenres(self, question):
        strippedQuestion = question
        genreList = []

        # Initialisiere 'movie' mit dem ersten Ergebnis
        genre = self.getHighestValueForGenre(strippedQuestion)

        # Schleife, die solange läuft, bis keine Filme mehr gefunden werden
        while genre is not None:
            strippedQuestion = strippedQuestion.replace(genre, "")
            genreList.append(genre)

            # Aktualisiere 'movie' für den nächsten Durchlauf
            genre = self.getHighestValueForMovie(strippedQuestion)

        return genreList

    def answer(self, question):
        stripped_question = self.remove_stopwords(question)
        movieList = self.extractMovies(stripped_question)
        for movie in movieList:
            stripped_question = stripped_question.replace(movie, "")
        print("Recognized Movies: " + str(movieList))
        genreList = self.extractGenres(stripped_question)
        release_date = None
        if (len(movieList) == 0) and (len(genreList) >= 1):
            return Querys.recommend_movie_from_with_highest_rating_from_genre(self.graph, genreList)
        if (len(movieList) > 1 and (len(genreList) == 0) and (release_date is None)):
            return Querys.recommend_from_similar_movies(self.graph, movieList)
        if (len(movieList) == 0) and (len(genreList) >= 1) and (release_date is not None):
            return Querys.recommend_movie_from_genre_and_release_date(self.graph, genreList, release_date)
        if (len(genreList) >= 1) and (release_date is not None):
            return ""

        return "I didnt find any useful movies but try Pulp Fiction, Fight Club or The Dark Knight (with the Joker)"
