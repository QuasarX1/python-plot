from pythonplot import CallableDependency
import numpy as np

def test_valid_passed_func():
    dep = CallableDependency("testfunc", lambda x: x**2)
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid
    func = dep.Value
    assert func(7) == 49

def test_valid_local_from_string():
    dep = CallableDependency("testfunc", ".int")
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid
    func = dep.Value
    assert func("123") == 123

def test_valid_imported_from_string():
    dep = CallableDependency("testfunc", "array", "numpy")
    dep.load({ "numpy": np })
    assert dep.IsLoaded
    assert dep.IsValid
    func = dep.Value
    assert list(func([1, 2, 3], dtype = int)) == [1, 2, 3]

def test_invalid_module():
    dep = CallableDependency("testfunc", "not a function!", "nonexistant_module")
    dep.load()
    assert dep.IsLoaded == False
    assert dep.IsValid == False

def test_invalid_func():
    dep = CallableDependency("testfunc", "not a function!", "numpy")
    dep.load()
    assert dep.IsLoaded == False
    assert dep.IsValid == False