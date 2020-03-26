from typing import Optional

from problog.logic import Term

from refactor.tilde_essentials.tree_node import TreeNode
from refactor.representation.TILDE_query import TILDEQuery, TILDEQueryHiddenLiteral
from refactor.tilde_essentials.refinement_controller import RefinementController
from refactor.representation.language import TypeModeLanguage

class TestGeneratorBuilder:
    """
    Builds a generator to produce possible tests in a node to be split.

    """
    def generate_possible_tests(self, examples, current_node):
        raise NotImplementedError('abstract method')


class FOLTestGeneratorBuilder(TestGeneratorBuilder):
    """
    Builds a generator to produce possible tests in a node to be split.
    Finds the associated test of the node, which is the test of the ancestor of the current node whose test should be refined.

    """
    def __init__(self, language: TypeModeLanguage,
                 query_head_if_keys_format: Optional[Term] = None):
        self.language = language
        # the associated query of the root node
        self.initial_query = FOLTestGeneratorBuilder.get_initial_query(query_head_if_keys_format)

    def generate_possible_tests(self, examples, current_node):
        query_to_refine = self._get_associated_query(current_node)
        generator = RefinementController.get_refined_query_generator(
            query_to_refine, self.language)
        return generator


    @staticmethod
    def get_initial_query(query_head_if_keys_format: Optional[Term] = None):
        if query_head_if_keys_format is not None:
            initial_query = TILDEQueryHiddenLiteral(query_head_if_keys_format)
        else:
            initial_query = TILDEQuery(None, None)
        return initial_query

    def _get_associated_query(self, current_node: TreeNode) -> TILDEQuery:

        query_to_refine = None
        ancestor = current_node

        while query_to_refine is None:
            if ancestor.parent is None:
                query_to_refine = self.initial_query
            else:
                # NOTE: this depends on whether the current node is the LEFT or RIGHT subtree
                # IF it is the left subtree:
                #       use the query of the parent
                # ELSE (if it is the right subtree:
                #       go higher up in the tree
                #          until a node is found that is the left subtree of a node
                #           OR the root is reached

                parent_of_ancestor = ancestor.parent
                if ancestor is parent_of_ancestor.left_child:
                    query_to_refine = parent_of_ancestor.test.tilde_query
                else:
                    ancestor = parent_of_ancestor
        return query_to_refine


