from .__about__ import __version__
import datetime

__doc__ = f"""
python-plot © Christopher Rowe {datetime.datetime.now().year}

Version: {__version__}

Project Source: https://github.com/QuasarX1/python-plot

This Python package defines the following commands:

    pplot
        Displays this. Welcome!
        If this is your first time using this software, see the help command below and the project source above for how to get started.

    pplot-help | help-pplot
        Display the help information. Contains the information on paramiters for each command.

    pplot-config

    pplot-new [-f filename] [-n namespace]

    pplot-cp | pplot-cp <source> <destination> [-n new-namespace]

    pplot-namespaces <target>

    pplot-test <target>

    pplot-run <target>

    pplot-log <target>
"""

try:

    from . import Dependencies, Plotting, Configuration
    from .Dependencies import LibraryDependency, CallableDependency, DataDependency, HDF5_DataDependency
    from .Configuration import load_config, Config
    from .Plotting import PlotDefinition, ExcecutionPlan, Autoploter

except Exception as e:
    raise RuntimeError("\n\nUnable to load pythonplot package. Ensure all dependancies are installed in the current environment. If the issue persists, please raise an issue on the project GitHub (see the PyPI listing for a link). Make sure to include your current version of the software and Python as well as the above error traceback.") from e
