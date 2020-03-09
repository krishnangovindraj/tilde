
class LeafStrategy:
    """
    Abstract LeafStrategy class used in a leaf node for making a prediction for an example
    """
    def to_string(self, node_indentation) -> str:
        raise NotImplementedError('abstract method')

    def to_string_compact(self):
        raise NotImplementedError('abstract method')

    def predict(self, example):
        raise NotImplementedError('abstract method')

    # Some constants

class DeterministicLeafStrategy(LeafStrategy):
    pass

class LeafBuilder:
    """
    Abstract class. Create a leaf strategy based on the training examples (sorted into a leaf node)
    """
    def __init__(self):
        raise NotImplementedError('abstract method')

    def build(self, examples):
        raise NotImplementedError('abstract method')
    
    def encode_to_tuple(self):
        raise NotImplementedError('abstract method')
    
    @staticmethod
    def get_leaf_builder(leaf_strategy: str):
        if leaf_strategy == 'mean_value':
            from refactor.tilde_essentials.leaf_strategies import MeanValueLeafBuilder 
            return MeanValueLeafBuilder()
        elif leaf_strategy == 'majority_class':
            from refactor.tilde_essentials.leaf_strategies import MajorityClassLeafBuilder 
            return MajorityClassLeafBuilder()
        else:
            raise KeyError("Unknown leaf strategy: " + leaf_strategy)
