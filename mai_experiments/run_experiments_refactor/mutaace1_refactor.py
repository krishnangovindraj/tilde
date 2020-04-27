from mai_experiments.experiment_settings import DebugPrintingOptions, FileNameData
from mai_experiments.fold_control import FoldInfoController

from mai_experiments.run_experiments_refactor.refactor_experiment_template import run_experiment
from refactor.model_factory import ModelFactory
from refactor.query_testing_back_end import BackendChoice
from refactor.tilde_config import TildeConfig

# RANDOM_FOREST_OPTIONS = ModelFactory.RandomForestOptions(5, 0, 10)
RANDOM_FOREST_OPTIONS = None

# CHANGE THESE TWO FOR EACH TEST
test_name = 'mutaace1'
logic_name = 'muta-d'

import sys

# sys.path.append("/home/joschout/Repos/Django-subsumption")
from tilde_config import _default_config_file_name, _package_directory, \
    _subtle_path_key, _split_criterion_key, _leaf_strategy_key, \
    _s_file_key, _kb_file_key, _bg_file_key

tilde_config_data = {
    _subtle_path_key: "test_datasets/theta-subsumption-engines/subtle/subtle-2.2.pl",
    _split_criterion_key: "entropy",
    _leaf_strategy_key: "majority_class",
}


# --- command-line printing settings ---
debug_printing_options = DebugPrintingOptions()

filter_out_unlabeled_examples = False
hide_printouts = False

# --- directories ---
droot = '/home/krishnan/wprogs/workcode/tilde/data-mai-experiments'
dlogic_relative = 't-0-0-0'
dfold_relative = 'folds'
dout_relative = 'output'


file_name_data = FileNameData(root_dir=droot,
                              logic_relative_dir=dlogic_relative,
                              fold_relative_dir=dfold_relative,
                              output_relative_dir=dout_relative,
                              test_name=test_name,
                              logic_name=logic_name)

# --- fold settings ---
fname_prefix_fold = 'test'
fold_start_index = 0
nb_folds = 10
fold_suffix = '.txt'


fold_info_controller = FoldInfoController(
    fold_file_directory=file_name_data.fold_dir,
    fold_fname_prefix=fname_prefix_fold,
    fold_start_index=fold_start_index,
    nb_folds=nb_folds,
    fold_suffix=fold_suffix)

tilde_config = TildeConfig.from_dict(tilde_config_data)

run_experiment(tilde_config, BackendChoice.DJANGO,
               file_name_data, fold_info_controller,
               hide_printouts, filter_out_unlabeled_examples, debug_printing_options,
               random_forest_options=RANDOM_FOREST_OPTIONS)
