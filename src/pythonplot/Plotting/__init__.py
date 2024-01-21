import QuasarCode as qc
from matplotlib import pyplot as plt
from typing import Union, List, Tuple, Dict, Callable
from enum import Enum
import uuid
import numpy as np
import os

from ..Dependencies import LibraryDependency, CallableDependency, DataDependency_Base, DataDependency, HDF5_DataDependency

from ._planning import ExcecutionPlan
from ._plot_definition import PlotDefinition

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Configuration import Config



class Autoploter(object):
    """
    """

    def __init__(self: "Autoploter",
                 config: "Config",
                 execution_plan: ExcecutionPlan,
                 imports: Dict[str, LibraryDependency] = None,
                 functions: Dict[str, CallableDependency] = None,
                 data: Dict[str, DataDependency_Base] = None,
                 plots: Dict[str, PlotDefinition] = None):
        self.__config = config

        self.__imports = imports if imports is not None else {}
        self.__functions = functions if functions is not None else {}
        self.__data = data if data is not None else {}
        self.__plots = plots if plots is not None else {}

        self.__plan = execution_plan
        
        #TODO: ensure logs path exists (init logging object)

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

    def load_data(self: "Autoploter", names: Union[str, List[str]], namespaces: Union[str, List[str], None] = None, namespace_ids: Union[str, List[str], None] = None):
        if isinstance(names, str):
            names = [names]
        if isinstance(namespaces, str):
            namespaces = [namespaces]
        if isinstance(namespace_ids, str):
            namespace_ids = [namespace_ids]

        if namespaces is not None and namespace_ids is not None:
            raise ValueError("You cannot specify both namespaces and namespace_ids.")
        
        if namespace_ids is None and namespaces is not None:
            namespace_ids = [self.__config.get_namspace_id_by_name(namespace) for namespace in namespaces]
        
        fullnames = None
        if namespace_ids is not None:
            fullnames = []
            for id, name in zip(namespace_ids, names):
                fullnames.append(f"{id}:{name}")
        else:
            fullnames = names
            
        for fullname in fullnames:
            dependency = self.__data[fullname]
            if not (dependency.IsLoaded and dependency.IsValid):
                dependency.load()


    def run(self: "Autoploter"):
        """
        """

        try:
            self.verify()
        except Exception as e:
            raise RuntimeError("Unable to run as the definition was not valid.") from e

        processed_data_products = {}
        #self.__plan.execute_all()
        plans = self.__plan.as_chunks()
        for plan_chunk in plans:
            self.load_data(plan_chunk.data_required)
            processed_data_products.update(plan_chunk.execute_all())
            plan_chunk.mark_data_used()

        #TODO: make plots here
