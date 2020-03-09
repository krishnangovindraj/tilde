from typing import List

from problog.logic import Term, And, Not

class PartialSubstitutionDict:
    def __init__(self, partial_dict):
        self.partial_dict = partial_dict

    def __getitem__(self, key):
        self.partial_dict.get(key, key)


class TermManipulationUtils:

    @staticmethod
    def conjunction_to_list(conj: Term):
        def _conj2list_rec(conj, acc):
            if isinstance(conj, And):
                acc.append(conj.args[0])
                return _conj2list_rec(conj.args[1], acc)
            else:
                acc.append(conj)
                return acc

        return _conj2list_rec(conj, [])

    @staticmethod
    def list_to_conjunction(conj_list: List[Term]):
        def _list2conj_rec(conj_list, at_index):
            if at_index == len(conj_list) - 1:
                return conj_list[-1]
            else:
                return And(conj_list[at_index], _list2conj_rec(conj_list, at_index+1))

        return _list2conj_rec(conj_list, 0)

    @staticmethod
    def term_is_functor_or_negation(term: Term, functor: str):
            t = term.child if isinstance(term, Not) else term
            return t.functor == functor
        