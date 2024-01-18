"""
python-plot © Christopher Rowe 2023

Project Source: https://github.com/QuasarX1/python-plot

Version: 0.0.1



This Python package defines the following commands:

    pplot
        Displays this. Welcome! If this is your first usage, see the help command below and the project source above for how to get started.

    pplot-help | help-pplot
        Display the help information. Contains the information on paramiters for each command.

    pplot-config
        Configure the default settings for this instance of python-plot.

    pplot-new [filename [namespace]]
        Create a new plot automation definition.

    pplot-cp <source> <destination> [new-namespace]
        Copy an automation.
        This assigns the copy a new identifier to prevent confusion when loading multiple files.

    pplot-namespaces <target>
        Checks for namespace conflicts and lists all included namespaces for a target.

    pplot-test <target>
        Test that all nessessary dependancies for a definition can be loaded.
        - SHOULD not actually load any data or create any plots (assuming target functions are correctly written).
        - May create a log file.

    pplot-run <target>
        Run an automation. These are usually a .autoplot file.

    pplot-log <target>
        Returns the filepath of a log (default latest) for an automation. View with your prefered tool.
"""

from . import testscript

from . import Dependencies
from .Dependencies import LibraryDependency, CallableDependency, DataDependency, HDF5_DataDependency

from ._temp import load_config as pconfig#TODO: update this
