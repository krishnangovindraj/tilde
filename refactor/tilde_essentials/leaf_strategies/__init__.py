from refactor.tilde_essentials.leaf_strategy import LeafBuilder

class MajorityClassLeafBuilder(LeafBuilder):
    def __init__(self):
        pass

    def build(self, examples):
        from .majority_class_strategy import MajorityClassLS
        return MajorityClassLS(examples)

class MeanValueLeafBuilder(LeafBuilder):
    def __init__(self):
        pass

    def build(self, examples):
        from .mean_value_strategy import MeanValueLS
        return MeanValueLS(examples)
