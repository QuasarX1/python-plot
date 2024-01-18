import QuasarCode as qc
from matplotlib import pyplot as plt
from typing import Union, List, Tuple, Dict, Callable
from enum import Enum
import uuid
import numpy as np
import os

from . import __version__
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
    """
    Loads a configuration from a file.
    """

    return Config.from_file(filepath)

class ConfigurationInvalidError(RuntimeError):
    """
    Configuration was not formatted correctly.
    """

    def __init__(self, message: str):
        super().__init__(f"Configuration was improperly formatted. {message}")

class Config(qc.IO.Configurations.JsonConfig):
    """
    Configuration type containing the settings nessessary to generate plots.
    """

    def __init__(self: "Config", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__filepath: Union[str, None] = None
        self.__namespace_ids: Dict[str, str] = {}
        self.__namespace_names: Dict[str, str] = {}
        self.__namespace_file_targets: Dict[str, str] = {}
        self.__namespace_configs: Dict[str, "Config"] = {}
        self.__namespace_is_dependency_only: Dict[str, bool] = {}

        self.__valid: bool = self.validate()
        self.load_namespaces()

    @property
    def filepath(self: "Config") -> str:
        """
        Location on disk from which the target configuration was read.
        """
        return self.__filepath

    @property
    def valid(self: "Config") -> str:
        """
        Is the configuration valid?
        This DOES NOT gaurentee that the individual elements are correct, just that they can be read in by this object.
        """
        return self.__valid

    @classmethod
    def from_file(cls, filepath: str) -> "Config":
        new_config = super().from_file(filepath)
        new_config.__filepath = filepath
        return new_config

    RESERVED_LOADER_NAMES: Tuple[str] = ("HDF5", )

    def validate(self: "Config") -> bool:
        """
        Test the contence of the configuration to ensure it is valid.
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
                    
        for key in self.loaders:
            if key in self.RESERVED_LOADER_NAMES:
                raise ConfigurationInvalidError(f"A defined loading function attempted to use reserved name \"{key}\"\nThe names {self.RESERVED_LOADER_NAMES} are reserved.")

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

        import_dependancies: Dict[str, LibraryDependency] = {}
        function_dependancies: Dict[str, CallableDependency] = {}
        data_dependancies: Dict[str, DataDependency_Base] = {}
        plot_definitions: Dict[str, PlotDefinition] = {}

        for cfg_uuid, cfg in self.__namespace_configs.items():

            for manual_import in cfg.imports.keys:
                if manual_import not in import_dependancies:
                    import_dependancies[manual_import] = LibraryDependency(manual_import,
                                                                           relitive_import_path = cfg.imports[manual_import].importpath if "importpath" in cfg.imports[manual_import].keys else None,
                                                                           filepath = cfg.imports[manual_import].filepath)

        for cfg_uuid, cfg in self.__namespace_configs.items():

            for func_def in cfg.functions.keys:
                if f"{cfg_uuid}:{func_def}" not in function_dependancies:
                    namespace, path = cfg.functions[func_def].split(".", maxsplit = 1)
                    if namespace == "":
                        namespace = None
                        path = f".{path}"
                    elif namespace not in import_dependancies:
                        import_dependancies[namespace] = LibraryDependency(namespace)
                    function_dependancies[f"{cfg_uuid}:{func_def}"] = CallableDependency(func_def, path, namespace)

        for cfg_uuid, cfg in self.__namespace_configs.items():

            if not self.__namespace_is_dependency_only[cfg_uuid]:
                for data_definition_key in cfg.disk_data.keys:
                    if f"{cfg_uuid}:{data_definition_key}" not in import_dependancies:
                        filepath = cfg.disk_data[data_definition_key].filepath
                        loader = cfg.disk_data[data_definition_key].loader
                        new_dependency = None
                        if loader not in self.RESERVED_LOADER_NAMES:
                            if ":" not in loader:
                                loader = f"{cfg_uuid}:{loader}"
                            else:
                                namespace, func = loader.split(':', maxsplit = 1)
                                loader = f"{self.__namespace_ids[namespace]}:{func}"
                            if loader not in function_dependancies:
                                raise KeyError(f"Data \"{data_definition_key}\" references a loader function \"{loader.split(':', maxsplit = 1)[-1]}\" that has not been defined.")
                            new_dependency = DataDependency(data_definition_key, filepath, function_dependancies[loader])
                        elif loader == "HDF5":
                            new_dependency = HDF5_DataDependency(data_definition_key, filepath)
                        import_dependancies[f"{cfg_uuid}:{data_definition_key}"] = new_dependency

                for plot_definition_key in cfg.disk_data.plots:
                    if f"{cfg_uuid}:{plot_definition_key}" not in plot_definitions:
                        plot_definitions[f"{cfg_uuid}:{plot_definition_key}"] = PlotDefinition()#TODO:

        for v in import_dependancies.values():
            v.load()
        for v in function_dependancies.values():
            v.load()

        plotter = Autoploter(self, import_dependancies, function_dependancies, data_dependancies, plot_definitions)

        return plotter



class Autoploter(object):
    """
    """

    def __init__(self: "Autoploter",
                 config: "Config" = None,
                 imports: Dict[str, LibraryDependency] = {},
                 functions: Dict[str, CallableDependency] = {},
                 data: Dict[str, DataDependency_Base] = {},
                 plots: Dict[str, PlotDefinition] = {}):
        self.__imports = imports
        self.__functions = functions
        self.__data = data
        self.__plots = plots
        #TODO:

    def verify(self: "Autoploter") -> None:
        """
        Ensures all non-data definitions are able to be loaded.
        Raises exceptions if anything isn't valid.
        """

        for key in self.__imports:
            assert self.__imports[key].IsValid, f"Module {key} wasn't valid."
        for key in self.__functions:
            assert self.__functions[key].IsValid, f"Callable {key} wasn't valid."
        for key in self.__plots:
            assert self.__plots[key].IsValid, f"Plot {key} wasn't valid."

    def run(self: "Autoploter"):
        """
        """

        try:
           self.verify()
        except Exception as e:
            raise RuntimeError("Unable to run as the definition was not valid.") from e
        
        #TODO: run
