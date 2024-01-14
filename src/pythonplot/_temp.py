
import QuasarCode as qc
from matplotlib import pyplot as plt
from typing import Union, List, Tuple, Dict, Callable
from enum import Enum
import uuid
import numpy as np

from ..pythonplot import __version__
from .Dependencies import LibraryDependency, CallableDependency, DataDependency_Base, DataDependency, HDF5_DataDependency

class PlotDefinition(object):
    pass

class Requirement(Enum):
    REQUIRED = 0
    OPTIONAL = 1

FIELDS = {
          "file_version": Requirement.REQUIRED,
         "pplot_version": Requirement.REQUIRED,
               "imports": Requirement.REQUIRED,
             "disk_data": Requirement.REQUIRED,
        "processed_data": Requirement.REQUIRED,
             "functions": Requirement.REQUIRED,
                 "plots": Requirement.REQUIRED,

    "required_externals": Requirement.OPTIONAL,
      "target_externals": Requirement.OPTIONAL,
}

def load_config(filepath: str) -> "Config":
    return Config.from_file(filepath)

class ConfigurationInvalidError(RuntimeError):
    """
    Configuration was not formatted correctly.
    """

    def __init__(self, message: str):
        super().__init__(message = f"Configuration was improperly formatted. {message}")

class Config(qc.IO.Configurations.JsonConfig):
    """
    """

    def __init__(self: "Config", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__filepath: Union[str, None] = None
        self.__namespace_ids: Dict[str, str] = {}
        self.__namespace_names: Dict[str, str] = {}
        self.__namespace_file_targets: Dict[str, str] = {}
        self.__namespace_configs: Dict[str, "Config"] = {}

        self.__valid: bool = self.validate()
        self.load_namespaces()

    @property
    def filepath(self: "Config") -> str:
        return self.__filepath
    
    @property
    def valid(self: "Config") -> str:
        return self.__valid
    
    @classmethod
    def from_file(cls, filepath: str) -> "Config":
        new_config = super().from_file(filepath)
        new_config.__filepath = filepath
        return new_config

    def validate(self: "Config") -> bool:
        """
        """

        if self.pplot_version != __version__:
            pass#TODO: display & log a warning about compatibility

        missing_fields = [field for field in FIELDS if FIELDS[field] == Requirement.REQUIRED]
        
        for option in self.keys:
            if option in FIELDS:
                if FIELDS[option] == Requirement.REQUIRED:
                    try:
                        missing_fields.remove(option)
                    except ValueError:
                        raise ConfigurationInvalidError(f"Option {option} was duplicated.")

    @staticmethod
    def create_new(filepath: str = "new_plot_automation.autoplot") -> None:
        uuid.uuid4()
        pass#TODO:

    def load_namespaces(self: "Config") -> None:
        if not self.valid:
            #TODO: log invalid target file
            return

        self.__namespace_ids[self.namespace] = self.uuid
        self.__namespace_names[self.uuid] = self.namespace
        self.__namespace_file_targets[self.uuid] = self.filepath
        self.__namespace_configs[self.uuid] = self

        files_to_load: List[str] = self.required_externals + self.target_externals

        while len(files_to_load) > 0:
            test_filepath = files_to_load.pop(0)

            try:
                loaded_config = Config.from_file(test_filepath)
            except:
                #TODO: log file missing
                continue

            if loaded_config.valid:
                test_uuid = loaded_config.uuid
                test_namespace = loaded_config.namespace

                if test_uuid in self.__namespace_names:
                    if test_filepath != self.__namespace_file_targets[test_uuid]:
                        pass#TODO: handle UUID conflict

                elif test_namespace in self.__namespace_ids:
                    pass#TODO: handle namespace conflicts

                else:
                    self.__namespace_ids[loaded_config.namespace] = loaded_config.uuid
                    self.__namespace_names[loaded_config.uuid] = loaded_config.namespace
                    self.__namespace_file_targets[loaded_config.uuid] = loaded_config.filepath
                    self.__namespace_configs[loaded_config.uuid] = test_filepath

            else:
                pass#TODO: log unable to read file

    def create_namespace_report(self: "Config", ids = False, filepaths = False) -> str:
        report_template = """Loaded Namespaces:
{}
{}
"""

        report_headdings = ["NAMESPACE"]
        if ids: report_headdings.append("UUID")
        if filepaths: report_headdings.append("FILE")

        report_content = []
        for name in sorted(self.__namespace_names.keys()):
            uuid = self.__namespace_ids[name]
            row = [name]
            if ids:
                row.append(uuid)
            if filepaths:
                row.append(self.__namespace_file_targets[uuid])
            report_content.append(row)

        lengths = np.array([len(headding) for headding in report_headdings[:-1]], dtype = int)
        if len(lengths) > 0:
            for i in range(len(report_content)):
                for j in range(len(lengths)):
                    lengths[j] = max(len(report_content[i][j]), lengths[j])

            for i in range(len(report_content)):
                for j in range(len(lengths)):
                    report_content[i][j] += " " * (lengths[j] - len(report_content[i][j]))

        for i in range(len(report_content)):
            report_content[i] = "".join(report_content[i])
        
        return report_template.format([headding + (" " * (lengths[j] - len(headding))) for headding in report_headdings], "\n".join(report_content))
        


    def initialise(self: "Config") -> "Autoploter":

        for key in self.imports.keys:
            pass

        plotter = Autoploter()

        return plotter



class Autoploter(object):
    """
    """

    def __init__(self: "Autoploter",
                 config: "Config" = None,
                 imports: List[LibraryDependency] = [],
                 data: List[DataDependency_Base] = [],
                 functions: List[CallableDependency] = [],
                 plots: List[PlotDefinition] = []):
        pass#TODO:
