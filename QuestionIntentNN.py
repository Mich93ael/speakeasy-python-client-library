from enum import Enum
from joblib import load, dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline

from NERModel import NERModel


class QuestionIntentNN:

    def __init__(self):
        pass

    def createTrainset(self):
        train_data_set = []
        train_data_set.append((["Who directed of the movie", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Who directed of ", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Who was the director of ", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Can you tell me who directed", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["I'd like to know the director of", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Who's the person behind the direction of", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["MOVIE", "was directed by whom?"], Intentions.AskDirector))
        train_data_set.append((["Tell me the filmmaker of", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["The movie", "MOVIE", "was directed by?"], Intentions.AskDirector))
        train_data_set.append((["I'm curious, who directed", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Who was in charge of the direction for", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Who is the filmmaker behind ", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Who took the director's seat for", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Do you know the director of ", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Who guided the production of ", "MOVIE"], Intentions.AskDirector))
        train_data_set.append((["Which individual directed", "MOVIE"], Intentions.AskDirector))

        train_data_set.append((["Who is the screenwriter of the movie", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["Who wrote the screenplay for", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["Can you tell me the writer of", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["Who's the screenwriter behind", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["Who is the author of the", "MOVIE", "script"], Intentions.AskScreenwriter))
        train_data_set.append((["Who crafted the story for", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["Tell me, who was the writer for", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["Which individual wrote the screenplay for", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["I'm curious about the scriptwriter of", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["Who was responsible for the", "MOVIE", "script"], Intentions.AskScreenwriter))
        train_data_set.append((["Do you know who wrote the story for", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["Who is the playwright for", "MOVIE"], Intentions.AskScreenwriter))
        train_data_set.append((["I'd love to know the writer of", "MOVIE"], Intentions.AskScreenwriter))

        train_data_set.append((["When was the movie", "MOVIE", "released"], Intentions.AskReleaseDate))
        train_data_set.append((["When was", "MOVIE", "released"], Intentions.AskReleaseDate))
        train_data_set.append((["I'd like to know when", "MOVIE", "came out"], Intentions.AskReleaseDate))
        train_data_set.append((["What's the release year of", "MOVIE"], Intentions.AskReleaseDate))
        train_data_set.append((["On which date did", "MOVIE", "hit the theaters"], Intentions.AskReleaseDate))
        train_data_set.append((["Do you recall the release date for", "MOVIE"], Intentions.AskReleaseDate))
        train_data_set.append((["I'm curious, when was", "MOVIE", "launched"], Intentions.AskReleaseDate))
        train_data_set.append((["Tell me, when did", "MOVIE", "debut in cinemas"], Intentions.AskReleaseDate))
        train_data_set.append((["Which year was", "MOVIE", "released"], Intentions.AskReleaseDate))
        train_data_set.append((["When was", "MOVIE", "released"], Intentions.AskReleaseDate))
        train_data_set.append((["When was", "MOVIE", "released"], Intentions.AskReleaseDate))

        train_data_set.append((["Name the main actor in", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Who was the lead actor in", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Can you tell me the main actor of", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Who played the principal role in", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Who's the leading performer in", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Who took the main role in", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Tell me, who was the star of", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Which actor had the lead role in", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["I'm curious about the main cast of", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Who was the headlining actor for", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Who played the central character in", "MOVIE"], Intentions.AskMainActor))
        train_data_set.append((["Who was the lead in", "MOVIE"], Intentions.AskMainActor))

        train_data_set.append((["Is", "PERSON", "the director of", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Is", "PERSON", "behind", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Is", "PERSON", "responsible for", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Is", "PERSON", "the filmmaker of", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Is", "PERSON", "the one who directed", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Is", "PERSON", "the filmmaker for", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Is", "PERSON", "responsible for", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Is", "PERSON", "the one who directed", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Has", "PERSON", "directed", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Has", "PERSON", "made", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Has", "PERSON", "helmed", "MOVIE"], Intentions.AskIsDirector))
        train_data_set.append((["Has", "PERSON", "taken charge of", "MOVIE"], Intentions.AskIsDirector))

        train_data_set.append((["Is", "PERSON", "the screenwriter for", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Is", "PERSON", "the writer behind", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append(
            (["Is", "PERSON", "credited as the screenwriter of ", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Is", "PERSON", "the writer of", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Is", "PERSON", "credited with", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Has", "PERSON", "written the script for", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Has", "PERSON", "penned", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Has", "PERSON", "written the script for", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Has", "PERSON", "scripted", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Has", "PERSON", "written the screenplay for", "MOVIE"], Intentions.AskIsScreenwriter))
        train_data_set.append((["Has", "PERSON", "the writer of", "MOVIE"], Intentions.AskIsScreenwriter))

        train_data_set.append((["Is", "PERSON", "the main actor of", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Is", "PERSON", "the lead actor in", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Has", "PERSON", "starred as the main role in", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Is", "PERSON", "the primary performer of", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Did", "PERSON", "take the main role in", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Is", "PERSON", "the main protagonist in", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Was", "PERSON", "the leading character in", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Has", "PERSON", "been the chief performer of", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Is", "PERSON", "the main cast of", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Did", "PERSON", "play the principal role in", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Is", "PERSON", "the star of", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Has", "PERSON", "been the leading face for", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Is", "PERSON", "the top performer in", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Did", "PERSON", "have the main role in", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Is", "PERSON", "the central character of", "MOVIE"], Intentions.AskIsMainActor))
        train_data_set.append((["Was", "PERSON", "the primary actor for", "MOVIE"], Intentions.AskIsMainActor))

        train_data_set.append((["Was", "RELEASE_DATE", "the release date of", "MOVIE"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Was", "RELEASE_DATE", "the release date of", "MOVIE"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Is", "RELEASE_DATE", "when", "MOVIE", "was first shown"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Did", "MOVIE", "premiere on", "RELEASE_DATE"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Is", "RELEASE_DATE", "the day", "MOVIE", "came out"], Intentions.AskIsReleaseDate))
        train_data_set.append(
            (["Was", "MOVIE", "introduced to audiences on", "RELEASE_DATE"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Did", "MOVIE", "make its debut on", "RELEASE_DATE"], Intentions.AskIsReleaseDate))
        train_data_set.append(
            (["Is", "RELEASE_DATE", "the official launch date of", "MOVIE"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Did", "MOVIE", "get released on", "RELEASE_DATE"], Intentions.AskIsReleaseDate))
        train_data_set.append(
            (["Is", "RELEASE_DATE", "the day", "MOVIE", "was presented"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Did", "MOVIE", "begin screening on", "RELEASE_DATE"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Was", "MOVIE", "out in theaters on", "RELEASE_DATE"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Is", "RELEASE_DATE", "when", "MOVIE", "started showing"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Did", "MOVIE", "hit the big screen on", "RELEASE_DATE"], Intentions.AskIsReleaseDate))
        train_data_set.append((["Was", "MOVIE", "officially released on", "RELEASE_DATE"], Intentions.AskIsReleaseDate))
        train_data_set.append(
            (["Is", "RELEASE_DATE", "the first screening date of", "MOVIE"], Intentions.AskIsReleaseDate))

        train_data_set.append((["What genre has the movie", "MOVIE", "?"], Intentions.AskGenre))
        train_data_set.append((["What genre has the movie", "MOVIE"], Intentions.AskGenre))
        train_data_set.append((["Can you tell me the genre of ", "MOVIE", "?"], Intentions.AskGenre))
        train_data_set.append((["What is the film genre of ", "MOVIE", "?"], Intentions.AskGenre))
        train_data_set.append((["Which category does ", "MOVIE", " fall into?"], Intentions.AskGenre))
        train_data_set.append((["What type of movie is ", "MOVIE", "?"], Intentions.AskGenre))
        train_data_set.append((["In which genre is ", "MOVIE", " classified?"], Intentions.AskGenre))
        train_data_set.append((["What genre category does ", "MOVIE", " belong to?"], Intentions.AskGenre))
        train_data_set.append((["Could you classify the genre of ", "MOVIE", "?"], Intentions.AskGenre))
        train_data_set.append((["What is the style of ", "MOVIE", "?"], Intentions.AskGenre))
        train_data_set.append((["What cinematic genre is associated with ", "MOVIE", "?"], Intentions.AskGenre))
        train_data_set.append((["Which genre does the film ", "MOVIE", " represent?"], Intentions.AskGenre))

        train_data_set.append((["Is ", "MOVIE", "a", "GENRE", "movie?"], Intentions.AskIsGenre))
        train_data_set.append((["Is ", "MOVIE", "a", "GENRE", " movie"], Intentions.AskIsGenre))

        train_data_set.append((["Is ", "MOVIE", " considered a ", "GENRE", " film?"], Intentions.AskIsGenre))
        train_data_set.append((["Does ", "MOVIE", " fall under the ", "GENRE", " category?"], Intentions.AskIsGenre))
        train_data_set.append((["Would you classify ", "MOVIE", " as a ", "GENRE", " movie?"], Intentions.AskIsGenre))
        train_data_set.append(
            (["Is the movie ", "MOVIE", " a part of the ", "GENRE", " genre?"], Intentions.AskIsGenre))
        train_data_set.append((["Can ", "MOVIE", " be categorized as a ", "GENRE", " film?"], Intentions.AskIsGenre))
        train_data_set.append((["Does ", "MOVIE", " belong to the ", "GENRE", " genre?"], Intentions.AskIsGenre))
        train_data_set.append((["Is ", "MOVIE", " an example of a ", "GENRE", " movie?"], Intentions.AskIsGenre))
        train_data_set.append(
            (["Would ", "MOVIE", " be considered a ", "GENRE", " genre film?"], Intentions.AskIsGenre))
        train_data_set.append((["Is ", "MOVIE", " typically classified as ", "GENRE", "?"], Intentions.AskIsGenre))
        train_data_set.append((["Do people categorize ", "MOVIE", " as a ", "GENRE", " movie?"], Intentions.AskIsGenre))

        train_data_set.append((["What is the rating of the movie", "MOVIE", "?"], Intentions.AskRating))
        train_data_set.append((["What is the rating of the movie", "MOVIE", ], Intentions.AskRating))
        train_data_set.append((["What is the rating of ", "MOVIE", ], Intentions.AskRating))
        train_data_set.append((["Which movie has the highest rating?"], Intentions.AskRating))
        train_data_set.append((["Which movie has the highest rating"], Intentions.AskRating))
        train_data_set.append(([f"Which movie has the highest rating from the genre ", "GENRE"], Intentions.AskRating))
        train_data_set.append((["What rating did ", "MOVIE", " receive from critics? "], Intentions.AskRating))
        train_data_set.append(
            (["What is the audience score for ", "MOVIE", " on Rotten Tomatoes? "], Intentions.AskRating))
        train_data_set.append((["Which ", "GENRE", " movie has the best reviews? "], Intentions.AskRating))
        train_data_set.append((["Can you tell me the rating of ", "MOVIE", " by viewers? "], Intentions.AskRating))
        train_data_set.append((["What are the top-rated movies in the ", "GENRE", " genre? "], Intentions.AskRating))
        train_data_set.append((["How is ", "MOVIE", " rated on Metacritic? "], Intentions.AskRating))
        train_data_set.append(
            (["Which film in the ", "GENRE", " category has the lowest ratings? "], Intentions.AskRating))
        train_data_set.append(
            (["What is the average rating for movies directed by ", "PERSON", "? "], Intentions.AskRating))
        train_data_set.append((["Are there any 5-star rated movies in ", "RELEASE_DATE", "? "], Intentions.AskRating))
        train_data_set.append((["What rating did ", "MOVIE", " get compared to ", "MOVIE", "? "], Intentions.AskRating))
        train_data_set.append(
            (["Which movie released in ", "RELEASE_DATE", " has the highest viewer rating? "], Intentions.AskRating))
        train_data_set.append((["What are the ratings of ", "PERSON", "'s latest movies? "], Intentions.AskRating))
        train_data_set.append((["Do any movies from ", "PERSON", " have a perfect score? "], Intentions.AskRating))

            train_data_set.append(
                (["Recommend movies similar to", "MOVIE", "MOVIE", "or", "MOVIE"], Intentions.RecommenderQuestion))
            train_data_set.append((["Given that I like ", "MOVIE", " ", "MOVIE", ", and ", "MOVIE",
                                    ", can you recommend some movies? "], Intentions.RecommenderQuestion))
            train_data_set.append((["Recommend movies like ", "MOVIE", ", ", "MOVIE", ", and ", "MOVIE", ". "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Can you suggest movies starring ", "PERSON", " and ", "PERSON", "? "], Intentions.RecommenderQuestion))
            train_data_set.append((["What are some films similar to ", "MOVIE", " featuring ", "PERSON", "? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["I enjoy movies directed by ", "PERSON", ", can you recommend others? "], Intentions.RecommenderQuestion))
            train_data_set.append((["List some movies in the genre of ", "GENRE", " that are like ", "MOVIE", ". "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append((["What movies should I watch if I liked ", "MOVIE", " and ", "MOVIE", " directed by ",
                                    "PERSON", "? "], Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Recommend movies with themes similar to ", "MOVIE", ". "], Intentions.RecommenderQuestion))
            train_data_set.append((["I'm a fan of ", "PERSON", ", can you suggest some of their lesser-known films? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append((["If I liked ", "MOVIE", ", which other ", "GENRE", " movies would I enjoy? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append((["Suggest some movies that blend the genres of ", "GENRE", " and ", "GENRE", ". "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append((["Can you recommend films that have a similar vibe to ", "MOVIE", " and star ", "PERSON",
                                    "? "], Intentions.RecommenderQuestion))
            random_genre = NERModel.randGenre()
            train_data_set.append((["What are some critically acclaimed films in the ", "GENRE", " category? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append((["If I enjoy the work of ", "PERSON", ", what other directors should I explore? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append((["Give me movie recommendations based on ", "MOVIE", "'s storytelling style. "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["What are some movies with a plot similar to ", "MOVIE", "? "], 
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["What are some hidden gem movies similar to ", "MOVIE", "? "], 
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["If I enjoyed ", "MOVIE", ", what are some other must-watch movies? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Can you recommend some classic ", "GENRE", " films similar to ", "MOVIE", "? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["I'm a fan of ", "GENRE", " movies like ", "MOVIE", ", any recommendations? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Give me suggestions for movies with a ", "GENRE", " theme similar to ", "MOVIE", ". "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["If I liked ", "MOVIE", " and ", "MOVIE", ", what other ", "GENRE", " films would you suggest? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Recommend some ", "GENRE", " movies that capture the essence of ", "MOVIE", ". "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["What are some highly-rated ", "GENRE", " films similar to ", "MOVIE", "? "], 
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Can you suggest movies with a ", "GENRE", " vibe similar to ", "MOVIE", "? "], 
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["If I enjoyed the cinematography of ", "MOVIE", ", what other films would you recommend for visuals? "],
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["I'm looking for movies that have a ", "GENRE", " feel, any recommendations? "], 
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["What are some lesser-known films similar to ", "MOVIE", "? "], 
                                   Intentions.RecommenderQuestion))
            train_data_set.append(
                (["If I enjoyed ", "MOVIE", " and ", "MOVIE", ", what are some other movies in the same ", "GENRE", "? "],
                 Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Can you recommend movies similar to the style of ", "PERSON", "? "], Intentions.RecommenderQuestion))
            train_data_set.append(
                (["What are some classic movies in the ", "GENRE", " genre that I might like if I enjoyed ", "MOVIE", "? "],
                 Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Suggest some movies similar to the works of ", "PERSON", ". "], Intentions.RecommenderQuestion))
            train_data_set.append(
                (["If I liked the soundtrack of ", "MOVIE", ", can you recommend other movies with a similar music style? "],
                 Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Recommend movies with a similar atmosphere to ", "MOVIE", ". "], Intentions.RecommenderQuestion))
            train_data_set.append(
                (["I'm a fan of ", "PERSON", "'s acting, can you suggest movies where they deliver outstanding performances? "],
                 Intentions.RecommenderQuestion))
            train_data_set.append(
                (["What are some thought-provoking movies similar to ", "MOVIE", "? "], Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Can you recommend movies with a twist ending similar to ", "MOVIE", "? "], Intentions.RecommenderQuestion))
            train_data_set.append(
                (["If I enjoyed the storytelling of ", "PERSON",
                  ", what other films with compelling narratives would you recommend? "],
                 Intentions.RecommenderQuestion))
            train_data_set.append(
                (["Suggest movies with a ", "GENRE", " theme similar to ", "MOVIE", ". "], Intentions.RecommenderQuestion))

        return train_data_set

    def loadModel(self):
        model = load('QuestionIntentModel.joblib')
        return model

    def trainModel(self):
        X_train = []
        train_labels = []
        for s in self.createTrainset():
            X_train.append(" ".join(s[0]))  # Satz als Ganzer
            train_labels.append(s[1].name)
        model = make_pipeline(TfidfVectorizer(), RandomForestClassifier())
        model.fit(X_train, train_labels)
        dump(model, 'QuestionIntentModel.joblib')


class Intentions(Enum):
    AskDirector = "AskDirector"
    AskScreenwriter = "AskScreenwriter"
    AskMainActor = "AskMainActor"
    AskReleaseDate = "AskReleaseDate"
    AskIsDirector = "AskIsDirector"
    AskIsScreenwriter = "AskIsScreenwriter"
    AskIsMainActor = "AskIsMainActor"
    AskIsReleaseDate = "AskIsReleaseDate"
    AskIsGenre = "AskIsGenre"
    AskGenre = "AskGenre"
    AskRating = "AskRating"
    RecommenderQuestion = "RecommenderQuestion"

    MultimediaQuestion = "MultimediaQuestion"
    CrowdSourcingQuestion = "CrowdSourcingQuestion"
