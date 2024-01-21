"""
"""

__all__ = ["load_config", "Config", "ConfigurationInvalidError", "FIELDS", "Requirement"]



from ._fields import FIELDS, Requirement
from._config import Config, ConfigurationInvalidError

def load_config(filepath: str) -> "Config":
    """
    Loads a configuration from a file.
    """

    return Config.from_file(filepath)
