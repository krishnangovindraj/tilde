from typing import List
from refactor.representation.TILDE_query import TILDEQuery 

from random import randint, choice as random_choice
from refactor.logic_manipulation_utils import TermManipulationUtils

class TestSampler:
    def __init__(self, all_tests: List[TILDEQuery]):
        self.all_tests = all_tests

    def pop_random(self) -> TILDEQuery:
        raise NotImplementedException("abstract method")

class UniformRandomTestSampler(TestSampler):
    def __init__(self, all_tests):
        super().__init__(all_tests)

    def pop_random(self):
        i = randint(0, len(self.all_tests)-1)
        candidate_test = self.all_tests[i]
        self.all_tests[i] = self.all_tests[-1]
        self.all_tests.pop()

        return candidate_test

class HierarchicalTestSampler(TestSampler):
    def __init__(self, all_tests):
        super().__init__(all_tests)
        tests_by_functor = { }
        for t in all_tests:
            k = tuple( (t.functor,t.arity) for t in TermManipulationUtils.conjunction_to_list(t.literal))
            if k not in tests_by_functor:
                tests_by_functor[k] = []
            tests_by_functor[k].append(t)
        self.tests_by_functor = tests_by_functor
        self.functor_keys = list(self.tests_by_functor.keys())
        self.n_tests = len(all_tests)

    def pop_random(self):
        possible_tests = []
        while len(possible_tests) == 0 and len(self.functor_keys) > 0:
            ki = randint(0, len(self.functor_keys)-1) 
            possible_tests = self.tests_by_functor[ self.functor_keys[ki] ]
            if len(possible_tests) <= 1:
                self.functor_keys[ki] = self.functor_keys[-1]
                self.functor_keys.pop()

        if len(possible_tests) == 0:
            return None

        i = randint(0, len(possible_tests)-1)
        candidate_test = possible_tests[i]
        possible_tests[i] = possible_tests[-1]
        possible_tests.pop()

        return candidate_test
