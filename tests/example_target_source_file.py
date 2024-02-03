import h5py as h5
import numpy as np
from QuasarCode import Console

def read_n_elements(file: h5.File) -> int:
    return int(file["dataset_1"]["n_random_elements"][:])

def generate_random_data(n_elements: int):
    return np.random.standard_normal(size = n_elements)

def hello_world():
    Console.print_warning("Hello world!")
