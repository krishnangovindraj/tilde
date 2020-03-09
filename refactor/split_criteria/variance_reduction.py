from refactor.tilde_essentials.split_criterion import SplitCriterion

class VarianceReduction(SplitCriterion):
    """
    Calculates the information gain (for use as a split criterion)
    """
    threshold = 0.001

    def __init__(self, examples):
        self.n_examples = len(examples)
        self.variance_all_examples = self._variance(examples)

    def get_threshold(self):
        return VarianceReduction.threshold

    def calculate(self, examples_satisfying_test, examples_not_satisfying_test):
        score = self._variance_reduction(examples_satisfying_test, examples_not_satisfying_test)
        return score

    def _variance(self, list_of_examples) -> float:
        """Calculates the entropy of a list of examples. Entropy is also known as information.

        An example is an object containing a label, e.g. an instance of representation.example
        It is necessary to provide the list of all possible labels.

        :param list_of_examples
                A list of examples
        """

        nb_of_examples = len(list_of_examples)

        if nb_of_examples == 0:
            return 0
        y_sum = 0
        y2_sum = 0  # type: float


        for example in list_of_examples:
            y_sum += example.regressand
            y2_sum += example.regressand * example.regressand
        
        y_mean = y_sum/nb_of_examples

        return y2_sum/nb_of_examples - y_mean*y_mean

    def _variance_reduction(self, sublist_left, sublist_right) -> float:
        """
        Calculates the information gain of splitting a set of examples into two subsets.
        """
        if self.n_examples == 0:
            return 0

        var_redxn = self.variance_all_examples  # type: float

        var_redxn -= len(sublist_left) / self.n_examples * self._variance(sublist_left)
        var_redxn -= len(sublist_right) / self.n_examples * self._variance(sublist_right)
        return var_redxn

    def get_name(self):
        return 'variance_reduction'
