from refactor.tilde_essentials.split_criterion import SplitCriterion
import math 

class DummyAllEqual(SplitCriterion):
    
    def __init__(self, examples=None, possible_labels=None):
        pass
    
    def get_threshold(self):
        return 0

    def calculate(self, examples_satisfying_test, examples_not_satisfying_test):
        return 1

    def get_name(self):
        return 'dummy_all_equal'


# class GiniIndex(SplitCriterion):
#     pass
