from refactor.tilde_essentials.query_wrapping import QueryWrapper
from refactor.representation.TILDE_query import TILDEQuery

class DjangoQueryWrapper(QueryWrapper):
    def __str__(self):
        return str(self.tilde_query.to_conjunction())

    def destruct(self):
        self.external_representation.destruct()
