from typing import List, Tuple, Dict
# from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery
from refactor.tilde_essentials.split_criterion import SplitCriterion

from problog.program import SimpleProgram
from problog.logic import Term, Constant, Not, Clause

from refactor.logic_manipulation_utils import TermManipulationUtils, PartialSubstitutionDict
from .special_test import SpecialTest, TildeTestResult
# from refactor.representation.language import TypeModeLanguage

class RandomChoiceRealNumberLEQTest(SpecialTest):
    # This doesn't support conjunctions of non-special tests and special tests yet. (I updated it so that it might, but I'm unlikely to have tested it)
    # It shouldn't be impossible to integrate though.
    # My ideal solution would look like this:
    #   Chain special_tests to just be a wrapper around evaluate (evaluate_wrapper) function, which is still a theta-subsumption.
    #   So if you have 2 special tests, the first one would prepare the test and call evaluate_wrapper on the second,
    #   The second would prepare the test and then call evaluate: TILDEQuery_wrapper, which does the regular evaluate for every example.

    TEST_FUNCTOR_PREFIX = 'tilde__randomchoice_realnumber_leq_functor__'
    TEST_PLACEHOLDER_TERM = 'tilde__randomchoice_realnumber_leq__placeholder'

    ARG_MODES = ('+', 'c')
    REAL_CONST_TYPENAME = 'tilde_real_const'

    TEST_VARIABLE_AUTOINC = 0
    _POS_INF = 99999999

    DEFAULT_MAX_RETRIES = 5

    def __init__(self, test_functor : str, type_name : str, max_retries: int = DEFAULT_MAX_RETRIES):
        super().__init__(test_functor, 2, self.ARG_MODES, (type_name, self.REAL_CONST_TYPENAME), [(test_functor+'_1', Constant(self.TEST_PLACEHOLDER_TERM))] )
        self.test_functor = test_functor

        self.type_name = type_name
        self.all_values = set()
        self.bg_values = set()
        self.example_values = {}    # Example -> SortedCollection(values)
        self.max_retries = max_retries

    def is_stable(self):
        return False

    def run(self, placeholder_tilde_query: TILDEQuery, examples: List[Example], test_evaluator: 'TestEvaluator', split_criterion: SplitCriterion) \
        -> TildeTestResult:

        from random import sample as random_sample
        insufficient_split = 0

        # Pre-generate split_vals so django can be pre-saturated.
        candidate_split_vals = random_sample(self.all_values, self.max_retries)
        example_clone_map = {e:e.clone() for e in examples}
        self._augment_examples(example_clone_map, candidate_split_vals)

        sample_i = 0
        while insufficient_split!=3 and sample_i < len(candidate_split_vals):
            random_split_val = candidate_split_vals[sample_i]
            sample_i += 1
            test_conj = self._replace_placeholder(placeholder_tilde_query, random_split_val)

            test_conj.literal.refine_state = placeholder_tilde_query.literal.refine_state

            self._fix_refine_state(test_conj, random_split_val)

            test_results = []
            test = test_evaluator.wrap_query(test_conj)

            insufficient_split = 0
            for e in example_clone_map:
                passes_test = test_evaluator.evaluate(example_clone_map[e], test)
                insufficient_split |= 1 if passes_test else 2
                test_results.append( (e, passes_test) )

            test.destruct()

        self._augment_examples( {e:e for e in examples}, [random_split_val])

        return TildeTestResult( test_conj, test_results)

    def setup(self, prediction_goal_handler, language, examples, bg_sp):
        # we need to get all the possible values of the real_type
        value_locations = {}
        for functor, arg_modes in language.list_refinement_modes():
            locations = []
            arity = len(arg_modes)
            arg_types = language.get_argument_types(functor, arity)
            for i in range(len(arg_modes)):
                if arg_modes[i] == '-' and arg_types[i] == self.type_name:
                    locations.append(i)

            if len(locations) > 0:
                value_locations[(functor, arity)] = locations


        # TODO: Add occurences in prediction_goal to value_locations
        locations = []
        for i in range(len(prediction_goal_handler.modes)):
            if prediction_goal_handler.modes[i] == '+' and prediction_goal_handler.types[i] == self.type_name:
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

    def _augment_examples(self, example_target_map: Dict[Example,Example], split_vals: List[float] ):
        split_constants = [Constant(split_val) for split_val in split_vals]

        for original_e in example_target_map:
            e = example_target_map.get(original_e,original_e)
            new_facts = []
            for split_val, split_constant in zip(split_vals, split_constants):
                new_facts = [ Term(self.test_functor, Constant(v), split_constant) for v in self.example_values[original_e] if v <= split_val]
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
