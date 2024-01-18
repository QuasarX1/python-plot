"""
python-plot/Dependencies

Objects for loading dependancies from disk.
"""

__all__ = ["DependencyNotLoadedError", "DependencyCorruptError", "Dependency", "LibraryDependency", "CallableDependency", "DataDependency_Base", "DataDependency", "HDF5_DataDependency", "load_from_pickle", "load_from_hdf5"]



from abc import ABC, abstractmethod
from typing import Union, List, Tuple, Dict, Callable
import importlib
import collections
import pickle
import unyt
import numpy as np
import h5py

import builtins



class DependencyNotLoadedError(RuntimeError):
    """
    Dependency has not been loaded (successfully).
    """

    def __init__(self, dependency: "Dependency"):
        super().__init__(f"Dependancy {dependency.Name} either not yet loaded or could not be successfully loaded.\n\nError Details:\n\n{dependency._error_details}")



class DependencyCorruptError(RuntimeError):
    """
    Dependency was loaded successfully, but is deleted, corrupt or has been mutated in some braking way.
    """

    def __init__(self, dependency: "Dependency"):
        super().__init__(f"Dependancy {dependency.Name} is deleted, corrupt or has been mutated in some braking way.\n\nError Details:\n\n{dependency._error_details}")



class Dependency(ABC):
    """
    Defines behaviours for all dependency types.
    """

    def __init__(self: "Dependency", name: str):
        self.__name: str = name
        self.__value = None
        self.__loaded: bool = False
        self.__valid: bool = False
        self.__error_details: Union[str, None] = None

    @property
    def _error_details(self: "Dependency") -> Union[str, None]:
        """
        Provides access to the details of the latest error.
        """

        return self.__error_details

    @property
    def IsLoaded(self: "Dependency") -> bool:
        """
        Has the dependancy been successfully loaded?
        """

        return self.__loaded

    @property
    def IsValid(self: "Dependency") -> bool:
        """
        Has the dependancy been successfully loaded?
        """

        return self.__valid

    @property
    def Name(self: "Dependency") -> str:
        """
        Human redable name for the dependency. Used for logs.
        """

        return self.__name

    @property
    def Value(self: "Dependency") -> object:
        """
        Get the value of the dependency.
        This could be any thing but is likley a package namespace, a function/callable or a peice of data.

        Errors:
            DependencyNotLoadedError -> Dependency has not been loaded (successfully).

            DependencyCorruptError -> Dependency was loaded successfully, but is deleted, corrupt or has been mutated in some braking way.
        """

        if not self.__loaded:
            raise DependencyNotLoadedError(self)
        
        elif not self.__valid:
            raise DependencyCorruptError(self)
        
        else:
            return self.__value
    
    def load(self: "Dependency", *args, **kwargs) -> bool:
        """
        Load the Dependency.
        This will always return without throwing errors.
        If unsuccessfull, attempting to access .Value will raise an error with more details.
        """
        
        try:
            self.__value = self._load(*args, **kwargs)
            self.__loaded = True
            self.__valid = True
        except Exception as e:
            self.__loaded = False
            self.__valid = False
            self.__error_details = str(e.with_traceback(None))

        try:
            self._validate(*args, **kwargs)
            self.__valid = True
        except Exception as e:
            self.__valid = False
            self.__error_details = str(e.with_traceback(None))

        return self.__loaded and self.__valid

    @abstractmethod
    def _load(self: "Dependency", *args, **kwargs) -> None:
        """
        Load the dependency. Raise an error if this fails.
        """
        raise NotImplementedError()
    
    @abstractmethod
    def _validate(self: "Dependency", *args, **kwargs) -> None:
        """
        Validate the loaded dependency. Raise an error if this fails.
        """
        raise NotImplementedError()



class LibraryDependency(Dependency):
    """
    Importable code namespace.
    """

    def __init__(self: "LibraryDependency", name: str):
        super().__init__(name)
    
    def _load(self: "Dependency", *args, **kwargs) -> None:
        """
        Load the library. Raises an error if this fails.
        """
        
        return importlib.import_module(self.Name)
    
    def _validate(self: "Dependency", *args, **kwargs) -> None:
        """
        Validate the library is accessable. Raises an error if this fails.
        """
        
        assert isinstance(self.Value, type(importlib)), "Target was not a valid module."
        
    #@property
    #def Value(self: "Dependency") -> "module":
    #    return super().Value



class CallableDependency(Dependency):
    """
    Loadable, function or callable object.

    Constructor Parameters:
                              [str] name           -> Human redable name.

        [str | Function | Callable] target         -> Target function reference or membership path relitive to the specified namespace root.

                       [str | None] namespace_root -> Namespace to load target from. Specify as an empty string if no module import is required (e.g. for the \"print\" function).
    """

    def __init__(self: "CallableDependency", name: str, target: Union[str, Callable], namespace_root: Union[str, None] = None):
        super().__init__(name)
        self.__is_direct: bool = not isinstance(target, str)
        self.__target_namespace: Union[str, None] = None
        self.__target_path_in_namespace: Union[List[str], None] = None
        self.__target: Union[Callable, None] = None

        if not self.__is_direct:
            if target[0] != "." and namespace_root is None:
                raise ValueError("No argument provided for paramiter \"namespace_root\" but target was a string. String targets require the root namespace from which they are imported.")
            
            self.__target_namespace = namespace_root if namespace_root is not None else ""
            self.__target_path_in_namespace = target.lstrip(".").split(".")

        else:
            if not callable(target):
                raise TypeError("Invalid argument datatype provided for paramiter \"target\". Must be a string or callable.")
            
            self.__target = target

    def load(self: "Dependency", loaded_module_dependancies: Dict[str, object] = None, *args, **kwargs) -> bool:
        return super().load(loaded_module_dependancies if loaded_module_dependancies is not None else {}, *args, **kwargs)
    
    def _load(self: "Dependency", loaded_module_dependancies: Dict[str, object], *args, **kwargs) -> None:
        """
        Load the Python function or callable object. Raises an error if this fails.
        """
        
        if not self.__is_direct:
            try:
                target = loaded_module_dependancies[self.__target_namespace] if self.__target_namespace != "" else builtins
            except ValueError as e:
                raise ValueError(f"Callable dependance {self.Name} is either an invalid function path or required loading from a module and the module root was not provided.") from e
            for path_element in self.__target_path_in_namespace:
                target = getattr(target, path_element)
            self.__target = target

        return self.__target
    
    def _validate(self: "Dependency", *args, **kwargs) -> None:
        """
        Validate the Python function or callable object is not None and if an object, that it defines the callable behaviour. Raises an error if this fails.
        """
        
        if not callable(self.Value):
            raise TypeError("Invalid argument datatype provided for paramiter \"target\". Must be a string or callable.")
        
    @property
    def Value(self: "Dependency") -> Callable:
        return super().Value
    
    @property
    def Namespace(self: "Dependency") -> Union[str, None]:
        return self.__target_namespace



class DataDependency_Base(Dependency):
    """
    Base class for data dependancies. Inherit from this class to define custom dependancy types.
    """
    pass



class DataDependency(DataDependency_Base):
    """
    Data to be loaded from disk.
    """

    def __init__(self: "DataDependency", name: str, filepath: str, file_loader: Callable[[str], object], datatype: type = object, dimensions: Union[int, None] = None, dimension_lengths: Union[List[Union[int, None]], int, None] = None, phsyical_units: Union[List[Union[str, None]], str, None] = None):
        super().__init__(name)
        self.__filepath = filepath
        self.__file_loader = file_loader
        self.__datatype = datatype
        self.__dimensions = dimensions
        self.__dimension_lengths = dimension_lengths
        self.__physical_units = phsyical_units

        if isinstance(dimensions, int):
            if isinstance(dimension_lengths, list) and len(dimension_lengths) != dimensions:
                raise ValueError(f"The number of dimensions ({dimensions}) does not match the number of lengths provided for each dimension ({len(dimension_lengths)}). If specifying lengths, use None for dimensions of unknown length.")
            if isinstance(phsyical_units, list) and len(phsyical_units) != dimensions:
                raise ValueError(f"The number of dimensions ({dimensions}) does not match the number of physical units provided for each dimension ({len(phsyical_units)}). If specifying lengths, use None for dimensions with unknown units.")
                
        if isinstance(dimension_lengths, list) and isinstance(phsyical_units, list) and len(dimension_lengths) != len(phsyical_units):
            raise ValueError(f"The number of expected dimensions by the arguments for paramiters \"dimension_lengths\" and \"phsyical_units\" are inconsistent ({len(dimension_lengths)} and {len(phsyical_units)} respectivley).")
    
    def _load(self: "Dependency", *args, **kwargs) -> None:
        """
        Load the data. Raises an error if this fails.
        """
        
        return self.__file_loader(self.__filepath)
    
    def _validate(self: "Dependency", *args, **kwargs) -> None:
        """
        Validate the data is the right datatype and has the correct dimensions (both data and physical where appropriate). Raises an error if this fails.
        """
        
        if self.__datatype is not None:
            assert isinstance(self.Value, self.__datatype), f"The loaded data was of an unexpected datatype (was {type(self.Value)} not {self.__datatype})."

        expected_dims = self.__dimensions if self.__dimensions is not None else len(self.__dimension_lengths) if isinstance(self.__dimension_lengths, list) else len(self.__physical_units) if isinstance(self.__physical_units, list) else None
        if expected_dims is not None:
            d = 0
            test = self.Value
            while isinstance(test, collections.abc.Iterable) and not isinstance(test, (str, bytes, unyt.unyt_quantity)) and not (isinstance(test, np.ndarray) and test.shape != tuple()):
                test = test[0]
                d += 1
            assert d == expected_dims, f"The loaded data contained an unexpected number of dimensions (was {d} not {expected_dims})."

        if self.__dimension_lengths is not None:
            if isinstance(self.__dimension_lengths, list):
                test = self.Value
                for i, dim_len in enumerate(self.__dimension_lengths):
                    if dim_len is None:
                        continue
                    assert len(test) == dim_len, f"The loaded data contained an unexpected number of elements in dimension {i}. Length (was {len(test)} not {dim_len})"
                    test = test[0]
            else:
                d = 0
                test = self.Value
                while isinstance(test[0], collections.abc.Iterable) and not isinstance(test[0], (str, bytes, unyt.unyt_quantity)) and not (isinstance(test, np.ndarray) and test.shape != tuple()):
                    assert len(test) == self.__dimension_lengths, f"The loaded data contained an unexpected number of elements in dimension {d}. Length (was {len(test)} not {self.__dimension_lengths})"
                    test = test[0]
                    d += 1

        if self.__physical_units is not None:
            if isinstance(self.Value, (unyt.unyt_array, unyt.unyt_quantity)):
                if isinstance(self.__physical_units, list):
                    pass
                else:
                    assert self.Value.units == self.__physical_units, f"Units of the loaded data are present, but are \"{self.Value.units}\", wich does not match \"{self.__physical_units}\"."
            else:
                raise TypeError("Loaded data was not a unyt data structure but units were expected.")



class HDF5_DataDependency(DataDependency_Base):
    """
    Data to be loaded from an hdf5 file on disk.
    """

    def __init__(self: "DataDependency", name: str, filepath: str, expected_data_paths: List[str] = None):
        super().__init__(name)
        self.__filepath: str = filepath
        self.__expected_data_paths: List[str] = expected_data_paths if expected_data_paths is not None else []
    
    def _load(self: "Dependency", *args, **kwargs) -> None:
        """
        Load the data. Raises an error if this fails.
        """

        assert h5py.is_hdf5(self.__filepath), f"Filepath provided for {self.Name} was not a valid hdf5 file."
        
        return load_from_hdf5(self.__filepath)
    
    def _validate(self: "Dependency", *args, **kwargs) -> None:
        """
        Validate the data is the right datatype and has the correct dimensions (both data and physical where appropriate). Raises an error if this fails.
        """

        for path in self.__expected_data_paths:
            assert path in self.Value, "hdf5 file did not contain the path \"{path}\"."
        
    @property
    def Value(self: "Dependency") -> h5py.File:
        return super().Value



def load_from_pickle(filepath) -> object:
    """
    WARNING: Pickle files can be used maliciousley! Only read from a pickle file that you trust (i.e. have created yourself).

    Load data from a pickle file.
    """
    
    data = None
    with open(filepath, "rb") as f:
        data = pickle.load(f)
    return data



def load_from_hdf5(filepath) -> h5py.File:
    """
    Load data from an hdf5 file.
    """
    
    return h5py.File(filepath)
