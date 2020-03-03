class TildeTestResult:
    def __init__(self, test_conj, test_results):
        self.test_conj = test_conj
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
    def setup(self, language, examples, bg_sp):
        raise NotImplementedError('abstract method')

    """
     Notifies the test of whether or not it was selected.
     Tests can then augment the examples with if required.
    """
    def notify_result(self, is_selected, test_result: TildeTestResult):
        raise NotImplementedError('abstract method')