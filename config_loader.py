import json
import logging

class ConfigLoader:
    @staticmethod
    def load_config(file_path, target_class=None):
        """Loads the configuration from the specified file."""
        try:
            with open(file_path, 'r') as file:
                if target_class:
                    return target_class(json.load(file))
        except FileNotFoundError:
            logging.error(f"Configuration file {file_path} not found.")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error during configuration file parsing {file_path}: {e}")
            return None

# TODO: Add missing fields
class TBConnectionConfig:
    def __init__(self, dict_config: dict):
        self.url = dict_config.get('url')


# TODO: Realize configuration object for teamcity configuration
class TeamCityConfig:
    pass