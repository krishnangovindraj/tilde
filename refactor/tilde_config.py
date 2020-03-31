import json
import os

class TildeConfig:
    import refactor
    _package_directory = os.path.dirname(os.path.dirname(refactor.__file__))

    _default_config_file_path = os.path.join(_package_directory, 'config.json')

    class SettingsKeys:
        _subtle_path_key = 'SUBTLE_PATH'
        _split_criterion_key = 'SPLIT_CRITERION'
        _leaf_strategy_key = 'LEAF_STRATEGY'
        _kb_file_key = 'KB_FILE'
        _s_file_key = 'S_FILE'
        _bg_file_key = 'BG_FILE'

    DEFAULT_CONFIG_FILE_PATH = _default_config_file_path
    # Removed all the ones which should cause failure if they don't exist.
    _default_settings = {SettingsKeys._split_criterion_key: 'entropy', SettingsKeys._leaf_strategy_key: "majority_class",
                        SettingsKeys._kb_file_key: None, SettingsKeys._bg_file_key: None}

    @staticmethod
    def none_if_emptystr(s):
        return s if s.strip() else None

    @staticmethod
    def from_dict(config_data):
        return TildeConfig(config_data)

    @staticmethod
    def from_file(config_file_name):
        if os.path.isabs(config_file_name):
            config_file_path = config_file_name
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
        path_str = self._get_setting(self.SettingsKeys._subtle_path_key)
        from os import path, getcwd
        if path.isabs(path_str):
            return path_str
        else:
            return path.join(getcwd(), path_str)

    @property
    def split_criterion(self):
        return self._get_setting(self.SettingsKeys._split_criterion_key)

    @property
    def leaf_strategy(self):
        return self._get_setting(self.SettingsKeys._leaf_strategy_key)

    @property
    def kb_file(self):
        return self._get_setting(self.SettingsKeys._kb_file_key)

    @property
    def s_file(self):
        return self._get_setting(self.SettingsKeys._s_file_key)

    @property
    def bg_file(self):
        return self._get_setting(self.SettingsKeys._bg_file_key)
