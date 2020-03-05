from typing import Tuple
from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery
class TildeTestResult:
    def __init__(self, test_query: TILDEQuery, test_results: Tuple[Example, bool]):
        self.test_query = test_query
        self.test_results = test_results

class SpecialTest:
    """
     Returns a SpecialTestResult object
    """
    def run(self, examples):
        raise NotImplementedError('abstract method')


    """
     Called once before the tree building begins so that any required pre-processing may be performed.
    """
    def setup(self, prediction_goal_handler, language, examples, bg_sp):
        raise NotImplementedError('abstract method')

    """
     Notifies the test of whether or not it was selected.
     Tests can then augment the examples with if required.
    """
    def notify_result(self, is_selected, test_result: TildeTestResult):
        raise NotImplementedError('abstract method')


    """
     If the test is stable, we can chain it with later ones.
     Else, an exception is thrown if chaining is attempted.
    """
    def is_stable(self):
        raise NotImplementedError('abstract method')