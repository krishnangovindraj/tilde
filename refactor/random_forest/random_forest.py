from random import choices as random_choices 

from refactor.tilde_essentials.destuctable import Destructible
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_essentials.tree_node import TreeNode

from refactor.tilde_essentials.tree import DecisionTree

class RandomForest(DecisionTree):
    """
    Decision tree used for making predictions. Initially empty.
    An internal TreeNode tree is fitted on training examples using a TreeBuilder.
    """

    def __init__(self, n_trees, resample_size):
        self.trees = None
        self.tree_builder = None  # type: Optional[TreeBuilder]
        self.test_evaluator = None  # type: Optional[TestEvaluator]
        self.tree_pruner = None

        self.n_trees = n_trees
        self.resample_size = resample_size

        self.labels = None
        self._trees_left = 0


    def fit(self, examples, tree_builder: TreeBuilder):
        self.tree_builder = tree_builder
        self.test_evaluator = self.tree_builder.splitter.test_evaluator

        self._trees_left = self.n_trees
        self.trees = [self._build_one_tree(examples, tree_builder) for _ in range(self.n_trees)]

        labels = set()
        for t in self.trees:
            labels.update(t.get_labels())
        self.labels = list(labels)

    def _build_one_tree(self, examples, tree_builder: TreeBuilder) -> DecisionTree:
        resample_size = self.resample_size if self.resample_size > 0 else len(examples)
        resampled_examples = random_choices(examples, k=resample_size)
        decision_tree = DecisionTree()
        decision_tree.fit(resampled_examples, tree_builder)

        self._trees_left -= 1
        if self._trees_left % (self.n_trees/10)==0:
            print("Built ~%d%% of trees"%( 100*(1-float(self._trees_left)/self.n_trees)))

        return decision_tree

    def prune(self, pruning_function):
        for t in self.trees:
            pruning_function(t.tree)

    def predict(self, example):
        from collections import Counter
        all_predictions = [tree.predict(example) for tree in self.trees]

        # TODO: Other combination techniques?
        count_dict = Counter(all_predictions)
        highest_count, majority_class = max( ((count_dict[k],k) for k in count_dict), key= lambda x: x[0] )
        return majority_class

    def destruct(self):
        for t in self.trees:
            t.destruct()

    def get_labels(self):
        return self.labels

    def get_nb_of_nodes(self) -> int:
        return sum( t.get_nb_of_nodes() for t in self.trees ) / self.n_trees

    def get_nb_of_inner_nodes(self):
        return sum( t.get_nb_of_inner_nodes() for t in self.trees ) / self.n_trees

    def __str__(self):
        return  '\n'.join( "---Tree[%d]---\n%s\n\n"%(i, str(t)) for i, t in enumerate(self.trees))

def write_out_tree(fname: str, tree: DecisionTree):
    # write out tree
    print('\t--- writing out tree to: ' + fname)
    with open(fname, 'w') as f:
        f.write(str(tree))
