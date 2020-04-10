from refactor.tilde_essentials.splitter import SplitInfo

from refactor.tilde_essentials.stop_criterion import StopCriterion

import math

class IsolationForestStopCriterion(StopCriterion):
    
    def __init__(self, max_depth: int = math.inf):
        self.max_depth = max_depth
        
    def cannot_split_before_test(self, examples, depth):
        """
        """
        if depth >= self.max_depth:
            return True

        if len(examples) <= 1:
            return True

    def cannot_split_on_test(self, split_info: SplitInfo):
        if split_info is None:
            return True
        
        return False


