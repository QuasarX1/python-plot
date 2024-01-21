from pythonplot import __version__

HELP_INFO = f"""
Help information for python-plot (version {__version__}):

pplot
    Displays the welcome message and breif command reference.

pplot-help | help-pplot
    Display the help information (this). Contains the information on paramiters for each command.

pplot-config
    Configure the default settings for this instance of python-plot.

pplot-new [-f filename] [-n namespace]
    Create a new plot automation definition.
    filename -> (optional)
                Name to give the new automation file.
                Can include a file path.
                Names without extension will be given the ".autoplot" file extension.
    namespace -> (optional)
                 Namespace to assign the new automation file.

pplot-copy | pplot-cp <source> <destination> [-n new-namespace]
    Copy an automation.
    This assigns the copy a new identifier to prevent confusion when loading multiple files.
    source -> Target automation file to copy.
    destination -> Location of the new automation file.
                   Include file name to name the new file.
    new-namespace -> (optional)
                     Namespace to assign the copied automation file.

pplot-namespaces <target>
    Checks for namespace conflicts and lists all included namespaces for a target.
    target -> Target automation file.

pplot-test <target>
    Test that all nessessary dependancies for a definition can be loaded.
    - SHOULD not actually load any data or create any plots (assuming target functions are correctly written).
    - May create a log file.
    target -> Target automation file.

pplot-run <target>
    Run an automation. These are usually a .autoplot file.
    target -> Target automation file (must be valid).

pplot-log <target>
    Returns the filepath of a log (default latest) for an automation. View with your prefered tool.
    target -> Target automation file (must be valid).
"""

def main():
    print(HELP_INFO)
