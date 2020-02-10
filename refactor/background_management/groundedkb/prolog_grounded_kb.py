from problog.logic import Term, Var, Constant
from problog.program import LogicProgram
from pyswip import Prolog
from .groundedkb import GroundedKB

""" For now, we use prolog """
class PrologGroundedKB(GroundedKB):
    def __init__(self):
        self._prolog = Prolog()
    
    def add_fact(self, fact):
        self._prolog.assertz(PrologGroundedKB._encode_term(term))

    def query_fact(self, fact):
        self._prolog.query(PrologGroundedKB._encode_term(query))

    @staticmethod
    def _encode_term(term:Term):
        # Use strings for now
        return str(term)

    