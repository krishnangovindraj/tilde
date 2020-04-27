import math


class SplitCriterion:
    """
    Abstract class for calculating a split criterion heuristic using the training examples in a node, split into the
    subsets of examples satisfying a test and those not satisfying that test.

    """

    def calculate(self, examples_satisfying_test, examples_not_satisfying_test):
        raise NotImplementedError('abstract method')

    def get_threshold(self):
        raise NotImplementedError('abstract method')

    def get_name(self):
        raise NotImplementedError('abstract method')


class SplitCriterionBuilder:
    """
    Get a split criterion based on its name as a string.
    """
    @staticmethod
    def get_split_criterion(split_criterion_str: str, examples, node_labels):
        if split_criterion_str == 'entropy':
            from refactor.split_criteria import InformationGain
            return InformationGain(examples, node_labels)
        elif split_criterion_str == 'variance_reduction':
            from refactor.split_criteria import VarianceReduction
            return VarianceReduction(examples)
        elif split_criterion_str == 'dummy_all_equal':
            from refactor.split_criteria import DummyAllEqual
            return DummyAllEqual(examples, node_labels)
        else:
            raise KeyError("Unknown leaf strategy: " + split_criterion_str)