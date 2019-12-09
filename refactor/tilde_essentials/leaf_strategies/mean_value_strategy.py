from refactor.tilde_essentials.leaf_strategy import DeterministicLeafStrategy, LeafBuilder


class MeanValueLS(DeterministicLeafStrategy):
    """
    Predict for an example the mean value of the target variable for the leaf 
    """
    def __init__(self, examples):
        self.mean_value = sum([ ex.regressand for ex in examples])/len(examples)
        self.variance = sum([ ex.regressand*ex.regressand for ex in examples])/len(examples) - self.mean_value * self.mean_value
        self.n_examples = len(examples)  # nb of examples in this leaf
    
    def to_string(self, node_indentation) -> str:
        # Maybe give an estimate of the variance as well
        return node_indentation + "Leaf, mean: " + "{:0.3f}".format(self.mean_value) + ", [var=" + "{:0.3f}".format(
            self.variance) + " ; n_examples= " + str(self.n_examples) + "]" + '\n'

    def to_string_compact(self):
        return '[' + self.mean_value + " +- " + str(
            self.variance) + " ; #" +  str(self.n_examples) + "]" + '\n'

    def predict(self, example):
        return self.mean_value

    def merge(self, other: 'MeanValueLS'):
        our_y_sum = self.mean * self.n_examples
        our_y2_sum = (self.variance + self.mean*self.mean) * self.n_examples
        
        other_y_sum = other.mean * other.n_examples
        other_y2_sum = (other.variance + other.mean*other.mean) * other.n_examples

        self.n_examples += other.n_examples
        self.mean = (our_y_sum + other_y_sum) / self.n_examples
        self.variance = (our_y2_sum + other_y2_sum)/self.n_examples - (self.mean * self.mean)
        
