import json
import os

from tilde_config import _default_config_file_name, _package_directory, \
    _subtle_path_key, _split_criterion_key, _leaf_strategy_key, \
    _s_file_key, _kb_file_key, _bg_file_key

class TildeConfig:

    DEFAULT_CONFIG_FILE_NAME = _default_config_file_name
    # Removed all the ones which should cause failure if they don't exist.
    _default_settings = {_split_criterion_key: 'entropy', _leaf_strategy_key: "majority_class",
                        _kb_file_key: None, _bg_file_key: None}

    _static_instance = None

    @staticmethod
    def none_if_emptystr(s):
        return s if s.strip() else None

    @staticmethod
    def get_instance():
        if TildeConfig._static_instance is not None:
            return TildeConfig._static_instance
        else:
            raise ReferenceError("The _static_instance has not been instantiated yet")

    @staticmethod
    def create_instance(config_file):
        if TildeConfig._static_instance is None:
            TildeConfig._static_instance = TildeConfig(config_file)
            return TildeConfig._static_instance
        else:
            raise ReferenceError("The _static_instance has previously been created. Cannot recreate.")

    """ Accepts a config.json """
    def __init__(self, config_file):
        if config_file == TildeConfig.DEFAULT_CONFIG_FILE_NAME:
            self.config_file_name = os.path.join(_package_directory, config_file)
        else:
            self.config_file_name = os.path.join(os.getcwd(), config_file)

        with open(self.config_file_name, "r") as config_file:
            print("Reading configuration from: ", self.config_file_name)
            self.config_file_data = json.load(config_file)

    def _get_setting(self, key):
        try:
            return self.none_if_emptystr(self.config_file_data[key])
        except KeyError as err:
            if key in self._default_settings:
                return self.none_if_emptystr(self._default_settings[key])
            else:
                print(key, ' is not defined in ', self.config_file_name)
                raise err

    @property
    def subtle_path(self):
        return self._get_setting(_subtle_path_key)

    @property
    def split_criterion(self):
        return self._get_setting(_split_criterion_key)

    @property
    def leaf_strategy(self):
        return self._get_setting(_leaf_strategy_key)

    @property
    def kb_file(self):
        return self._get_setting(_kb_file_key)

    @property
    def s_file(self):
        return self._get_setting(_s_file_key)

    @property
    def bg_file(self):
        return self._get_setting(_bg_file_key)
