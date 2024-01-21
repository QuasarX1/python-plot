#import pythonplot
from QuasarCode import Console
from QuasarCode.Tools import ScriptWrapper
from typing import Union
import os

def __main(source: str, destination: str, new_namespace: Union[str, None]):
    raise NotImplementedError()

    if not os.path.valid(source):
        Console.print_error(f"Invalid filepath \"{source}\"")
    if not os.path.exists(source):
        Console.print_error(f"No file at \"{source}\"")

    if not os.path.valid(destination):
        Console.print_error(f"Invalid filepath \"{destination}\"")

    destination_path_chunks = destination.split(os.sep)
    if destination_path_chunks[-1] == "": # Path is a directory - add a filename
        source_file_name = source.split(os.sep)[-1]
        test_target = os.path.join(destination, source_file_name)
        if os.path.exists(test_target):
            source_file_name_chunks = source_file_name_chunks.rsplit(".", maxsplit = 1)
            if len(source_file_name_chunks) == 1:
                source_file_name_chunks.append("")
            counter = 1
            while os.path.exists(test_target):
                test_target = os.path.join(destination, source_file_name_chunks[0], f"_{counter}", source_file_name_chunks[1])
                counter += 1

    with open(source, "r") as file:
        with open(destination, "w") as target_file:
            target_file.write(file.read())

    if new_namespace is not None:
        pass#TODO: update namespace

def main():
    script = ScriptWrapper("pplot-copy",
                           "Christopher Rowe",
                           "1.0.0",
                           "21/01/2024",
                           "Copy an automation.",
                           ["pythonplot"],
                           [""],
                           [["source", "", None],
                            ["destination", "", None]],
                           [["new-namespace", "n", "", False, False, None, None]])
    script.run(__main)
