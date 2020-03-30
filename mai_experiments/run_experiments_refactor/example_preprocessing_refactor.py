from typing import Optional, List, Set

from problog.engine import DefaultEngine
from problog.logic import Term
from problog.program import SimpleProgram

from mai_experiments.experiment_settings import FileNameData, DebugPrintingOptions

from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.query_testing_back_end.django.clause_handling import destruct_tree_tests
from refactor.io.input_format import KnowledgeBaseFormat
from refactor.io.label_collector import LabelCollectorMapper
from refactor.io.parsing_background_knowledge import parse_background_knowledge_keys
from refactor.io.parsing_examples import KeysExampleBuilder
from refactor.io.parsing_settings.setting_parser import KeysSettingsParser, SettingsParserMapper
from refactor.representation.example import InternalExampleFormat, ClauseDBExampleWrapper
from refactor.model_factory import ModelFactory

from mai_experiments.experiment_settings import FileNameData, DebugPrintingOptions


class Experiment:
    """
    NOTE: we store the examples in 2 ways:
    * 'usable for training': the examples containing the classification predicate
    * 'usable for testing': the examples with the classification predicate removed
    """

    def __init__(self, file_name_data: FileNameData):
        self.file_name_data = file_name_data

        self.training_examples_collection = None
        self.examples_usable_for_testing = None
        self.possible_labels = None

        self.language = None
        self.prediction_goal_handler = None

        self.model_factory = None

    def parse_settings(self):
        settings_file_parser = SettingsParserMapper.get_settings_parser(KnowledgeBaseFormat.KEYS)
        parsed_settings = settings_file_parser.parse(self.file_name_data.fname_settings)

        self.language = parsed_settings.language  # type: TypeModeLanguage
        self.prediction_goal_handler = parsed_settings.get_prediction_goal_handler()  # type: KeysPredictionGoalHandler
        self.prediction_goal = self.prediction_goal_handler.get_prediction_goal()  # type: Term

    def preprocess_examples_and_background_knowledge(self,
                                                     model_factory: ModelFactory,
                                                     filter_out_unlabeled_examples: bool,
                                                     debug_printing_options: DebugPrintingOptions):
        engine = DefaultEngine()
        engine.unknown = 1

        kb_format = KnowledgeBaseFormat.KEYS
        internal_ex_format = InternalExampleFormat.CLAUSEDB

        # ------------------------------------------------
        # --- BACKGROUND KNOWLEDGE -----------------------
        # ------------------------------------------------

        background_knowledge_wrapper \
            = parse_background_knowledge_keys(self.file_name_data.fname_background,
                                              self.prediction_goal)  # type: BackgroundKnowledgeWrapper

        full_background_knowledge_sp \
            = background_knowledge_wrapper.get_full_background_knowledge_simple_program()  # type: Optional[SimpleProgram]
        stripped_background_knowledge = background_knowledge_wrapper.get_stripped_background_knowledge()  # type: Optional[SimpleProgram]
        # ------------------------------------------------

        # EXAMPLES
        example_builder = KeysExampleBuilder(self.prediction_goal, debug_printing_options.example_parsing)
        self.training_examples_collection = example_builder.parse(internal_ex_format, self.file_name_data.fname_examples,
                                                                  full_background_knowledge_sp)  # type: ExampleCollection

        # ------------------------------------------------
        # --- LABELS -------------------------------------
        index_of_label_var =  self.prediction_goal_handler.get_predicate_goal_index_of_label_var()  # type: int
        label_collector = LabelCollectorMapper.get_label_collector(internal_ex_format, self.prediction_goal,
                                                                   index_of_label_var,
                                                                   engine=engine)

        keys_of_unlabeled_examples = label_collector.extract_labels(self.training_examples_collection)
        nb_of_unlabeled_examples = len(keys_of_unlabeled_examples)

        possible_labels = label_collector.get_labels()  # type: Set[Label]
        self.possible_labels = list(possible_labels)  # type: List[Label]
        # ------------------------------------------------

        # TODO: change this back if necessary
        if filter_out_unlabeled_examples and nb_of_unlabeled_examples > 0:
            total_nb_of_examples = len(self.training_examples_collection.example_wrappers_sp)
            self.training_examples_collection = self.training_examples_collection.filter_examples_not_in_key_set(
                keys_of_unlabeled_examples)
            print("DANGEROUS: FILTERED OUT UNLABELED EXAMPLES")

        # ------------------------------------------------


        # Saturate the examples.
        print("Start saturating examples")
        rule_grounder = model_factory.get_rule_grounder(full_background_knowledge_sp, self.language, self.prediction_goal_handler)
        rule_grounder.setup()
        rule_grounder.saturate_examples(self.training_examples_collection.get_example_wrappers_sp())
        print("Finish saturating examples")

        stripped_examples_simple_program = self.training_examples_collection.get_labeled_example_wrappers_sp()  # type: List[SimpleProgramExampleWrapper]

        self.examples_usable_for_testing = stripped_examples_simple_program  # type: List[SimpleProgramExampleWrapper]

        if internal_ex_format == InternalExampleFormat.CLAUSEDB:
            stripped_examples_clausedb = ClauseDBExampleWrapper.get_clause_db_examples(stripped_examples_simple_program,
                                                                                       background_knowledge=stripped_background_knowledge)
            self.examples_usable_for_testing = stripped_examples_clausedb  # type: List[ClauseDBExampleWrapper]
