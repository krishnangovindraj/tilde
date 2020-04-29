from typing import List, Tuple
# from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery
from refactor.tilde_essentials.split_criterion import SplitCriterion

from problog.program import SimpleProgram
from problog.logic import Term, Constant, Not, Clause

from refactor.logic_manipulation_utils import TermManipulationUtils, PartialSubstitutionDict
from .special_test import SpecialTest, TildeTestResult
""" A really simple 'auto' mode for constants """
class UnifyToValueTest(SpecialTest):

    ARG_MODES = ('+', 'c')
   
    def __init__(self, test_functor, type_name):
        self.constant_type_name = type_name
        super().__init__(test_functor, 2, self.ARG_MODES, (type_name, self.constant_type_name), [])
        self.test_functor = test_functor
        self.type_name = type_name

        self.all_values = set()

    """
     Returns a TildeTestResult object
    """
    def run(self, placeholder_tilde_query: TILDEQuery, examples: List[Example], test_evaluator: 'TestEvaluator', split_criterion: SplitCriterion) \
        -> TildeTestResult:
        conj_list = TermManipulationUtils.conjunction_to_list(placeholder_tilde_query.literal)
        matches = [ t for t in conj_list if TermManipulationUtils.term_is_functor_or_negation(t, self.test_functor) ]

        for m in matches:       
            self._augment_examples(examples, m.args[1])
        return TildeTestResult(placeholder_tilde_query, [])

    """
     Called once before the tree building begins so that any required pre-processing may be performed.
    """
    def setup(self, prediction_goal_handler, language, examples, bg_sp):
        # we need to get all the possible values of the real_type
        value_locations = {}
        for functor, arg_modes in language.list_refinement_modes():
            locations = []
            arity = len(arg_modes)
            arg_types = language.get_argument_types(functor, arity)
            for i in range(len(arg_modes)):
                if arg_types[i] == self.type_name: # and arg_modes[i] == '-':
                    locations.append(i)

            if len(locations) > 0:
                value_locations[(functor, arity)] = locations

        locations = []
        for i in range(len(prediction_goal_handler.modes)):
            if prediction_goal_handler.types[i] == self.type_name: # and prediction_goal_handler.modes[i] == '+': 
                locations.append(i)

        if len(locations) > 0:
            value_locations[(prediction_goal_handler.functor, len(prediction_goal_handler.modes))] = locations


        for e in examples:
            for d in list(e.data) + [e.classification_term]:
                if (d.functor, d.arity) in value_locations:
                    for i in value_locations[(d.functor, d.arity)]:
                        self.all_values.add( d.args[i] )

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
                        self.all_values.add( d.args[i] )

        # All work done here:
        language.add_values(self.test_functor+'_1', *self.all_values)


    """
     Notifies the test of whether or not it was selected.
     Tests can then augment the examples with if required.
    """
    def notify_result(self, is_selected, test_result: TildeTestResult):
        pass


    """
     If the test is stable, we can chain it with later ones.
     Else, an exception is thrown if chaining is attempted.
    """
    def is_stable(self):
        return True

    def _augment_examples(self, examples: List[Example], value: float):
        value_constant = Constant(value)

        for e in examples:
            new_facts = [ Term(self.test_functor, value_constant, value_constant)]
            if self._needs_presaturation(e):
                with e.extension_context() as ec:
                    ec.extend(new_facts)
            else:
                e.add_facts(new_facts)
    
    def _needs_presaturation(self, example: Example):
        from refactor.query_testing_back_end.django.django_example import DjangoExample
        return isinstance(example, DjangoExample)
