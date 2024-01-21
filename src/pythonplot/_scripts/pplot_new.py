import pythonplot
from QuasarCode.Tools import ScriptWrapper
from typing import Union

def __main(filename: str, namespace: Union[str, None]):
    raise NotImplementedError()
    #TODO: validate file name
    #TODO: add file extension to extensionless file name
    pythonplot.Config.create_new(filename, namespace)

def main():
    script = ScriptWrapper("pplot-new",
                           "Christopher Rowe",
                           "1.0.0",
                           "21/01/2024",
                           "Create a new plot automation definition.",
                           ["pythonplot"],
                           [""],
                           [],
                           [["filename", "f", "", False, False, None, "new_plot_automation.autoplot"],
                            ["namespace", "n", "", False, False, None, None]])
    script.run(__main)
