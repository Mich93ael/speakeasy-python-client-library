from enum import Enum

from difflib import SequenceMatcher


class RelationMapper:

    @staticmethod
    def similar(a, b):
        # Überprüfen, ob einer der Strings im anderen enthalten ist
        if (a in b or b in a) and len(a)>3:
            return 1.0-0.001*(abs(len(a)-len(b)))
        else:
            return SequenceMatcher(None, a, b).ratio()

    def extract_matching_relation_from_mapping(self, relevant_text):
        value = 0
        safedRelation = None
        for mapping in MappingRelation:
            if self.similar(mapping.value[0], relevant_text) > value:
                safedRelation = mapping
                value = self.similar(mapping.value[0], relevant_text)
        if (value < 0.1):
            return None
        return safedRelation


class MappingRelation(Enum):
    DIRECTOR = ("director", "P57")
    SCREENWRITER = ("screenwriter", "P58")
    ACTOR = ("actor", "P161")
    RELEASE_DATE = ("releaseDate", "P577")
    GENRE = ("genre", "P136")
    RATING = ("rating", "P31")
    MAIN_ACTOR = ("mainActor", "P161")
    MAIN_DIRECTOR = ("mainDirector", "P57")
    MAIN_SCREENWRITER = ("mainScreenwriter", "P58")
    MAIN_GENRE = ("mainGenre", "P136")
