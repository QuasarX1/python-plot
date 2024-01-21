from enum import Enum

class Requirement(Enum):
    """
    Is a field a required field or is it optional?
    """

    REQUIRED = 0
    OPTIONAL = 1

FIELDS = {
             "namespace": Requirement.REQUIRED,
                  "uuid": Requirement.REQUIRED,
             "logs_path": Requirement.REQUIRED,
          "file_version": Requirement.REQUIRED,
         "pplot_version": Requirement.REQUIRED,
               "imports": Requirement.REQUIRED,
             "disk_data": Requirement.REQUIRED,
        "processed_data": Requirement.REQUIRED,
             "functions": Requirement.REQUIRED,
                 "plots": Requirement.REQUIRED,

           "output_root": Requirement.OPTIONAL,
    "required_externals": Requirement.OPTIONAL,
      "target_externals": Requirement.OPTIONAL,
}
