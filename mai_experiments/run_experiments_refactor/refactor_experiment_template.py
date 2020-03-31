import os
import statistics
import sys
import time
from typing import List

from mai_experiments.experiment_settings import FileNameData, DebugPrintingOptions
from mai_experiments.fold_control import FoldInfo
from mai_experiments.fold_control import FoldInfoController
from mai_experiments.fold_example_splitting import FoldExampleSplitter
from mai_experiments.run_experiments_refactor.example_preprocessing_refactor import Experiment
from refactor.model_factory import ModelFactory
from refactor.tilde_config import TildeConfig
from refactor.tilde_essentials.tree import DecisionTree, write_out_tree
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_essentials.tree_pruning import prune_leaf_nodes_with_same_label
from refactor.tilde_essentials.verification import verify
from mai_version.representation.example import ExampleWrapper
from mai_version.representation.example_collection import ExampleCollection


def run_experiment(tilde_config: TildeConfig, backend_choice: ModelFactory.BackendChoice,
                   file_name_data: FileNameData, fold_info_controller: FoldInfoController,
                   hide_printouts: bool = False,
                   filter_out_unlabeled_examples=False,
                   debug_printing_options=DebugPrintingOptions(),
                   random_forest_options: ModelFactory.RandomForestOptions=None):
    # -- create output directory
    if not os.path.exists(file_name_data.output_dir):
        os.makedirs(file_name_data.output_dir)

    print("start", file_name_data.test_name)
    save_stdout = sys.stdout
    if hide_printouts:
        sys.stdout = open(os.devnull, "w")

    experiment = Experiment(file_name_data)
    experiment.parse_settings()
    model_factory = ModelFactory(tilde_config, experiment.language, backend_choice)
    experiment.preprocess_examples_and_background_knowledge(model_factory, filter_out_unlabeled_examples, debug_printing_options)
    
    fold_example_splitter = FoldExampleSplitter(fold_info_controller)
    for fold_info, training_examples_collection, test_examples in fold_example_splitter.fold_split_generator(
            experiment):  # type: FoldInfo, ExampleCollection, List[ExampleWrapper]
        print("fold: ", fold_info.index)
        
        if random_forest_options is None:
            tree_builder = model_factory.get_default_decision_tree_builder()  # type: TreeBuilder
            model = DecisionTree()
        else:
            tree_builder = model_factory.get_default_random_forest_tree_builder(random_forest_options)
            model = model_factory.create_random_forest(random_forest_options)

        training_examples = tree_builder.splitter.test_evaluator.get_transformed_example_list(training_examples_collection.get_example_wrappers_sp())

        start_build_time = time.time()
        model.fit(examples=training_examples, tree_builder=tree_builder)

        if debug_printing_options.tree_building:
            print("unpruned:")
            print(model)
        model.prune(prune_leaf_nodes_with_same_label)
        end_build_time = time.time()

        # run_time_sec = end_time - start_time
        build_time_sec = end_build_time - start_build_time
        build_time_ms = 1000.0 * build_time_sec
        fold_info.dt_build_time_ms = build_time_ms
        if debug_printing_options.tree_building or debug_printing_options.tree_pruning:
            print("build time (ms):", build_time_ms)
            print("pruned")
            print(model)

        # write out tree
        tree_fname = os.path.join(file_name_data.output_dir,
                                  model_factory.backend_choice.name + "_" + fold_info_controller.fname_prefix_fold + '_fold' + str(
                                      fold_info.index) + ".tree")
        write_out_tree(tree_fname, model)

        start_test_example_transformation = time.time()
        test_examples_reformed = tree_builder.splitter.test_evaluator.get_transformed_example_list(test_examples)
        # for ex_wr_sp in test_examples:
        #     example_clause = build_clause(ex_wr_sp, training=False)
        #     example = Example(data=example_clause, label=ex_wr_sp.label)
        #     example.classification_term = ex_wr_sp.classification_term
        #     test_examples_reformed.append(example)
        end_test_example_transformation = time.time()

        statistics_handler = verify(model, test_examples_reformed)
        accuracy = statistics_handler.get_accuracy()
        if debug_printing_options.get_classifier:
            print("accuracy:", accuracy)

        # ===================
        end_time = time.time()
        # time in seconds: # time in seconds
        elapsed_time = end_time - start_build_time - (end_test_example_transformation - start_test_example_transformation)
        elapsed_time_ms = 1000.0 * elapsed_time
        fold_info.execution_time_ms = elapsed_time_ms

        accuracy, _ = statistics_handler.get_accuracy()
        fold_info.accuracy = accuracy

        statistics_fname = os.path.join(file_name_data.output_dir,
                                        model_factory.backend_choice.name + "_" + fold_info_controller.fname_prefix_fold + '_fold'
                                        + str(fold_info.index) + ".statistics")

        # statistics_fname = file_name_data.output_dir + .fname_prefix_fold + '_fold' + str(fold_index) + ".statistics"
        statistics_handler.write_out_statistics_to_file(statistics_fname)

        with open(statistics_fname, 'a') as f:
            f.write('\n\nnb of TRAINING ex: ' + str(len(training_examples)) + "\n")
            f.write('nb of TEST ex: ' + str(len(test_examples)) + "\n\n")
            if random_forest_options is not None:
                f.write('nb of trees: ' + str(model.n_trees))
                
            nb_nodes = model.get_nb_of_nodes()
            fold_info.n_nodes = nb_nodes
            f.write("total nb of nodes: " + str(nb_nodes) + "\n")
            nb_inner_nodes = model.get_nb_of_inner_nodes()
            fold_info.n_inner_nodes = nb_inner_nodes
            f.write("nb of internal nodes: " + str(nb_inner_nodes) + "\n\n")
            f.write("execution time of fold (ms): " + str(elapsed_time_ms) + "\n")

        # verify(decision_tree, )

        # ------------------------------------------

        # --- DESTRUCTION (necessary for Django) ---
        model.destruct()

        for ex in training_examples:
            ex.destruct()

    mean_accuracy_of_folds = statistics.mean(
        [fold_info.accuracy for (_index, fold_info) in fold_info_controller.fold_infos.items()])

    dt_build_times = [fold_info.dt_build_time_ms for (_index, fold_info) in fold_info_controller.fold_infos.items()]
    mean_decision_tree_build_time = statistics.mean(dt_build_times)

    fold_execution_times_ms = [
        fold_info.execution_time_ms for (_index, fold_info) in fold_info_controller.fold_infos.items()
    ]
    total_execution_time_ms_of_cross_validation = sum(fold_execution_times_ms)
    mean_execution_time_ms_of_folds = statistics.mean(fold_execution_times_ms)

    folds_total_nb_of_nodes = [
        fold_info.n_nodes for (_index, fold_info) in fold_info_controller.fold_infos.items()
    ]
    mean_total_nb_of_nodes = statistics.mean(folds_total_nb_of_nodes)

    fold_nb_of_inner_nodes = [
        fold_info.n_inner_nodes for (_index, fold_info) in fold_info_controller.fold_infos.items()
    ]
    mean_nb_of_inner_nodes = statistics.mean(fold_nb_of_inner_nodes)

    if debug_printing_options.debug_printing_classification:
        print("mean decision tree build time (ms):", mean_decision_tree_build_time)
        print("total time cross  (sum folds): " + str(total_execution_time_ms_of_cross_validation) + "\n")

    statistics_fname = os.path.join(file_name_data.output_dir,
                                    model_factory.backend_choice.name + "_" + fold_info_controller.fname_prefix_fold + ".statistics")
    # statistics_fname = fd.dir_output_files + fd.fname_prefix_fold + ".statistics"
    with open(statistics_fname, 'w') as f:
        f.write("mean accuracy: " + str(mean_accuracy_of_folds) + "\n")
        f.write("mean decision tree build time (ms):" + str(mean_decision_tree_build_time) + "\n")
        f.write("mean fold execution time (ms):" + str(mean_execution_time_ms_of_folds) + "\n")

        f.write("mean total nb of nodes:" + str(mean_total_nb_of_nodes) + "\n")
        f.write("mean nb of inner nodes:" + str(mean_nb_of_inner_nodes) + "\n")

        f.write("total time cross  (sum folds) (ms): " + str(total_execution_time_ms_of_cross_validation) + "\n")

    if hide_printouts:
        sys.stdout = save_stdout
    print("finished", file_name_data.test_name)
