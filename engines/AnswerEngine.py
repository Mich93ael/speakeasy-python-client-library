from html import entities

from engines.CrowdsourcingEngine import CrowdsourcingEngine, CrowdsourcingKeys
from engines.EmbeddedEngine import EmbeddedEngine
from QuestionClassifier import Questions
from engines.MultiMediaEngine import MultiMediaEngine
from engines.OthersEngine import OthersEngine
from engines.RecommenderEngine import RecommenderEngine


class AnswerEngine:
    def __init__(self, graph,movieList):
        self.graph = graph
        print("movieList loading:")
        self.movieList = movieList
        print("movieList loaded")
        self.embeddedEngine = EmbeddedEngine(graph, self.movieList)
        self.recommenderEngine = RecommenderEngine(graph, self.movieList)
        self.multimediaEngine = MultiMediaEngine(graph, self.movieList)
        self.crowdsourcingEngine = CrowdsourcingEngine(graph, self.movieList)

    def getAllPersonsAndDirectorsAndActors(self):
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
        for result in self.graph.query(query):
            person_list.append(result)
        return person_list

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

    def answer(self, questiontyp, question):
        for keys in CrowdsourcingKeys:
            if keys.value[1].lower() in question.lower():
                return self.crowdsourcingEngine.answer(question,keys)
        if str(questiontyp[0]) == Questions.EmbeddedQuestion.value:
            return self.embeddedEngine.answer(question)
        if str(questiontyp[0]) == Questions.RecommenderQuestion.value:
            return self.recommenderEngine.answer(question)
        if str(questiontyp[0]) == Questions.MultiMediaQuestion.value:
            return self.multimediaEngine.answer(question)
        if str(questiontyp[0]) == Questions.CrowdsourcingQuestion.value:
            return self.crowdsourcingEngine.answer(question)
        return OthersEngine().answer(question)
