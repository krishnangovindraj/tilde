""" TODO: 
Consider committing to a restricted set of split values based on a heuristic such as MDL.
As described in Fayyad & Irani '93.
This is an inefficient exact test.
"""

from typing import List, Tuple
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery
from refactor.tilde_essentials.split_criterion import SplitCriterion

from problog.program import SimpleProgram
from problog.logic import Term, Constant

from refactor.logic_manipulation_utils import TermManipulationUtils, PartialSubstitutionDict
from .special_test import SpecialTest, TildeTestResult
# from refactor.representation.language import TypeModeLanguage

class RealNumberLessThanTest(SpecialTest):
    # This doesn't support conjunctions of non-special tests and special tests yet. (I updated it so that it might, but I'm unlikely to have tested it)
    # It shouldn't be impossible to integrate though.
    # My ideal solution would look like this: 
    #   Chain special_tests to just be a wrapper around evaluate (evaluate_wrapper) function, which is still a theta-subsumption.
    #   So if you have 2 special tests, the first one would prepare the test and call evaluate_wrapper on the second,
    #   The second would prepare the test and then call evaluate: TILDEQuery_wrapper, which does the regular evaluate for every example. 

    TEST_FUNCTOR_PREFIX = 'tilde__realnumber_lessthan_functor__'
    TEST_PLACEHOLDER_TERM = 'Tilde__realnumber_lessthan__placeholder'

    TEST_VARIABLE_AUTOINC = 0
    _POS_INF = 99999999

    def __init__(self, test_functor, test_arity, type_name):
        self.test_functor = test_functor
        self.test_arity = test_arity
        self.type_name = type_name
        self.all_values = set()
        self.bg_values = set()
        self.example_values = {}    # Example -> SortedCollection(values)
        
    def run(self, placeholder_tilde_query: TILDEQuery, examples: List[Example], test_evaluator: TestEvaluator, split_criterion: SplitCriterion) -> TildeTestResult:
        min_failing_vals = []
        for e in examples:
            val = self._find_smallest_failing_values(placeholder_tilde_query, e, test_evaluator)
            min_failing_vals.append( (val, e) ) 

        best_split_val = self._pick_best_split(examples, min_failing_vals, split_criterion)
        test_conj = self._replace_placeholder(placeholder_tilde_query, best_split_val)
        test_results = [ (e, True if val < best_split_val else False) for (val,e) in min_failing_vals]
        
        return TildeTestResult( test_conj, test_results)

    def setup(self, language, examples, bg_sp):
        # we need to get all the possible values of the real_type
        value_locations = {}
        for functor, arg_modes in language.list_refinement_modes():
            locations = []
            arity = len(arg_modes)
            arg_types = language.get_argument_types( (functor, arity) )
            for i in range(len(arg_modes)):
                if arg_modes[i] == '-' and arg_types[i] == self.type_name:
                    locations.append(i)
            
            if len(locations) > 0:
                value_locations[(functor, arity)] = i
            
                    
        for e in examples:
            self.example_values[e] = []
            for d in e.data:
                if (d.functor, d.arity) in value_locations:
                    for i in value_locations[(d.functor, d.arity)]:
                        self.example_values[e].append(d.args[i])
                        self.all_values.add( d.args[i] )
            sorted(self.example_values[e])
        
        for b in bg_sp:
            head = b.head
            if (b.head.functor, b.head.arity) in value_locations:
                for i in value_locations[(d.functor, d.arity)]:
                    if isinstance(d.args[i], Constant): 
                        self.bg_values.add(d.args[i])
                        self.all_values.add( d.args[i] )


    def notify_result(self, is_selected, test_result):
        if is_selected:
            conj = test_result.test_conj
            boundary_value = conj.args[1]
            for (e,passes_test) in test_result.test_results:
                if passes_test:
                    for v in self.example_values[e]:
                        if v < boundary_value:
                            e.example_data.add_fact( conj.apply( {conj.args[0]: Constant(v) } ) )
                    for v in self.bg_values:
                        if v < boundary_value:
                            e.example_data.add_fact( conj.apply( {conj.args[0]: Constant(v) } ) )
                    

    @staticmethod
    def merge_sorted_lists(a,b):
        i = 0
        j = 0
        c = []
        while i < len(a) and j < len(b):
            if a[i] == b[j]:
                j+=1
            elif a[i] < b[j]:
                c.append(a[i])
                i+=1
            else:
                c.append(b[j])
                j += 1
        
        c.append(a[i:])
        c.append(b[j:])
        return c
    
    def _run_test(self, placeholder_tilde_query: TILDEQuery, example: Example, split_point: float, test_evaluator: TestEvaluator) -> bool:
        lt_grounded_facts = [ Term(self.test_functor, v, split_point) for v in self.example_values[example] ]
        example.data.update(lt_grounded_facts)
        instantiated_test_conj = self._replace_placeholder(placeholder_tilde_query, split_point)
        return test_evaluator.evaluate(example, instantiated_test_conj)

    # WARNING: This does not handle multiple occurences of this test in the conjunction.
    def _replace_placeholder(self, placeholder_tilde_query: TILDEQuery, split_value: float) -> TILDEQuery:
        # The test for multiple occurences
        
        matches = [ t for t in TermManipulationUtils.conjunction_to_list(placeholder_tilde_query.literal) if t.functor == self.test_functor ]
        if matches != 1:
            raise NotImplementedError("Implementation only supports exactly one occurence of the functor " + self.test_functor)
        instantiated_literal = placeholder_tilde_query.literal.apply( PartialSubstitutionDict({self.TEST_PLACEHOLDER_TERM: Constant(split_value)}) )
        return TILDEQuery(placeholder_tilde_query.parent, instantiated_literal)
        
    def _find_smallest_failing_values(self, placeholder_tilde_query, e: Example, test_evaluator) -> float:
        candidate_points = self.merge_sorted_lists(self.example_values[e], self.bg_values)
        l = 0
        r = len(candidate_points)
        # Find first failing value - much more normal
        # TODO: what if all pass / all fail? 
        #   All fail should be impossible. All pass -> return biggest
        while l < r:
            mid = (l+r)//2 
            if self._run_test(placeholder_tilde_query, e, candidate_points[mid], test_evaluator):
                r = mid
            else:
                l = mid + 1
       
        return candidate_points[l]

    def _pick_best_split(self, examples: List[Example], min_failing_vals: List[Tuple[float, Example]], split_criterion: SplitCriterion ) -> float:
        # TODO: Make split criteria incremental
        
        sorted_ex = sorted([t for t in min_failing_vals])
        examples_satisfying = [t[1] for t in sorted_ex]
        vals = [t[0] for t in sorted_ex]
        examples_failing = []

        best_split = RealNumberLessThanTest._POS_INF
        best_split_score = split_criterion.calculate(examples_satisfying, examples_failing) 

        while len(examples_satisfying) > 0:
            val = vals.pop()
            e = examples_satisfying.pop()
            examples_failing.append(e)
            split_score = split_criterion.calculate(examples_satisfying, examples_failing)
            if split_score > best_split_score:
                best_split = val
                best_split_score = split_score

        return best_split
        
