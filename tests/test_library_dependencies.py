from pythonplot import LibraryDependency

def test_valid():
    dep = LibraryDependency("numpy")
    dep.load()
    assert dep.IsLoaded
    assert dep.IsValid
    numpy = dep.Value
    assert list(numpy.array([0, 1, 2], dtype = int)) == [0, 1, 2]

def test_invalid():
    dep = LibraryDependency("not_avalible")
    dep.load()
    assert dep.IsLoaded == False
    assert dep.IsValid == False