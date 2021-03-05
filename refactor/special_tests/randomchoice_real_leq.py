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
            for e in examples:
                passes_test = test_evaluator.evaluate(e, test)
                insufficient_split |= 1 if passes_test else 2
                test_results.append( (e, passes_test) )

            test.destruct()

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
                        self.example_values[e].append(d.args[i])
                        self.all_values.add( d.args[i] )
            sorted(self.example_values[e], key=lambda x: x.value)

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
                        bg_values.add(d.args[i])
                        self.all_values.add( d.args[i] )

        self.bg_values = list(bg_values)

        self._saturate_examples(examples)

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


    def _saturate_examples(self, examples: List[Example]):
        for e in examples:
            visible_values = set(self.bg_values)  # These are silly outdated thanks to saturation, but meh.
            visible_values.update(self.example_values[e])
            new_facts = [Term(self.test_functor, l, g) for l in visible_values for g in self.all_values if l.value <= g.value]
            if self._needs_presaturation(e):
                with e.extension_context() as ec:
                    ec.extend(new_facts)
            else:
                e.add_facts(new_facts)
