
from refactor.tilde_essentials.destuctable import Destructible
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_essentials.tree_node import TreeNode, count_nb_of_nodes, count_nb_of_inner_nodes


from refactor.tilde_essentials.tree import DecisionTree

# TODO: Everything here.


class RandomForest:
    """
    Decision tree used for making predictions. Initially empty.
    An internal TreeNode tree is fitted on training examples using a TreeBuilder.

    """

    def __init__(self, n_trees):
        self.tree = None  # type: Optional[TreeNode]
        self.tree_builder = None  # type: Optional[TreeBuilder]
        self.test_evaluator = None  # type: Optional[TestEvaluator]
        self.tree_pruner = None
        
        self.n_trees = n_trees

    def fit(self, examples, tree_builder: TreeBuilder):
        self.tree_builder = tree_builder
        self.test_evaluator = self.tree_builder.splitter.test_evaluator
        
        self.trees = [self._build_one_tree(examples) for _ in range(self.n_trees)]
        
    # TODO: Example resampling
    def _build_one_tree(self, examples):
        tree = self.tree_builder.build(examples)
        if self.tree_pruner is not None:
            tree = self.tree_pruner.prune(tree)
        return tree

    def predict(self, example):
        from collections import Counter
        all_predictions = [tree.predict(example) for tree in self.trees]

        # TODO: Other combination techniques?
        count_dict = Counter(all_predictions)
        highest_count, majority_class = max( (count_dict[k],k) for k in count_dict )
        return majority_class

    def __str__(self):
        return self.tree.__str__()

    def destruct(self):
        self.tree.destruct()

    def get_nb_of_nodes(self) -> int:
        return count_nb_of_nodes(self.tree)

    def get_nb_of_inner_nodes(self):
        return count_nb_of_inner_nodes(self.tree)

    def __str__(self):
        return  '\n'.join( "---\nTree[%d]\n%s\n---\n"%(i, str(t)) for i, t in enumerate(self.trees))   

def write_out_tree(fname: str, tree: DecisionTree):
    # write out tree
    print('\t--- writing out tree to: ' + fname)
    with open(fname, 'w') as f:
        f.write(str(tree))
