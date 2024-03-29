import QuasarCode as qc
from typing import Union, List, Tuple, Dict, Callable
import uuid
import numpy as np
import os

from .. import __version__
from ..Dependencies import LibraryDependency, CallableDependency, DataDependency_Base, DataDependency, HDF5_DataDependency
from ..Plotting import PlotDefinition, ExcecutionPlan, Autoploter

from ._fields import FIELDS, Requirement



class ConfigurationInvalidError(SyntaxError):
    """
    Configuration was not formatted correctly.
    """

    def __init__(self, message: str):
        super().__init__(f"Configuration was improperly formatted. {message}")

#class Config(qc.IO.Configurations.JsonConfig):
class Config(object):
    """
    Configuration type containing the settings nessessary to generate plots.
    """

    #def __init__(self: "Config", *args, **kwargs):
    #    super().__init__(*args, **kwargs)

    def __init__(self: "Config", target: qc.IO.Configurations.JsonConfig, filepath: str = ".", is_root: bool = True):
        self.__raw_config = target
        self.__is_root = is_root

        self.__filepath: str = filepath
        self.__namespace_ids: Dict[str, str] = {}
        self.__namespace_names: Dict[str, str] = {}
        self.__namespace_file_targets: Dict[str, str] = {}
        self.__namespace_configs: Dict[str, "Config"] = {}
        self.__namespace_is_dependency_only: Dict[str, bool] = {}

        self.__declared_optionals = { key: False for key in FIELDS if key == Requirement.OPTIONAL }
        self.__valid: bool = self.validate()
        if is_root:
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

    @property
    def raw_config(self: "Config") -> qc.IO.Configurations.JsonConfig:
        """
        """
        return self.__raw_config

    #@classmethod
    #def from_file(cls, filepath: str) -> "Config":
    #    new_config = super().from_file(filepath)
    #    new_config.__filepath = filepath
    #    return new_config

    @classmethod
    def from_file(cls, filepath: str, is_root: bool = True) -> "Config":
        filepath = filepath if os.path.isabs(filepath) else os.path.abspath(filepath)
        new_config = Config(qc.IO.Configurations.JsonConfig.from_file(filepath), filepath, is_root)
        return new_config

    RESERVED_LOADER_NAMES: Tuple[str] = ("HDF5", )

    def validate(self: "Config") -> bool:
        """
        Test the contence of the configuration to ensure it is valid.
        """

        try:

            if self.__raw_config.pplot_version.strip("v") != __version__.strip("v"):
                qc.Console.print_warning(f"Configuration file with namespace {self.__raw_config.namespace} specifies pythonplot version {self.__raw_config.pplot_version} but current version is {__version__}. This file may not be compatible.")

            missing_fields = [field for field in FIELDS if FIELDS[field] == Requirement.REQUIRED]

            for option in self.__raw_config.keys:
                if option in FIELDS:
                    if FIELDS[option] == Requirement.REQUIRED:
                        try:
                            missing_fields.remove(option)
                        except ValueError:
                            raise ConfigurationInvalidError(f"Option {option} was duplicated.")
                    elif FIELDS[option] == Requirement.OPTIONAL:
                        self.__declared_optionals[option] = True
                    else:
                        raise ConfigurationInvalidError(f"Option {option} is not a valid option. Check the spelling and list of valid options for this version ({__version__}).")
                        
            if len(missing_fields) > 0:
                raise ConfigurationInvalidError("Missing required fields:\n{}".format("\n".join(missing_fields)))
                        
    #        for key in self.__raw_config.loaders:
    #            if key in self.RESERVED_LOADER_NAMES:
    #                raise ConfigurationInvalidError(f"A defined loading function attempted to use reserved name \"{key}\"\nThe names {self.RESERVED_LOADER_NAMES} are reserved.")
                
            disk_data_names = self.__raw_config.disk_data.keys
            for key in self.__raw_config.processed_data.keys:
                if key in disk_data_names:
                    raise ConfigurationInvalidError(f"Processed data key \"{key}\" matches a loaded data key in the smae file. All data keys must be unique within the same file.")
                
            return True
        
        except Exception as e:
            #TODO: log vaild validation and reason.
            return False

    @staticmethod
    def create_new(filepath: str = "new_plot_automation.autoplot", namespace: Union[str, None] = None) -> str:
        uuid.uuid4()
        pass#TODO: handle duplicate file (add numbering) - important for multiple new files!
        #return filepath
    
    def _evaluate_filepath(self: "Config", filepath: str) -> str:
        if os.path.isabs(filepath):
            return filepath
        else:
            return os.path.abspath(os.path.join(os.path.dirname(self.__filepath), filepath))

    def load_namespaces(self: "Config") -> None:
        if not self.valid:
            #TODO: log invalid target file
            return

        self.__namespace_ids[self.__raw_config.namespace] = self.__raw_config.uuid
        self.__namespace_names[self.__raw_config.uuid] = self.__raw_config.namespace
        self.__namespace_file_targets[self.__raw_config.uuid] = self.filepath
        self.__namespace_configs[self.__raw_config.uuid] = self

        files_to_load: List[str] = [self._evaluate_filepath(v) for v in self.__raw_config.required_externals] + [self._evaluate_filepath(v) for v in self.__raw_config.target_externals]

        while len(files_to_load) > 0:
            test_filepath = files_to_load.pop(0)

            try:
                loaded_config = Config.from_file(test_filepath, is_root = False)
            except:
                qc.Console.print_error(f"Unable to find file at {test_filepath}")
                #TODO: log file missing
                continue

            if loaded_config.valid:
                test_uuid = loaded_config.raw_config.uuid
                test_namespace = loaded_config.raw_config.namespace

                if test_uuid in self.__namespace_names:
                    if test_filepath != self.__namespace_file_targets[test_uuid]:
                        qc.Console.print_error(f"UUID CONFLICT: {test_namespace} ({test_uuid})")
                        pass#TODO: handle UUID conflict
                    else:
                        qc.Console.print_debug(f"Skipping already loaded config: {test_namespace} ({test_uuid})")

                elif test_namespace in self.__namespace_ids:
                    qc.Console.print_error(f"NAMESPACE CONFLICT: {test_namespace} ({test_uuid} and {self.__namespace_ids[test_namespace]})")
                    pass#TODO: handle namespace conflicts

                else:
                    self.__namespace_ids[loaded_config.raw_config.namespace] = loaded_config.raw_config.uuid
                    self.__namespace_names[loaded_config.raw_config.uuid] = loaded_config.raw_config.namespace
                    self.__namespace_file_targets[loaded_config.raw_config.uuid] = loaded_config.filepath
                    self.__namespace_configs[loaded_config.raw_config.uuid] = test_filepath

                    #TODO: fix inclusion of "target_externals" for files selected as "required_externals" (how to deal with circular inclusion??? re-check! use flag for full inclusion to prevent loop!)
                    files_to_load.extend([loaded_config._evaluate_filepath(v) for v in loaded_config.raw_config.required_externals] + [loaded_config._evaluate_filepath(v) for v in loaded_config.raw_config.target_externals])

            else:
                qc.Console.print_warning(f"Unable to read config file at {test_filepath}")
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
        """
        Generate a new Autoploter object from this config.
        """

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
                    if f"{cfg_uuid}:{data_definition_key}" not in data_dependancies:
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
                        data_dependancies[f"{cfg_uuid}:{data_definition_key}"] = new_dependency

                for plot_definition_key in cfg.disk_data.plots:
                    if f"{cfg_uuid}:{plot_definition_key}" not in plot_definitions:
                        plot_definitions[f"{cfg_uuid}:{plot_definition_key}"] = PlotDefinition()#TODO:

        for v in import_dependancies.values():
            v.load()
        for v in function_dependancies.values():
            v.load()

        plan = ExcecutionPlan(plot_definitions)

        plotter = Autoploter(self, plan, import_dependancies, function_dependancies, data_dependancies, plot_definitions)

        return plotter
    
    @property
    def namespace_ids(self: "Config") -> List[str]:
        return list(self.__namespace_names.keys())
    
    @property
    def namespaces(self: "Config") -> List[str]:
        return list(self.__namespace_ids.keys())
    
    def get_namspace_id_by_name(self: "Config", name: str) -> str:
        return self.__namespace_ids[name]
    
    def get_namspace_name_by_id(self: "Config", id: str) -> str:
        return self.__namespace_names[id]