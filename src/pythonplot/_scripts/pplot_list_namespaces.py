import pythonplot
from QuasarCode import Console
from QuasarCode.Tools import ScriptWrapper
import os

def __main(target: str):
    if not os.path.exists(target):
        Console.print_error(f"No file at \"{target}\"")

    cfg = pythonplot.Config.from_file(target)

    print(cfg.create_namespace_report(ids = True, filepaths = True))

def main():
    script = ScriptWrapper("pplot-namespaces",
                           "Christopher Rowe",
                           "1.0.0",
                           "21/01/2024",
                           "Checks for namespace conflicts and lists all included namespaces for a target.",
                           ["pythonplot"],
                           [""],
                           [["target", "", None]],
                           [])
    script.run(__main)
