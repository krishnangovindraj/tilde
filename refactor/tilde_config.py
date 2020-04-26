import json
import os
from enum import Enum

class TildeConfig:
    import refactor
    _package_directory = os.path.dirname(os.path.dirname(refactor.__file__))

    _default_config_file_path = os.path.join(_package_directory, 'config.json')

    class SettingsKeys(Enum):
        _split_criterion_key = 'SPLIT_CRITERION'
        _leaf_strategy_key = 'LEAF_STRATEGY'

        _s_file_key = 'S_FILE'
        _kb_file_key = 'KB_FILE'
        _bg_file_key = 'BG_FILE'

        _backend_choice = 'BACKEND'
        _subtle_path_key = 'SUBTLE_PATH'

    DEFAULT_CONFIG_FILE_PATH = _default_config_file_path
    # Removed all the ones which should cause failure if they don't exist.
    _default_settings = {SettingsKeys._split_criterion_key: 'entropy', SettingsKeys._leaf_strategy_key: "majority_class",
                        SettingsKeys._kb_file_key: None, SettingsKeys._bg_file_key: None, SettingsKeys._backend_choice: 'PROBLOG' }



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

    def _get_setting(self, key: SettingsKeys):
        try:
            return self.none_if_emptystr(self.config_data[key.value])
        except KeyError as err:
            if key in self._default_settings:
                return self.none_if_emptystr(self._default_settings[key])
            else:
                print(key, ' is not defined in ', self.config_file_path)
                raise err

    def override_setting(self, setting_key: SettingsKeys, new_value_str: str):
        if setting_key not in self.SettingsKeys:
            raise KeyError("The setting to override was not recognized :" + str(setting_key))
        self.config_data[setting_key.value] = new_value_str

    # The properties
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

    @property
    def subtle_path(self):
        path_str = self._get_setting(self.SettingsKeys._subtle_path_key)
        from os import path, getcwd
        if path.isabs(path_str):
            return path_str
        else:
            return path.join(getcwd(), path_str)

    @property
    def backend_choice(self):
        from refactor.model_factory import BackendChoice
        backend_choice_str = self._get_setting(self.SettingsKeys._backend_choice)
        if backend_choice_str not in BackendChoice.__members__:
            raise ValueError("Unrecognized backend " + backend_choice_str)
        else:
            return BackendChoice[backend_choice_str]
