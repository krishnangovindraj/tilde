from refactor.tilde_essentials.query_wrapping import QueryWrapper
from refactor.representation.TILDE_query import TILDEQuery

class ProblogQueryWrapper(QueryWrapper):
    def __str__(self):
        return str(self.external_representation)
