from tilde.IO.parsing_settings.setting_parser import KeysSettingsParser
from tilde.representation.example import InternalExampleFormat
from tilde.run.run_keys import run_keys
from tilde.trees.TreeBuilder import TreeBuilderType

file_name_labeled_examples = 'D:\\KUL\\KUL MAI\\Masterproef\\data\\ACE-examples-data\\ace\\mach\\keys\\mach.kb'
file_name_settings = 'D:\\KUL\\KUL MAI\\Masterproef\\data\\ACE-examples-data\\ace\\mach\\keys\\mach.s'
file_name_background = 'D:\\KUL\\KUL MAI\\Masterproef\\data\\ACE-examples-data\\ace\\mach\\keys\mach.bg'

use_clausedb = True
use_mle = False

debug_printing_example_parsing = False
debug_printing_tree_building = False
debug_printing_tree_pruning = False
debug_printing_program_conversion = False
debug_printing_get_classifier = False
debug_printing_classification = True

parsed_settings = KeysSettingsParser().parse(file_name_settings)

treebuilder_type = TreeBuilderType.DETERMINISTIC

# background_knowledge = parse_background_knowledge(file_name_background)

if use_clausedb:
    internal_ex_format = InternalExampleFormat.CLAUSEDB
else:
    internal_ex_format = InternalExampleFormat.SIMPLEPROGRAM

run_keys(file_name_labeled_examples, parsed_settings, internal_ex_format, treebuilder_type,
         fname_background_knowledge=file_name_background,
         debug_printing_example_parsing=debug_printing_example_parsing,
         debug_printing_tree_building=debug_printing_tree_building,
         debug_printing_tree_pruning=debug_printing_tree_pruning,
         debug_printing_program_conversion=debug_printing_program_conversion,
         debug_printing_get_classifier=debug_printing_get_classifier,
         debug_printing_classification=debug_printing_classification
         )