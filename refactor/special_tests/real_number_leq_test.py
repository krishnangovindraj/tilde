""" TODO: 
Consider committing to a restricted set of split values based on a heuristic such as MDL.
As described in Fayyad & Irani '93.
This is an inefficient exact test.
"""

from typing import List, Tuple
# from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery
from refactor.tilde_essentials.split_criterion import SplitCriterion

from problog.program import SimpleProgram
from problog.logic import Term, Constant, Not, Clause

from refactor.logic_manipulation_utils import TermManipulationUtils, PartialSubstitutionDict
from .special_test import SpecialTest, TildeTestResult
# from refactor.representation.language import TypeModeLanguage

class RealNumberLEQTest(SpecialTest):
    # This doesn't support conjunctions of non-special tests and special tests yet. (I updated it so that it might, but I'm unlikely to have tested it)
    # It shouldn't be impossible to integrate though.
    # My ideal solution would look like this: 
    #   Chain special_tests to just be a wrapper around evaluate (evaluate_wrapper) function, which is still a theta-subsumption.
    #   So if you have 2 special tests, the first one would prepare the test and call evaluate_wrapper on the second,
    #   The second would prepare the test and then call evaluate: TILDEQuery_wrapper, which does the regular evaluate for every example. 

    TEST_FUNCTOR_PREFIX = 'tilde__realnumber_leq_functor__'
    TEST_PLACEHOLDER_TERM = 'tilde__realnumber_leq__placeholder'

    ARG_MODES = ('+', 'c')
    REAL_CONST_TYPENAME = 'tilde_real_const'
    TEST_VARIABLE_AUTOINC = 0
    _POS_INF = 99999999

    def __init__(self, test_functor, type_name):

        super().__init__(test_functor, 2, self.ARG_MODES, (type_name, self.REAL_CONST_TYPENAME), [(test_functor+'_1', Constant(self.TEST_PLACEHOLDER_TERM))] )
        self.test_functor = test_functor
        self.type_name = type_name

        self.all_values = set()
        self.bg_values = set()
        self.example_values = {}    # Example -> SortedCollection(values)

    def is_stable(self):
        return False

    def run(self, placeholder_tilde_query: TILDEQuery, examples: List[Example], test_evaluator: 'TestEvaluator', split_criterion: SplitCriterion) \
        -> TildeTestResult:

        min_passing_vals = []
        for e in examples:
            val = self._find_smallest_passing_values(placeholder_tilde_query, e, test_evaluator)
            min_passing_vals.append( (val, e) )

        best_split_val = self._pick_best_split(examples, min_passing_vals, split_criterion)
        test_conj = self._replace_placeholder(placeholder_tilde_query, best_split_val)
        
        self._augment_examples(examples, best_split_val)

        test_conj.literal.refine_state = placeholder_tilde_query.literal.refine_state

        self._fix_refine_state(test_conj, best_split_val)
        
        test_results = [ (e, True if val <= best_split_val else False) for (val,e) in min_passing_vals]
        

        return TildeTestResult( test_conj, test_results)

    def setup(self, prediction_goal_handler, language, examples, bg_sp):
        # we need to get all the possible values of the real_type
        value_locations = {}
        for functor, arg_modes in language.list_refinement_modes():
            locations = []
            arity = len(arg_modes)
            arg_types = language.get_argument_types(functor, arity)
            for i in range(len(arg_modes)):
                if arg_types[i] == self.type_name: # and arg_modes[i] == '-' :
                    locations.append(i)
            
            if len(locations) > 0:
                value_locations[(functor, arity)] = locations
        
        
        # TODO: Add occurences in prediction_goal to value_locations
        locations = []
        for i in range(len(prediction_goal_handler.modes)):
            if prediction_goal_handler.types[i] == self.type_name:  # and prediction_goal_handler.modes[i] == '+':
                locations.append(i) 
        
        if len(locations) > 0:
            value_locations[(prediction_goal_handler.functor, len(prediction_goal_handler.modes))] = locations
        
                    
        for e in examples:
            self.example_values[e] = []
            for d in list(e.data) + [e.classification_term]:
                if (d.functor, d.arity) in value_locations:
                    for i in value_locations[(d.functor, d.arity)]:
                        self.example_values[e].append(d.args[i].value)
                        self.all_values.add( d.args[i].value )
            sorted(self.example_values[e])
        
        bg_values = set()
        for b in bg_sp:
            if type(b) == Clause and (b.head.functor, b.head.arity) in value_locations:
                d = b.head
            elif type(b) == Term and (b.functor, b.arity) in value_locations:
                d = b
            else:
                d = None
            if d is not None:
                # This code is pointless if we are saturating examples.
                for i in value_locations[(d.functor, d.arity)]:
                    if isinstance(d.args[i], Constant):
                        bg_values.add(d.args[i].value)
                        self.all_values.add( d.args[i].value )

        self.bg_values = [float(i) for i in list(bg_values)]

    # def notify_result(self, is_selected, test_result):
    #     NOT IMPLEMENTED!
    #     if is_selected:
    #         conj = test_result.test_conj
    #         boundary_value = conj.args[1]
    #         for (e,passes_test) in test_result.test_results:
    #             if passes_test:
    #                 for v in self.example_values[e]:
    #                     if v <= boundary_value:
    #                         e.example_data.add_fact( conj.apply( {conj.args[0]: Constant(v) } ) )
    #                 for v in self.bg_values:
    #                     if v <= boundary_value:
    #                         e.example_data.add_fact( conj.apply( {conj.args[0]: Constant(v) } ) )
                    

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
        
        c.extend(a[i:])
        c.extend(b[j:])
        return c
    
    def _run_test(self, placeholder_tilde_query: TILDEQuery, example: Example, example_values: List[float], split_point: float, test_evaluator: 'TestEvaluator')\
         -> bool:
        # TODO: Use value in self.example instead of the whole  constant
        # If you're wondering where the test is, it's here and one in _augment_examples:
        if not self._needs_presaturation(example):
            leq_grounded_facts = [ Term(self.test_functor, Constant(v), Constant(split_point)) for v in example_values if v <= split_point ]
            example.add_facts(leq_grounded_facts)

        instantiated_query = self._replace_placeholder(placeholder_tilde_query, Constant(split_point))
        test = test_evaluator.wrap_query(instantiated_query)
        test_result = test_evaluator.evaluate(example, test)
        test.destruct()
        
        return test_result

    def _replace_placeholder_in_term(self, conj: Term, split_value):
        conj_list = TermManipulationUtils.conjunction_to_list(conj)
        matches = [ i for i,t in enumerate(conj_list) if TermManipulationUtils.term_is_functor_or_negation(t, self.test_functor) ]
        if len(matches) != 1:
            raise NotImplementedError("Implementation only supports exactly one occurence of the functor " + self.test_functor)
        simple_match = conj_list[matches[0]]

        match = simple_match.child if isinstance(simple_match, Not) else simple_match
        
        modified_args = list(match.args)
        modified_args[1] = Constant(split_value)
        simple_replaced_literal = Term(match.functor, *modified_args)
        replaced_literal = Not(simple_match.functor, simple_replaced_literal) if isinstance(simple_match, Not) else simple_replaced_literal  

        conj_list[matches[0]] = replaced_literal
        
        return TermManipulationUtils.list_to_conjunction( conj_list )

    # WARNING: This does not handle multiple occurences of this test in the conjunction.
    def _replace_placeholder(self, placeholder_tilde_query: TILDEQuery, split_value: float) -> TILDEQuery:
        # The test for multiple occurences
        modified_conj = self._replace_placeholder_in_term(placeholder_tilde_query.literal, split_value)
        return TILDEQuery(placeholder_tilde_query.parent, modified_conj)
        
    def _find_smallest_passing_values(self, placeholder_tilde_query, example: Example, test_evaluator) -> float:
        candidate_points = self.merge_sorted_lists(self.example_values[example], self.bg_values)
        l = 0
        r = len(candidate_points)
        # Find first failing value - much more normal
        if self._needs_presaturation(example):
            e = self._presaturate_example(example, candidate_points)
        else:
            e = example.clone()

        while l < r:
            mid = (l+r)//2 
            if self._run_test(placeholder_tilde_query, e, self.example_values[example], candidate_points[mid], test_evaluator):
                r = mid
            else:
                l = mid + 1

        e.destruct()

        return candidate_points[l]

    def _pick_best_split(self, examples: List[Example], min_passing_vals: List[Tuple[float, Example]], split_criterion: SplitCriterion ) -> float:
        # TODO: Make split criteria incremental
        
        sorted_ex = sorted([t for t in min_passing_vals], key=lambda x: x[0])
        examples_satisfying = [t[1] for t in sorted_ex]
        vals = [-RealNumberLEQTest._POS_INF] + [t[0] for t in sorted_ex]
        examples_failing = []

        best_split = vals[-1]
        best_split_score = split_criterion.calculate(examples_satisfying, examples_failing) 

        while len(examples_satisfying) > 0:
            vals.pop()
            e = examples_satisfying.pop()
            examples_failing.append(e)
            split_score = split_criterion.calculate(examples_satisfying, examples_failing)
            if split_score > best_split_score:
                best_split = vals[-1]
                best_split_score = split_score

        return best_split
        
    def _augment_examples(self, examples: List[Example], best_split: float):
        best_split_constant = Constant(best_split)

        for e in examples:
            new_facts = [ Term(self.test_functor, Constant(v), best_split_constant) for v in self.example_values[e] if v <= best_split]
            if self._needs_presaturation(e):
                with e.extension_context() as ec:
                    ec.extend(new_facts)
            else:
                e.add_facts(new_facts)

    def _fix_refine_state(self, test_conj: Term, split_value: float):
        def _term_matches(term: Term):
            t = term.args[0] if term.functor == '\\+' else term
            return t.functor == self.test_functor and self.TEST_PLACEHOLDER_TERM in t.args
        
        l = test_conj.literal
        placeholder_terms = [t for t in l.refine_state if _term_matches(t)]
        for t in placeholder_terms:
            l.refine_state.remove(t)
            modified_term = self._replace_placeholder_in_term(t, split_value)
            l.refine_state.add( modified_term )

    def _needs_presaturation(self, example: Example):
        from refactor.query_testing_back_end.django.django_example import DjangoExample
        return isinstance(example, DjangoExample)

    def _presaturate_example(self, example: Example, candidate_points: List[float]):
        e = example.clone()
        for i in range(len(candidate_points)):
            for j in range(i,len(candidate_points)): # i, not i+1 because leq
                if candidate_points[i] <= candidate_points[j]:
                    e.add_fact(Term(self.test_functor, Constant(candidate_points[i]), Constant(candidate_points[j])))
        e.lock_example()
        return e
