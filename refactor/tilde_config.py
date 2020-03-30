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

    @staticmethod
    def none_if_emptystr(s):
        return s if s.strip() else None

    @staticmethod
    def from_dict(config_data):
        return TildeConfig(config_data)

    @staticmethod
    def from_file(config_file_name):
        if config_file_name == TildeConfig.DEFAULT_CONFIG_FILE_NAME:
            config_file_path = os.path.join(_package_directory, config_file_name)
        else:
            config_file_path = os.path.join(os.getcwd(), config_file_name)

        with open(config_file_path, "r") as config_file:
            print("Reading configuration from: ", config_file_path)
            config_data = json.load(config_file)
        return TildeConfig(config_data, config_file_path)

    """ Accepts a config.json """
    def __init__(self, config_data, config_file_path='__direct_json__'):
        self.config_data = config_data
        self.config_file_path = config_file_path

    def _get_setting(self, key):
        try:
            return self.none_if_emptystr(self.config_data[key])
        except KeyError as err:
            if key in self._default_settings:
                return self.none_if_emptystr(self._default_settings[key])
            else:
                print(key, ' is not defined in ', self.config_file_path)
                raise err

    @property
    def subtle_path(self):
        path_str = self._get_setting(_subtle_path_key)
        from os import path, getcwd
        if path.isabs(path_str):
            return path_str
        else:
            return path.join(getcwd(), path_str)

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
