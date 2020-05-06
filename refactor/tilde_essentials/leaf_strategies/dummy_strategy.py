from refactor.tilde_essentials.example import calculate_label_frequencies_and_absolute_counts
from refactor.tilde_essentials.leaf_strategy import DeterministicLeafStrategy

class DummyStrategy(DeterministicLeafStrategy):
    """
    Predict for an example the majority class of a leaf
    """
    def __init__(self, examples):
        self.label_frequencies, self.label_counts = calculate_label_frequencies_and_absolute_counts(examples)
        self.n_examples = len(examples)  # nb of examples in this leaf

    def to_string(self, node_indentation) -> str:
        return node_indentation + "DummyLeaf[" +str(self.n_examples) + "]" + '\n'

    def to_string_compact(self):
        return "[" + str(self.n_examples) + "]" + '\n'

    def predict(self, example):
        return None

    def merge(self, other: 'MajorityClassLS'):
        self.n_examples += other.n_examples

        for label in other.label_frequencies:
            self.label_frequencies[label] = self.label_frequencies.get(label, 0) + other.label_frequencies[label]
            self.label_counts[label] = self.label_counts.get(label, 0) + other.label_counts[label]
        
    def encode_to_tuple(self):
        return ( str("dummy"), [ (str(t[0]), str(t[1])) for t in self.label_frequencies.items() ] )
    