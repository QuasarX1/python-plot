from pythonplot import DataDependency
import csv
import typing

def load_csv_ints(filepath):
    data = []

    with open(filepath, "r") as file:
        reader = csv.reader(file)
        for line in reader:
            data.append([int(v) for v in line])

    return data

def test_valid():
    dep = DataDependency("data", "tests/example_data.csv", load_csv_ints)
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid
    data = dep.Value
    assert data == [[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]]

def test_valid_datatype():
    dep = DataDependency("data", "tests/example_data.csv", load_csv_ints, datatype = list)
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid
    data = dep.Value
    assert data == [[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]]

def test_valid_dimensions():
    dep = DataDependency("data", "tests/example_data.csv", load_csv_ints, dimensions = 2)
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid
    data = dep.Value
    assert data == [[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]]

def test_valid_dimension_lengths():
    dep = DataDependency("data", "tests/example_data.csv", load_csv_ints, dimension_lengths = [2, 5])
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid
    data = dep.Value
    assert data == [[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]]

def test_invalid_no_file():
    dep = DataDependency("data", "not_a_file", load_csv_ints)
    dep.load()
    assert dep.IsLoaded == False
    assert dep.IsValid == False

def test_invalid_wrong_datatype():
    dep = DataDependency("data", "tests/example_data.csv", load_csv_ints, datatype = bool)
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid == False

def test_invalid_wrong_number_of_dimensions_too_small():
    dep = DataDependency("data", "tests/example_data.csv", load_csv_ints, dimensions = 1)
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid == False

def test_invalid_wrong_number_of_dimensions_too_large():
    dep = DataDependency("data", "tests/example_data.csv", load_csv_ints, dimensions = 3)
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid == False

def test_invalid_wrong_dimension_lengths():
    dep = DataDependency("data", "tests/example_data.csv", load_csv_ints, dimension_lengths = [2, 2])
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid == False