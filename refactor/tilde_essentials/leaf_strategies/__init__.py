from refactor.tilde_essentials.leaf_strategy import LeafBuilder

class MajorityClassLeafBuilder(LeafBuilder):
    def __init__(self):
        pass

    def build(self, examples):
        from .majority_class_strategy import MajorityClassLS
        return MajorityClassLS(examples)


    def is_classification(self):
        return True

class MeanValueLeafBuilder(LeafBuilder):
    def __init__(self):
        pass

    def build(self, examples):
        from .mean_value_strategy import MeanValueLS
        return MeanValueLS(examples)

    def is_classification(self):
        return False

class DummyLeafBuilder(LeafBuilder):
    def __init__(self):
        pass

    def build(self, examples):
        from .dummy_strategy import DummyStrategy
        return DummyStrategy(examples)

    def is_classification(self):
        return False
