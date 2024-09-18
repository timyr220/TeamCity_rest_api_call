import json
import logging

class ConfigLoader:
    @staticmethod
    def load_config(file_path):
        """Loads the configuration from the specified file."""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error(f"Configuration file {file_path} not found.")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error during configuration file parsing {file_path}: {e}")
            return None