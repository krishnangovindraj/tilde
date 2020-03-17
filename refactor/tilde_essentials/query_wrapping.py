from refactor.representation.TILDE_query import TILDEQuery
from refactor.tilde_essentials.destuctable import Destructible


class QueryWrapper(Destructible):
    def __init__(self, tilde_query: TILDEQuery, external_representation):
        self.tilde_query = tilde_query
        self.external_representation = external_representation
    
    def destruct(self):
        pass